from typing import Any

from repenseai.genai.tasks.base_task import BaseTask


class Task(BaseTask):

    def __init__(
        self,
        selector: Any,
        instruction: str = "",
        prompt_template: str = "",
        history: list | None = None,
        vision_key: str = "image",
        audio_key: str = "audio",
        base_image_key: str = "base_image"
    ) -> None:

        self.instruction = instruction
        self.prompt_template = prompt_template
        self.history = history

        self.selector = selector

        self.vision_key = vision_key
        self.audio_key = audio_key
        self.base_image_key = base_image_key

        self.prompt = None

    def __build_prompt(self, **kwargs):

        if self.prompt_template != "":
            content = self.prompt_template.format(
                instruction=self.instruction, **kwargs
            )
        else:
            content = self.instruction

        self.prompt = [
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
            self.prompt = self.history + self.prompt
        
        return self.prompt
    
    def __process_chat_or_search(self) -> dict:
        api = self.selector.get_api()
        response = api.call_api(self.prompt)

        final_response = {
            "response": response,
            "tokens": api.tokens,
            "cost": self.selector.calculate_cost(api.tokens),
        }

        if self.selector.model_type == "search":
            final_response["citations"] = api.response.json().get("citations", [])   

        return final_response       

    def __process_vision(self, context: dict) -> dict:
        api = self.selector.get_api()
        image = context.get(self.vision_key)

        response = api.call_api(self.prompt, image)

        return {
            "response": response,
            "tokens": api.tokens,
            "cost": self.selector.calculate_cost(api.tokens),
        }
    
    def __process_audio(self, context: dict) -> dict:
        api = self.selector.get_api()
        audio = context.get(self.audio_key)

        response = api.call_api(audio)

        return {
            "response": response,
            "tokens": api.tokens,
            "cost": self.selector.calculate_cost(api.tokens),
        }
    
    def __process_image(self, context: dict) -> dict:
        api = self.selector.get_api()
        image = context.get(self.base_image_key)

        instruction = self.prompt[-1]["content"][0]["text"]

        response = api.call_api(instruction, image)

        return {
            "response": response,
            "tokens": api.tokens,
            "cost": self.selector.calculate_cost(api.tokens),
        }

    def _process_api_call(self, context: dict) -> dict:
        match self.selector.model_type:
            case "chat" | "search":
                return self.__process_chat_or_search()
            case "vision":
                return self.__process_vision(context)
            case "audio":
                return self.__process_audio(context)
            case "image":
                return self.__process_image(context)                             
    
    def predict(self, context: dict) -> str:
        try:
            self.__build_prompt(**context)

            return self._process_api_call(context)

        except Exception as e:
            raise e
        
    