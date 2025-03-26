import base64
import io

from typing import Any, Dict, List, Union

from PIL import Image

from openai import OpenAI
from repenseai.utils.logs import logger

from repenseai.genai.providers import VISION_MODELS


class ChatAPI:
    def __init__(
        self,
        api_key: str,
        model: str = "grok-beta",
        temperature: float = 0.0,
        max_tokens: int = 3500,
        stream: bool = False,
        **kwargs,
    ):
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.stream = stream
        self.max_tokens = max_tokens

        self.tool_flag = False

        self.response = None
        self.tokens = None

        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://api.x.ai/v1",
        )

    def __process_prompt_list(self, prompt: list) -> list:

        if self.model not in VISION_MODELS:
            for history in prompt:
                content = history.get("content", [])

                if content[0].get("type") == "image_url":
                    prompt.remove(history)

        return prompt

    def call_api(self, prompt: Union[List[Dict[str, str]], str]) -> None:
        json_data = {
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "stream": self.stream,
            "stream_options": {"include_usage": True},
        }

        if isinstance(prompt, list):
            json_data["messages"] = self.__process_prompt_list(prompt)
        else:
            json_data["messages"] = [{"role": "system", "content": prompt}]

        try:
            self.response = self.client.chat.completions.create(**json_data)

            if not self.stream:
                self.tokens = self.get_tokens()
                return self.get_output()

            return self.response
        except Exception as e:
            logger(f"Erro na chamada da API - modelo {json_data['model']}: {e}")

    def get_output(self) -> Union[None, str]:
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


class VisionAPI:
    def __init__(
        self,
        api_key: str,
        model: str = "",
        temperature: float = 0.0,
        max_tokens: int = 3500,
        stream: bool = False,
    ):

        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.x.ai/v1",
        )

        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.stream = stream

        self.response = None
        self.tokens = None

    def __process_image(self, image: Any) -> Any:
        if isinstance(image, str):
            if "http" in image:
                return image
            else:
                f"data:image/png;base64,{image}"
        elif isinstance(image, Image.Image):
            img_byte_arr = io.BytesIO()

            image.save(img_byte_arr, format="PNG")
            img_byte_arr = img_byte_arr.getvalue()

            image_string = base64.b64encode(img_byte_arr).decode("utf-8")

            return f"data:image/png;base64,{image_string}"
        else:
            raise Exception("Incorrect image type! Accepted: img_string or Image")

    def __create_content_image(self, image: Any) -> Dict[str, Any]:
        img = self.__process_image(image)

        img_dict = {
            "type": "image_url",
            "image_url": {
                "url": img,
                "detail": "high",
            },
        }

        return img_dict

    def __process_prompt_content(self, prompt: str | list) -> list:
        if isinstance(prompt, str):
            content = [{"type": "text", "text": prompt}]
        else:
            content = prompt[-1].get("content", [])

        return content

    def __process_content_image(self, content: list, image: Any) -> list:

        if isinstance(image, str) or isinstance(image, Image.Image):
            img = self.__create_content_image(image)
            content.append(img)

        elif isinstance(image, list):
            for img in image:
                img = self.__create_content_image(img)
                content.append(img)
        else:
            raise Exception(
                "Incorrect image type! Accepted: img_string or list[img_string]"
            )

        return content

    def __process_prompt(self, prompt: str | list, content: list) -> list:
        if isinstance(prompt, list):
            prompt[-1] = {"role": "user", "content": content}
        else:
            prompt = [{"role": "user", "content": content}]

        return prompt

    def call_api(self, prompt: str | list, image: Any):

        content = self.__process_prompt_content(prompt)
        content = self.__process_content_image(content, image)

        prompt = self.__process_prompt(prompt, content)

        json_data = {
            "model": self.model,
            "messages": prompt,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "stream": self.stream,
        }

        try:
            if self.stream:
                json_data["stream_options"] = {"include_usage": True}

            self.response = self.client.chat.completions.create(**json_data)

            if not self.stream:
                self.tokens = self.get_tokens()
                return self.get_output()

            return self.response

        except Exception as e:
            logger(f"Erro na chamada da API - modelo {json_data['model']}: {e}")

    def get_output(self) -> Union[None, str]:
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
    def __init__(self, api_key: str, model: str = "grok-2-image", **kwargs):
        self.api_key = api_key
        self.model = model

        self.response = None
        self.tokens = None

        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://api.x.ai/v1",
        )

    def call_api(self, prompt: Any, image: Any):
        _ = image

        json_data = {
            "model": self.model,
            "prompt": prompt,
            "response_format": "b64_json",
        }

        self.response = self.client.images.generate(**json_data)
        self.tokens = self.get_tokens()

        return self.get_output()

    def get_output(self):
        return self.response.data[0].b64_json

    def get_tokens(self):
        return 1


class AudioAPI:
    def __init__(self, api_key: str, model: str, **kwargs):
        self.api_key = api_key
        self.model = model

    def call_api(self, audio: Any):
        _ = audio

        return self.get_output()

    def get_output(self):
        return "Not Implemented"

    def get_tokens(self):
        return {"completion_tokens": 0, "prompt_tokens": 0, "total_tokens": 0}


class SpeechAPI:
    def __init__(self, api_key: str, model: str, **kwargs):
        self.api_key = api_key
        self.model = model

    def call_api(self, text: str) -> bytes:
        _ = text

        return self.get_output()

    def get_output(self):
        return "Not Implemented"

    def get_tokens(self):
        return 0
