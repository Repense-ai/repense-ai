import importlib

from repenseai.utils.logs import logger
from repenseai.config.selection_params import MODELS


class APISelector:
    def __init__(self, model: str, api: str) -> None:
        self.model = model
        self.api = api
        self.provider = MODELS[model]

    def __get_modules(self):

        api_str = f"repenseai.genai.api.{self.provider}"
        params_str = f"repenseai.config.{self.provider}_params"

        self.module_api = importlib.import_module(api_str)
        self.module_params = importlib.import_module(params_str)

    def get_api(self, **kwargs):
        self.__get_modules()

        chat_api = self.module_api.ChatAPI(
            api_key=self.module_params.API_KEY, model=self.model, **kwargs
        )

        vision_api = self.module_api.VisionAPI(
            api_key=self.module_params.API_KEY, model=self.model, **kwargs
        )

        audio_api = self.module_api.AudioAPI(
            api_key=self.module_params.API_KEY, model=self.model, **kwargs
        )

        api_dict = {"chat": chat_api, "vision": vision_api, "audio": audio_api}
        api = api_dict.get(self.api)

        if api is None:
            logger(self.api + " API not found")

        return api
