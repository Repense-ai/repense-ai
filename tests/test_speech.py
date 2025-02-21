import pytest

from tests.config import SPEECH

from repenseai.genai.agent import Agent
from repenseai.genai.tasks.api import Task


@pytest.mark.parametrize("model", SPEECH)
def test_audio_task(model):

    agent = Agent(
        model=model, 
        model_type="speech",
        voice="shimmer",
    )

    task = Task(
        agent=agent,
        speech_key="teste"
    )

    response = task.run({"teste": "Estou testando um audio em portugues gerado pela openai"})

    assert response.get('response') is not None
    assert response.get('cost') > 0
