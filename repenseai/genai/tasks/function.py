from repenseai.genai.tasks.base import BaseTask
from typing import Callable


class FunctionTask(BaseTask):
    def __init__(self, function: Callable):
        self.function = function

    def run(self, context: dict | None = None, **kwargs):
        if not context:
            context = {}
            
        response = self.function(context)
        return response
