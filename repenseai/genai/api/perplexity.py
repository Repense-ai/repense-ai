import io
import requests

from typing import Any, Dict, List, Union

from repenseai.utils.logs import logger


class ChatAPI:
    def __init__(
        self,
        api_key: str,
        model: str = "",
        temperature: float = 0.0,
        max_tokens: int = 3500,
        stream: bool = False,
        **kwargs,
    ):
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.stream = stream
        self.max_tokens = max_tokens

        self.tool_flag = False

        self.url = "https://api.perplexity.ai/chat/completions"

        self.response = None
        self.tokens = None

        self.__build_headers()

    def __build_headers(self):
        self.headers = {
            "Authorization": f"Bearer {self.api_key }",
            "Content-Type": "application/json"
        }

    def __process_prompt_list(self, prompt: list) -> list:

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

    def call_api(self, prompt: list | str) -> Any:

        json_data = {
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.tokens,
            "stream": self.stream,
            "stream_options": {"include_usage": True},
            "search_recency_filter": "day",
        }

        if isinstance(prompt, list):
            json_data["messages"] = self.__process_prompt_list(prompt)
        else:
            json_data["messages"] = [{"role": "user", "content": prompt}]

        try:
            self.response = requests.post(
                url=self.url,
                headers=self.headers,
                json=json_data
            )

            if not self.stream:
                self.tokens = self.get_tokens()
                return self.get_output()

            return self.response

        except Exception as e:
            logger(f"Erro na chamada da API - modelo {json_data['model']}: {e}")

    def get_output(self) -> Union[None, str]:
        if self.response is not None:
            return self.response.json()["choices"][0]["message"]["content"]
        else:
            return None

    def get_tokens(self) -> Union[None, str]:
        if self.response is not None:
            return self.response.json()["usage"]
        else:
            return None

    def process_stream_chunk(self, chunk: Any) -> Union[str, None]:
        if chunk.choices[0].finish_reason == "stop":
            self.tokens = chunk.json()["usage"]
        else:
            string += chunk.choices[0].delta.content
                

class VisionAPI:
    def __init__(
        self,
        api_key: str,
        model: str = "",
        temperature: float = 0.0,
        max_tokens: int = 3500,
        stream: bool = False,
    ):
        self.client = api_key

        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.stream = stream

        self.response = None
        self.tokens = None

    def call_api(self, prompt: str, image: Any):
        _ = prompt
        _ = image

        return "Not Implemented"

    def get_output(self) -> Union[None, str]:
        if self.response is not None:
            return self.response.model_dump()["choices"][0]["message"]["content"]
        else:
            return None

    def get_tokens(self):
        return {"completion_tokens": 0, "prompt_tokens": 0, "total_tokens": 0}

    def process_stream_chunk(self, chunk: Any) -> Union[str, None]:
        if chunk.choices[0].finish_reason == "stop":
            tokens = chunk.model_dump()["usage"]
        else:
            string += chunk.choices[0].delta.content


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