from copy import deepcopy
import json
from typing import Any
from repenseai.genai.tasks.base import BaseTask


class Task(BaseTask):

    def __init__(
        self,
        agent: Any,
        user: str = "",
        simple_response: bool = False,
        history: list | None = None,
        vision_key: str = "image",
        audio_key: str = "audio",
        speech_key: str = "speech",      
        base_image_key: str = "base_image"
    ) -> None:

        self.user = user
        self.history = history

        self.agent = agent
        self.simple_response = simple_response

        self.vision_key = vision_key
        self.audio_key = audio_key
        self.speech_key = speech_key
        self.base_image_key = base_image_key

        self.prompt = None
        self.api = self.agent.get_api()


    def __replace_tokens(self, text: str, tokens: dict) -> str:
        for key, value in tokens.items():
            text = text.replace("{" + key + "}", str(value))

        return text

    def __build_prompt(self, **kwargs):
        content = self.__replace_tokens(self.user, kwargs)

        self.prompt = [
            {
                "role": "user",
                "content": [{"type": "text", "text": content}]
            }
        ]
        
        if self.history:
            self.prompt = self.history + self.prompt
        
        return self.prompt
        
    def __process_chat_or_search(self) -> dict:
        prompt = deepcopy(self.prompt)

        response = self.api.call_api(prompt)

        final_response = {
            "response": response,
            "tokens": self.api.tokens,
            "cost": self.agent.calculate_cost(self.api.tokens),
        }

        if self.agent.model_type == "search":
            final_response["citations"] = self.api.response.json().get("citations", [])   

        return final_response       

    def __process_vision(self, context: dict) -> dict:
        prompt = deepcopy(self.prompt)

        image = context.get(self.vision_key)

        response = self.api.call_api(prompt, image)

        return {
            "response": response,
            "tokens": self.api.tokens,
            "cost": self.agent.calculate_cost(self.api.tokens),
        }
    
    def __process_audio(self, context: dict) -> dict:
        audio = context.get(self.audio_key)

        response = self.api.call_api(audio)

        return {
            "response": response,
            "tokens": self.api.tokens,
            "cost": self.agent.calculate_cost(self.api.tokens),
        }
    
    def __process_speech(self, context: dict) -> dict:
        speech = context.get(self.speech_key)
        response = self.api.call_api(speech)

        return {
            "response": response,
            "tokens": self.api.tokens,
            "cost": self.agent.calculate_cost(self.api.tokens),
        }    
    
    def __process_image(self, context: dict) -> dict:
        image = context.get(self.base_image_key)
        user = self.prompt[-1]["content"][0]["text"]

        response = self.api.call_api(user, image)

        return {
            "response": response,
            "tokens": self.api.tokens,
            "cost": self.agent.calculate_cost(self.api.tokens),
        }

    def _process_api_call(self, context: dict) -> dict:
        match self.agent.model_type:
            case "chat" | "search":
                return self.__process_chat_or_search()
            case "vision":
                return self.__process_vision(context)
            case "audio":
                return self.__process_audio(context)
            case "speech":
                return self.__process_speech(context)            
            case "image":
                return self.__process_image(context)                           
    
    def run(self, context: dict | None = None) -> str:
        if not context:
            context = {}

        try:
            if not self.prompt:
                self.__build_prompt(**context)

            response = self._process_api_call(context)                 

            if self.agent.model_type == "chat":

                while self.api.tool_flag:
                    tools_response = self.api.process_tool_calls(response["response"])

                    self.prompt.append(response["response"])   
                    self.prompt += tools_response

                    response = self._process_api_call(context)

            self.prompt.append(
                {
                    "role": "assistant",
                    "content": response["response"]
                }
            )   

            if self.simple_response:
                return response["response"]
            
            return response

        except Exception as e:
            raise e
        
    def add_user_message(self, message: str) -> None:
        self.prompt.append(
            {
                "role": "user",
                "content": [{"type": "text", "text": message}]
            }
        )

    def add_assistant_message(self, message: str) -> bool:
        self.prompt.append(
            {
                "role": "assistant",
                "content": [{"type": "text", "text": message}]
            }
        )

        
class AsyncTask(BaseTask):
    def __init__(
        self,
        agent: Any,
        user: str = "",
        simple_response: bool = False,
        history: list | None = None,
    ) -> None:
        
        self.user = user
        self.history = history
        self.agent = agent
        self.simple_response = simple_response

        self.prompt = None
        self.api = None

    def __replace_tokens(self, text: str, tokens: dict) -> str:
        for key, value in tokens.items():
            text = text.replace("{" + key + "}", str(value))
        return text

    def __build_prompt(self, **kwargs):
        content = self.__replace_tokens(self.user, kwargs)
        self.prompt = [
            {
                "role": "user",
                "content": [{"type": "text", "text": content}]
            }
        ]
        if self.history:
            self.prompt = self.history + self.prompt
        return self.prompt

    async def __process_chat(self) -> dict:
        prompt = deepcopy(self.prompt)

        self.api = await self.agent.get_api()
        response = await self.api.call_api(prompt)
        
        final_response = {
            "response": response,
            "tokens": self.api.tokens,
            "cost": self.agent.calculate_cost(self.api.tokens),
        }

        return final_response

    async def _process_api_call(self, context: dict) -> dict:
        match self.agent.model_type:
            case "chat":
                return await self.__process_chat()
            case _:
                raise NotImplementedError(f"Model type {self.agent.model_type} not implemented for async")

    async def run(self, context: dict | None = None) -> str:
        if not context:
            context = {}

        try:
            if not self.prompt:
                self.__build_prompt(**context)

            response = await self._process_api_call(context)

            while self.api.tool_flag:
                tools_response = await self.api.process_tool_calls(response["response"])

                self.prompt.append(response["response"])   
                self.prompt += tools_response
                
                response = await self._process_api_call(context)

            self.prompt.append(
                {
                    "role": "assistant",
                    "content": response["response"]
                }
            )   

            if self.simple_response:
                return response["response"]
            
            return response

        except Exception as e:
            raise e    