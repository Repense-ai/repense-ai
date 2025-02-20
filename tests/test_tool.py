import pytest

from tests.config import TOOL
from repenseai.genai.agent import Agent
from repenseai.genai.tasks.api import Task


@pytest.mark.parametrize("model", TOOL)
def test_tool_usage(model):
    
    def get_lat_long_from_id(id):
        """get latitude and longitude from id"""
        return 48.8566, 2.3522

    def get_weather(latitude, longitude):
        """get weather from latitude and longitude"""
        return "The weather is sunny"

    agent = Agent(
        model=model, 
        model_type="chat",
        tools=[get_lat_long_from_id, get_weather],
    )

    task = Task(
        user="What's the weather like in Paris today?",
        agent=agent,
    )

    response = task.run({})

    assert "sunny" in response.get('response').lower()
    assert response.get('cost') > 0