from typing import Optional

from repenseai.genai.tasks.api_task import Task
from repenseai.genai.selector import APISelector

class BaseLLMProvider:
    def __init__(
        self,
        name: str,
        model: str,
        model_type: str = "chat",
        api_key: Optional[str] = None,
        **kwargs
    ):
        self.name = name
        self.model = model
        self.model_type = model_type
        self.api_key = api_key
        self.kwargs = kwargs
        
        self.selector = APISelector(
            model=model,
            model_type=model_type,
            api_key=api_key,
            **kwargs
        )
        
        self.total_tokens = 0
        self.total_cost = 0.0

    async def generate(self, prompt: str, **kwargs) -> str:
        task = Task(
            selector=self.selector,
            instruction=prompt,
            simple_response=True,
            **kwargs
        )
        
        response = task.predict(context={})
        
        # Update usage statistics
        self.total_tokens += task.selector.api.tokens["total_tokens"]
        self.total_cost += task.selector.calculate_cost(task.selector.api.tokens)
        
        return response

    def calculate_cost(self) -> float:
        return self.total_cost