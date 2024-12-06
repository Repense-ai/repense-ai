import pytest

from repenseai.config.test_models import TEST_TEXT_MODELS
from repenseai.genai.api.selector import APISelector
from repenseai.genai.tasks.api_task import Task


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
            {"role": "user", "content": [{"type": "text", "text": "You are a helpful assistant."}]},
            {"role": "assistant", "content": [{"type": "text", "text": "Ok! I will help you."}]},
        ]
    )

    response = task.predict()

    assert "Hello, World!" in response.get('response')
    assert response.get('cost') > 0


@pytest.mark.parametrize("model", TEST_TEXT_MODELS)
def test_text_streaming_hello_world(model):

    selector = APISelector(
        model=model, 
        model_type="chat", 
        stream=True, 
        max_tokens=100
    )
    
    api = selector.get_api()

    response = api.call_api("Say 'Hello, World!'")
    string = ""

    for chunk in response:
        text = api.process_stream_chunk(chunk)

        if text:
            string += text

    cost = selector.calculate_cost(tokens=api.tokens, as_string=False)

    assert "Hello, World!" in string
    assert cost > 0
