import os
import importlib
import typing as tp

from repenseai.aws.secrets_manager import SecretsManager

from repenseai.config.selection_params import (
    TEXT_MODELS,
    VISION_MODELS,
    IMAGE_MODELS,
    VIDEO_MODELS,
)

from dotenv import find_dotenv, load_dotenv
load_dotenv(find_dotenv())


class APISelector:
    def __init__(self, model: str, model_type: str, api_key: str = None) -> None:
        self.model = model
        self.model_type = model_type
        self.api_key = api_key

        self.tokens = None
        self.api = None

        self.models = {
            "chat": TEXT_MODELS,
            "vision": VISION_MODELS,
            "image": IMAGE_MODELS,
            "video": VIDEO_MODELS,
        }
        
        self.__get_provider()
        self.__get_prices()
        self.__get_module()
    

    def __get_provider(self) -> None:

        if self.model_type not in self.models:
            raise Exception("Model type not found")
        
        models_dict = self.models[self.model_type]

        self.provider = models_dict[self.model]["provider"]

    def __get_prices(self) -> None:
        models_dict = self.models[self.model_type]
        self.price = models_dict[self.model]["cost"]

    def __get_module(self) -> None:
        api_str = f"repenseai.genai.api.{self.provider}"
        self.module_api = importlib.import_module(api_str)

    def get_api_key(
        self, 
        secret_name: str = "genai", 
        region_name: str = "us-east-2"
    ):
        if not self.api_key:
            string = f"{self.provider.upper()}_API_KEY"
            api_key = os.getenv(string)

            if api_key:
                return api_key
            
            try:
                secret_manager = SecretsManager(
                    secret_name=secret_name, 
                    region_name=region_name,
                )

                api_key = secret_manager.get_secret(string)
                return api_key
            except Exception:
                return None   
        return self.api_key

    def get_api(
        self,         
        secret_name: str = "genai", 
        region_name: str = "us-east-2",
        **kwargs
    ):
        api_key = self.get_api_key(secret_name, region_name)

        match self.model_type:
            case "chat":
                self.api = self.module_api.ChatAPI(
                    api_key=api_key, model=self.model, **kwargs
                )
            case "vision":
                self.api = self.module_api.VisionAPI(
                    api_key=api_key, model=self.model, **kwargs
                )
            case "audio":
                self.api = self.module_api.AudioAPI(
                    api_key=api_key, model=self.model, **kwargs
                )
            case _:
                raise Exception(self.model_type + " API not found")
            
        return self.api

    def process_stream_chunk(self, chunk: tp.Any) -> tp.Union[str, None]:
        match self.provider:
            case "anthropic":
                if chunk.type == "content_block_delta":
                    return chunk.delta.text
                if chunk.type == 'message_stop':
                    usage = chunk.model_dump()['message']['usage']

                    input_tokens = usage.get("input_tokens", 0)
                    output_tokens = usage.get("output_tokens", 0)

                    self.tokens = {
                        "completion_tokens": output_tokens,
                        "prompt_tokens": input_tokens,
                        "total_tokens": output_tokens + input_tokens,
                    }
            case "cohere":
                if chunk.type == "content-delta":
                    return chunk.delta.message.content.text
                elif chunk.type == "message-end":
                    usage = chunk.model_dump()['delta']['usage']["tokens"]

                    input_tokens = usage.get("input_tokens", 0)
                    output_tokens = usage.get("output_tokens", 0)

                    self.tokens = {
                        "completion_tokens": output_tokens,
                        "prompt_tokens": input_tokens,
                        "total_tokens": output_tokens + input_tokens,
                    }
            case "google":
                if chunk.usage_metadata.candidates_token_count == 0:
                    return chunk.text
                else:
                    input_tokens = chunk.usage_metadata.prompt_token_count
                    output_tokens = chunk.usage_metadata.candidates_token_count

                    self.tokens = {
                        "completion_tokens": output_tokens,
                        "prompt_tokens": input_tokens,
                        "total_tokens": output_tokens + input_tokens,
                    }

                    return chunk.text
            case "mistral":
                if chunk.data.usage:
                    self.tokens = chunk.data.model_dump()["usage"]
                else:
                    return chunk.data.choices[0].delta.content
            case _:
                if chunk.choices:
                    content = chunk.choices[0].delta.content
                    if content:
                        return content
                    else:
                        if chunk.model_dump().get('x_groq', {}).get('usage'):
                            self.tokens = chunk.model_dump()['x_groq']['usage']
                        else:
                            self.tokens = chunk.model_dump()['usage']
                else:
                    if chunk.model_dump()['usage']:
                        self.tokens = chunk.model_dump()['usage']


    def get_costs(self, as_string: str = False) -> tp.Union[float, str]:
        input_cost = self.tokens["prompt_tokens"] * self.price["input"]
        output_cost = self.tokens["completion_tokens"] * self.price["output"]

        total = (input_cost + output_cost) / 1_000_000

        if as_string:
            return f"U${total:.5f}"
        
        return total


