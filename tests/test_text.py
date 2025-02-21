import pytest

from tests.config import TEXT
from repenseai.genai.agent import Agent
from repenseai.genai.tasks.api import Task


@pytest.mark.parametrize("model", ["gemini-2.0-flash"])
def test_chat_with_image_history(model):

    agent = Agent(
        model=model, 
        model_type="chat",
        temperature=0.0,
        max_tokens=100,
    )

    task = Task(
        user="Say 'Hello, World!'",
        agent=agent,
        history=[
            {"role": "user", "content": [{"type": "image_url", "image_url": {"url":"https://canto-wp-media.s3.amazonaws.com/app/uploads/2019/08/19194138/image-url-3.jpg"}}]},
            {"role": "user", "content": [{"type": "text", "text": "Hi! How is it going??"}]},
            {"role": "assistant", "content": [{"type": "text", "text": "Hi there! How can I help?"}]},
        ]
    )

    response = task.run({})

    assert "world" in response.get('response').lower()
    assert response.get('cost') > 0