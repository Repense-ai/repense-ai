TEXT_MODELS = {
    "sabia-3": {
        "provider": "maritaca", 
        "cost": {"input": 1.0, "output": 2.0}
    },
    "sabiazinho-3": {
        "provider": "maritaca", 
        "cost": {"input": 0.2, "output": 0.6}
    },
    "gpt-4o-mini": {
        "provider": "openai", 
        "cost": {"input": 0.15, "output": 0.6}
    },
    "gpt-4o": {
        "provider": "openai", 
        "cost": {"input": 2.50, "output": 10.0}
    },
    "claude-3-haiku-20240307": {
        "provider": "anthropic",
        "cost": {"input": 0.25, "output": 1.25},
    },
    "claude-3-5-haiku-20241022": {
        "provider": "anthropic",
        "cost": {"input": 1.0, "output": 5.0},
    },
    "claude-3-5-sonnet-20240620": {
        "provider": "anthropic",
        "cost": {"input": 3.0, "output": 15.0},
    },
    "claude-3-5-sonnet-20241022": {
        "provider": "anthropic",
        "cost": {"input": 3.0, "output": 15.0},
    },
    "gemini-1.5-pro": {
        "provider": "google", 
        "cost": {"input": 2.50, "output": 10.0}
    },
    "gemini-1.5-flash": {
        "provider": "google", 
        "cost": {"input": 0.15, "output": 0.60}
    },
    "mistral-large-latest": {
        "provider": "mistral",
        "cost": {"input": 2.0, "output": 6.0},
    },
    "mistral-small-latest": {
        "provider": "mistral",
        "cost": {"input": 0.2, "output": 0.6},
    },
    "pixtral-12b-2409": {
        "provider": "mistral",
        "cost": {"input": 0.15, "output": 0.15},
    },
    "command-r-plus-08-2024": {
        "provider": "cohere",
        "cost": {"input": 2.50, "output": 10.0},
    },
    "command-r-08-2024": {
        "provider": "cohere",
        "cost": {"input": 0.15, "output": 0.60},
    },
    "llama-3.1-70b-versatile": {
        "provider": "groq",
        "cost": {"input": 0.59, "output": 0.79},
    },
    "llama-3.1-8b-instant": {
        "provider": "groq",
        "cost": {"input": 0.05, "output": 0.08},
    },
    "Meta-Llama-3.1-8B-Instruct": {
        "provider": "sambanova",
        "cost": {"input": 0.10, "output": 0.20},
    },
    "Meta-Llama-3.1-70B-Instruct": {
        "provider": "sambanova",
        "cost": {"input": 0.60, "output": 1.2},
    },
    "Meta-Llama-3.1-405B-Instruct": {
        "provider": "sambanova",
        "cost": {"input": 5.0, "output": 10.0},
    },
    "Meta-Llama-3.2-1B-Instruct": {
        "provider": "sambanova",
        "cost": {"input": 0.04, "output": 0.08},
    },
    "Meta-Llama-3.2-3B-Instruct": {
        "provider": "sambanova",
        "cost": {"input": 0.08, "output": 0.16},
    },
    "Llama-3.2-11B-Vision-Instruct": {
        "provider": "together",
        "cost": {"input": 0.15, "output": 0.30},
    },
    "Llama-3.2-90B-Vision-Instruct": {
        "provider": "together",
        "cost": {"input": 0.80, "output": 1.60},
    },
    "meta-llama/Llama-3.2-11B-Vision-Instruct-Turbo": {
        "provider": "together",
        "cost": {"input": 0.18, "output": 0.18},
    },
    "meta-llama/Llama-3.2-90B-Vision-Instruct-Turbo": {
        "provider": "together",
        "cost": {"input": 1.20, "output": 1.20},
    },
    "databricks/dbrx-instruct": {
        "provider": "together",
        "cost": {"input": 1.20, "output": 1.20},
    },
    "grok-beta": {
        "provider": "x", 
        "cost": {"input": 5.0, "output": 15.0}
    },
}


VISION_MODELS = {
    "gpt-4o-mini": {
        "provider": "openai", 
        "cost": {"input": 0.15, "output": 0.6}
    },
    "gpt-4o": {
        "provider": "openai", 
        "cost": {"input": 2.50, "output": 10.0}
    },
    "claude-3-haiku-20240307": {
        "provider": "anthropic",
        "cost": {"input": 0.25, "output": 1.25},
    },
    "claude-3-5-sonnet-20240620": {
        "provider": "anthropic",
        "cost": {"input": 3.0, "output": 15.0},
    },
    "claude-3-5-sonnet-20241022": {
        "provider": "anthropic",
        "cost": {"input": 3.0, "output": 15.0},
    },
    "gemini-1.5-pro": {
        "provider": "google", 
        "cost": {"input": 2.50, "output": 10.0}
    },
    "gemini-1.5-flash": {
        "provider": "google", 
        "cost": {"input": 0.15, "output": 0.60}
    },
    "pixtral-12b-2409": {
        "provider": "mistral",
        "cost": {"input": 0.15, "output": 0.15},
    },
    "Llama-3.2-11B-Vision-Instruct": {
        "provider": "together",
        "cost": {"input": 0.15, "output": 0.30},
    },
    "Llama-3.2-90B-Vision-Instruct": {
        "provider": "together",
        "cost": {"input": 0.80, "output": 1.60},
    },
    "meta-llama/Llama-3.2-11B-Vision-Instruct-Turbo": {
        "provider": "together",
        "cost": {"input": 0.18, "output": 0.18},
    },
    "meta-llama/Llama-3.2-90B-Vision-Instruct-Turbo": {
        "provider": "together",
        "cost": {"input": 1.20, "output": 1.20},
    },                 
}


EMBEDDINGS_MODELS = {}


AUDIO_MODELS = {}


RANK_MODELS = {}


MODERATION_MODELS = {}


IMAGE_MODELS = {
    "black-forest-labs/FLUX.1.1-pro": {
        "provider": "together",
        "cost": 0.04
    },
    "stability-image-gen/ultra": {
        "provider": "stability",
        "cost": 0.08
    },
    "stability-image-gen/core": {
        "provider": "stability",
        "cost": 0.06
    },
    "stability-image-gen/diffusion": {
        "provider": "stability",
        "cost": 0.05
    },
}


VIDEO_MODELS = {
    "stability-video-gen/core": {
        "provider": "stability",
        "cost": 0.2
    },
}
