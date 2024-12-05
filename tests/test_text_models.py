import pytest

from repenseai.config.test_models import TEST_TEXT_MODELS
from repenseai.genai.api.selector import APISelector
from repenseai.genai.tasks.api_task import ChatTask


@pytest.mark.parametrize("model", TEST_TEXT_MODELS)
def test_chat_task_hello_world(model):

    selector = APISelector(model=model, model_type="chat")
    api = selector.get_api(temperature=0.0)

    task = ChatTask(
        instruction="Say 'Hello, World!'",
        api=api,
        history=[
            {"role": "user", "content": [{"type": "text", "text": "You are a helpful assistant."}]},
            {"role": "assistant", "content": [{"type": "text", "text": "Ok! I will help you."}]},
        ]
    )

    response = task.predict({})
    cost = selector.calculate_cost(tokens=api.tokens, as_string=False)

    assert "Hello, World!" in response
    assert cost > 0


@pytest.mark.parametrize("model", TEST_TEXT_MODELS)
def test_text_streaming_hello_world(model):

    selector = APISelector(model=model, model_type="chat")
    api = selector.get_api(stream=True, max_tokens=100)

    response = api.call_api("Say 'Hello, World!'")
    string = ""

    for chunk in response:
        text = api.process_stream_chunk(chunk)

        if text:
            string += text

    cost = selector.calculate_cost(tokens=api.tokens, as_string=False)

    assert "Hello, World!" in string
    assert cost > 0
