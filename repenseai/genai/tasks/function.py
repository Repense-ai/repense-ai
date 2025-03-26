from repenseai.genai.tasks.base import BaseTask
from typing import Callable, Awaitable, Any


class AsyncFunctionTask(BaseTask):
    """
    A task that wraps an async function to be used in an AsyncWorkflow
    """

    def __init__(self, function: Callable[..., Awaitable[Any]]):
        """
        Initialize the task with an async function

        Args:
            function: The async function to be executed
        """
        self.function = function

    async def run(self, context: dict | None = None, **kwargs):
        """
        Execute the async function with the given context

        Args:
            context: Dictionary containing data to be passed to the function

        Returns:
            The result of the function execution
        """
        if not context:
            context = {}

        response = await self.function(context)
        return response


class FunctionTask(BaseTask):
    """
    A task that wraps a synchronous function to be used in a Workflow
    """

    def __init__(self, function: Callable):
        """
        Initialize the task with a function

        Args:
            function: The function to be executed
        """
        self.function = function

    def run(self, context: dict | None = None, **kwargs):
        """
        Execute the function with the given context

        Args:
            context: Dictionary containing data to be passed to the function

        Returns:
            The result of the function execution
        """
        if not context:
            context = {}

        response = self.function(context)
        return response
