from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from repenseai.genai.benchmark.core.base_provider import BaseLLMProvider

class BaseTest(ABC):
    def __init__(self, name: str, description: Optional[str] = None):
        self.name = name
        self.description = description
        self.results = []

    @abstractmethod
    async def run(self, llm_provider: BaseLLMProvider) -> Dict[str, Any]:
        """Execute the test using the provided LLM"""
        pass

    @abstractmethod
    def validate(self) -> bool:
        """Validate if the test is properly configured"""
        pass