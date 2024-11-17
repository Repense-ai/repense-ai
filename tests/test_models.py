import pytest

from repenseai.config.selection_params import TEXT_MODELS
from repenseai.genai.api.selector import APISelector
from repenseai.genai.tasks.api_task import ChatTask


@pytest.mark.parametrize("model", TEXT_MODELS.keys())
def test_text_models_hello_world(model):

    selector = APISelector(model=model, model_type="chat")
    chat_api = selector.get_api()

    task = ChatTask(
        instruction="Say 'Hello, World!'",
        api=chat_api,
    )

    response = task.predict({})

    assert "Hello, World!" in response
