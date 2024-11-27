import os
import importlib
import typing as tp

from repenseai.aws.secrets_manager import SecretsManager

from repenseai.config.selection_params import (
    TEXT_MODELS,
    VISION_MODELS,
    IMAGE_MODELS,
    VIDEO_MODELS,
    SEARCH_MODELS,
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
            "search": SEARCH_MODELS,
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

    def get_api_key(self, secret_name: str = "genai", region_name: str = "us-east-2"):
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
        self, secret_name: str = "genai", region_name: str = "us-east-2", **kwargs
    ):
        api_key = self.get_api_key(secret_name, region_name)

        match self.model_type:
            case "chat" | "search":
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
            case "image":
                self.api = self.module_api.ImageAPI(
                    api_key=api_key, model=self.model, **kwargs
                )                
            case _:
                raise Exception(self.model_type + " API not found")

        return self.api

    def calculate_cost(
        self, tokens: tp.Dict[str, int], as_string: str = False
    ) -> tp.Union[float, str]:
        
        if not tokens:
            return 0

        if isinstance(tokens, dict):
            if isinstance(self.price, dict):
                input_cost = tokens["prompt_tokens"] * self.price["input"]
                output_cost = tokens["completion_tokens"] * self.price["output"]

                total = (input_cost + output_cost) / 1_000_000

            else:
                input_cost = tokens["prompt_tokens"] * self.price
                output_cost = tokens["completion_tokens"] * self.price

                total = (input_cost + output_cost) / 1_000_000
        else:
            total = self.price * tokens
            
        if as_string:
            return f"U${total:.5f}"

        return total
        
        
