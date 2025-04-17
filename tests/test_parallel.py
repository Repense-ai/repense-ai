import pytest

from repenseai.genai.agent import Agent
from repenseai.genai.tasks.api import Task
from repenseai.genai.tasks.parallel import ParallelTask


@pytest.mark.parametrize("model", ["gpt-4o-mini"])
def test_parallel_shared_context(model):
    # Initialize agents
    agent1 = Agent(
        model=model,
        model_type="chat",
        temperature=0.0,
    )

    agent2 = Agent(
        model=model,
        model_type="chat",
        temperature=0.0,
    )

    # Create tasks
    task1 = Task(
        user="Summarize this text in one sentence: {text}",
        agent=agent1,
        simple_response=True,
    )

    task2 = Task(
        user="List the main topics in this text: {text}",
        agent=agent2,
        simple_response=True,
    )

    # Create parallel task
    parallel_task = ParallelTask([task1, task2])

    # Test context
    shared_context = {
        "text": "Artificial Intelligence has transformed many industries. From healthcare to finance, AI applications are becoming increasingly common. Machine learning models can now perform complex tasks that once required human expertise."
    }

    # Run tasks
    results = parallel_task.run(shared_context)

    # Assertions
    assert len(results) == 2
    assert isinstance(results[0], str)
    assert isinstance(results[1], str)


@pytest.mark.parametrize("model", ["gpt-4o-mini"])
def test_parallel_unique_contexts(model):
    # Initialize agent
    agent = Agent(
        model=model,
        model_type="chat",
        temperature=0.0,
    )

    # Create task template
    analysis_task = Task(
        user="Analyze the sentiment of this text: {text}",
        agent=agent,
        simple_response=True,
    )

    # Create parallel task
    parallel_task = ParallelTask(analysis_task)

    # Test contexts
    unique_contexts = [
        {"text": "I love this product! It's amazing!"},
        {"text": "This service is terrible, would not recommend."},
        {"text": "The weather is quite nice today."},
    ]

    # Run tasks
    results = parallel_task.run(unique_contexts)

    # Assertions
    assert len(results) == 3
    assert all(isinstance(result, str) for result in results)


@pytest.mark.parametrize("model", ["gpt-4o-mini"])
def test_parallel_single_task(model):
    """Test ParallelTask with a single task"""
    agent = Agent(
        model=model,
        model_type="chat",
        temperature=0.0,
    )

    task = Task(
        user="Say hello",
        agent=agent,
        simple_response=True,
    )

    parallel_task = ParallelTask(task)
    result = parallel_task.run()

    assert isinstance(result, list)
    assert len(result) == 1
    assert "hello" in result[0].lower()


@pytest.mark.parametrize("model", ["gpt-4o-mini"])
def test_parallel_empty_context(model):
    """Test ParallelTask with empty context"""
    agent = Agent(
        model=model,
        model_type="chat",
        temperature=0.0,
    )

    task1 = Task(
        user="Say hello",
        agent=agent,
        simple_response=True,
    )

    task2 = Task(
        user="Say goodbye",
        agent=agent,
        simple_response=True,
    )

    parallel_task = ParallelTask([task1, task2])
    results = parallel_task.run()

    assert len(results) == 2
