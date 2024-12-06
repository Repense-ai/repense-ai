from typing import Any

from repenseai.genai.tasks.base_task import BaseTask


class Task(BaseTask):

    def __init__(
        self,
        selector: Any,
        instruction: str = "",
        prompt_template: str = "",
        history: list | None = None,
        image_key: str = "image",
        audio_key: str = "audio"
    ) -> None:

        self.instruction = instruction
        self.prompt_template = prompt_template
        self.history = history

        self.selector = selector

        self.image_key = image_key
        self.audio_key = audio_key

    def __build_prompt(self, **kwargs):

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
    
    def __process_api_call(self, context: dict, prompt: list) -> dict:
        match self.selector.model_type:
            case "chat" | "search":
                api = self.selector.get_api()
                response = api.call_api(prompt)

                final_response = {
                    "response": response,
                    "tokens": api.tokens,
                    "cost": self.selector.calculate_cost(api.tokens),
                }

                if self.selector.model_type == "search":
                    final_response["citations"] = api.response.model_dump().get("citations", [])   

                return final_response      
            case "vision":
                api = self.selector.get_api()
                image = context.get(self.image_key)

                response = api.call_api(prompt, image)

                return {
                    "response": response,
                    "tokens": api.tokens,
                    "cost": self.selector.calculate_cost(api.tokens),
                }
            case "audio":
                api = self.selector.get_api()
                audio = context.get(self.audio_key)

                response = api.call_api(audio)

                return {
                    "response": response,
                    "tokens": api.tokens,
                    "cost": self.selector.calculate_cost(api.tokens),
                }                      
    
    def predict(self, context: dict) -> str:
        try:
            prompt = self.__build_prompt(**context)
            response = self.__process_api_call(context, prompt)

            return response

        except Exception as e:
            raise e