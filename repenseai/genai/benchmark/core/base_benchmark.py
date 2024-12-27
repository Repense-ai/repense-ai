from typing import List, Dict, Any
import asyncio

from repenseai.genai.benchmark.core.base_test import BaseTest
from repenseai.genai.benchmark.core.base_provider import BaseLLMProvider
from repenseai.genai.benchmark.core.base_evaluator import BaseEvaluator

class Benchmark:
    def __init__(self):
        self.tests: List[BaseTest] = []
        self.providers: List[BaseLLMProvider] = []
        self.evaluators: Dict[str, BaseEvaluator] = {}
        self.results: Dict[str, Any] = {}

    def add_test(self, test: BaseTest) -> None:
        if test.validate():
            self.tests.append(test)
        else:
            print(f"Test {test.name} is not properly configured")

    def add_provider(self, provider: BaseLLMProvider) -> None:
        self.providers.append(provider)

    def add_evaluator(self, test_name: str, evaluator: BaseEvaluator) -> None:
        self.evaluators[test_name] = evaluator

    def run_sync(self) -> Dict[str, Any]:
        """Run all tests synchronously with all providers"""
        return asyncio.run(self.run())

    async def run(self) -> Dict[str, Any]:
        """Run all tests with all providers sequentially"""
        for provider in self.providers:
            self.results[provider.name] = {}
            for test in self.tests:
                await self._run_single_test(provider, test)
        return self.results

    async def run_parallel(self) -> Dict[str, Any]:
        """Run all tests in parallel"""
        tasks = []
        for provider in self.providers:
            for test in self.tests:
                tasks.append(self._run_single_test(provider, test))
        
        await asyncio.gather(*tasks)
        return self.results

    async def _run_single_test(self, provider: BaseLLMProvider, test: BaseTest) -> None:
        """Helper method to run a single test"""
        if provider.name not in self.results:
            self.results[provider.name] = {}

        try:
            test_results = await test.run(provider)
            evaluator = self.evaluators.get(test.name)
            
            if evaluator:
                evaluation = await evaluator.evaluate(test_results)
                self.results[provider.name][test.name] = {
                    'test_results': test_results,
                    'evaluation': evaluation,
                    'score': evaluator.get_score()
                }
            else:
                self.results[provider.name][test.name] = {
                    'test_results': test_results,
                    'evaluation': None,
                    'score': None
                }
        except Exception as exc:
            self.results[provider.name][test.name] = {
                'test_results': None,
                'evaluation': None,
                'score': None,
                'issue': str(exc)
            }