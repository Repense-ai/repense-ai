from repenseai.genai.tasks.base import BaseTask


class AsyncDummyTask(BaseTask):
    """A simple dummy task that returns the context unchanged"""

    async def run(self, context: dict | None = None) -> dict:
        return context or {}  # returns empty dict if context is None


class AsyncBooleanConditionalTask(BaseTask):
    """
    An async version of BooleanConditionalTask that executes asynchronously.

    A chatbot Workflow step that initializes with:
    - a condition to evaluate (i.e. len(json.loads(response)) > 0)
    - a task to execute if the condition is true
    - a task to execute if the condition is false

    It then interfaces using the same interface as a Task, with the .run method
    requiring a context, and the context requiring the response
    from the previous step (which needs evaluation).
    """

    def __init__(self, condition, true_task, false_task):
        self.condition = condition
        self.true_task = true_task
        self.false_task = false_task

    async def run(self, context: dict | None = None):
        """
        Execute the appropriate task based on the condition evaluation

        Args:
            context: Dictionary containing data for condition evaluation

        Returns:
            The result of the executed task
        """
        if not context:
            context = {}

        if self.condition(context):
            return await self.true_task.run(context)
        else:
            return await self.false_task.run(context)


class AsyncConditionalTask(BaseTask):
    """
    An async version of ConditionalTask that executes asynchronously.

    A chatbot Workflow step that initializes with:
    - a condition to evaluate
    - a dict with {value: task} pairs

    It then interfaces using the same interface as a Task, with the .run method
    requiring a context, executing the task that matches the value
    from the condition.
    """

    def __init__(self, condition, tasks, default_task=None):
        self.condition = condition
        self.tasks = tasks
        self.default_task = default_task or AsyncDummyTask()

    async def run(self, context: dict | None = None):
        """
        Execute the task corresponding to the condition's result value

        Args:
            context: Dictionary containing data for condition evaluation

        Returns:
            The result of the executed task
        """
        if not context:
            context = {}

        condition_result = self.condition(context)
        if condition_result in self.tasks:
            return await self.tasks[condition_result].run(context)
        else:
            return await self.default_task.run(context)


class DummyTask(BaseTask):
    def run(self, context: dict | None = None) -> dict:
        return context or {}  # returns empty dict if context is None


class BooleanConditionalTask(BaseTask):
    """
    A chatbot Workflow step that initializes with:

    - a condition to evaluate (i.e. len(json.loads(response)) > 0)
    - a task to execute if the condition is true
    - a task to execute if the condition is false

    It then interfaces using the same interface as a Task, with the .run method
        requiring a user_input and a context, and the context requiring the response
        from the previous step (which needs evaluation).
    """

    def __init__(self, condition, true_task, false_task):
        self.condition = condition
        self.true_task = true_task
        self.false_task = false_task

    def run(self, context: dict | None = None):

        if not context:
            context = {}

        if self.condition(context):
            return self.true_task.run(context)
        else:
            return self.false_task.run(context)


class ConditionalTask(BaseTask):
    """
    A chatbot Workflow step that initializes with:

    - a condition to evaluate
    - a dict with {value: task} pairs

    It then interfaces using the same interface as a Task, with the .run method
        requiring a user_input and a context, executing the task that matches the value
        from the condition.
    """

    def __init__(self, condition, tasks, default_task=None):
        self.condition = condition
        self.tasks = tasks
        self.default_task = default_task

    def run(self, context: dict | None = None):

        if not context:
            context = {}

        if self.condition(context) in self.tasks.keys():
            return self.tasks[self.condition(context)].run(context)
        else:
            return self.default_task.run(context)
