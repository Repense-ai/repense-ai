import io

from typing import Any

from repenseai.genai.tasks.base_task import BaseTask
from repenseai.config.selection_params import TEXT_MODELS
from repenseai.utils.logs import logger


def log_costs(model: Any) -> None:
    try:
        tokens = model.get_tokens()
        cost = TEXT_MODELS[model.model]["cost"]

        input_cost = (cost["input"] * tokens["prompt_tokens"]) / 1_000_000
        output_cost = (cost["output"] * tokens["completion_tokens"]) / 1_000_000

        logger(f"Custo da requisição: ${input_cost + output_cost:.8f}")
        logger(f"Tokens: {tokens['total_tokens']}")
    except Exception as e:
        logger(f"Erro para calcular o custo do modelo {model.model}: {e}")


class ChatTask(BaseTask):
    """
    A Task is a step in the chatbot process that takes an user input and a context, and given an instruction,
    creates a response by requesting completion from an LLM.

    Args:

    """

    def __init__(
        self,
        api: Any,
        instruction: str = "",
        prompt_template: str = "",
        history: list | None = None,
    ) -> None:

        self.instruction = instruction
        self.prompt_template = prompt_template
        self.history = history

        self.model = api

    def build_prompt(self, **kwargs):

        if self.prompt_template != "":
            content = self.prompt_template.format(
                instruction=self.instruction, **kwargs
            )
        else:
            content = self.instruction

        prompt = [
            {
                "role": "user", 
                "content": [
                    {
                        "type": "text", 
                        "text": content
                    }
                ]
            }
        ]
        
        if self.history:
            return self.history + prompt
        
        return prompt
    
    def predict(self, context: dict) -> str:
        try:
            prompt = self.build_prompt(**context)
            self.model.call_api(prompt)

            log_costs(self.model)

            return self.model.get_text()
        except Exception as e:
            raise e


class AudioTask(BaseTask):
    def __init__(self, api: Any, context_audio_key: str = "audio") -> None:
        self.model = api
        self.context_audio_key = context_audio_key

    def predict(self, context: dict) -> str:
        try:
            if context.get(self.context_audio_key) is None:
                return ""

            text_response = self.model.call_api(context[self.context_audio_key])
            log_costs(self.model)

            return text_response
                
        except Exception as e:
            raise e
        
    def predict_audio(self, audio: io.BufferedReader) -> str:
        try:
            if audio is not None:

                text_response = self.model.call_api(audio)
                log_costs(self.model)

                return text_response
            else:
                return ""
        except Exception as e:
            raise e


class VisionTask(BaseTask):

    def __init__(
        self,
        api: Any,
        instruction: str = "",
        prompt_template: str = "",
        history: list | None = None,
        context_image_key: str = "image",
    ) -> None:

        self.instruction = instruction
        self.prompt_template = prompt_template
        self.history = history
        self.context_image_key = context_image_key

        self.model = api

    def build_prompt(self, **kwargs):

        if self.prompt_template != "":
            content = self.prompt_template.format(
                instruction=self.instruction, **kwargs
            )
        else:
            content = self.instruction

        prompt = [
            {
                "role": "user", 
                "content": [
                    {
                        "type": "text", 
                        "text": content
                    }
                ]
            }
        ]
        
        if self.history:
            return self.history + prompt
        
        return prompt
    
    def predict(self, context: dict) -> str:
        try:
            if context.get(self.context_image_key) is None:
                return ''
            
            prompt = self.build_prompt(**context)
            self.model.call_api(prompt, context[self.context_image_key])

            log_costs(self.model)

            return self.model.get_text()
        except Exception as e:
            raise e
        
    def predict_image(self, image: Any) -> str:
        try:
            prompt = self.build_prompt()
            self.model.call_api(prompt, image)

            log_costs(self.model)

            return self.model.get_text()
        except Exception as e:
            raise e
