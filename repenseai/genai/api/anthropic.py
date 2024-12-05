import base64
import io
from typing import Any, Dict, List, Union

from anthropic import Anthropic

from PIL import Image
from repenseai.utils.logs import logger


class ChatAPI:
    def __init__(
        self,
        api_key: str,
        model: str = "claude-3-haiku-20240307",
        temperature: float = 0.0,
        max_tokens: int = 3500,
        stream: bool = False,
    ):
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.stream = stream

        self.response = None
        self.tokens = None

        self.client = Anthropic(api_key=self.api_key)

    def _stream_api_call(self, json_data: Dict[str, Any]) -> Any:
        with self.client.messages.stream(**json_data) as stream:
            for message in stream:
                yield message

    def call_api(self, prompt: Union[List[Dict[str, str]], str]) -> Any:
        json_data = {
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }

        if isinstance(prompt, list):
            json_data.update(messages=prompt)
        else:
            json_data.update(messages=[{"role": "user", "content": prompt}])

        try:
            if self.stream:
                return self._stream_api_call(json_data)

            self.response = self.client.messages.create(**json_data)
            self.tokens = self.get_tokens()

            return self.get_text()

        except Exception as e:
            logger(f"Erro na chamada da API - modelo {json_data['model']}: {e}")

    def get_response(self) -> Any:
        return self.response

    def get_text(self) -> Union[None, str]:
        if self.response is not None:
            return self.response.content[0].text
        else:
            return None

    def get_tokens(self) -> Union[None, str]:
        if self.response is not None:

            input_tokens = self.response.usage.input_tokens
            output_tokens = self.response.usage.output_tokens

            return {
                "completion_tokens": output_tokens,
                "prompt_tokens": input_tokens,
                "total_tokens": output_tokens + input_tokens,
            }
        else:
            return None

    def process_stream_chunk(self, chunk: Any) -> Union[str, None]:
        if chunk.type == "content_block_delta":
            return chunk.delta.text
        if chunk.type == "message_stop":
            usage = chunk.model_dump()["message"]["usage"]

            input_tokens = usage.get("input_tokens", 0)
            output_tokens = usage.get("output_tokens", 0)

            self.tokens = {
                "completion_tokens": output_tokens,
                "prompt_tokens": input_tokens,
                "total_tokens": output_tokens + input_tokens,
            }


class AudioAPI:
    def __init__(self, api_key: str, model: str = ""):
        self.client = Anthropic(api_key=api_key)
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
        model: str = "claude-3-sonnet-20240229",
        temperature: float = 0.0,
        max_tokens: int = 3500,
        stream: bool = False,
    ):
        self.client = Anthropic(api_key=api_key)
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.stream = stream

        self.response = None
        self.tokens = None

    def _stream_api_call(self, json_data: Dict[str, Any]) -> Any:
        with self.client.messages.stream(**json_data) as stream:
            for message in stream:
                yield message

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

    def call_api(self, prompt: str | list, image: Any):

        if isinstance(prompt, str):
            content = [{"type": "text", "text": prompt}]
        else:
            content = prompt[-1].get("content", [])

        if isinstance(image, str) or isinstance(image, Image.Image):
            img = self.process_image(image)
            img_dict = {
                "type": "image",
                "source": {
                    "data": img,
                    "type": "base64",
                    "media_type": "image/png",
                },
            }

            content.insert(0, img_dict)

        elif isinstance(image, list):

            for img in image:

                img = self.process_image(img)
                img_dict = {
                    "type": "image",
                    "source": {
                        "data": img,
                        "type": "base64",
                        "media_type": "image/png",
                    },
                }

                content.insert(0, img_dict)
        else:
            raise Exception(
                "Incorrect image type! Accepted: img_string or list[img_string]"
            )
        
        if isinstance(prompt, list):
            prompt[-1] = {"role": "user", "content": content}
        else:
            prompt = [{"role": "user", "content": content}]

        json_data = {
            "model": self.model,
            "messages": prompt,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
        }

        try:
            if self.stream:
                return self._stream_api_call(json_data)

            self.response = self.client.messages.create(**json_data)
            self.tokens = self.get_tokens()

            return self.get_text()
        except Exception as e:
            logger(f"Erro na chamada da API - modelo {json_data['model']}: {e}")

    def get_text(self) -> Union[None, str]:
        if self.response is not None:
            return self.response.content[0].text
        else:
            return None

    def get_tokens(self) -> Union[None, str]:
        if self.response is not None:

            input_tokens = self.response.usage.input_tokens
            output_tokens = self.response.usage.output_tokens

            return {
                "completion_tokens": output_tokens,
                "prompt_tokens": input_tokens,
                "total_tokens": output_tokens + input_tokens,
            }
        else:
            return None

    def process_stream_chunk(self, chunk: Any) -> Union[str, None]:
        if chunk.type == "content_block_delta":
            return chunk.delta.text
        if chunk.type == "message_stop":
            usage = chunk.model_dump()["message"]["usage"]

            input_tokens = usage.get("input_tokens", 0)
            output_tokens = usage.get("output_tokens", 0)

            self.tokens = {
                "completion_tokens": output_tokens,
                "prompt_tokens": input_tokens,
                "total_tokens": output_tokens + input_tokens,
            }


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