import pytest

from repenseai.config.test_models import TEST_TEXT_MODELS
from repenseai.genai.selector import APISelector
from repenseai.genai.tasks.api import Task


@pytest.mark.parametrize("model", TEST_TEXT_MODELS)
def test_chat_task_hello_world(model):

    selector = APISelector(
        model=model, 
        model_type="chat",
        temperature=0.0,
        max_tokens=100,
    )

    task = Task(
        instruction="Say 'Hello, World!'",
        selector=selector,
        history=[
            {"role": "user", "content": [{"type": "image_url", "image_url": {"url":"https://pps.whatsapp.net/v/t61.24694-24/55989707_1039454986247770_23937124050927616_n.jpg?stp=dst-jpg_tt6&ccb=11-4&oh=01_Q5AaICemAxyZWlzLXhOjAMDg88wbG9Ph8Ld0gz7nlbMNFxhf&oe=676D41D4&_nc_sid=5e03e0&_nc_cat=100"}}]},
            {"role": "user", "content": [{"type": "text", "text": "Tudo bem??"}]},
            {"role": "assistant", "content": [{"type": "text", "text": "Oi, como posso ajudar?"}]},
        ]
    )

    response = task.predict({})

    assert "world" in response.get('response').lower()
    assert response.get('cost') > 0


@pytest.mark.parametrize("model", TEST_TEXT_MODELS)
def test_text_streaming_hello_world(model):

    selector = APISelector(
        model=model, 
        model_type="chat",
        temperature=0.0,
        max_tokens=100,
        stream=True,
    )
    
    api = selector.get_api()

    task = Task(
        instruction="Say 'Hello, World!'",
        selector=selector,
        history=[
            {"role": "user", "content": [{"type": "image_url", "image_url": {"url":"https://pps.whatsapp.net/v/t61.24694-24/55989707_1039454986247770_23937124050927616_n.jpg?stp=dst-jpg_tt6&ccb=11-4&oh=01_Q5AaICemAxyZWlzLXhOjAMDg88wbG9Ph8Ld0gz7nlbMNFxhf&oe=676D41D4&_nc_sid=5e03e0&_nc_cat=100"}}]},
            {"role": "user", "content": [{"type": "text", "text": "Tudo bem??"}]},
            {"role": "assistant", "content": [{"type": "text", "text": "Oi, como posso ajudar?"}]},
        ],
        simple_response=True,
    )

    response = task.predict({})
    string = ""

    for chunk in response:
        text = api.process_stream_chunk(chunk)

        if text:
            string += text

    cost = selector.calculate_cost(tokens=api.tokens, as_string=False)

    assert "world" in string.lower()
    assert cost > 0
