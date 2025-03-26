from repenseai.genai.tasks.base import BaseTask
from repenseai.utils import logs


class AsyncWorkflow(BaseTask):
    """
    Async version of the Workflow class to execute a series of steps asynchronously.
    Steps are executed in sequence, but each step can be an async task.
    """

    def __init__(self, steps):
        self.steps = steps

    async def run(self, context: dict | None = None):
        """
        Run each step in the workflow asynchronously

        Args:
            context: Dictionary containing data to be passed between steps

        Returns:
            The updated context dictionary after all steps have been executed
        """
        if not context:
            context = {}

        for step in self.steps:
            try:
                if isinstance(step[0], BaseTask):
                    if step[1] is None:
                        await step[0].run(context)
                    else:
                        context[step[1]] = await step[0].run(context)
                else:
                    context[step[1]] = await step[0](context)

            except Exception as e:
                logs.logger(f"step {step[1]} -> Error: {e}")

        return context


class Workflow(BaseTask):

    def __init__(self, steps):
        self.steps = steps

    def run(self, context: dict | None = None):

        if not context:
            context = {}

        for step in self.steps:
            try:
                if isinstance(step[0], BaseTask):
                    if step[1] is None:
                        step[0].run(context)
                    else:
                        context[step[1]] = step[0].run(context)
                else:
                    context[step[1]] = step[0](context)

            except Exception as e:
                logs.logger(f"step {step[1]} -> Erro: {e}")

        return context
