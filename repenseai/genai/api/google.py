from typing import Any, List, Union

import google.generativeai as genai


class ChatAPI:
    def __init__(self, api_key: str, model: str = "gemini-1.5-pro-latest"):

        self.api_key = api_key
        genai.configure(api_key=self.api_key)

        self.model = model

        self.client = genai.GenerativeModel(self.model)
        self.config = genai.types.GenerationConfig(
            candidate_count=1,
            temperature=0.0,
        )

    def call_api(self, prompt: str):

        self.prompt = prompt

        self.response = self.client.generate_content(
            self.prompt,
            stream=False,
            generation_config=self.config,
        )

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
    def __init__(self, api_key: str, model: str = "gemini-pro-vision"):
        self.api_key = api_key

        self.config = genai.types.GenerationConfig(candidate_count=1, temperature=0.0)

        genai.configure(api_key=self.api_key)

        self.model = model
        self.client = genai.GenerativeModel(self.model)

    def call_api(self, prompt: str, image: Union[Any, List[Any]]):
        self.prompt = prompt
        self.image = image

        if isinstance(image, list):
            self.response = self.client.generate_content(
                [prompt] + image, stream=False, generation_config=self.config
            )

            return self.response.text
        else:
            self.response = self.client.generate_content(
                [prompt, image], stream=False, generation_config=self.config
            )

            return self.response.text

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
