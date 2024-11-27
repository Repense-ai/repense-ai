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
    "o1-preview": {
        "provider": "openai", 
        "cost": {"input": 15.00, "output": 60.0}
    },
    "o1-mini": {
        "provider": "openai", 
        "cost": {"input": 3.00, "output": 12.0}
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
        "provider": "sambanova",
        "cost": {"input": 0.15, "output": 0.30},
    },
    "Llama-3.2-90B-Vision-Instruct": {
        "provider": "sambanova",
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
    "grok-beta": {
        "provider": "x", 
        "cost": {"input": 5.0, "output": 15.0}
    },
    "grok-vision-beta": {
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
    "meta-llama/Llama-3.2-11B-Vision-Instruct-Turbo": {
        "provider": "together",
        "cost": {"input": 0.18, "output": 0.18},
    },
    "meta-llama/Llama-3.2-90B-Vision-Instruct-Turbo": {
        "provider": "together",
        "cost": {"input": 1.20, "output": 1.20},
    },
    # "grok-vision-beta": {
    # "provider": "x", 
    # "cost": {"input": 10.0, "output": 15.0}
    # },
}


SEARCH_MODELS = {
    "llama-3.1-sonar-small-128k-online": {
        "provider": "perplexity",
        "cost": {"input": 1.20, "output": 1.20},
    },
    "llama-3.1-sonar-large-128k-online": {
        "provider": "perplexity",
        "cost": {"input": 2.0, "output": 2.0},
    },
    "llama-3.1-sonar-huge-128k-online": {
        "provider": "perplexity",
        "cost": {"input": 6.0, "output": 6.0},
    }, 
}


EMBEDDINGS_MODELS = {}


AUDIO_MODELS = {}


RANK_MODELS = {}


MODERATION_MODELS = {}


IMAGE_MODELS = {
    "black-forest-labs/FLUX.1.1-pro": {
        "provider": "together", 
        "cost": {'input': 0.04, 'output': 0.04}
    },
    "stability-image-gen/default/ultra": {
        "provider": "stability", 
        "cost": 0.08
    },
    "stability-image-gen/default/core": {
        "provider": "stability", 
        "cost": 0.03
    },
    "stability-image-gen/sd3.5-large/sd3": {
        "provider": "stability",
        "cost": 0.065
    },
    "stability-image-gen/sd3.5-large-turbo/sd3": {
        "provider": "stability", 
        "cost": 0.04
    },
    "stability-image-gen/sd3.5-medium/sd3": {
        "provider": "stability", 
        "cost": 0.035
    },
}


VIDEO_MODELS = {
    "stability-video-gen/default/core": {
        "provider": "stability",
        "cost": 0.2
    },
}
