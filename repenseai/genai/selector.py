import os
import importlib
import typing as tp

from repenseai.aws.secrets_manager import SecretsManager

from repenseai.config.selection_params import (
    TEXT_MODELS,
    VISION_MODELS,
    IMAGE_MODELS,
    VIDEO_MODELS,
    SEARCH_MODELS,
    AUDIO_MODELS,
)

from dotenv import find_dotenv, load_dotenv
load_dotenv(find_dotenv())


def list_models(model_type: str = 'all') -> tp.List[str] | tp.Dict[str, tp.List[str]]:
    models_dict = {}

    models = {
        "chat": TEXT_MODELS,
        "vision": VISION_MODELS,
        "image": IMAGE_MODELS,
        "video": VIDEO_MODELS,
        "search": SEARCH_MODELS,
        "audio": AUDIO_MODELS,
    }

    for model in models:
        models_dict[model] = list(models[model].keys())

    if model_type in models:
        return models_dict[model_type]
    
    return models_dict


class APISelector:
    def __init__(
            self, 
            model: str, 
            model_type: str, 
            api_key: str = None,
            secrets_manager: SecretsManager = None,
            **kwargs
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
        }

        self.all_models = {}
        self.__build()


    def __build(self) -> None:
        self.__gather_models()
        self.__get_provider()
        self.__get_prices()
        self.__get_module()

    def __gather_models(self) -> None:
        for models in self.models.values():
            self.all_models.update(models)

    def __get_provider(self) -> None:
        if self.model_type not in self.models:
            raise Exception("Model type not found")

        self.provider = self.all_models[self.model]["provider"]

    def __get_prices(self) -> None:
        self.price = self.all_models[self.model]["cost"]

    def __get_module(self) -> None:
        api_str = f"repenseai.genai.api.{self.provider}"
        self.module_api = importlib.import_module(api_str)

    def __get_secret_manager(self) -> SecretsManager:
        if not self.secrets_manager:
            self.secrets_manager = SecretsManager(
                secret_name="genai",
                region_name="us-east-2",
            )

    def __get_api_key(self) -> str:
        if not self.api_key:
            string = f"{self.provider.upper()}_API_KEY"
            self.api_key = os.getenv(string)

            if self.api_key:
                return self.api_key

            try:
                self.__get_secret_manager()
                self.api_key = self.secret_manager.get_secret(string)
                return self.api_key
            
            except Exception:
                return None
            
        return self.api_key

    def get_api(self) -> tp.Any:
        self.api_key = self.__get_api_key()

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
            case _:
                raise Exception(self.model_type + " API not found")

        return self.api

    def get_price(self) -> dict:
        return self.price

    def calculate_cost(
        self, tokens: tp.Dict[str, int], as_string: str = False
    ) -> tp.Union[float, str]:
        
        if not tokens:
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


