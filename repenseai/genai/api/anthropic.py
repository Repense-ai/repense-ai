import os
import base64
import io

from PIL import Image

from anthropic import Anthropic

from typing import List, Dict, Union, Any

from repenseai.utils.logs import logger
from repenseai.aws.secrets_manager import SecretsManager

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())


def get_api_key():
    secret_manager = SecretsManager(secret_name="genai", region_name="us-east-2")
    key = os.getenv("ANTHROPIC_API_KEY") or secret_manager.get_secret("ANTHROPIC_API_KEY")

    if key:
        return key
    else:
        raise Exception("ANTHROPIC_API_KEY not found!")


class ChatAPI:
    def __init__(
        self,
        api_key: str,
        model: str = "claude-3-haiku-20240307",
        temperature: float = 0.0,
        max_tokens: int = 3500,
        stream=False,
    ):
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.tokens = max_tokens
        self.response = None
        self.stream = stream

        self.client = Anthropic(api_key=self.api_key)

    def call_api(self, prompt: Union[List[Dict[str, str]], str]) -> None:

        json_data = {
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.tokens,
            "stream": self.stream,
        }

        if isinstance(prompt, list):
            json_data.update(messages=prompt)
        else:
            json_data.update(messages=[{"role": "user", "content": prompt}])

        try:
            self.response = self.client.messages.create(**json_data)

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


class AudioAPI:
    def __init__(self, api_key: str, model: str = ""):
        self.client = Anthropic(api_key=api_key)
        self.model = model

    def call_api(self, audio: Any):
        _ = audio

        return "Not inplemented"

    def get_tokens(self):
        return {"completion_tokens": 0, "prompt_tokens": 0, "total_tokens": 0}


class VisionAPI:
    def __init__(self, api_key: str, model: str = "claude-3-sonnet-20240229"):
        self.client = Anthropic(api_key=api_key)
        self.model = model

    def process_image(self, image: Any) -> bytearray:
        if isinstance(image, str):
            return image
        elif isinstance(image, Image.Image):
            img_byte_arr = io.BytesIO()

            image.save(img_byte_arr, format="PNG")
            img_byte_arr = img_byte_arr.getvalue()

            image_string = base64.b64encode(img_byte_arr).decode("utf-8")

            return image_string
        else:
            raise Exception("Incorrect image type! Accepted: img_string or Image")

    def call_api(self, prompt: str, image: Any):
        if isinstance(image, str) or isinstance(image, Image.Image):
            image = self.process_image(image)
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "data": image,
                                    "type": "base64",
                                    "media_type": "image/png",
                                },
                            },
                            {"type": "text", "text": prompt},
                        ],
                    }
                ],
                "max_tokens": 3500,
                "temperature": 0,
            }

            self.response = self.client.messages.create(**payload)
            return self.response.content[0].text

        elif isinstance(image, list):

            content = []

            for img in image:
                img = self.process_image(img)
                content.append(
                    {
                        "type": "image",
                        "source": {
                            "data": img,
                            "type": "base64",
                            "media_type": "image/png",
                        },
                    },
                )

            content.append({"type": "text", "text": prompt})

            payload = {
                "model": self.model,
                "messages": [{"role": "user", "content": content}],
                "max_tokens": 3500,
                "temperature": 0,
            }

            self.response = self.client.messages.create(**payload)
            return self.response.content[0].text
        else:
            raise Exception(
                "Incorrect image type! Accepted: img_string or list[img_string]"
            )

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
