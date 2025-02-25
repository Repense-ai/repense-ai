TEXT_MODELS = {
    "deepseek-chat": {
        "provider": "deepseek",
        "cost": {"input": 0.14, "output": 0.28},
    },
    "deepseek-reasoner": {
        "provider": "deepseek",
        "cost": {"input": 0.55, "output": 2.19},
    },    
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
        "cost": {"input": 1.10, "output": 4.40}
    },
    "o3-mini": {
        "provider": "openai", 
        "cost": {"input": 1.10, "output": 4.40}
    },    
    "claude-3-5-haiku-20241022": {
        "provider": "anthropic",
        "cost": {"input": 1.0, "output": 5.0},
    },
    "claude-3-5-sonnet-20241022": {
        "provider": "anthropic",
        "cost": {"input": 3.0, "output": 15.0},
    },
    "claude-3-7-sonnet-20250219": {
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
    "gemini-2.0-flash": {
        "provider": "google", 
        "cost": {"input": 0.10, "output": 0.70}
    },
    "gemini-2.0-flash-lite-preview-02-05": {
        "provider": "google", 
        "cost": {"input": 0.075, "output": 0.30}
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
    "llama-3.3-70b-versatile": {
        "provider": "groq",
        "cost": {"input": 0.59, "output": 0.79},
    },
    "Meta-Llama-3.1-405B-Instruct": {
        "provider": "sambanova",
        "cost": {"input": 5.0, "output": 10.0},
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
    "grok-2-1212": {
        "provider": "x", 
        "cost": {"input": 2.0, "output": 10.0}
    },
    "grok-2-vision-1212": {
        "provider": "x", 
        "cost": {"input": 2.0, "output": 10.0}
    },    
    "amazon.nova-pro-v1:0": {
        "provider": "aws", 
        "cost": {"input": 0.8, "output": 3.2}
    },
    "amazon.nova-lite-v1:0": {
        "provider": "aws", 
        "cost": {"input": 0.06, "output": 0.24}
    },
    "amazon.nova-micro-v1:0": {
        "provider": "aws", 
        "cost": {"input": 0.035, "output": 0.14}
    },
    "writer/palmyra-med-70b": {
        "provider": "nvidia",
        "cost": {"input": 1.00, "output": 1.00},
    },
    "writer/palmyra-med-70b-32k": {
        "provider": "nvidia",
        "cost": {"input": 1.00, "output": 1.00},
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
    "llama-3.2-90b-vision-preview": {
        "provider": "groq",
        "cost": {"input": 0.59, "output": 0.79},
    },    
    "grok-vision-beta": {
        "provider": "x", 
        "cost": {"input": 10.0, "output": 15.0}
    },
    "grok-2-vision-1212": {
        "provider": "x", 
        "cost": {"input": 2.0, "output": 10.0}
    },     
    "amazon.nova-pro-v1:0": {
        "provider": "aws", 
        "cost": {"input": 0.8, "output": 3.2}
    },
    "amazon.nova-lite-v1:0": {
        "provider": "aws", 
        "cost": {"input": 0.06, "output": 0.24}
    },    
}


SEARCH_MODELS = {
    "sonar-pro": {
        "provider": "perplexity",
        "cost": {"input": 4.0, "output": 16.0},
    },
    "sonar": {
        "provider": "perplexity",
        "cost": {"input": 2.0, "output": 2.0},
    },
}


EMBEDDINGS_MODELS = {}


AUDIO_MODELS = {
    "whisper-1": {
        "provider": "openai", 
        "cost": 0.006
    }
}


SPEECH_MODELS = {
    "tts-1": {
        "provider": "openai", 
        "cost": 0.000015
    },
    "tts-1-hd": {
        "provider": "openai", 
        "cost": 0.000030
    },
}


RANK_MODELS = {}


MODERATION_MODELS = {}


IMAGE_MODELS = {
    "black-forest-labs/FLUX.1.1-pro": {
        "provider": "together", 
        "cost": {'input': 0.04, 'output': 0.04}
    },
    "stability/generate/default/ultra": {
        "provider": "stability", 
        "cost": 0.08
    },
    "stability/generate/default/core": {
        "provider": "stability", 
        "cost": 0.03
    },
    "stability/generate/sd3.5-large/sd3": {
        "provider": "stability",
        "cost": 0.065
    },
    "stability/generate/sd3.5-large-turbo/sd3": {
        "provider": "stability", 
        "cost": 0.04
    },
    "stability/generate/sd3.5-medium/sd3": {
        "provider": "stability", 
        "cost": 0.035
    },
    "stability/upscale/fast": {
        "provider": "stability", 
        "cost": 0.01
    },
    "stability/upscale/conservative": {
        "provider": "stability", 
        "cost": 0.25
    },
    "stability/upscale/creative": {
        "provider": "stability", 
        "cost": 0.25
    },            
    "amazon.nova-canvas-v1:0": {
        "provider": "aws", 
        "cost": 0.08
    },
    "imagen-3.0-generate-002": {
        "provider": "google", 
        "cost": {'input': 0.03, 'output': 0.03}
    },
    # "aurora": {
    #     "provider": "x", 
    #     "cost": ?
    # },    
}


VIDEO_MODELS = {
    "stability-video-gen/default/core": {
        "provider": "stability",
        "cost": 0.2
    },
    "amazon-video-gen/amazon.nova-reel-v1:0": {
        "provider": "aws", 
        "cost": 0.48
    },    
}


TOOL_USAGE_MODELS = {
    "gpt-4o": {
        "provider": "openai", 
        "cost": {"input": 2.50, "output": 10.0}
    },
}