import io
import base64
import json

from PIL import Image
from typing import Any, Dict, List, Union

import boto3

from repenseai.utils.logs import logger


class ChatAPI:
    def __init__(
        self,
        api_key: str,
        model: str = "amazon.nova-micro-v1:0",
        temperature: float = 0.0,
        max_tokens: int = 3500,
        stream: bool = False,
    ):
        _ = api_key
        self.model = model
        self.temperature = temperature
        self.stream = stream
        self.max_tokens = max_tokens

        self.response = None
        self.tokens = None

        self.client = boto3.client(
            "bedrock-runtime", 
            region_name="us-east-1"
        )      

    def call_api(self, prompt: Union[List[Dict[str, str]], str]) -> None:

        inference_config =  {
            "temperature": self.temperature,
            "maxTokens": self.max_tokens,
        }

        json_data = {
            "modelId": f"us.{self.model}",
            "inferenceConfig": inference_config,
        }

        if isinstance(prompt, list):
            json_data["messages"] = prompt
        else:
            json_data["messages"] = [{"role": "user", "content": [{"text": prompt}]}]

        try:
            if self.stream:
                self.response = self.client.converse_stream(**json_data)
                return self.response['stream']

            self.response = self.client.converse(**json_data)
            self.tokens = self.get_tokens()

            return self.get_text()

        except Exception as e:
            logger(f"Erro na chamada da API - modelo {json_data['modelId']}: {e}")

    def get_response(self) -> Any:
        return self.response

    def get_text(self) -> Union[None, str]:
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
            return chunk["contentBlockDelta"]["delta"]["text"]
        if "metadata" in chunk:

            input_tokens = chunk["metadata"]['usage']['inputTokens']
            output_tokens = chunk["metadata"]['usage']['outputTokens']

            self.tokens = {
                "completion_tokens": output_tokens,
                "prompt_tokens": input_tokens,
                "total_tokens": output_tokens + input_tokens,
            }


class AudioAPI:
    def __init__(self, api_key: str, model: str = ""):
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

    def process_image(self, image: Any, format: str = "PNG") -> bytearray:
        if isinstance(image, str):
            return base64.b64decode(image)
        elif isinstance(image, Image.Image):
            img_byte_arr = io.BytesIO()

            image.save(img_byte_arr, format=format)

            img_byte_arr = img_byte_arr.getvalue()

            return img_byte_arr
        else:
            raise Exception("Incorrect image type! Accepted: img_string or Image")          

    def call_api(self, prompt: str, image: Any):

        content = [{"text": prompt}]

        if isinstance(image, str) or isinstance(image, Image.Image):
            img = self.process_image(image)

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

                img = self.process_image(img)
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

        inference_config =  {
            "temperature": self.temperature,
            "maxTokens": self.max_tokens,
        }

        json_data = {
            "modelId": f"us.{self.model}",
            "inferenceConfig": inference_config,
            "messages": [{"role": "user", "content": content}],
        }

        try:
            if self.stream:
                return self.client.converse_stream(**json_data)

            self.response = self.client.converse(**json_data)
            self.tokens = self.get_tokens()

            return self.get_text()

        except Exception as e:
            logger(f"Erro na chamada da API - modelo {json_data['modelId']}: {e}")

    def get_response(self) -> Any:
        return self.response

    def get_text(self) -> Union[None, str]:
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
            return chunk["contentBlockDelta"]["delta"]["text"]
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
        base64_image_data = self.response["images"][0]
        return base64.b64decode(base64_image_data)

    def get_tokens(self):
        return 1