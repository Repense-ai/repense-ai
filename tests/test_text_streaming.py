import pytest

from tests.config import TEXT
from repenseai.genai.agent import Agent
from repenseai.genai.tasks.api import Task


@pytest.mark.parametrize("model", TEXT)
def test_streaming_with_image_history(model):

    agent = Agent(
        model=model, 
        model_type="chat",
        temperature=0.0,
        max_tokens=100,
        stream=True,
    )
    
    task = Task(
        user="Say 'Hello, World!'",
        agent=agent,
        history=[
            {"role": "user", "content": [{"type": "image_url", "image_url": {"url":"https://canto-wp-media.s3.amazonaws.com/app/uploads/2019/08/19194138/image-url-3.jpg"}}]},
            {"role": "user", "content": [{"type": "text", "text": "Hi! How is it going??"}]},
            {"role": "assistant", "content": [{"type": "text", "text": "Hi there! How can I help?"}]},
        ],
        simple_response=True,
    )

    response = task.run({})
    string = ""

    for chunk in response:
        text = agent.api.process_stream_chunk(chunk)

        if text:
            string += text

    cost = agent.calculate_cost(tokens=agent.api.tokens, as_string=False)

    assert "world" in string.lower()
    assert cost > 0






