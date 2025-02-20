from typing import Optional

from repenseai.genai.tasks.api import Task
from repenseai.genai.agent import Agent

class BaseagentProvider:
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
        
        self.agent = Agent(
            model=model,
            model_type=model_type,
            api_key=api_key,
            **kwargs
        )
        
        self.total_tokens = 0
        self.total_cost = 0.0

    async def generate(self, prompt: str, **kwargs) -> str:
        task = Task(
            agent=self.agent,
            instruction=prompt,
            simple_response=True,
            **kwargs
        )
        
        response = task.run(context={})
        
        # Update usage statistics
        self.total_tokens += task.agent.api.tokens["total_tokens"]
        self.total_cost += task.agent.calculate_cost(task.agent.api.tokens)
        
        return response

    def calculate_cost(self) -> float:
        return self.total_cost