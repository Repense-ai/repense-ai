import io
import json

from google import genai
from google.genai import types

from pydantic import BaseModel

from typing import Any, List, Union, Callable

from repenseai.utils.text import extract_json_text


class ChatAPI:
    def __init__(
        self,
        api_key: str,
        model: str = "gemini-2.0-flash",
        temperature: float = 0.0,
        max_tokens: int = 3500,
        stream: bool = False,
        tools: List[Callable] = None,
        json_schema: BaseModel = None,
        **kwargs,
    ):
        self.api_key = api_key
        self.stream = stream
        self.json_schema = json_schema

        self.response = None
        self.tokens = None

        self.tool_flag = False
        self.tools = tools

        self.client = genai.Client(api_key=self.api_key)
        self.model = model

        self.config = types.GenerateContentConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
            tools=self.tools,
            response_mime_type="application/json" if self.json_schema else None,
            response_schema=self.json_schema,
        )

    def __convert_image_to_bytes(self, img):
        if hasattr(img, "convert"):  # Check if it's a PIL Image
            img_byte_arr = io.BytesIO()
            img.convert("RGB").save(img_byte_arr, format="JPEG")
            return img_byte_arr.getvalue()
        return img  # Return as-is if already bytes

    def __process_str_prompt(
        self, prompt: str, image: Union[Any, List[Any]] = None
    ) -> str:
        self.prompt = prompt
        content = [{"role": "user", "parts": [{"text": prompt}]}]

        # Add images if provided
        if image is not None:
            if isinstance(image, list):
                for img in image:
                    img_bytes = self.__convert_image_to_bytes(img)
                    content[0]["parts"].append(
                        {"inline_data": {"mime_type": "image/jpeg", "data": img_bytes}}
                    )
            else:
                img_bytes = self.__convert_image_to_bytes(image)
                content[0]["parts"].append(
                    {"inline_data": {"mime_type": "image/jpeg", "data": img_bytes}}
                )

        if self.stream:
            self.response = self.client.models.generate_content_stream(
                model=self.model,
                contents=content,
                config=self.config,
            )
        else:
            self.response = self.client.models.generate_content(
                model=self.model,
                contents=content,
                config=self.config,
            )
            self.tokens = self.get_tokens()
            return self.get_output()

        return self.response

    def __process_list_prompt(self, prompt: list) -> str:
        # Convert the prompt list to the format expected by Gemini
        contents = []
        for message in prompt:
            role = "user" if message.get("role") == "user" else "model"
            parts = []

            # Handle text content
            if isinstance(message.get("content"), str):
                text = message.get("content")
                parts.append({"text": text})
            else:
                for content_item in message.get("content", []):
                    if content_item.get("type") == "text":
                        parts.append({"text": content_item.get("text", "")})
                    elif content_item.get("type") == "image":
                        img_bytes = self.__convert_image_to_bytes(
                            content_item.get("image")
                        )
                        parts.append(
                            {
                                "inline_data": {
                                    "mime_type": "image/jpeg",
                                    "data": img_bytes,
                                }
                            }
                        )

            if parts:  # Only add message if it has parts
                contents.append({"role": role, "parts": parts})

        if not contents:
            raise ValueError("No valid content found in prompt messages")

        # Get the last text part for token counting
        self.prompt = next(
            (
                part["text"]
                for msg in reversed(contents)
                for part in msg["parts"]
                if "text" in part
            ),
            "",
        )

        if self.stream:
            self.response = self.client.models.generate_content_stream(
                model=self.model,
                contents=contents,
                config=self.config,
            )
        else:
            self.response = self.client.models.generate_content(
                model=self.model,
                contents=contents,
                config=self.config,
            )
            self.tokens = self.get_tokens()
            return self.get_output()

        return self.response

    def call_api(self, prompt: Union[str, list], image: Union[Any, List[Any]] = None):
        if isinstance(prompt, str):
            return self.__process_str_prompt(prompt, image)
        else:
            return self.__process_list_prompt(prompt)

    def get_response(self) -> Any:
        return self.response

    def get_output(self) -> Union[None, str]:
        if self.response is not None:
            if self.json_schema:
                return json.loads(extract_json_text(self.response.text))
            return self.response.text
        else:
            return None

    def get_tokens(self) -> Union[None, dict]:
        if self.response is not None:
            try:
                prompt_tokens = self.client.models.count_tokens(
                    model=self.model, contents=self.prompt
                ).total_tokens

                output_tokens = self.client.models.count_tokens(
                    model=self.model, contents=self.response.text
                ).total_tokens

                return {
                    "completion_tokens": output_tokens,
                    "prompt_tokens": prompt_tokens,
                    "total_tokens": output_tokens + prompt_tokens,
                }
            except Exception as e:
                return {
                    "completion_tokens": 0,
                    "prompt_tokens": 0,
                    "total_tokens": 0,
                }
        else:
            return None

    def process_stream_chunk(self, chunk: Any) -> str:
        if chunk.usage_metadata.candidates_token_count:
            self.tokens = {
                "completion_tokens": chunk.usage_metadata.candidates_token_count,
                "prompt_tokens": chunk.usage_metadata.prompt_token_count,
                "total_tokens": (
                    chunk.usage_metadata.candidates_token_count
                    + chunk.usage_metadata.prompt_token_count
                ),
            }
            return chunk.text
        else:
            return chunk.text


class VisionAPI:
    def __init__(
        self,
        api_key: str,
        model: str = "gemini-pro-vision",
        temperature: float = 0.0,
        max_tokens: int = 3500,
        stream: bool = False,
    ):
        self.api_key = api_key
        self.stream = stream

        self.client = genai.Client(api_key=self.api_key)
        self.model = model

        self.config = types.GenerateContentConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
        )

        self.prompt = None
        self.image = None
        self.response = None
        self.tokens = None

    def __process_list_prompt(self, prompt: list) -> str:
        if isinstance(prompt[-1].get("content"), str):
            return prompt[-1]["content"]
        return next(
            (
                item["text"]
                for item in prompt[-1]["content"]
                if item.get("type") == "text"
            ),
            "",
        )

    def __convert_image_to_bytes(self, img):
        if hasattr(img, "convert"):  # Check if it's a PIL Image
            img_byte_arr = io.BytesIO()
            img.convert("RGB").save(img_byte_arr, format="JPEG")
            return img_byte_arr.getvalue()
        return img  # Return as-is if already bytes

    def call_api(self, prompt: Union[str, list], image: Union[Any, List[Any]]):
        if isinstance(prompt, list):
            self.prompt = self.__process_list_prompt(prompt)
        else:
            self.prompt = prompt

        self.image = image

        contents = [{"role": "user", "parts": [{"text": self.prompt}]}]

        if isinstance(self.image, list):
            for img in self.image:
                img_bytes = self.__convert_image_to_bytes(img)
                contents[0]["parts"].append(
                    {"inline_data": {"mime_type": "image/jpeg", "data": img_bytes}}
                )
        else:
            img_bytes = self.__convert_image_to_bytes(self.image)
            contents[0]["parts"].append(
                {"inline_data": {"mime_type": "image/jpeg", "data": img_bytes}}
            )

        if self.stream:
            self.response = self.client.models.generate_content_stream(
                model=self.model,
                contents=contents,
                config=self.config,
            )
        else:
            self.response = self.client.models.generate_content(
                model=self.model,
                contents=contents,
                config=self.config,
            )
            self.tokens = self.get_tokens()
            return self.get_output()

        return self.response

    def get_output(self) -> Union[None, str]:
        if self.response is not None:
            return self.response.text
        else:
            return None

    def get_tokens(self) -> Union[None, dict]:
        if self.response is not None:
            prompt_tokens = self.client.models.count_tokens(
                model=self.model, contents=self.prompt
            ).total_tokens
            img_tokens = self.client.models.count_tokens(
                model=self.model, contents=self.image
            ).total_tokens
            output_tokens = self.client.models.count_tokens(
                model=self.model, contents=self.response.text
            ).total_tokens

            return {
                "completion_tokens": output_tokens,
                "prompt_tokens": prompt_tokens + img_tokens,
                "total_tokens": output_tokens + prompt_tokens + img_tokens,
            }
        else:
            return None

    def process_stream_chunk(self, chunk: Any) -> str:
        if chunk.usage_metadata.candidates_token_count:
            self.tokens = {
                "completion_tokens": chunk.usage_metadata.candidates_token_count,
                "prompt_tokens": chunk.usage_metadata.prompt_token_count,
                "total_tokens": (
                    chunk.usage_metadata.candidates_token_count
                    + chunk.usage_metadata.prompt_token_count
                ),
            }
            return chunk.text
        else:
            return chunk.text


class ImageAPI:
    def __init__(
        self,
        api_key: str,
        model: str = "imagen-2.0",
        aspect_ratio: str = "1:1",
        **kwargs,
    ):
        self.api_key = api_key
        self.client = genai.Client(api_key=self.api_key)
        self.model = model

        self.aspect_ratio = aspect_ratio
        self.allowed_ar = ["16:9", "1:1", "2:3", "3:2", "4:5", "5:4", "9:16"]
        self.__check_aspect_ratio()

        self.response = None
        self.tokens = None

    def __check_aspect_ratio(self):
        if self.aspect_ratio not in self.allowed_ar:
            self.aspect_ratio = "1:1"

    def call_api(self, prompt: Any, image: Any):
        _ = image  # Unused parameter

        self.response = self.client.models.generate_images(
            model=self.model,
            prompt=prompt,
            config=types.GenerateImagesConfig(
                number_of_images=1,
                aspect_ratio=self.aspect_ratio,
                safety_filter_level="block_low_and_above",
                person_generation="ALLOW_ADULT",
            ),
        )

        self.tokens = self.get_tokens()

        return self.get_output()

    def get_output(self):
        if images := self.response.generated_images:
            return images[0].image.image_bytes
        return None

    def get_tokens(self):
        if hasattr(self.response, "usage_metadata"):
            return {
                "completion_tokens": self.response.usage_metadata.candidates_token_count,
                "prompt_tokens": self.response.usage_metadata.prompt_token_count,
                "total_tokens": self.response.usage_metadata.total_token_count,
            }
        return {"completion_tokens": 1, "prompt_tokens": 1, "total_tokens": 2}


class AudioAPI:
    def __init__(self, api_key: str, model: str, **kwargs):
        self.api_key = api_key
        self.model = model
        self.client = genai.Client(api_key=self.api_key)

    def call_api(self, audio: Any):
        _ = audio  # Unused parameter
        return self.get_output()

    def get_output(self):
        return "Not Implemented"

    def get_tokens(self):
        return {"completion_tokens": 0, "prompt_tokens": 0, "total_tokens": 0}


class SpeechAPI:
    def __init__(self, api_key: str, model: str, **kwargs):
        self.api_key = api_key
        self.model = model
        self.client = genai.Client(api_key=self.api_key)

    def call_api(self, text: str) -> bytes:
        _ = text  # Unused parameter
        return self.get_output()

    def get_output(self):
        return "Not Implemented"

    def get_tokens(self):
        return 0
