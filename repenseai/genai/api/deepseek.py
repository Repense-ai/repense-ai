import json
import inspect

from typing import Any, List, Union, Callable
from openai import OpenAI

from pydantic import BaseModel

from repenseai.utils.logs import logger


class ChatAPI:
    def __init__(
        self,
        api_key: str,
        model: str = "deepseek-chat",
        temperature: float = 0.0,
        max_tokens: int = 3500,
        stream: bool = False,
        json_mode: bool = False,
        json_schema: BaseModel = None,
        tools: List[Callable] = None,
        **kwargs,
    ):
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.stream = stream
        self.max_tokens = max_tokens

        self.response = None
        self.tokens = None

        self.json_mode = json_mode
        self.json_schema = json_schema

        self.tools = None
        self.json_tools = None

        self.tool_flag = False

        if tools:
            self.tools = {tool.__name__: tool for tool in tools}
            self.json_tools = [self.__function_to_json(tool) for tool in tools]

        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://api.deepseek.com",
        )

    def __function_to_json(self, func: callable) -> dict:

        type_map = {
            str: "string",
            int: "integer",
            float: "number",
            bool: "boolean",
            list: "array",
            dict: "object",
            type(None): "null",
        }

        try:
            signature = inspect.signature(func)
        except ValueError as e:
            raise ValueError(
                f"Failed to get signature for function {func.__name__}: {str(e)}"
            )

        parameters = {}
        for param in signature.parameters.values():
            try:
                param_type = type_map.get(param.annotation, "string")
            except KeyError as e:
                raise KeyError(
                    f"Unknown type annotation {param.annotation} for parameter {param.name}: {str(e)}"
                )
            parameters[param.name] = {"type": param_type}

        required = [
            param.name
            for param in signature.parameters.values()
            if param.default == inspect._empty
        ]

        return {
            "type": "function",
            "function": {
                "name": func.__name__,
                "description": func.__doc__ or "",
                "parameters": {
                    "type": "object",
                    "properties": parameters,
                    "required": required,
                },
            },
        }

    def __process_prompt_list(self, prompt: list) -> list:
        for message in prompt:
            if isinstance(message.get("content"), list):
                message["content"] = message.get("content")[0].get("text", "")

        return prompt

    def call_api(self, prompt: list | str) -> Any:
        json_data = {
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.tokens,
            "stream": self.stream,
            "tools": self.json_tools,
        }

        if isinstance(prompt, list):
            json_data["messages"] = self.__process_prompt_list(prompt)
        else:
            json_data["messages"] = [{"role": "user", "content": prompt}]

        try:
            if self.stream and not self.json_mode:
                json_data["stream_options"] = {"include_usage": True}

            if self.tool_flag:
                json_data.pop("max_tokens")

            if self.json_mode:
                json_data["response_format"] = {
                    "type": "json_object",
                    "schema": self.json_schema.model_json_schema(),
                }

                json_data.pop("stream")
                json_data.pop("tools")

            self.response = self.client.chat.completions.create(**json_data)

            if not self.stream:
                self.tokens = self.get_tokens()
                return self.get_output()

            return self.response

        except Exception as e:
            logger(f"Erro na chamada da API - modelo {json_data['model']}: {e}")

    def get_response(self) -> Any:
        return self.response

    def get_output(self) -> Union[None, str]:
        if self.response is not None:
            dump = self.response.model_dump()

            if dump["choices"][0]["finish_reason"] == "tool_calls":
                self.tool_flag = True
                return dump["choices"][0]["message"]

            self.tool_flag = False
            return dump["choices"][0]["message"].get("content")
        else:
            return None

    def get_tokens(self) -> Union[None, str]:
        if self.response is not None:
            return self.response.model_dump()["usage"]
        else:
            return None

    def process_stream_chunk(self, chunk: Any) -> Union[str, None]:
        if chunk.choices:
            content = chunk.choices[0].delta.content
            if content:
                return content
            else:
                self.tokens = chunk.model_dump()["usage"]
        else:
            if chunk.model_dump()["usage"]:
                self.tokens = chunk.model_dump()["usage"]

    def process_tool_calls(self, message: dict) -> list:
        tools = message.get("tool_calls")
        tool_messages = []

        for tool in tools:

            config = tool.get("function")
            args = json.loads(config.get("arguments"))

            output = self.tools[config.get("name")](**args)

            tool_messages.append(
                {"role": "tool", "tool_call_id": tool.get("id"), "content": str(output)}
            )

        return tool_messages


class VisionAPI:
    def __init__(
        self,
        api_key: str,
        model: str = "",
        temperature: float = 0.0,
        max_tokens: int = 3500,
        stream: bool = False,
    ):
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.stream = stream

        self.response = None
        self.tokens = None

    def process_image(self, image: Any) -> bytearray:
        return image

    def call_api(self, prompt: str | list, image: Any):
        _ = prompt
        _ = image

        return "Not implemented"

    def get_output(self) -> Union[None, str]:
        if self.response is not None:
            return self.response.model_dump()["choices"][0]["message"]["content"]
        else:
            return None

    def get_tokens(self) -> Union[None, str]:
        if self.response is not None:
            return self.response.model_dump()["usage"]
        else:
            return None

    def process_stream_chunk(self, chunk: Any) -> Union[str, None]:
        if chunk.choices:
            content = chunk.choices[0].delta.content
            if content:
                return content
            else:
                self.tokens = chunk.model_dump()["usage"]
        else:
            if chunk.model_dump()["usage"]:
                self.tokens = chunk.model_dump()["usage"]


class ImageAPI:
    def __init__(self, api_key: str, model: str = "", **kwargs):
        self.api_key = api_key
        self.model = model

    def call_api(self, prompt: Any, image: Any):
        _ = image
        _ = prompt

        return self.get_output()

    def get_output(self):
        return "Not Implemented"

    def get_tokens(self):
        return {"completion_tokens": 0, "prompt_tokens": 0, "total_tokens": 0}


class AudioAPI:
    def __init__(self, api_key: str, model: str, **kwargs):
        self.api_key = api_key
        self.model = model

    def call_api(self, audio: Any):
        _ = audio

        return self.get_output()

    def get_output(self):
        return "Not Implemented"

    def get_tokens(self):
        return {"completion_tokens": 0, "prompt_tokens": 0, "total_tokens": 0}


class SpeechAPI:
    def __init__(self, api_key: str, model: str, **kwargs):
        self.api_key = api_key
        self.model = model

    def call_api(self, text: str) -> bytes:
        _ = text

        return self.get_output()

    def get_output(self):
        return "Not Implemented"

    def get_tokens(self):
        return 0
