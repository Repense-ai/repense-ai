import base64
import io
import inspect
import json

from pydantic import BaseModel

from typing import Any, Dict, List, Union, Callable
from openai import OpenAI

from PIL import Image

from repenseai.utils.audio import get_memory_buffer
from repenseai.utils.logs import logger


class ChatAPI:
    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o",
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

        self.json_mode = json_mode
        self.json_schema = json_schema

        self.response = None
        self.tokens = None

        self.tools = None
        self.json_tools = None

        self.tool_flag = False

        if tools:
            self.tools = {tool.__name__: tool for tool in tools}
            self.json_tools = [self.__function_to_json(tool) for tool in tools]

        self.client = OpenAI(api_key=self.api_key)

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

    def call_api(self, prompt: Union[List[Dict[str, str]], str]) -> Any:
        json_data = {
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.tokens,
            "stream": self.stream,
            "tools": self.json_tools,
        }

        if isinstance(prompt, list):
            json_data["messages"] = prompt
        else:
            json_data["messages"] = [{"role": "user", "content": prompt}]

        try:
            if self.stream:
                json_data["stream_options"] = {"include_usage": True}

            if "o1" or "o3" in self.model:
                json_data.pop("temperature")
                json_data.pop("max_tokens")

            if self.json_mode:
                json_data["response_format"] = self.json_schema
                json_data.pop("stream")
                json_data.pop("tools")

                self.response = self.client.beta.chat.completions.parse(**json_data)
            else:
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

            if dump["choices"][0]['finish_reason'] == "tool_calls":
                self.tool_flag = True
                return dump["choices"][0]["message"]
            
            self.tool_flag = False
            if self.json_mode:
                return dump["choices"][0]["message"].get("parsed")
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

            config = tool.get('function')
            args = json.loads(config.get('arguments'))

            output = self.tools[config.get('name')](**args)

            tool_messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool.get('id'),
                    "content": str(output)
                }
            ) 

        return tool_messages  


class AudioAPI:
    def __init__(self, api_key: str, model: str, **kwargs):
        self.client = OpenAI(api_key=api_key)
        self.model = model

        self.kwargs = kwargs

        self.response = None
        self.tokens = None

    def call_api(self, audio: io.BufferedReader | bytes) -> str:
        if not isinstance(audio, io.BufferedReader):
            audio = get_memory_buffer(audio)

        parameters = {
            "model": self.model,
            "file": audio,
            "response_format": "verbose_json",
        }

        if language := self.kwargs.get("language"):
            parameters["language"] = language

        self.response = self.client.audio.transcriptions.create(
            **parameters
        )

        self.tokens = self.get_tokens()
        return self.get_output()
    
    def get_output(self) -> Union[None, str]:
        if self.response is not None:
            return self.response.model_dump().get('text')
        else:
            return None

    def get_tokens(self) -> Union[None, str]:
        if self.response is not None:
            duration = self.response.model_dump().get('duration')
            duration = round(duration / 60, 2)

            return duration
        else:
            return None

class SpeechAPI:
    def __init__(
            self, 
            api_key: str, 
            model: str, 
            voice: str,
            **kwargs
        ):

        self.client = OpenAI(api_key=api_key)

        self.model = model
        self.voice = voice

        self.kwargs = kwargs

        self.response = None
        self.tokens = None
        self.response_format = None

        self.allowed_voices = [
            'alloy', 'ash', 'coral', 
            'echo', 'fable', 'onyx', 
            'nova', 'sage', 'shimmer'
        ]

        self.allowed_format = [
            'mp3', 'opus', 'aac', 
            'flac', 'wav', 'pcm'
        ]

        self.__validate_voice()
        self.__validate_format()

    def __validate_voice(self) -> None:
        if not self.voice in self.allowed_voices:
            raise ValueError(f"Voice {self.voice} not allowed for model {self.model}")
        
    def __validate_format(self) -> None:
        if format := self.kwargs.get("response_format"):
            if not format in self.allowed_format:

                logger(f"Format {format} not allowed for model {self.model}")
                logger(f"Setting format to 'mp3'")

                self.response_format = 'mp3'
            else:
                self.response_format = format


    def call_api(self, text: str) -> bytes:

        parameters = {
            "model": self.model,
            "voice": self.voice,
            "input": text,
            "response_format": self.response_format,
        }

        if speed := self.kwargs.get("speed"):
            if not 0.25 <= speed <= 4.0:

                logger("Speed must be between 0.25 and 4.0")
                logger("Setting speed to 1.0")

                speed = 1.0
            
            parameters["speed"] = speed         

        self.response = self.client.audio.speech.create(**parameters)
        self.tokens = self.get_tokens(text)

        return self.get_output()
    
    def get_output(self) -> Union[None, str]:
        if self.response is not None:
            return self.response.content
        else:
            return None

    def get_tokens(self, text: str) -> int:
        return round(len(text) / 4)


class VisionAPI:
    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o",
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

    def __process_image(self, image: Any) -> Any:
        if isinstance(image, str):
            if "http" in image:
                return image
            else:
                f"data:image/png;base64,{image}"
        elif isinstance(image, Image.Image):
            img_byte_arr = io.BytesIO()

            image.save(img_byte_arr, format="PNG")
            img_byte_arr = img_byte_arr.getvalue()

            image_string = base64.b64encode(img_byte_arr).decode("utf-8")

            return f"data:image/png;base64,{image_string}"
        else:
            raise Exception("Incorrect image type! Accepted: img_string or Image")
        
    def __create_content_image(self, image: Any) -> Dict[str, Any]:
        img = self.__process_image(image)

        img_dict = {
            "type": "image_url",
            "image_url": {
                "url": img,
                "detail": "high",
            },
        }

        return img_dict
        
    def __process_prompt_content(self, prompt: str | list) -> list:
        if isinstance(prompt, str):
            content = [{"type": "text", "text": prompt}]
        else:
            content = prompt[-1].get("content", [])

        return content

    def __process_content_image(self, content: list, image: Any) -> list:

        if isinstance(image, str) or isinstance(image, Image.Image):
            img = self.__create_content_image(image)
            content.append(img)

        elif isinstance(image, list):
            for img in image:
                img = self.__create_content_image(img)
                content.append(img)
        else:
            raise Exception(
                "Incorrect image type! Accepted: img_string or list[img_string]"
            )                

        return content

    def __process_prompt(self, prompt: str | list, content: list) -> list:
        if isinstance(prompt, list):
            prompt[-1] = {"role": "user", "content": content}
        else:
            prompt = [{"role": "user", "content": content}]

        return prompt

    def call_api(self, prompt: str | list, image: Any):

        content = self.__process_prompt_content(prompt)
        content = self.__process_content_image(content, image)

        prompt = self.__process_prompt(prompt, content)
           
        json_data = {
            "model": self.model,
            "messages": prompt,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "stream": self.stream,
        }

        try:
            if self.stream:
                json_data["stream_options"] = {"include_usage": True}

            self.response = self.client.chat.completions.create(**json_data)

            if not self.stream:
                self.tokens = self.get_tokens()
                return self.get_output()

            return self.response

        except Exception as e:
            logger(f"Erro na chamada da API - modelo {json_data['model']}: {e}")

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

        return "Not implemented"

    def get_tokens(self):
        return {"completion_tokens": 0, "prompt_tokens": 0, "total_tokens": 0}