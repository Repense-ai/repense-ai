import pytest

from tests.config import JSON
from repenseai.genai.agent import Agent
from repenseai.genai.tasks.api import Task


@pytest.mark.parametrize("model", JSON)
def test_json_mode(model):
    from pydantic import BaseModel

    class Response(BaseModel):
        reasoning: str
        response: str

    agent = Agent(
        model=model,
        model_type="chat",
        json_schema=Response,
    )

    task = Task(
        user="What is 2+2?",
        agent=agent,
        simple_response=True,
    )

    response = task.run({})

    try:
        formatted_response = Response(**response)
    except Exception as e:
        pytest.fail(f"Failed to format the response: {e}")

    assert "4" in formatted_response.response
