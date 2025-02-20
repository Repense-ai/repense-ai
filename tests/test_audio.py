import pytest

from tests.config import AUDIO

from repenseai.genai.agent import Agent
from repenseai.genai.tasks.api import Task


@pytest.fixture
def audio():
    return open("tests/assets/teste_audio.ogg", "rb")


@pytest.mark.parametrize("model", AUDIO)
def test_audio_task(model, audio):

    agent = Agent(
        model=model, 
        model_type="audio",
        language="pt"
    )

    task = Task(
        agent=agent,
        audio_key="teste"
    )

    response = task.run({"teste": audio})

    assert "teste" in response.get('response').lower()
    assert response.get('cost') > 0
