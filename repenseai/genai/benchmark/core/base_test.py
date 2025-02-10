from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from repenseai.genai.benchmark.core.base_provider import BaseagentProvider

class BaseTest(ABC):
    def __init__(self, name: str, description: Optional[str] = None):
        self.name = name
        self.description = description
        self.results = []

    @abstractmethod
    async def run(self, agent_provider: BaseagentProvider) -> Dict[str, Any]:
        """Execute the test using the provided agent"""
        pass

    @abstractmethod
    def validate(self) -> bool:
        """Validate if the test is properly configured"""
        pass