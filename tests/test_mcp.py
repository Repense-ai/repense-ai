import pytest
import logging
import asyncio

from tests.config import MCP

from repenseai.genai.agent import AsyncAgent
from repenseai.genai.tasks.api import AsyncTask
from repenseai.genai.tasks.workflow import AsyncWorkflow

from repenseai.genai.mcp.server import Server

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


@pytest.mark.asyncio
@pytest.mark.parametrize("model", MCP)
async def test_async_chat_with_two_servers(model):

    server1 = Server(
        name="bmi",
        command="python",
        args=["tests/mcp_server_bmi.py"],
    )

    server2 = Server(
        name="diet",
        command="python",
        args=["tests/mcp_server_diet.py"],
    )

    try:
        agent = AsyncAgent(model=model, model_type="chat", server=[server1, server2])

        task = AsyncTask(
            user="qual a minha dieta? altura: {altura}, peso: {peso}", agent=agent
        )

        try:
            response = await asyncio.wait_for(
                task.run({"altura": "1,77", "peso": "105kg"}), timeout=30.0
            )
        except asyncio.TimeoutError:
            raise TimeoutError("Task execution timed out after 30 seconds")

        assert isinstance(response, dict), "Response should be a dictionary"
        assert response["response"] is not None, "Response should not be None"
        assert response["cost"] > 0, "Tokens should be greater than 0"
        assert (
            "frutas" in response["response"].lower()
        ), "Response should contain 'frutas'"

        logger.info(response)

    except Exception as e:
        logger.error(f"Test failed with error: {str(e)}", exc_info=True)
        raise


@pytest.mark.asyncio
@pytest.mark.parametrize("model", MCP)
async def test_async_chat_api(model):

    server = Server(
        name="test_mcp",
        command="python",
        args=["tests/mcp_server_bmi.py"],
    )

    try:
        agent = AsyncAgent(model=model, model_type="chat", server=server)

        task = AsyncTask(
            user="qual o meu bmi? altura: {altura}, peso: {peso}", agent=agent
        )

        try:
            response = await asyncio.wait_for(
                task.run({"altura": "1,77", "peso": "105kg"}), timeout=30.0
            )
        except asyncio.TimeoutError:
            raise TimeoutError("Task execution timed out after 30 seconds")

        assert isinstance(response, dict), "Response should be a dictionary"
        assert response["response"] is not None, "Response should not be None"
        assert response["cost"] > 0, "Tokens should be greater than 0"
        assert "33" in response["response"], "Response should contain '33'"

        logger.info(response)

    except Exception as e:
        logger.error(f"Test failed with error: {str(e)}", exc_info=True)
        raise


@pytest.mark.asyncio
@pytest.mark.parametrize("model", MCP)
async def test_async_workflow(model):
    logger.info(f"Starting async workflow test with model: {model}")
    server = Server(
        name="test_mcp",
        command="python",
        args=["tests/mcp_server_bmi.py"],
    )
    try:
        # Create AsyncAgent instances
        logger.info("Creating AsyncAgent instances")
        agent = AsyncAgent(model=model, model_type="chat", server=server)

        # Create tasks for the workflow
        logger.info("Creating workflow tasks")
        bmi_task = AsyncTask(
            user="qual o meu bmi? altura: {altura}, peso: {peso}", agent=agent
        )

        # Define workflow steps
        logger.info("Setting up workflow")
        workflow_steps = [[bmi_task, "bmi_result"]]

        # Create workflow
        workflow = AsyncWorkflow(workflow_steps)

        # Run workflow with timeout
        logger.info("Running workflow with test parameters")
        try:
            result = await asyncio.wait_for(
                workflow.run({"altura": "1,77", "peso": "105kg"}), timeout=30.0
            )
        except asyncio.TimeoutError:
            raise TimeoutError("Workflow execution timed out after 30 seconds")

        # Assertions
        logger.info("Verifying workflow results")
        assert isinstance(result, dict), "Result should be a dictionary"
        assert "bmi_result" in result, "Result should contain 'bmi_result' key"
        assert isinstance(
            result["bmi_result"], dict
        ), "BMI result should be a dictionary"
        assert (
            "response" in result["bmi_result"]
        ), "BMI result should contain 'response'"
        assert (
            "33" in result["bmi_result"]["response"]
        ), "BMI response should contain '33'"
        assert result["bmi_result"]["cost"] > 0, "Cost should be greater than 0"

        logger.info(result)

    except Exception as e:
        logger.error(f"Test failed with error: {str(e)}", exc_info=True)
        raise
