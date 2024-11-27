import pytest

from repenseai.config.test_models import TEST_VISION_MODELS

from repenseai.genai.api.selector import APISelector
from repenseai.genai.tasks.api_task import VisionTask

from PIL import Image


@pytest.fixture
def image():
    return Image.open("tests/assets/certidao_nascimento_elisa.jpg")


@pytest.mark.parametrize("model", TEST_VISION_MODELS)
def test_vision_task_doc_type(model, image):

    selector = APISelector(model=model, model_type="vision")
    api = selector.get_api(temperature=0.0)

    task = VisionTask(
        instruction="Escreva apenas qual o tipo do documento em português",
        api=api,
    )

    response = task.predict({"image": image})
    cost = selector.calculate_cost(tokens=api.tokens, as_string=False)

    assert "nascimento" in response.lower()
    assert cost > 0


@pytest.mark.parametrize("model", TEST_VISION_MODELS)
def test_vision_streaming_doc_type(model, image):

    selector = APISelector(model=model, model_type="vision")
    api = selector.get_api(temperature=0.0, stream=True, max_tokens=100)

    response = api.call_api(
        prompt="Escreva apenas qual o tipo do documento em português",
        image=image,
    )

    string = ""

    for chunk in response:
        text = api.process_stream_chunk(chunk)

        if text:
            string += text

    cost = selector.calculate_cost(tokens=api.tokens, as_string=False)

    assert "nascimento" in string.lower()
    assert cost > 0
