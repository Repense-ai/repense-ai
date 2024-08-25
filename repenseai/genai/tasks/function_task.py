from repenseai.genai.tasks.base_task import BaseTask
from typing import Callable


class FunctionTask(BaseTask):
    def __init__(self, function: Callable):
        self.function = function

    def predict(self, context: dict, **kwargs):
        response = self.function(context)
        return response
