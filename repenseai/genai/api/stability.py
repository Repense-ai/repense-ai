import requests
import io
import base64

from typing import Any

from PIL import Image


class ChatAPI:
    def __init__(self, api_key: str, model: str = ""):
        self.api_key = api_key
        self.model = model

    def call_api(self, prompt: Any):
        _ = prompt

        return "Not implemented"

    def get_tokens(self):
        return {"completion_tokens": 0, "prompt_tokens": 0, "total_tokens": 0}


class AudioAPI:
    def __init__(self, api_key: str, model: str = ""):
        self.api_key = api_key
        self.model = model

    def call_api(self, prompt: Any):
        _ = prompt

        return "Not implemented"

    def get_tokens(self):
        return {"completion_tokens": 0, "prompt_tokens": 0, "total_tokens": 0}
    

class VisionAPI:
    def __init__(self, api_key: str, model: str = ""):
        self.api_key = api_key
        self.model = model

    def call_api(self, prompt: Any):
        _ = prompt

        return "Not implemented"

    def get_tokens(self):
        return {"completion_tokens": 0, "prompt_tokens": 0, "total_tokens": 0}


class ImageAPI:
    def __init__(
            self, 
            api_key: str, 
            model: str = "",
            action: str = 'generate', 
            aspect_ratio: str = '1:1',
            strength: float = 0.5,
            seed: int = 0, 
            cfg_scale: int = 10,
            style_preset: str = "",
            **kwargs,
        ):

        self.api_key = api_key
        self.model = model
        self.action = action
        self.aspect_ratio = aspect_ratio
        self.seed = seed
        self.cfg_scale = cfg_scale
        self.strength = strength
        self.style_preset = style_preset
        
        self.root_url = 'https://api.stability.ai/v2beta/stable-image'

        self.response = None
        self.tokens = None

        self.allowed_ar = [
            '16:9', '1:1', '21:9', 
            '2:3', '3:2', '4:5', 
            '5:4', '9:16', '9:21'
        ]

        self.allowed_sp = [
            "3d-model",
            "analog-film" ,
            "anime", 
            "cinematic", 
            "comic-book" ,
            "digital-art" ,
            "enhance", 
            "fantasy-art" ,
            "isometric", 
            "line-art" ,
            "low-poly" ,
            "modeling-compound" ,
            "neon-punk" ,
            "origami", 
            "photographic", 
            "pixel-art" ,
            "tile-texture",
        ]

        self.__set_model_info()
        self.__build_url()
        self.__check_aspect_ratio()
        self.__check_style_preset()


    def __set_model_info(self):
        splitted = self.model.split("/")

        self.model_type = splitted[-1]
        self.model_name = splitted[-2] if splitted[-2] != "default" else None


    def __build_url(self):
        self.url = f"{self.root_url}/{self.action}/{self.model_type}"
    

    def __check_aspect_ratio(self):
        if self.aspect_ratio not in self.allowed_ar:
            self.aspect_ratio = '1:1'

    def __check_style_preset(self):
        if self.style_preset not in self.allowed_sp:
            self.style_preset = 'photographic'
        
    def __build_data(self, prompt: Any, image: Any):

        payload = {
            "prompt": prompt,
            "output_format": "png",
            "seed": self.seed,
            "cfg_scale": self.cfg_scale,
            "style_preset": self.style_preset
        }

        if self.model_name:
            payload["model"] = self.model_name

        if image:
            payload["strength"] = self.strength
            payload["mode"] = "image-to-image"
        else:
            payload["aspect_ratio"] = self.aspect_ratio
            payload["mode"] = "text-to-image"

        return payload


    def __build_files(self, image: Any):
        if not image:
            return {"none": ''}
        else:
            if isinstance(image, str):
                img = Image.open(image)
                img_byte_arr = io.BytesIO()

                img = self._resize_image(image)
                img.save(img_byte_arr, format="PNG")

                img_byte_arr = img_byte_arr.getvalue()

                return {"image": img}
            elif isinstance(image, Image.Image):
                img_byte_arr = io.BytesIO()

                image = self._resize_image(image)
                image.save(img_byte_arr, format="PNG")

                img_byte_arr = img_byte_arr.getvalue()

                return {"image": img_byte_arr}
            else:
                raise Exception("Incorrect image type! Accepted: img_string or PIL Image")
            

    def _resize_image(self, image: Image.Image) -> Image.Image:
        max_size = 16384
        min_size = 64
        min_total = 4096

        width, height = image.size

        if width * height < min_total:
            ratio = (width * height) / min_total

            width = int(width * ratio)
            height = int(height * ratio)

            image = image.resize((new_width, new_height))

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


    def call_api(self, prompt: Any, image: Any = None):
        data = self.__build_data(prompt, image)
        files = self.__build_files(image)

        self.response = requests.post(
            self.url,
            headers={
                "authorization": f"Bearer {self.api_key}",
                "accept": "image/*"
            },
            files=files,
            data=data,
        )

        if self.response.status_code == 200:
            self.tokens = self.get_tokens()
            return self.get_image()
        else:
            raise Exception(str(self.response.json()))

    def get_image(self):
        return base64.b64encode(
            self.response.content
        ).decode('utf-8')

    def get_tokens(self):
        return 1