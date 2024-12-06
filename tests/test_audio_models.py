import pytest

from repenseai.config.test_models import TEST_AUDIO_MODELS

from repenseai.genai.api.selector import APISelector
from repenseai.genai.tasks.api_task import Task


@pytest.fixture
def audio():
    return open("tests/assets/teste_audio.ogg", "rb")


@pytest.mark.parametrize("model", TEST_AUDIO_MODELS)
def test_audio_task(model, audio):

    selector = APISelector(
        model=model, 
        model_type="audio",
    )

    task = Task(
        selector=selector,
        audio_key="teste"
    )

    response = task.predict({"teste": audio})

    assert "teste" in response.get('response').lower()
    assert response.get('cost') > 0
