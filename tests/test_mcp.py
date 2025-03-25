import pytest
import logging
import sys
import asyncio

from tests.config import MCP
from repenseai.genai.agent import AsyncAgent
from repenseai.genai.tasks.api import AsyncTask
from repenseai.genai.mcp.server import Server

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('test_mcp.log')
    ]
)
logger = logging.getLogger(__name__)


@pytest.mark.asyncio
@pytest.mark.parametrize("model", MCP)
async def test_async_chat_api(model):
    logger.info(f"Starting async chat API test with model: {model}")
    server = Server(
        name="test_mcp",
        command="python",
        args=[
            "tests/mcp_test_server.py"
        ],    
    )
    try:
        # Create AsyncAgent instance
        logger.info("Creating AsyncAgent instance")
        agent = AsyncAgent(
            model=model,
            model_type="chat",
            server=server
        )
        
        # Set up the API
        logger.info("Setting up API")
        agent.api = agent.module_api.AsyncChatAPI(
            api_key=agent.api_key,
            model=model,
            server=server
        )

        # Create and run task with timeout
        logger.info("Creating task")

        task = AsyncTask(
            user="qual o meu bmi? altura: {altura}, peso: {peso}",
            agent=agent
        )

        # Test API call with real tools
        logger.info("Running task with test parameters")
        try:
            response = await asyncio.wait_for(task.run({"altura": "1,77", "peso": "105kg"}), timeout=30.0)
        except asyncio.TimeoutError:
            raise TimeoutError("Task execution timed out after 30 seconds")
        
        # Assertions
        logger.info("Verifying response")
        
        assert isinstance(response, dict), "Response should be a dictionary"
        assert response['response'] is not None, "Response should not be None"
        assert response['cost'] > 0, "Tokens should be greater than 0"
        assert "33" in response['response'], "Response should contain '33'" 

        logger.info(response)
    
    except Exception as e:
        logger.error(f"Test failed with error: {str(e)}", exc_info=True)
        raise
