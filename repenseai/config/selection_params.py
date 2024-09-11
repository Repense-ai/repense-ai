MODELS = {
    "gpt-4o-mini": "openai",
    "gpt-4o": "openai",
    "gpt-4o-2024-08-06": "openai",
    "claude-3-haiku-20240307": "anthropic",
    "claude-3-sonnet-20240229": "anthropic",
    "claude-3-5-sonnet-20240620": "anthropic",
    "claude-3-opus-20240229": "anthropic",
    "gemini-1.5-pro": "google",
    "gemini-1.5-flash": "google",
    "mistral-large-latest": "mistral",
    "mistral-medium-latest": "mistral",
    "mistral-small-latest": "mistral",
    "command-r-plus-08-2024": "cohere",
    "command-r-08-2024": "cohere",
    "command-r-plus": "cohere",
    "command-r": "cohere",
    # "llama-3.1-405b-reasoning": "groq",
    "llama-3.1-70b-versatile": "groq",
    "llama-3.1-8b-instant": "groq",
    "llama3-70b-8192": "groq",
    "sabia-3": "maritaca",
    "Meta-Llama-3.1-8B-Instruct": "sambanova",
    "Meta-Llama-3.1-70B-Instruct": "sambanova",
    "Meta-Llama-3.1-405B-Instruct": "sambanova",
}


COSTS = {
    "gpt-4o-mini": {"input": 0.15, "output": 0.6},
    "gpt-4o": {"input": 5.0, "output": 15.0},
    "gpt-4o-2024-08-06": {"input": 2.50, "output": 10.0},
    "claude-3-haiku-20240307": {"input": 0.25, "output": 1.25},
    "claude-3-sonnet-20240229": {"input": 3.0, "output": 15.0},
    "claude-3-opus-20240229": {"input": 15.0, "output": 75.0},
    "claude-3-5-sonnet-20240620": {"input": 3.0, "output": 15.0},
    "gemini-1.5-pro": {"input": 3.5, "output": 10.5},
    "gemini-1.5-flash": {"input": 0.35, "output": 1.05},
    "mistral-large-latest": {"input": 8.0, "output": 24.0},
    "mistral-medium-latest": {"input": 2.7, "output": 8.1},
    "mistral-small-latest": {"input": 2.0, "output": 6.0},
    "command-r-plus-08-2024": {"input": 2.50, "output": 10.0},
    "command-r-plus": {"input": 3.0, "output": 15.0},
    "command-r-08-2024": {"input": 0.15, "output": 0.60},
    "command-r": {"input": 0.50, "output": 1.50},
    "textract": 1.5,
    "llama-3.1-405b-reasoning": {"input": 15.0, "output": 75.0},
    "llama-3.1-70b-versatile": {"input": 5.0, "output": 15.0},
    "llama-3.1-8b-instant": {"input": 0.5, "output": 1.5},
    "llama3-70b-8192": {"input": 0.59, "output": 0.79},
    "sabia-3": {"input": 2.0, "output": 2.0},
    "Meta-Llama-3.1-8B-Instruct": {"input": 0.10, "output": 0.20},
    "Meta-Llama-3.1-70B-Instruct": {"input": 0.60, "output": 1.2},
    "Meta-Llama-3.1-405B-Instruct": {"input": 5.0, "output": 10.0},
}
