import os
import importlib
import typing as tp

from repenseai.secrets.base import BaseSecrets
from repenseai.genai.mcp.server import Server

from repenseai.genai.providers import (
    TEXT_MODELS,
    VISION_MODELS,
    IMAGE_MODELS,
    VIDEO_MODELS,
    SEARCH_MODELS,
    AUDIO_MODELS,
    SPEECH_MODELS,
)

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())


def list_models(model_type: str = "all") -> tp.List[str] | tp.Dict[str, tp.List[str]]:
    models_dict = {}

    models = {
        "chat": TEXT_MODELS,
        "vision": VISION_MODELS,
        "image": IMAGE_MODELS,
        "video": VIDEO_MODELS,
        "search": SEARCH_MODELS,
        "audio": AUDIO_MODELS,
        "speech": SPEECH_MODELS,
    }

    for model in models:
        models_dict[model] = list(models[model].keys())

    if model_type in models:
        return models_dict[model_type]

    return models_dict


class AsyncAgent:
    def __init__(
        self,
        model: str,
        model_type: str,
        api_key: str = None,
        secrets_manager: BaseSecrets = None,
        server: Server = None,
        **kwargs,
    ) -> None:
        self.model = model
        self.model_type = model_type
        self.api_key = api_key
        self.secrets_manager = secrets_manager
        self.server = server
        self.tokens = None
        self.api = None
        self.kwargs = kwargs

        self.models = {
            "chat": TEXT_MODELS,
            "vision": VISION_MODELS,
            "image": IMAGE_MODELS,
            "video": VIDEO_MODELS,
            "search": SEARCH_MODELS,
            "audio": AUDIO_MODELS,
            "speech": SPEECH_MODELS,
        }

        self.all_models = {}
        self.__build()

    def __build(self) -> None:
        self.__gather_models()
        self.__get_provider()
        self.__get_prices()
        self.__get_module()
        self.__check_server()

        if self.api_key is None:
            self.api_key = self.__get_api_key()

            if self.api_key is None and self.provider != "aws":
                raise Exception(f"API_KEY not found for provider {self.provider}.")

    def __check_server(self) -> None:
        if self.server is not None and self.model_type != "chat":
            raise Exception("MCP servers only works with chat models")

    def __gather_models(self) -> None:
        for models in self.models.values():
            self.all_models.update(models)

    def __get_provider(self) -> None:
        if self.model_type not in self.models:
            raise Exception("Model type not found")

        if "provider" in self.kwargs:
            self.provider = self.kwargs["provider"]
        else:
            self.provider = self.all_models[self.model]["provider"]

    def __get_prices(self) -> None:
        if "price" in self.kwargs:
            self.price = self.kwargs["price"]
        else:
            self.price = self.all_models[self.model]["cost"]

    def __get_module(self) -> None:
        api_str = f"repenseai.genai.api.{self.provider}"
        self.module_api = importlib.import_module(api_str)

    def __get_api_key(self) -> str:
        if not self.api_key:
            string = f"{self.provider.upper()}_API_KEY"
            self.api_key = os.getenv(string)

            if self.api_key:
                return self.api_key

            try:
                self.api_key = self.secrets_manager.get_secret(string)
                return self.api_key

            except Exception:
                return None

        return self.api_key

    async def get_api(self) -> tp.Any:
        match self.model_type:
            case "chat":
                self.api = self.module_api.AsyncChatAPI(
                    api_key=self.api_key,
                    model=self.model,
                    server=self.server,
                    **self.kwargs,
                )
            case _:
                raise Exception(f"{self.model_type} async API not implemented")

        return self.api

    def get_price(self) -> dict:
        return self.price

    def calculate_cost(
        self,
        tokens: tp.Union[tp.Dict[str, int], int, None] = None,
        as_string: str = False,
    ) -> tp.Union[float, str]:
        if not tokens:
            if self.api:
                if tokens := self.api.tokens:
                    pass
                else:
                    return 0
            else:
                return 0

        if isinstance(tokens, dict):
            if isinstance(self.price, dict):
                input_cost = tokens["prompt_tokens"] * self.price["input"]
                output_cost = tokens["completion_tokens"] * self.price["output"]
                total = (input_cost + output_cost) / 1_000_000
            else:
                input_cost = tokens["prompt_tokens"] * self.price
                output_cost = tokens["completion_tokens"] * self.price
                total = (input_cost + output_cost) / 1_000_000
        else:
            total = self.price * tokens

        if as_string:
            return f"U${total:.5f}"

        return round(total, 5) + 0.00001


class Agent:
    def __init__(
        self,
        model: str,
        model_type: str,
        api_key: str = None,
        secrets_manager: BaseSecrets = None,
        **kwargs,
    ) -> None:

        self.model = model
        self.model_type = model_type
        self.api_key = api_key
        self.secrets_manager = secrets_manager

        self.tokens = None
        self.api = None
        self.kwargs = kwargs

        self.models = {
            "chat": TEXT_MODELS,
            "vision": VISION_MODELS,
            "image": IMAGE_MODELS,
            "video": VIDEO_MODELS,
            "search": SEARCH_MODELS,
            "audio": AUDIO_MODELS,
            "speech": SPEECH_MODELS,
        }

        self.all_models = {}
        self.__build()

    def __build(self) -> None:
        self.__gather_models()
        self.__get_provider()
        self.__get_prices()
        self.__get_module()

        if self.api_key is None:
            self.api_key = self.__get_api_key()

            if self.api_key is None and self.provider != "aws":
                raise Exception(f"API_KEY not found for provider {self.provider}.")

    def __gather_models(self) -> None:
        for models in self.models.values():
            self.all_models.update(models)

    def __get_provider(self) -> None:
        if self.model_type not in self.models:
            raise Exception("Model type not found")

        if "provider" in self.kwargs:
            self.provider = self.kwargs["provider"]
        else:
            self.provider = self.all_models[self.model]["provider"]

    def __get_prices(self) -> None:
        if "price" in self.kwargs:
            self.price = self.kwargs["price"]
        else:
            self.price = self.all_models[self.model]["cost"]

    def __get_module(self) -> None:
        api_str = f"repenseai.genai.api.{self.provider}"
        self.module_api = importlib.import_module(api_str)

    def __get_api_key(self) -> str:
        if not self.api_key:
            string = f"{self.provider.upper()}_API_KEY"
            self.api_key = os.getenv(string)

            if self.api_key:
                return self.api_key

            try:
                self.api_key = self.secrets_manager.get_secret(string)
                return self.api_key

            except Exception:
                return None

        return self.api_key

    def get_api(self) -> tp.Any:
        match self.model_type:
            case "chat" | "search":
                self.api = self.module_api.ChatAPI(
                    api_key=self.api_key, model=self.model, **self.kwargs
                )
            case "vision":
                self.api = self.module_api.VisionAPI(
                    api_key=self.api_key, model=self.model, **self.kwargs
                )
            case "audio":
                self.api = self.module_api.AudioAPI(
                    api_key=self.api_key, model=self.model, **self.kwargs
                )
            case "image":
                self.api = self.module_api.ImageAPI(
                    api_key=self.api_key, model=self.model, **self.kwargs
                )
            case "speech":
                self.api = self.module_api.SpeechAPI(
                    api_key=self.api_key, model=self.model, **self.kwargs
                )
            case _:
                raise Exception(self.model_type + " API not found")

        return self.api

    def get_price(self) -> dict:
        return self.price

    def calculate_cost(
        self,
        tokens: tp.Union[tp.Dict[str, int], int, None] = None,
        as_string: str = False,
    ) -> tp.Union[float, str]:

        if not tokens:
            if self.api:
                if tokens := self.api.tokens:
                    pass
                else:
                    return 0
            else:
                return 0

        if isinstance(tokens, dict):
            if isinstance(self.price, dict):
                input_cost = tokens["prompt_tokens"] * self.price["input"]
                output_cost = tokens["completion_tokens"] * self.price["output"]

                total = (input_cost + output_cost) / 1_000_000

            else:
                input_cost = tokens["prompt_tokens"] * self.price
                output_cost = tokens["completion_tokens"] * self.price

                total = (input_cost + output_cost) / 1_000_000
        else:
            total = self.price * tokens

        if as_string:
            return f"U${total:.5f}"

        return round(total, 5) + 0.00001
