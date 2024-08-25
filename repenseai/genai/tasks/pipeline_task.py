from repenseai.genai.tasks.base_task import BaseTask
from repenseai.utils import logs


class Pipeline(BaseTask):
    def __init__(self, steps):
        self.steps = steps

    def predict(self, context):
        for step in self.steps:
            try:
                if isinstance(step[0], BaseTask):
                    context[step[1]] = step[0].predict(context)
                else:
                    context[step[1]] = step[0](context)
            except Exception as e:
                logs.logger(f"step {step[1]} -> Erro: {e}")

        return context
