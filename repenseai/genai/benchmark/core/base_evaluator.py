from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseEvaluator(ABC):
    def __init__(self, name: str):
        self.name = name
        self.evaluation_results = []

    @abstractmethod
    async def evaluate(self, test_results: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate the results of a test"""
        pass

    @abstractmethod
    def get_score(self) -> float:
        """Return a normalized score (0-1) for the evaluation"""
        pass
