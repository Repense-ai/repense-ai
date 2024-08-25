import os
import base64
import io

from openai import OpenAI

from typing import List, Dict, Union, Any
from io import BufferedReader

from PIL import Image

from repenseai.utils.logs import logger


def get_api_key():
    if "MARITACA_API_KEY" not in os.environ.keys():
        from dotenv import load_dotenv

        load_dotenv()
    if os.getenv("MARITACA_API_KEY") is not None:
        return os.getenv("MARITACA_API_KEY")
    else:
        return os.getenv("REQUESTER_TOKEN")


class ChatAPI:
    def __init__(
        self,
        api_key: str,
        model: str = "sabia-3",
        temperature: float = 0.0,
        verbose=0,
    ):
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.verbose = verbose
        self.tokens = 3500
        self.response = None

        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://chat.maritaca.ai/api",
        )

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

            response = self.client.chat.completions.create(**json_data)

            self.response = response.model_dump()
            self.raw_response = response

        except Exception as e:
            logger(f"Erro na chamada da API - modelo {json_data['model']}: {e}")

    def get_response(self) -> Any:
        return self.response

    def get_raw_response(self) -> Any:
        return self.raw_response

    def get_text(self) -> Union[None, str]:
        if self.response is not None:
            return self.response["choices"][0]["message"]["content"]
        else:
            return None

    def get_function_blueprint(self) -> Union[None, str]:
        if self.response is not None:
            try:
                return self.response["choices"][0]["message"]["tool_calls"][0][
                    "function"
                ]["arguments"]
            except Exception:
                return self.response["choices"][0]["message"]["content"]
        else:
            return None

    def get_tokens(self) -> Union[None, str]:
        if self.response is not None:
            return self.response["usage"]
        else:
            return None


class AudioAPI:
    def __init__(self, api_key: str, model: str = "whisper-1"):
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def call_api(self, audio: BufferedReader):

        transcript = self.client.audio.transcriptions.create(
            model=self.model,
            file=audio,
            language="pt",
            response_format="text",
        )

        return transcript


class VisionAPI:
    def __init__(self, api_key: str, model: str = "gpt-4-turbo"):
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.tokens = 3500

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

        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": content}],
            "max_tokens": 3500,
            "temperature": 0,
        }

        self.response = self.client.chat.completions.create(**payload)

        return self.response.model_dump()["choices"][0]["message"]["content"]

    def get_tokens(self) -> Union[None, str]:
        if self.response is not None:
            return self.response.model_dump()["usage"]
        else:
            return None
