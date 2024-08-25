import os

from mistralai import Mistral

from typing import List, Dict, Union, Any
from io import BufferedReader

from repenseai.utils.logs import logger


def get_api_key():
    if "MISTRAL_API_KEY" not in os.environ.keys():
        from dotenv import load_dotenv

        load_dotenv()
    if os.getenv("MISTRAL_API_KEY") is not None:
        return os.getenv("MISTRAL_API_KEY")
    else:
        return os.getenv("REQUESTER_TOKEN")


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

    def call_api(self, audio: BufferedReader):
        _ = audio

        return "Not Implemented"

    def get_tokens(self):
        return {"completion_tokens": 0, "prompt_tokens": 0, "total_tokens": 0}


class VisionAPI:
    def __init__(self, api_key: str, model: str = "mistral-large-latest"):
        self.client = Mistral(api_key=api_key)
        self.model = model

    def call_api(self, prompt: str, image: Any):
        _ = prompt
        _ = image

        return "Not Implemented"

    def get_tokens(self):
        return {"completion_tokens": 0, "prompt_tokens": 0, "total_tokens": 0}
