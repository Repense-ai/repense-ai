import pytest

from tests.config import VISION

from repenseai.genai.agent import Agent
from repenseai.genai.tasks.api import Task

from PIL import Image


@pytest.fixture
def image():
    return Image.open("tests/assets/certidao_nascimento_elisa.jpg")


@pytest.mark.parametrize("model", VISION)
def test_vision_task_doc_type(model, image):

    agent = Agent(
        model=model,
        model_type="vision",
        temperature=0.0,
        max_tokens=100,
    )

    task = Task(
        user="Escreva apenas qual o tipo do documento em português",
        agent=agent,
    )

    response = task.run({"image": image})

    assert "nascimento" in response.get("response").lower()
    assert response.get("cost") > 0
