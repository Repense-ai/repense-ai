# RepenseAI

[![PyPI](https://img.shields.io/pypi/v/repenseai)](https://pypi.org/project/repenseai/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A Python-based artificial intelligence and machine learning toolkit for various AI tasks including audio processing, image generation, and language models.

## Features

- 🎵 Audio processing capabilities
- 🖼️ Image generation and manipulation
- 🤖 Integration with various AI models
- 🔍 Search functionality
- 📊 Benchmarking tools
- ⚡ Streaming support

## Providers

Currently supported providers are:
- Anthropic
- AWS
- Google
- Groq
- Mistral
- OpenAI
- Sambanova
- Maritaca
- Perplexity
- Together
- X
- Nvidia
- Deepseek
- Stability
- Cohere

## Project Structure

```
repenseai/
├── tests/       # Project Tests
├── error/       # Error handling
├── genai/       # AI/ML core functionality
├── secrets/     # Secrets management
└── utils/       # Utility functions
```

## Installation

1. Ensure you have Python installed (see `.python-version` for version)
2. Install Poetry (dependency management):
```sh
pip install poetry
```

3. Install dependencies:
```sh
poetry install
```

## Secrets

1. Using a `.env` file in the root directory with your API keys:

```
GOOGLE_API_KEY=
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
MISTRAL_API_KEY=
COHERE_API_KEY=
GROQ_API_KEY=
MARITACA_API_KEY=
SAMBANOVA_API_KEY=
TOGETHER_API_KEY=
X_API_KEY=
STABILITY_API_KEY=
DEEPSEEK_API_KEY=
PERPLEXITY_API_KEY=
NVIDIA_API_KEY=
AWS_KEY=
AWS_SECRET=
```

2. Using Cloud Providers:
You can create your own classes to get cloud secrets
```python
class BaseSecrets(object):
    """abstract object that implements a .get_secret() method"""

    def __init__(self):
        pass

    def get_secret(self, **kwargs):
        pass
```

You can use the `AWSSecrets` class that is already implemented
```python
from repenseai.secrets.aws import AWSSecrets

# Initialize AWS Secrets Manager
secrets = AWSSecrets(
    secret_name="my-app-secrets",
    region_name="us-east-1",
    # Optional: Use AWS profile
    profile_name="default",
    # Or use direct credentials
    # aws_access_key_id="YOUR_ACCESS_KEY",
    # aws_secret_access_key="YOUR_SECRET_KEY"
)

# Retrieve a secret
api_key = secrets.get_secret("API_KEY")
database_url = secrets.get_secret("DATABASE_URL")

# Secrets are cached after first retrieval
api_key_cached = secrets.get_secret("API_KEY")  # Uses cached value
```

## Usage Examples

### Check All Available Models

```python
from repenseai.genai.agent import list_models
print(list_models())
```

### Using models that are not listed

If you encounter a KeyError like this `KeyError: claude-3-7-sonnet-20250219'`, it is because our list of models is not updated.
You can solve this issue by adding the `provider` and the `price` as arguments.

Currently, we are only considering `input` and `output` tokens to calculate the cost.  
Keep in mind that this is only an approximation. Cached tokens or thinking tokens are still not considered.

```python
from repenseai.genai.agent import Agent
from repenseai.genai.tasks.api import Task

# Initialize Agent with Provider and Price
agent = Agent(
    model="claude-3-7-sonnet-20250219",
    model_type="chat",
    provider="anthropic",
    price={"input": 3.0, "output": 15.0},
)

task = Task(
    user="Write a short story about the color blue",
    agent=agent
)

response = task.run()
```

### Instantiate The Agent with Your Secrets Manager  
```python
from repenseai.secrets.aws import AWSSecrets
from repenseai.genai.agent import Agent

# Initialize AWS Secrets Manager
aws_secrets = AWSSecrets(
    secret_name="my-app-secrets",
    region_name="us-east-1",
)

# Initialize the Agent
agent = Agent(
    model="gpt-4o",
    model_type="chat",
    temperature=0.0,
    max_tokens=100,
    secrets_manager=aws_secrets,
)
```

### Basic Chat Interaction

```python
from repenseai.genai.agent import Agent
from repenseai.genai.tasks.api import Task

# Initialize the agent
agent = Agent(
    model="gpt-4o",
    model_type="chat",
    temperature=0.0,
    max_tokens=100
)

# Create and run a simple task
task = Task(
    user="Say {text}",
    agent=agent
)

response = task.run({"text": "'Hello, World!'"})

print(f"Response: {response['response']}")  # Outputs the model's response
print(f"Cost: {response['cost']}")  # Outputs the task's cost
print(f"Tokens: {response['tokens']}")  # Outputs the token consumption

# ---- #
# If you just want to output the response
# Add the simple response argument

task = Task(
    user="Say {text}",
    agent=agent,
    simple_response=True,
)

response = task.run({"text": "'Hello, World!'"})
print(f"Response: {response}")  # Outputs the model's response

# ---- #
# If you want to continue the chat

task.add_user_message("Hello!")
new_response = task.run()

print(f"New Response: {new_response}")  # Outputs the model's response

# ---- #
# To check conversation history
print(task.prompt)
```

## Anthropic Thinking

```python
from repenseai.genai.agent import Agent
from repenseai.genai.tasks.api import Task

# Initialize Agent with Provider and Price
agent = Agent(
    model="claude-3-7-sonnet-20250219",
    model_type="chat",
    thinking=True
)

task = Task(
    user="Write a short story about the color blue",
    agent=agent,
    simple_response=True
)

response = task.run()

print(f"Reasoning:\n\n{response['thinking']}\n\n")  # Outputs the model's reasoning
print(f"Response:\n\n{response['output']}")  # Outputs the model's response
```

### Vision Tasks

```python
from PIL import Image
from repenseai.genai.agent import Agent
from repenseai.genai.tasks.api import Task

# Initialize vision agent
agent = Agent(
    model="grok-2-vision-1212",
    model_type="vision",
    temperature=0.0,
)

# Load image
image = Image.open("path/to/your/image.jpg")

# Create vision task
task = Task(
    user="Describe what you see in this image",
    agent=agent,
    simple_response=True,
    vision_key="my_image",
)

# Run task with image
response = task.run({"my_image": image})
print(response)
```

### Tool Usage

```python
from repenseai.genai.agent import Agent
from repenseai.genai.tasks.api import Task

def get_weather(latitude: float, longitude: float) -> str:
    """Get weather information for a location"""
    return "Sunny, 22°C"

def get_location(city: str) -> tuple:
    """Get coordinates for a city"""
    return (48.8566, 2.3522)  # Example for Paris

# Initialize agent with tools
agent = Agent(
    model="claude-3-7-sonnet-20250219",
    model_type="chat",
    tools=[get_weather, get_location]
)

# Create task
task = Task(
    user="What's the weather like in Paris today?",
    agent=agent
)

response = task.run()
print(response['response'])
```

### MCP Servers

RepenseAI supports MCP (Model Control Protocol) servers for enhanced tool integration.  
You can use MCP servers either through Docker or by installing them directly with pip.


#### Using MCP in Jupyter Notebooks

When working with MCP servers in Jupyter notebooks, you'll need to apply `nest_asyncio` to enable asynchronous operations within the notebook environment:

```python
import nest_asyncio
nest_asyncio.apply()
```

#### Using Docker for MCP Servers

To use MCP servers with RepenseAI, you'll need to use the asynchronous classes (`AsyncAgent` and `AsyncTask`) since MCP server operations are inherently asynchronous. This ensures proper handling of concurrent operations and prevents blocking behavior.

Here's how to set up a Docker-based MCP server:

```python
import os
import asyncio

from repenseai.genai.mcp.server import Server
from repenseai.genai.agent import AsyncAgent
from repenseai.genai.tasks.api import AsyncTask


args = [
    "run",
    "-i",
    "--rm",
    "-e",
    "SLACK_BOT_TOKEN=" + os.getenv("SLACK_BOT_TOKEN"),
    "-e",
    "SLACK_TEAM_ID=" + os.getenv("SLACK_TEAM_ID"),
    "mcp/slack"
]

server = Server(name="slack", command='docker', args=args)

async def main():
    agent = AsyncAgent(
        model="claude-3-5-sonnet-20241022",
        model_type="chat",
        server=server
    )

    task = AsyncTask(
        user="What was the last message sent in the channel {slack_id}?",
        agent=agent
    )
    
    response = await task.run({"slack_id": os.getenv("SLACK_CHANNEL_ID")})
    print(response['response'])

asyncio.run(main())
```

### Streaming Responses

```python
from repenseai.genai.agent import Agent
from repenseai.genai.tasks.api import Task

# Initialize streaming agent
agent = Agent(
    model="amazon.nova-pro-v1:0",
    model_type="chat",
    stream=True
)

task = Task(
    user="Write a short story about a robot",
    agent=agent
)

# Handle streaming response
response = task.run()
for chunk in response['response']:
    text = agent.api.process_stream_chunk(chunk)
    if text:
        print(text, end='')

cost = agent.calculate_cost(tokens=agent.api.tokens, as_string=True)
print(cost)
```

### JSON Mode

```python
from pydantic import BaseModel
from repenseai.genai.agent import Agent
from repenseai.genai.tasks.api import Task

class Response(BaseModel):
    reasoning: str
    response: str

agent = Agent(
    model="gpt-4o",
    model_type="chat",
    json_schema=Response
)

task = Task(
    user="What is 2+2?",
    agent=agent,
    simple_response=True
)

response = task.run()
formatted_response = Response(**response)
print(formatted_response.response)
```

### Image Generation

```python
from repenseai.genai.agent import Agent
from repenseai.genai.tasks.api import Task

from repenseai.utils.image import display_base64_image

agent = Agent(
    model="black-forest-labs/FLUX.1.1-pro",
    model_type="image",
)

task = Task(
    user="A cute white fox in the forest",
    agent=agent,
    simple_response=True
)

response = task.run()
display_base64_image(response)
```

### Audio Transcription

```python
from repenseai.genai.agent import Agent
from repenseai.genai.tasks.api import Task

agent = Agent(
    model="whisper-1",
    model_type="audio",
)

task = Task(
    agent=agent,
    audio_key="my_audio",
)

my_audio = open("teste_audio.ogg", "rb")
response = task.run({"my_audio": my_audio})

print(f"Response: {response['response']}")  # Outputs the model's response
print(f"Cost: {response['cost']}")  # Outputs the task's cost
print(f"Tokens: {response['tokens']}")  # Outputs the token consumption
```

### Audio Generation

```python
from repenseai.genai.agent import Agent
from repenseai.genai.tasks.api import Task

agent = Agent(
    model="tts-1", 
    model_type="speech",
    voice="shimmer",
)

task = Task(
    agent=agent,
    speech_key="teste"
)

response = task.run({"teste": "Estou testando um audio em portugues gerado pela openai"})

with open("audios/output_speech.mp3", "wb") as f:
    f.write(response['response'])
```

## Workflows

All tasks can be bind togheter in workflows.  
We can mix tasks types and function to create the perfect solution.

```python
import json

from PIL import Image

from repenseai.genai.agent import Agent
from repenseai.genai.tasks.api import Task
from repenseai.genai.tasks.workflow import Workflow

from datetime import datetime

# Function to format the final output
def format_analysis(context):
    """Format the vision and chat analysis into a structured output"""
    vision_result = context.get('vision_analysis', '')
    chat_result = context.get('chat_summary', '')
    
    formatted = {
        'original_analysis': vision_result,
        'summary': chat_result,
        'timestamp': datetime.now().isoformat()
    }

    return formatted

# Initialize vision agent
vision_agent = Agent(
    model="claude-3-5-sonnet-20241022",  # Using Claude for vision
    model_type="vision",
    temperature=0.0,
    max_tokens=1000
)

# Initialize chat agent
chat_agent = Agent(
    model="gpt-4o",  # Using GPT-4 for text processing
    model_type="chat",
    temperature=0.0,
    max_tokens=150
)

# Create vision task
vision_task = Task(
    user="Analyze this image and describe what you see in detail",
    agent=vision_agent,
)

# Create chat task to summarize vision analysis
chat_task = Task(
    user="Summarize the following image analysis in 2-3 sentences: {vision_analysis}",
    agent=chat_agent,
)

# Create workflow
workflow = Workflow([
    [vision_task, "vision_analysis"],
    [chat_task, "chat_summary"],
    [format_analysis, "final_output"]
])

# Run workflow
image = Image.open("path/to/your/image.jpg")
context = {"image": image}
results = workflow.run(context)

# Print results
print(json.dumps(results['final_output'], indent=4))
```

### Conditonal Workflows

```python
from PIL import Image

from datetime import datetime
import json

from repenseai.genai.agent import Agent
from repenseai.genai.tasks.api import Task
from repenseai.genai.tasks.workflow import Workflow

from repenseai.genai.tasks.conditional import (
    BooleanConditionalTask, 
    ConditionalTask, 
    DummyTask
)

# Helper functions
def check_content_type(context):
    """Determine if the image contains a person or an object"""
    vision_result = context.get('vision_analysis', '').lower()
    return 'person' if 'person' in vision_result else 'object'

def contains_text(context):
    """Check if the image contains text"""
    vision_result = context.get('vision_analysis', '').lower()
    return 'text' in vision_result or 'writing' in vision_result

def format_final_output(context):
    """Format all analysis results into a structured output"""
    return {
        'timestamp': datetime.now().isoformat(),
        'content_type': context.get('content_type'),
        'vision_analysis': context.get('vision_analysis'),
        'detailed_analysis': context.get('detailed_analysis'),
        'text_content': context.get('text_content'),
    }

# Initialize agents for different purposes
vision_agent = Agent(
    model="claude-3-5-sonnet-20241022",
    model_type="vision",
    temperature=0.0,
    max_tokens=300
)

chat_agent_person = Agent(
    model="gpt-4o",
    model_type="chat",
    temperature=0.0,
    max_tokens=150
)

chat_agent_object = Agent(
    model="claude-3-5-sonnet-20241022",
    model_type="chat",
    temperature=0.0,
    max_tokens=150
)

# Create tasks
vision_task = Task(
    user="Analyze this image in detail, including any text if present",
    agent=vision_agent,
    simple_response=True

)

person_analysis_task = Task(
    user="Analyze the person in this description, focusing on appearance and actions: {vision_analysis}",
    agent=chat_agent_person,
    simple_response=True
)

object_analysis_task = Task(
    user="Provide a detailed analysis of the object described: {vision_analysis}",
    agent=chat_agent_object,
    simple_response=True
)

text_extraction_task = Task(
    user="Extract and clean up any text content from this description: {vision_analysis}",
    agent=chat_agent_person,
    simple_response=True
)

# Create conditional tasks
content_type_task = ConditionalTask(
    condition=check_content_type,
    tasks={
        'person': person_analysis_task,
        'object': object_analysis_task
    },
    default_task=DummyTask()
)

text_analysis_task = BooleanConditionalTask(
    condition=contains_text,
    true_task=text_extraction_task,
    false_task=DummyTask()
)

# Create workflow
workflow = Workflow([
    [vision_task, "vision_analysis"],
    [check_content_type, "content_type"],
    [content_type_task, "detailed_analysis"],
    [text_analysis_task, "text_content"],
    [format_final_output, "final_output"]
])

# Run workflow
def analyze_image(image_path):
    image = Image.open(image_path)
    context = {"image": image}
    results = workflow.run(context)
    return results['final_output']

results = analyze_image("path/to/your/image.jpg")
print(json.dumps(results, indent=2))
```

## Development

This project uses several development tools:

- poetry for dependency management
- pre-commit hooks for code quality
- pytest for testing
- flake8 for code linting
- black for formatting

### Setup Development Environment

```sh
# Install dependencies
poetry install

# Setup pre-commit hooks
pre-commit install
```

### Running Tests

```sh
poetry run pytest
```

## Environment Variables

Configure your environment by creating a `.env` file based on the provided template.

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## TODO

1. Benchmark Class
2. MultiAgent Setup
3. Reasoning Task (Agent can go back and fourth with the task)
4. Other models types (Embeddings, Rerank, Moderation)
5. Latest updates (OpenAI audio prompts, etc)
