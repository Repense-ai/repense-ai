import io
import base64

from typing import Any, Dict, List, Union

from mistralai import Mistral
from repenseai.utils.logs import logger

from PIL import Image


class ChatAPI:
    def __init__(
        self,
        api_key: str,
        model: str = "mistral-large-latest",
        temperature: float = 0.0,
        verbose=0,
    ):
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.verbose = verbose
        self.tokens = 3500
        self.response = None

        self.client = Mistral(api_key=self.api_key)

    def call_api(self, prompt: Union[List[Dict[str, str]], str]) -> None:
        json_data = {
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.tokens,
        }
        if isinstance(prompt, list):
            json_data["messages"] = prompt
        else:
            json_data["messages"] = [{"role": "system", "content": prompt}]

        try:

            response = self.client.chat.complete(**json_data)

            self.response = response.model_dump()

        except Exception as e:
            logger(f"Erro na chamada da API - modelo {json_data['model']}: {e}")

    def get_response(self) -> Any:
        return self.response

    def get_text(self) -> Union[None, str]:
        if self.response is not None:
            return self.response["choices"][0]["message"]["content"]
        else:
            return None

    def get_tokens(self) -> Union[None, str]:
        if self.response is not None:
            return self.response["usage"]
        else:
            return None


class AudioAPI:
    def __init__(self, api_key: str, model: str = "mistral-large-latest"):
        self.client = Mistral(api_key=api_key)
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
            model: str = "pixtral-12b-2409",
            temperature: float = 0.0,
        ):
        self.client = Mistral(api_key=api_key)
        self.model = model
        self.temperature = temperature

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
                    "image_url": f"data:image/png;base64,{image}",
                },
            )
        elif isinstance(image, list):
            for img in image:
                img = self.process_image(img)
                content.append(
                    {
                        "type": "image_url",
                        "image_url": f"data:image/png;base64,{image}", 
                    },
                )
        else:
            raise Exception(
                "Incorrect image type! Accepted: img_string or list[img_string]"
            )

        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": content}],
            "max_tokens": 3500,
            "temperature": self.temperature,
        }

        self.response = self.client.chat.complete(**payload)

        return self.response.model_dump()["choices"][0]["message"]["content"]

    def get_tokens(self) -> Union[None, str]:
        if self.response is not None:
            return self.response.model_dump()["usage"]
        else:
            return None
