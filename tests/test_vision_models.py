import pytest

from repenseai.config.selection_params import VISION_MODELS
from repenseai.genai.api.selector import APISelector
from repenseai.genai.tasks.api_task import VisionTask

from PIL import Image

@pytest.fixture
def image():
    return Image.open("tests/assets/certidao_nascimento_elisa.jpg")

@pytest.mark.parametrize("model", ["pixtral-12b-2409", "claude-3-haiku-20240307"])
def test_text_models_hello_world(model, image):

    selector = APISelector(model=model, model_type="vision")
    vision_api = selector.get_api(temperature=0.0)

    task = VisionTask(
        instruction="Escreva apenas qual o tipo do documento em português",
        api=vision_api,
    )

    response = task.predict({"image": image})

    assert "nascimento" in response.lower()
