import base64
import httpx
import io
import inspect
import json

from repenseai.genai.providers import VISION_MODELS

from typing import Any, Dict, Union, List, Callable

from anthropic import Anthropic

from PIL import Image
from repenseai.utils.logs import logger


class ChatAPI:
    def __init__(
        self,
        api_key: str,
        model: str = "claude-3-haiku-20240307",
        temperature: float = 0.0,
        max_tokens: int = 3500,
        stream: bool = False,
        tools: List[Callable] = None,
        **kwargs,
    ):
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.stream = stream

        self.response = None
        self.tokens = None

        self.tools = None
        self.json_tools = None

        self.tool_flag = False

        if tools:
            self.tools = {tool.__name__: tool for tool in tools}
            self.json_tools = [self.__function_to_json(tool) for tool in tools]

        self.client = Anthropic(api_key=self.api_key)


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
            "name": func.__name__,
            "description": func.__doc__ or "",
            "input_schema": {
                "type": "object",
                "properties": parameters,
                "required": required,
            },
        }         

    def _stream_api_call(self, json_data: Dict[str, Any]) -> Any:
        with self.client.messages.stream(**json_data) as stream:
            for message in stream:
                yield message

    def __process_content_image(self, image_url: dict) -> dict:
        url = image_url.get('url')

        image_content = httpx.get(url).content
        image = base64.standard_b64encode(image_content).decode("utf-8")

        return image

    def __get_media_type(self, image_url: dict) -> str:
        return "image/png" if "png" in image_url.get('url') else "image/jpeg"

    def __process_prompt_list(self, prompt: list) -> list:
        for history in prompt:
            content = history.get('content', [])
            
            if content[0].get('type') == 'image_url':
                if self.model not in VISION_MODELS:
                    prompt.remove(history)
                    continue

                image_url = content[0].get('image_url')

                img_dict = {
                    "type": "image",
                    "source": {
                        "data": self.__process_content_image(image_url),
                        "type": "base64",
                        "media_type": self.__get_media_type(image_url),
                    },
                }

                content[0] = img_dict                

        return prompt

    def call_api(self, prompt: list | str) -> Any:
        json_data = {
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }

        if isinstance(prompt, list):
            json_data['messages'] = self.__process_prompt_list(prompt)
        else:
            json_data['messages'] = [{"role": "user", "content": prompt}]

        try:
            if self.stream:
                return self._stream_api_call(json_data)
            
            if self.tools:
                json_data["tools"] = self.json_tools

            self.response = self.client.messages.create(**json_data)
            self.tokens = self.get_tokens()

            return self.get_output()

        except Exception as e:
            logger(f"Erro na chamada da API - modelo {json_data['model']}: {e}")

    def get_response(self) -> Any:
        return self.response

    def get_output(self) -> Union[None, str]:
        if self.response is not None:
            dump = self.response.model_dump()
            if dump['stop_reason'] == "tool_use":
                self.tool_flag = True
                return {"role": "assistant", "content": dump['content']}
            self.tool_flag = False
            return self.response.content[0].text
        else:
            return None

    def get_tokens(self) -> Union[None, str]:
        if self.response is not None:

            input_tokens = self.response.usage.input_tokens
            output_tokens = self.response.usage.output_tokens

            return {
                "completion_tokens": output_tokens,
                "prompt_tokens": input_tokens,
                "total_tokens": output_tokens + input_tokens,
            }
        else:
            return None

    def process_stream_chunk(self, chunk: Any) -> Union[str, None]:
        if chunk.type == "content_block_delta":
            return chunk.delta.text
        if chunk.type == "message_stop":
            usage = chunk.model_dump()["message"]["usage"]

            input_tokens = usage.get("input_tokens", 0)
            output_tokens = usage.get("output_tokens", 0)

            self.tokens = {
                "completion_tokens": output_tokens,
                "prompt_tokens": input_tokens,
                "total_tokens": output_tokens + input_tokens,
            }

    def process_tool_calls(self, message: dict) -> list:
        tools = message.get("content")
        tool_messages = []

        for tool in tools:
            if tool['type'] == "tool_use":
                args = tool.get('input')
                output = self.tools[tool.get('name')](**args)

                tool_messages.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": tool.get('id'),
                        "content": str(output)
                    }
                )

        return [{"role": "user", "content": tool_messages}]

class AudioAPI:
    def __init__(self, api_key: str, model: str, **kwargs):
        self.client = Anthropic(api_key=api_key)
        self.model = model

    def call_api(self, audio: Any):
        _ = audio

        return "Not implemented"

    def get_tokens(self):
        return {"completion_tokens": 0, "prompt_tokens": 0, "total_tokens": 0}


class VisionAPI:
    def __init__(
        self,
        api_key: str,
        model: str = "claude-3-sonnet-20240229",
        temperature: float = 0.0,
        max_tokens: int = 3500,
        stream: bool = False,
    ):
        self.client = Anthropic(api_key=api_key)
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.stream = stream

        self.response = None
        self.tokens = None

    def _stream_api_call(self, json_data: Dict[str, Any]) -> Any:
        with self.client.messages.stream(**json_data) as stream:
            for message in stream:
                yield message

    def _resize_image(self, image: Image.Image) -> Image.Image:
        max_size = 1568
        min_size = 200
        width, height = image.size

        if max(width, height) > max_size:
            aspect_ratio = width / height
            if width > height:
                new_width = max_size
                new_height = int(new_width / aspect_ratio)
            else:
                new_height = max_size
                new_width = int(new_height * aspect_ratio)
            image = image.resize((new_width, new_height))
        elif min(width, height) < min_size:
            aspect_ratio = width / height
            if width < height:
                new_width = min_size
                new_height = int(new_width / aspect_ratio)
            else:
                new_height = min_size
                new_width = int(new_height * aspect_ratio)
            image = image.resize((new_width, new_height))

        return image

    def _process_image(self, image: Any) -> bytearray:
        if isinstance(image, str):
            return image
        elif isinstance(image, Image.Image):
            img_byte_arr = io.BytesIO()

            image = self._resize_image(image)
            image.save(img_byte_arr, format="PNG")

            img_byte_arr = img_byte_arr.getvalue()
            image_string = base64.b64encode(img_byte_arr).decode("utf-8")

            return image_string
        else:
            raise Exception("Incorrect image type! Accepted: img_string or Image")
        
    def __create_content_image(self, image: str | Image.Image) -> dict:
        img = self._process_image(image)
        img_dict = {
            "type": "image",
            "source": {
                "data": img,
                "type": "base64",
                "media_type": "image/png",
            },
        }

        return img_dict
    
    def __process_prompt_content(self, prompt: str | list) -> bytearray:
        if isinstance(prompt, str):
            content = [{"type": "text", "text": prompt}]
        else:
            content = prompt[-1].get("content", [])

        return content
    
    def __process_content_image(self, content: list, image: str | Image.Image | list) -> list:
        if isinstance(image, str) or isinstance(image, Image.Image):
            img_dict = self.__create_content_image(image)
            content.insert(0, img_dict)

        elif isinstance(image, list):
            for img in image:
                img_dict = self.__create_content_image(img)
                content.insert(0, img_dict)
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

    def call_api(self, prompt: str | list, image: str | Image.Image | list) -> Any:

        content = self.__process_prompt_content(prompt)
        content = self.__process_content_image(content, image)

        prompt = self.__process_prompt(prompt, content)

        json_data = {
            "model": self.model,
            "messages": prompt,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
        }

        try:
            if self.stream:
                return self._stream_api_call(json_data)

            self.response = self.client.messages.create(**json_data)
            self.tokens = self.get_tokens()

            return self.get_output()
        except Exception as e:
            logger(f"Erro na chamada da API - modelo {json_data['model']}: {e}")

    def get_output(self) -> Union[None, str]:
        if self.response is not None:
            return self.response.content[0].text
        else:
            return None

    def get_tokens(self) -> Union[None, str]:
        if self.response is not None:

            input_tokens = self.response.usage.input_tokens
            output_tokens = self.response.usage.output_tokens

            return {
                "completion_tokens": output_tokens,
                "prompt_tokens": input_tokens,
                "total_tokens": output_tokens + input_tokens,
            }
        else:
            return None

    def process_stream_chunk(self, chunk: Any) -> Union[str, None]:
        if chunk.type == "content_block_delta":
            return chunk.delta.text
        if chunk.type == "message_stop":
            usage = chunk.model_dump()["message"]["usage"]

            input_tokens = usage.get("input_tokens", 0)
            output_tokens = usage.get("output_tokens", 0)

            self.tokens = {
                "completion_tokens": output_tokens,
                "prompt_tokens": input_tokens,
                "total_tokens": output_tokens + input_tokens,
            }


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