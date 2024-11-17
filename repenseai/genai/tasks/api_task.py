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
        temperature: float = 0,
    ) -> None:
        self.instruction = instruction
        self.prompt_template = prompt_template
        self.temperature = temperature
        self.model = api

        self.provider = TEXT_MODELS.get(self.model.model)["provider"]

    def build_prompt(self, **kwargs):
        
        if self.prompt_template != "":
            content = self.prompt_template.format(
                instruction=self.instruction, **kwargs
            )
        else:
            content = self.instruction

        if self.provider == "google":
            return content

        return [{"role": "user", "content": content}]

    def predict(self, context: dict) -> str:
        try:
            prompt = self.build_prompt(**context)
            self.model.call_api(prompt)

            log_costs(self.model)

            return self.model.get_text()
        except Exception as e:
            raise e


class AudioTask(BaseTask):
    def __init__(self, api: Any) -> None:
        self.model = api

    def predict(self, context: dict) -> str:
        try:
            if context["audio"] is not None:

                text_response = self.model.call_api(context["audio"])
                log_costs(self.model)

                return text_response
            else:
                return ""
        except Exception as e:
            raise e


class VisionTask(BaseTask):
    def __init__(self, api: Any, instruction: str = "") -> None:

        self.instruction = instruction
        self.model = api

    def predict(self, context: dict) -> str:
        try:
            if context["image"] is not None:
                text_response = self.model.call_api(self.instruction, context["image"])
                log_costs(self.model)

                return text_response
            else:
                return ""
        except Exception as e:
            raise e
