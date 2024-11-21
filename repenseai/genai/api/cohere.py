from io import BufferedReader
from typing import Any, Dict, List, Union

from cohere import ClientV2
from repenseai.utils.logs import logger


class ChatAPI:
    def __init__(
        self,
        api_key: str,
        model: str = "command-r-08-2024",
        temperature: float = 0.0,
        verbose=0,
    ):
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.verbose = verbose
        self.tokens = 3500
        self.response = None

        self.client = ClientV2(api_key=self.api_key)

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

            response = self.client.chat(**json_data)

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
            return self.response["message"]["content"][0]["text"]
        else:
            return None

    def get_tokens(self) -> Union[None, str]:
        if self.response is not None:

            usage = self.response["usage"]

            prompt_tokens = usage["billed_units"]["input_tokens"]
            completion_tokens = usage["billed_units"]["output_tokens"]

            total_tokens = prompt_tokens + completion_tokens

            return {
                "prompt_tokens": prompt_tokens, 
                "completion_tokens": completion_tokens, 
                "total_tokens": total_tokens,
            }
        else:
            return None


class AudioAPI:
    def __init__(self, api_key: str, model: str = ""):
        self.client = ClientV2(api_key=api_key)
        self.model = model

    def call_api(self, audio: BufferedReader):
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
        ):
        self.client = ClientV2(api_key=api_key)
        self.model = model

    def call_api(self, prompt: str, image: Any):
        _ = prompt
        _ = image

        return "Not Implemented"

    def get_tokens(self):
        return {"completion_tokens": 0, "prompt_tokens": 0, "total_tokens": 0}
