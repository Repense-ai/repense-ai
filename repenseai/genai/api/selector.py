import os
import importlib

from repenseai.aws.secrets_manager import SecretsManager

from repenseai.config.selection_params import TEXT_MODELS
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())


class APISelector:
    def __init__(self, model: str, model_type: str, api_key: str = None) -> None:
        self.model = model
        self.model_type = model_type
        self.provider = TEXT_MODELS[model]["provider"]
        self.api_key = api_key

        self.__get_module()

    def __get_module(self):
        api_str = f"repenseai.genai.api.{self.provider}"
        self.module_api = importlib.import_module(api_str)

    def get_api_key(
        self, 
        secret_name: str = "genai", 
        region_name: str = "us-east-2"
    ):
        if not self.api_key:
            string = f"{self.provider.upper()}_API_KEY"
            api_key = os.getenv(string)

            if api_key:
                return api_key
            
            try:
                secret_manager = SecretsManager(
                    secret_name=secret_name, 
                    region_name=region_name,
                )

                api_key = secret_manager.get_secret(string)
                return api_key
            except Exception:
                return None   
        return self.api_key

    def get_api(
        self,         
        secret_name: str = "genai", 
        region_name: str = "us-east-2",
        **kwargs
    ):
        api_key = self.get_api_key(secret_name, region_name)

        match self.model_type:
            case "chat":
                return self.module_api.ChatAPI(
                    api_key=api_key, model=self.model, **kwargs
                )
            case "vision":
                return self.module_api.VisionAPI(
                    api_key=api_key, model=self.model, **kwargs
                )
            case "audio":
                return self.module_api.AudioAPI(
                    api_key=api_key, model=self.model, **kwargs
                )
            case _:
                raise Exception(self.model_type + " API not found")
