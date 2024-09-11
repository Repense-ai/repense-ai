import base64
import io
import os
from io import BufferedReader
from typing import Any, Dict, List, Union

from dotenv import find_dotenv, load_dotenv
from openai import OpenAI
from PIL import Image

from repenseai.aws.secrets_manager import SecretsManager
from repenseai.utils.logs import logger

load_dotenv(find_dotenv())


def get_api_key():
    secret_manager = SecretsManager(secret_name="genai", region_name="us-east-2")
    key = os.getenv("SAMBANOVA_API_KEY") or secret_manager.get_secret(
        "SAMBANOVA_API_KEY"
    )

    if key:
        return key
    else:
        raise Exception("SAMBANOVA_API_KEY not found!")


class ChatAPI:
    def __init__(
        self,
        api_key: str,
        model: str = "Meta-Llama-3.1-8B-Instruct",
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
            base_url="https://api.sambanova.ai/v1",
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
    def __init__(self, api_key: str, model: str = ""):
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def call_api(self, audio: BufferedReader):
        _ = audio

        return "Not Implemented"

    def get_tokens(self):
        return {"completion_tokens": 0, "prompt_tokens": 0, "total_tokens": 0}


class VisionAPI:
    def __init__(self, api_key: str, model: str = ""):
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def call_api(self, prompt: str, image: Any):
        _ = prompt
        _ = image

        return "Not Implemented"

    def get_tokens(self):
        return {"completion_tokens": 0, "prompt_tokens": 0, "total_tokens": 0}
