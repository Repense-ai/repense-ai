import io
import base64
import json
import httpx

from PIL import Image
from typing import Any, Union

import boto3

from repenseai.utils.logs import logger

from repenseai.genai.providers import VISION_MODELS


class ChatAPI:
    def __init__(
        self,
        api_key: str,
        model: str = "amazon.nova-micro-v1:0",
        temperature: float = 0.0,
        max_tokens: int = 3500,
        stream: bool = False,
        **kwargs,
    ):
        _ = api_key
        self.model = model
        self.temperature = temperature
        self.stream = stream
        self.max_tokens = max_tokens

        self.tool_flag = False

        self.response = None
        self.tokens = None

        self.client = boto3.client(
            "bedrock-runtime", 
            region_name="us-east-1"
        )

    def __process_content_image(self, image_url: dict) -> dict:
        url = image_url.get('url')
        image_content = httpx.get(url).content

        return image_content

    def __get_media_type(self, image_url: dict) -> str:
        return "png" if "png" in image_url.get('url') else "jpeg"

    def __process_prompt_list(self, prompt: list) -> list:

        # Remove type if exists
        for message in prompt:
            for i, content in enumerate(message.get('content', [])):                
                if content:
                    if content.get('type'):
                        del message['content'][i]['type']
                    if image_url := content.get('image_url'):
                        message['content'][i] = {
                            "image": {
                                "format": self.__get_media_type(image_url), 
                                'source': {
                                    "bytes": self.__process_content_image(image_url),
                                }
                            }
                        }
                        
        if self.model not in VISION_MODELS:
            for message in prompt:
                if "image" in message.get('content', [{"": ""}])[0]:
                    prompt.remove(message)

        # Merge consecutive user messages
        i = 0
        while i < len(prompt) - 1:
            if prompt[i]['role'] == 'user' and prompt[i + 1]['role'] == 'user':
                if isinstance(prompt[i]['content'], list):
                    prompt[i]['content'].extend(prompt[i + 1]['content'])
                else:
                    prompt[i]['content'] = [prompt[i]['content']] + (
                        prompt[i + 1]['content'] if isinstance(prompt[i + 1]['content'], list) 
                        else [prompt[i + 1]['content']]
                    )
                prompt.pop(i + 1)
            else:
                i += 1

        return prompt

    def call_api(self, prompt: list | str) -> None:

        inference_config =  {
            "temperature": self.temperature,
            "maxTokens": self.max_tokens,
        }

        json_data = {
            "modelId": f"us.{self.model}",
            "inferenceConfig": inference_config,
        }

        if isinstance(prompt, list):
            json_data["messages"] = self.__process_prompt_list(prompt)
        else:
            json_data["messages"] = [{"role": "user", "content": [{"text": prompt}]}]

        try:
            if self.stream:
                self.response = self.client.converse_stream(**json_data)
                return self.response['stream']

            self.response = self.client.converse(**json_data)
            self.tokens = self.get_tokens()

            return self.get_output()

        except Exception as e:
            logger(f"Erro na chamada da API - modelo {json_data['modelId']}: {e}")

    def get_response(self) -> Any:
        return self.response

    def get_output(self) -> Union[None, str]:
        if self.response is not None:
            return self.response["output"]["message"]["content"][0]["text"]
        else:
            return None

    def get_tokens(self) -> Union[None, str]:
        if self.response is not None:

            input_tokens = self.response['usage']['inputTokens']
            output_tokens = self.response['usage']['outputTokens']

            return {
                "completion_tokens": output_tokens,
                "prompt_tokens": input_tokens,
                "total_tokens": output_tokens + input_tokens,
            }
        else:
            return None

    def process_stream_chunk(self, chunk: Any) -> Union[str, None]:
        if "contentBlockDelta" in chunk:

            text = chunk["contentBlockDelta"]["delta"]["text"]

            if text:
                return text
            
        if "metadata" in chunk:

            input_tokens = chunk["metadata"]['usage']['inputTokens']
            output_tokens = chunk["metadata"]['usage']['outputTokens']

            self.tokens = {
                "completion_tokens": output_tokens,
                "prompt_tokens": input_tokens,
                "total_tokens": output_tokens + input_tokens,
            }


class AudioAPI:
    def __init__(self, api_key: str, model: str, **kwargs):
        self.api_key = api_key
        self.model = model

    def call_api(self, audio: io.BufferedReader):
        _ = audio

        return "Not Implemented"

    def get_tokens(self):
        return {"completion_tokens": 0, "prompt_tokens": 0, "total_tokens": 0}


class VisionAPI:
    def __init__(
        self,
        api_key: str,
        model: str = "",
        temperature: float = 0.0,
        max_tokens: int = 3500,
        stream: bool = False,
    ):
        self.client = boto3.client(
            "bedrock-runtime", 
            region_name="us-east-1"
        )

        _ = api_key

        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.stream = stream

        self.response = None
        self.tokens = None

    def _process_image(self, image: Any, format: str = "PNG") -> bytearray:
        if isinstance(image, str):
            return base64.b64decode(image)
        elif isinstance(image, Image.Image):
            img_byte_arr = io.BytesIO()

            image.save(img_byte_arr, format=format)

            img_byte_arr = img_byte_arr.getvalue()

            return img_byte_arr
        else:
            raise Exception("Incorrect image type! Accepted: img_string or Image")

    def __process_prompt_content(self, prompt: str | list) -> bytearray:
        if isinstance(prompt, str):
            content = [{"text": prompt}]
        else:
            content = prompt[-1].get("content", [])

        return content
    
    def __process_content_image(self, content: list, image: str | Image.Image | list) -> bytearray:
        if isinstance(image, str) or isinstance(image, Image.Image):
            img = self._process_image(image)

            img_dict = {
                "image": {
                    "format": "png", 
                    'source': {
                        "bytes": img,
                    }
                }
            }

            content.append(img_dict)

        elif isinstance(image, list):

            for img in image:

                img = self._process_image(img)
                img_dict = {
                    "image": {
                        "format": "png", 
                        'source': {
                            "bytes": img,
                        }
                    }
                }

                content.append(img_dict)
        else:
            raise Exception(
                "Incorrect image type! Accepted: img_string or list[img_string]"
            )
        
        return content

    def __process_prompt(self, prompt: str | list, content: list) -> list:
        if isinstance(prompt, list):
            prompt[-1] = {"role": "user", "content": content}

            # Remove type if exists
            for message in prompt:
                for i, content in enumerate(message.get('content', [])):
                    if content:
                        if content.get('type'):
                            del message['content'][i]['type']
            
            # Merge consecutive user messages
            i = 0
            while i < len(prompt) - 1:
                if prompt[i]['role'] == 'user' and prompt[i + 1]['role'] == 'user':
                    if isinstance(prompt[i]['content'], list):
                        prompt[i]['content'].extend(prompt[i + 1]['content'])
                    else:
                        prompt[i]['content'] = [prompt[i]['content']] + (
                            prompt[i + 1]['content'] if isinstance(prompt[i + 1]['content'], list) 
                            else [prompt[i + 1]['content']]
                        )
                    prompt.pop(i + 1)
                else:
                    i += 1
        else:
            prompt = [{"role": "user", "content": content}]

        logger(prompt)
        return prompt

    def call_api(self, prompt: str | list, image: Any):

        content = self.__process_prompt_content(prompt)
        content = self.__process_content_image(content, image)

        prompt = self.__process_prompt(prompt, content)

        inference_config =  {
            "temperature": self.temperature,
            "maxTokens": self.max_tokens,
        }

        json_data = {
            "modelId": f"us.{self.model}",
            "inferenceConfig": inference_config,
            "messages": prompt,
        }

        try:
            if self.stream:
                self.response = self.client.converse_stream(**json_data)
                return self.response['stream']

            self.response = self.client.converse(**json_data)
            self.tokens = self.get_tokens()

            return self.get_output()

        except Exception as e:
            logger(f"Erro na chamada da API - modelo {json_data['modelId']}: {e}")

    def get_response(self) -> Any:
        return self.response

    def get_output(self) -> Union[None, str]:
        if self.response is not None:
            return self.response["output"]["message"]["content"][0]["text"]
        else:
            return None

    def get_tokens(self) -> Union[None, str]:
        if self.response is not None:

            input_tokens = self.response['usage']['inputTokens']
            output_tokens = self.response['usage']['outputTokens']

            return {
                "completion_tokens": output_tokens,
                "prompt_tokens": input_tokens,
                "total_tokens": output_tokens + input_tokens,
            }
        else:
            return None

    def process_stream_chunk(self, chunk: Any) -> Union[str, None]:
        if "contentBlockDelta" in chunk:
            
            text = chunk["contentBlockDelta"]["delta"]["text"]

            if text:
                return text
            
        if "metadata" in chunk:

            input_tokens = chunk["metadata"]['usage']['inputTokens']
            output_tokens = chunk["metadata"]['usage']['outputTokens']

            self.tokens = {
                "completion_tokens": output_tokens,
                "prompt_tokens": input_tokens,
                "total_tokens": output_tokens + input_tokens,
            }


class ImageAPI:
    def __init__(
            self, 
            api_key: str, 
            model: str = "", 
            aspect_ratio: str = '1:1',
            cfg_scale: int = 10,
            **kwargs,
        ):

        _ = api_key

        self.client = boto3.client(
            "bedrock-runtime", 
            region_name="us-east-1"
        )

        self.cfg_scale = cfg_scale

        self.model = model.split("/")[-1]
        self.aspect_ratio = aspect_ratio

        self.allowed_ar = [
            '16:9', '1:1', '2:3',
            '3:2', '4:5', '5:4', '9:16'
        ]

        self.response = None
        self.tokens = None

        self.ratio = self.__check_aspect_ratio()

    def __check_aspect_ratio(self):

        if self.aspect_ratio not in self.allowed_ar:
            self.aspect_ratio = '1:1'

        sizes = {
            '16:9': {'width': 1024, 'height': 576},
            '1:1': {'width': 512, 'height': 512},
            '2:3': {'width': 512, 'height': 768},
            '3:2': {'width': 768, 'height': 512},
            '4:5': {'width': 512, 'height': 640},
            '5:4': {'width': 640, 'height': 512},
            '9:16': {'width': 576, 'height': 1024},
        }
        
        return sizes[self.aspect_ratio]

    def call_api(self, prompt: Any, image: Any = None):

        _ = image

        payload = {
            "taskType": "TEXT_IMAGE",
            "textToImageParams": {"text": prompt},
            "imageGenerationConfig": {
                "width": self.ratio["width"],
                "height": self.ratio["height"],
                "cfgScale": self.cfg_scale,
                "numberOfImages": 1,
                "quality": "premium",
            }
        }

        model_response = self.client.invoke_model(
            modelId=f"{self.model}", 
            body=json.dumps(payload)
        )

        self.response = json.loads(model_response["body"].read())
        self.tokens = self.get_tokens()

        return self.get_image()
    
    def get_image(self):
        return self.response["images"][0]

    def get_tokens(self):
        return 1