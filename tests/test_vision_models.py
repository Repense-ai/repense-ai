import pytest

from repenseai.config.test_models import TEST_VISION_MODELS

from repenseai.genai.agent import Agent
from repenseai.genai.tasks.api import Task

from PIL import Image


@pytest.fixture
def image():
    return Image.open("tests/assets/certidao_nascimento_elisa.jpg")


@pytest.mark.parametrize("model", TEST_VISION_MODELS)
def test_vision_task_doc_type(model, image):

    agent = Agent(
        model=model, 
        model_type="vision",
        temperature=0.0,
        max_tokens=100,
    )

    task = Task(
        instruction="Escreva apenas qual o tipo do documento em português",
        agent=agent,
    )

    response = task.run({"image": image})

    assert "nascimento" in response.get('response').lower()
    assert response.get('cost') > 0


@pytest.mark.parametrize("model", TEST_VISION_MODELS)
def test_vision_streaming_doc_type(model, image):

    agent = Agent(
        model=model,
        model_type="vision", 
        temperature=0.0, 
        stream=True,
        max_tokens=100
    )
    
    api = agent.get_api()

    response = api.call_api(
        prompt="Escreva apenas qual o tipo do documento em português",
        image=image,
    )

    string = ""

    for chunk in response:
        text = api.process_stream_chunk(chunk)

        if text:
            string += text

    cost = agent.calculate_cost(tokens=api.tokens, as_string=False)

    assert "nascimento" in string.lower()
    assert cost > 0
