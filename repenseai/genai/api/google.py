import time
from typing import Any, List, Union, Dict

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

    def _process_str_prompt(self, prompt: str) -> str:
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

    def _process_list_prompt(self, prompt: List[Dict[str, str]]) -> str:
        self.prompt = prompt[-1].get("content", [{}])[0].get("text", "")

        history = []

        for message in prompt[:-1]:
            history.append(
                {
                    "role": "user" if message.get("role") == "user" else "model",
                    "parts": message.get("content", [{}])[0].get("text", "")
                }
            )

        chat = self.client.start_chat(history=history)

        self.response = chat.send_message(
            self.prompt,
            stream=self.stream,
            generation_config=self.config,
        )

        if not self.stream:
            self.tokens = self.get_tokens()
            return self.get_text()
        
        return self.response              

    def call_api(self, prompt: Union[List[Dict[str, str]], str]):

        if isinstance(prompt, str):
            return self._process_str_prompt(prompt)
        else:
            return self._process_list_prompt(prompt)


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

        return "Not implemented"

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

    def call_api(self, prompt: str | list, image: Union[Any, List[Any]]):
        if isinstance(prompt, list):
            self.prompt = prompt[-1]["content"][0].get("text", "")  
        else:      
            self.prompt = prompt
            
        self.image = image

        json_data = {
            "stream": self.stream,
            "generation_config": self.config,
        }

        if isinstance(image, list):
            json_data["contents"] = [self.prompt] + self.image
        else:
            json_data["contents"] = [self.prompt, self.image]

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


class ImageAPI:
    def __init__(self, api_key: str, model: str = "", **kwargs):
        self.api_key = api_key
        self.model = model

    def call_api(self, prompt: Any, image: Any):
        _ = image
        _ = prompt

        return "Not implemented"

    def get_tokens(self):
        return {"completion_tokens": 0, "prompt_tokens": 0, "total_tokens": 0}