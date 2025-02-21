from typing import Any, List, Union
from google import genai
from google.genai import types

class ChatAPI:
    def __init__(
        self,
        api_key: str,
        model: str = "gemini-2.0-flash",
        temperature: float = 0.0,
        max_tokens: int = 3500,
        stream: bool = False,
        **kwargs,
    ):
        self.api_key = api_key
        self.stream = stream
        self.response = None
        self.tokens = None
        self.tool_flag = False
        
        self.client = genai.Client(api_key=self.api_key)
        self.model = model
        
        self.config = types.GenerateContentConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
        )

    def __process_str_prompt(self, prompt: str) -> str:
        self.prompt = prompt
        content = [{"role": "user", "parts": [{"text": prompt}]}]

        if self.stream:
            self.response = self.client.models.generate_content_stream(
                model=self.model,
                contents=content,
                config=self.config,
            )
        else:
            self.response = self.client.models.generate_content(
                model=self.model,
                contents=content,
                config=self.config,
            )
            self.tokens = self.get_tokens()
            return self.get_output()
        
        return self.response

    def __process_list_prompt(self, prompt: list) -> str:
        # Convert the prompt list to the format expected by Gemini
        contents = []
        for message in prompt:
            role = "user" if message.get("role") == "user" else "model"
            text = message.get("content", [{}])[0].get("text", "")
            contents.append({
                "role": role,
                "parts": [{"text": text}]
            })

        self.prompt = contents[-1]["parts"][0]["text"]

        if self.stream:
            self.response = self.client.models.generate_content_stream(
                model=self.model,
                contents=contents,
                config=self.config,
            )
        else:
            self.response = self.client.models.generate_content(
                model=self.model,
                contents=contents,
                config=self.config,
            )
            self.tokens = self.get_tokens()
            return self.get_output()
        
        return self.response

    def call_api(self, prompt: list | str):
        if isinstance(prompt, str):
            return self.__process_str_prompt(prompt)
        else:
            return self.__process_list_prompt(prompt)

    def get_response(self) -> Any:
        return self.response

    def get_output(self) -> Union[None, str]:
        if self.response is not None:
            return self.response.text
        else:
            return None

    def get_tokens(self) -> Union[None, dict]:
        if self.response is not None:
            prompt_tokens = self.client.models.count_tokens(
                model=self.model, 
                contents=self.prompt
            ).total_tokens

            output_tokens = self.client.models.count_tokens(
                model=self.model, 
                contents=self.response.text
            ).total_tokens

            return {
                "completion_tokens": output_tokens,
                "prompt_tokens": prompt_tokens,
                "total_tokens": output_tokens + prompt_tokens,
            }
        else:
            return None

    def process_stream_chunk(self, chunk: Any) -> str:
        if not hasattr(chunk, 'candidates_token_count') or chunk.candidates_token_count == 0:
            return chunk.text
        else:
            self.tokens = {
                "completion_tokens": chunk.candidates_token_count,
                "prompt_tokens": chunk.prompt_token_count,
                "total_tokens": chunk.candidates_token_count + chunk.prompt_token_count,
            }
            return chunk.text


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
        
        self.client = genai.Client(api_key=self.api_key)
        self.model = model
        
        self.config = types.GenerateContentConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
        )

        self.prompt = None
        self.image = None
        self.response = None
        self.tokens = None

    def __process_list_prompt(self, prompt: list) -> str:
        return prompt[-1]["content"][0].get("text", "")

    def call_api(self, prompt: str | list, image: Union[Any, List[Any]]):
        if isinstance(prompt, list):
            self.prompt = self.__process_list_prompt(prompt)
        else:
            self.prompt = prompt

        self.image = image

        contents = []
        contents.append({"text": self.prompt})
        
        if isinstance(self.image, list):
            for img in self.image:
                contents.append({"image": img})
        else:
            contents.append({"image": self.image})

        if self.stream:
            self.response = self.client.models.generate_content_stream(
                model=self.model,
                contents=contents,
                config=self.config,
            )
        else:
            self.response = self.client.models.generate_content(
                model=self.model,
                contents=contents,
                config=self.config,
            )
            self.tokens = self.get_tokens()
            return self.get_output()

        return self.response

    def get_output(self) -> Union[None, str]:
        if self.response is not None:
            return self.response.text
        else:
            return None

    def get_tokens(self) -> Union[None, dict]:
        if self.response is not None:
            prompt_tokens = self.client.models.count_tokens(model=self.model, contents=self.prompt).total_tokens
            img_tokens = self.client.models.count_tokens(model=self.model, contents=self.image).total_tokens
            output_tokens = self.client.models.count_tokens(model=self.model, contents=self.response.text).total_tokens

            return {
                "completion_tokens": output_tokens,
                "prompt_tokens": prompt_tokens + img_tokens,
                "total_tokens": output_tokens + prompt_tokens + img_tokens,
            }
        else:
            return None

    def process_stream_chunk(self, chunk: Any) -> str:
        if not hasattr(chunk, 'candidates_token_count') or chunk.candidates_token_count == 0:
            return chunk.text
        else:
            self.tokens = {
                "completion_tokens": chunk.candidates_token_count,
                "prompt_tokens": chunk.prompt_token_count,
                "total_tokens": chunk.candidates_token_count + chunk.prompt_token_count,
            }
            return chunk.text


class ImageAPI:
    def __init__(self, api_key: str, model: str = "imagen-2.0", aspect_ratio: str = '1:1', **kwargs):
        self.api_key = api_key
        self.client = genai.Client(api_key=self.api_key)
        self.model = model

        self.aspect_ratio = aspect_ratio
        self.allowed_ar = [
            '16:9', '1:1', '2:3',
            '3:2', '4:5', '5:4', '9:16'
        ]
        self.__check_aspect_ratio()

        self.response = None
        self.tokens = None

    def __check_aspect_ratio(self):
        if self.aspect_ratio not in self.allowed_ar:
            self.aspect_ratio = '1:1'

    def call_api(self, prompt: Any, image: Any):
        _ = image  # Unused parameter

        self.response = self.client.models.generate_images(
            model=self.model,
            prompt=prompt,
            config=types.GenerateImagesConfig(
                number_of_images=1,
                aspect_ratio=self.aspect_ratio,
                safety_filter_level= "block_low_and_above",
                person_generation= "ALLOW_ADULT",                
            )
        )

        self.tokens = self.get_tokens()

        return self.get_output()
    
    def get_output(self):
        if images := self.response.generated_images:
            return images[0].image.image_bytes
        return None

    def get_tokens(self):
        if hasattr(self.response, 'usage_metadata'):
            return {
                "completion_tokens": self.response.usage_metadata.candidates_token_count,
                "prompt_tokens": self.response.usage_metadata.prompt_token_count,
                "total_tokens": self.response.usage_metadata.total_token_count,
            }
        return {"completion_tokens": 1, "prompt_tokens": 1, "total_tokens": 2}


class AudioAPI:
    def __init__(self, api_key: str, model: str, **kwargs):
        self.api_key = api_key
        self.model = model
        self.client = genai.Client(api_key=self.api_key)

    def call_api(self, audio: Any):
        _ = audio  # Unused parameter
        return self.get_output()
    
    def get_output(self):
        return "Not Implemented"

    def get_tokens(self):
        return {"completion_tokens": 0, "prompt_tokens": 0, "total_tokens": 0}


class SpeechAPI:
    def __init__(self, api_key: str, model: str, **kwargs):
        self.api_key = api_key
        self.model = model
        self.client = genai.Client(api_key=self.api_key)

    def call_api(self, text: str) -> bytes:
        _ = text  # Unused parameter
        return self.get_output()
    
    def get_output(self):
        return "Not Implemented"

    def get_tokens(self):
        return 0