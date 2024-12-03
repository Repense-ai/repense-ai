import io
import base64

from typing import Any, Dict, List, Union

from together import Together
from repenseai.utils.logs import logger

from PIL import Image


class ChatAPI:
    def __init__(
        self,
        api_key: str,
        model: str = "databricks/dbrx-instruct",
        temperature: float = 0.0,
        max_tokens: int = 3500,
        stream: bool = False,
    ):
        
        self.model = model
        self.temperature = temperature
        self.stream = stream
        self.max_tokens = max_tokens

        self.response = None
        self.tokens = None

        self.client = Together(api_key=api_key)

    def call_api(self, prompt: Union[List[Dict[str, str]], str]) -> None:
        json_data = {
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "stream": self.stream,
            "stream_options": {"include_usage": True},
        }

        if isinstance(prompt, list):
            json_data["messages"] = prompt
        else:
            json_data["messages"] = [{"role": "system", "content": prompt}]

        try:
            self.response = self.client.chat.completions.create(**json_data)

            if not self.stream:
                self.tokens = self.get_tokens()
                return self.get_text()

            return self.response

        except Exception as e:
            logger(f"Erro na chamada da API - modelo {json_data['model']}: {e}")

    def get_response(self) -> Any:
        return self.response

    def get_text(self) -> Union[None, str]:
        if self.response is not None:
            return self.response.model_dump()["choices"][0]["message"]["content"]
        else:
            return None

    def get_tokens(self) -> Union[None, str]:
        if self.response is not None:
            return self.response.model_dump()["usage"]
        else:
            return None

    def process_stream_chunk(self, chunk: Any) -> Union[str, None]:
        if chunk.choices:
            content = chunk.choices[0].delta.content
            if content:
                return content
            else:
                self.tokens = chunk.model_dump()["usage"]
        else:
            if chunk.model_dump()["usage"]:
                self.tokens = chunk.model_dump()["usage"]


class AudioAPI:
    def __init__(self, api_key: str, model: str = ""):
        self.client = Together(api_key=api_key)
        self.model = model

    def call_api(self, audio: io.BufferedReader):
        _ = audio

        return "Not Implemented"

    def get_tokens(self):
        return {"completion_tokens": 0, "prompt_tokens": 0, "total_tokens": 0}


class VisionAPI:
    def __init__(
        self,
        api_key: str,
        model: str = "",
        temperature: float = 0.0,
        max_tokens: int = 3500,
        stream: bool = False,
    ):
        self.client = Together(api_key=api_key)
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.stream = stream

        self.response = None
        self.tokens = None

    def resize_image(self, image: Image.Image) -> Image.Image:
        max_size = 1568
        min_size = 200
        width, height = image.size

        if max(width, height) > max_size:
            aspect_ratio = width / height
            if width > height:
                new_width = max_size
                new_height = int(new_width / aspect_ratio)
            else:
                new_height = max_size
                new_width = int(new_height * aspect_ratio)
            image = image.resize((new_width, new_height))
        elif min(width, height) < min_size:
            aspect_ratio = width / height
            if width < height:
                new_width = min_size
                new_height = int(new_width / aspect_ratio)
            else:
                new_height = min_size
                new_width = int(new_height * aspect_ratio)
            image = image.resize((new_width, new_height))

        return image

    def process_image(self, image: Any) -> bytearray:
        if isinstance(image, str):
            return image
        elif isinstance(image, Image.Image):
            img_byte_arr = io.BytesIO()

            image = self.resize_image(image)
            image.save(img_byte_arr, format="PNG")

            img_byte_arr = img_byte_arr.getvalue()

            image_string = base64.b64encode(img_byte_arr).decode("utf-8")

            return image_string
        else:
            raise Exception("Incorrect image type! Accepted: img_string or Image")

    def call_api(self, prompt: str, image: Any):

        content = [{"type": "text", "text": prompt}]

        if isinstance(image, str) or isinstance(image, Image.Image):
            image = self.process_image(image)
            content.append(
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{image}",
                        "detail": "high",
                    },
                },
            )
        elif isinstance(image, list):
            for img in image:
                img = self.process_image(img)
                content.append(
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{img}",
                            "detail": "high",
                        },
                    },
                )
        else:
            raise Exception(
                "Incorrect image type! Accepted: img_string or list[img_string]"
            )

        json_data = {
            "model": self.model,
            "messages": [{"role": "user", "content": content}],
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "stream": self.stream,
            "stream_options": {"include_usage": True},
        }

        try:
            self.response = self.client.chat.completions.create(**json_data)

            if not self.stream:
                self.tokens = self.get_tokens()
                return self.get_text()

            return self.response
        except Exception as e:
            logger(f"Erro na chamada da API - modelo {json_data['model']}: {e}")

    def get_text(self) -> Union[None, str]:
        if self.response is not None:
            return self.response.model_dump()["choices"][0]["message"]["content"]
        else:
            return None

    def get_tokens(self) -> Union[None, str]:
        if self.response is not None:
            return self.response.model_dump()["usage"]
        else:
            return None

    def process_stream_chunk(self, chunk: Any) -> Union[str, None]:
        if chunk.choices:
            content = chunk.choices[0].delta.content
            if content:
                return content
            else:
                self.tokens = chunk.model_dump()["usage"]
        else:
            if chunk.model_dump()["usage"]:
                self.tokens = chunk.model_dump()["usage"]


class ImageAPI:
    def __init__(
            self, 
            api_key: str, 
            model: str = "", 
            aspect_ratio: str = '1:1',
            **kwargs,
        ):

        self.client = Together(api_key=api_key)

        self.model = model
        self.aspect_ratio = aspect_ratio

        self.allowed_ar = [
            '16:9', '1:1', '2:3',
            '3:2', '4:5', '5:4', '9:16'
        ]

        self.response = None
        self.tokens = None

        self.ratio = self.__check_aspect_ratio()

    def __check_aspect_ratio(self):

        if self.aspect_ratio not in self.allowed_ar:
            self.aspect_ratio = '1:1'

        sizes = {
            '16:9': {'width': 1024, 'height': 576},
            '1:1': {'width': 512, 'height': 512},
            '2:3': {'width': 512, 'height': 768},
            '3:2': {'width': 768, 'height': 512},
            '4:5': {'width': 512, 'height': 640},
            '5:4': {'width': 640, 'height': 512},
            '9:16': {'width': 576, 'height': 1024},
        }
        
        return sizes[self.aspect_ratio]

    def call_api(self, prompt: Any, image: Any = None):

        _ = image

        payload = {
            "prompt": prompt,
            "model": self.model,
            "width": self.ratio["width"],
            "height": self.ratio["height"],
            "response_format": "b64_json",
            "steps": 1,
            "n": 1,
        }

        self.response = self.client.images.generate(**payload)
        self.tokens = self.get_tokens()

        return self.get_image()
    
    def get_image(self):
        return self.response.data[0].b64_json

    def get_tokens(self):
        completion_tokens = self.ratio["width"] * self.ratio["height"]
        prompt_tokens = 0

        return {
            "completion_tokens": completion_tokens, 
            "prompt_tokens": prompt_tokens, 
            "total_tokens": prompt_tokens + completion_tokens,
        }