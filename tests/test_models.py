import pytest

from repenseai.config.selection_params import MODELS
from repenseai.genai.api.selector import APISelector
from repenseai.genai.tasks.api_task import ChatTask


@pytest.mark.parametrize("model", MODELS.keys())
def test_model_hello_world(model):

    selector = APISelector(model=model, api="chat")
    chat_api = selector.get_api()

    task = ChatTask(
        instruction="Say 'Hello, World!'",
        prompt_template="{instruction}",
        api=chat_api,
    )

    response = task.predict({})

    assert "Hello, World!" in response
