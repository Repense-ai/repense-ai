import time
from typing import Any, List, Union

import google.generativeai as genai


class ChatAPI:
    def __init__(
        self,
        api_key: str,
        model: str = "gemini-1.5-pro-latest",
        temperature: float = 0.0,
        max_tokens: int = 3500,
        stream: bool = False,
    ):

        self.api_key = api_key
        self.stream = stream

        self.response = None
        self.tokens = None

        genai.configure(api_key=self.api_key)

        self.model = model

        self.client = genai.GenerativeModel(self.model)

        self.config = genai.types.GenerationConfig(
            candidate_count=1,
            temperature=temperature,
            max_output_tokens=max_tokens,
        )

    def call_api(self, prompt: str):

        self.prompt = prompt

        self.response = self.client.generate_content(
            self.prompt,
            stream=self.stream,
            generation_config=self.config,
        )

        if not self.stream:
            self.tokens = self.get_tokens()
            return self.get_text()
        
        return self.response

    def get_response(self) -> Any:
        return self.response

    def get_text(self) -> Union[None, str]:
        if self.response is not None:
            return self.response.text
        else:
            return None

    def get_tokens(self) -> Union[None, str]:
        if self.response is not None:

            input_tokens = self.client.count_tokens(self.prompt).total_tokens
            output_tokens = self.client.count_tokens(self.response.text).total_tokens

            return {
                "completion_tokens": output_tokens,
                "prompt_tokens": input_tokens,
                "total_tokens": output_tokens + input_tokens,
            }
        else:
            return None

    def process_stream_chunk(self, chunk: Any) -> str:
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


class AudioAPI:
    def __init__(self, api_key: str, model: str = ""):
        self.api_key = api_key
        self.model = model

    def call_api(self, audio: Any):
        _ = audio

        return "Not inplemented"

    def get_tokens(self):
        return {"completion_tokens": 0, "prompt_tokens": 0, "total_tokens": 0}


class VisionAPI:
    def __init__(
        self,
        api_key: str,
        model: str = "gemini-pro-vision",
        temperature: float = 0.0,
        max_tokens: int = 3500,
        stream: bool = False,
    ):
        self.api_key = api_key
        self.stream = stream

        self.config = genai.types.GenerationConfig(
            candidate_count=1,
            temperature=temperature,
            max_output_tokens=max_tokens,
        )

        genai.configure(api_key=self.api_key)

        self.model = model
        self.client = genai.GenerativeModel(self.model)

        self.prompt = None
        self.image = None
        self.response = None
        self.tokens = None

    def call_api(self, prompt: str, image: Union[Any, List[Any]]):
        self.prompt = prompt
        self.image = image

        json_data = {
            "stream": self.stream,
            "generation_config": self.config,
        }

        if isinstance(image, list):
            json_data["contents"] = [prompt] + image
        else:
            json_data["contents"] = [prompt, image]

        self.response = self.client.generate_content(**json_data)

        if not self.stream:
            self.tokens = self.get_tokens()
            return self.get_text()
        
        return self.response

    def get_text(self) -> Union[None, str]:
        if self.response is not None:
            return self.response.text
        else:
            return None

    def get_tokens(self) -> Union[None, str]:
        if self.response is not None:

            prompt_input_tokens = self.client.count_tokens(self.prompt).total_tokens
            img_input_tokens = self.client.count_tokens(self.image).total_tokens

            input_tokens = prompt_input_tokens + img_input_tokens

            output_tokens = self.client.count_tokens(self.response.text).total_tokens

            return {
                "completion_tokens": output_tokens,
                "prompt_tokens": input_tokens,
                "total_tokens": output_tokens + input_tokens,
            }
        else:
            return None

    def process_stream_chunk(self, chunk: Any) -> str:
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
