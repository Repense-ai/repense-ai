import os

import cohere

from typing import List, Dict, Union, Any
from io import BufferedReader

from repenseai.utils.logs import logger
from repenseai.aws.secrets_manager import SecretsManager


def get_api_key():
    secret_manager = SecretsManager(secret_name="genai", region_name="us-east-2")
    key = os.getenv("COHERE_API_KEY") or secret_manager.get_secret("COHERE_API_KEY")

    if key:
        return key
    else:
        raise Exception("COHERE_API_KEY not found!")


class ChatAPI:
    def __init__(
        self,
        api_key: str,
        model: str = "command-r-plus",
        temperature: float = 0.0,
        verbose=0,
    ):
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.verbose = verbose
        self.tokens = 3500
        self.response = None

        self.client = cohere.Client(api_key=self.api_key)

    def call_api(self, prompt: Union[List[Dict[str, str]], str]) -> None:
        json_data = {
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.tokens,
        }

        if isinstance(prompt, list):
            json_data.update({"chat_history": prompt, "message": prompt[-1]["message"]})

        else:
            json_data.update(
                {
                    "chat_history": [{"role": "system", "message": prompt}],
                    "message": prompt,
                }
            )

        try:

            self.response = self.client.chat(**json_data)

        except Exception as e:
            logger(f"Erro na chamada da API - modelo {json_data['model']}: {e}")

    def get_response(self) -> Any:
        return self.response

    def get_text(self) -> Union[None, str]:
        if self.response is not None:
            return self.response.text
        else:
            return None

    def get_tokens(self) -> Union[None, str]:
        if self.response is not None:

            input_tokens = self.response.meta.tokens.input_tokens
            output_tokens = self.response.meta.tokens.output_tokens

            return {
                "completion_tokens": int(output_tokens),
                "prompt_tokens": int(input_tokens),
                "total_tokens": int(output_tokens + input_tokens),
            }
        else:
            return None


class AudioAPI:
    def __init__(self, api_key: str, model: str = "command-r-plus"):
        self.client = cohere.Client(api_key=api_key)
        self.model = model

    def call_api(self, audio: BufferedReader):
        _ = audio

        return "Not Implemented"

    def get_tokens(self):
        return {"completion_tokens": 0, "prompt_tokens": 0, "total_tokens": 0}


class VisionAPI:
    def __init__(self, api_key: str, model: str = "command-r-plus"):
        self.client = cohere.Client(api_key=api_key)
        self.model = model

    def call_api(self, prompt: str, image: Any):
        _ = prompt
        _ = image

        return "Not Implemented"

    def get_tokens(self):
        return {"completion_tokens": 0, "prompt_tokens": 0, "total_tokens": 0}
