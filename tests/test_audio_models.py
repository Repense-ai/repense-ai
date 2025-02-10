import pytest

from repenseai.config.test_models import TEST_AUDIO_MODELS

from repenseai.genai.agent import Agent
from repenseai.genai.tasks.api import Task


@pytest.fixture
def audio():
    return open("tests/assets/teste_audio.ogg", "rb")


@pytest.mark.parametrize("model", TEST_AUDIO_MODELS)
def test_audio_task(model, audio):

    agent = Agent(
        model=model, 
        model_type="audio",
    )

    task = Task(
        agent=agent,
        audio_key="teste"
    )

    response = task.run({"teste": audio})

    assert "teste" in response.get('response').lower()
    assert response.get('cost') > 0
