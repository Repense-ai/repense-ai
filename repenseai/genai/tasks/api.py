from copy import deepcopy
import json
from typing import Any
from repenseai.genai.tasks.base import BaseTask


class Task(BaseTask):

    def __init__(
        self,
        agent: Any,
        simple_response: bool = False,
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

        self.agent = agent
        self.simple_response = simple_response

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
    
    def __process_tool_calls(self, response: list) -> None:

        self.prompt.append(
            {
                "role": "assistant",
                "tool_calls": response
            }
        )

        for r in response:
            if r.get("type") == "function":

                config = r.get('function')
                args = json.loads(config.get('arguments'))

                api = self.agent.get_api()
                output = api.tools[config.get('name')](**args)

                self.prompt.append(
                    {
                        "role": "tool",
                        "tool_call_id": r.get('id'),
                        "content": str(output)
                    }
                )        
    
    def __process_chat_or_search(self) -> dict:
        api = self.agent.get_api()
        prompt = deepcopy(self.prompt)

        response = api.call_api(prompt)

        final_response = {
            "response": response,
            "tokens": api.tokens,
            "cost": self.agent.calculate_cost(api.tokens),
        }

        if self.agent.model_type == "search":
            final_response["citations"] = api.response.json().get("citations", [])   

        return final_response       

    def __process_vision(self, context: dict) -> dict:
        api = self.agent.get_api()
        prompt = deepcopy(self.prompt)

        image = context.get(self.vision_key)

        response = api.call_api(prompt, image)

        return {
            "response": response,
            "tokens": api.tokens,
            "cost": self.agent.calculate_cost(api.tokens),
        }
    
    def __process_audio(self, context: dict) -> dict:
        api = self.agent.get_api()
        audio = context.get(self.audio_key)

        response = api.call_api(audio)

        return {
            "response": response,
            "tokens": api.tokens,
            "cost": self.agent.calculate_cost(api.tokens),
        }
    
    def __process_image(self, context: dict) -> dict:
        api = self.agent.get_api()
        image = context.get(self.base_image_key)

        instruction = self.prompt[-1]["content"][0]["text"]

        response = api.call_api(instruction, image)

        return {
            "response": response,
            "tokens": api.tokens,
            "cost": self.agent.calculate_cost(api.tokens),
        }

    def _process_api_call(self, context: dict) -> dict:
        match self.agent.model_type:
            case "chat" | "search":
                return self.__process_chat_or_search()
            case "vision":
                return self.__process_vision(context)
            case "audio":
                return self.__process_audio(context)
            case "image":
                return self.__process_image(context)                             
    
    def run(self, context: dict) -> str:
        try:
            self.__build_prompt(**context)
            response = self._process_api_call(context)

            if isinstance(response["response"], list):
                self.__process_tool_calls(response["response"])
                response = self._process_api_call(context)

            if self.simple_response:
                return response["response"]
            
            return response

        except Exception as e:
            raise e
        
    