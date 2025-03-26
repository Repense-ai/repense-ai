import pytest

from tests.config import IMAGE

from repenseai.genai.agent import Agent
from repenseai.genai.tasks.api import Task


@pytest.mark.parametrize("model", IMAGE)
def test_image_task(model):

    agent = Agent(
        model=model,
        model_type="image",
    )

    task = Task(agent=agent, user="a funny fox")

    response = task.run({})

    assert response.get("response") is not None
    assert response.get("cost") > 0
