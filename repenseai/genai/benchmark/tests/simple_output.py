from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum, auto
from datetime import datetime
import asyncio

from repenseai.genai.benchmark.core.base_provider import BaseLLMProvider
from repenseai.genai.benchmark.core.base_test import BaseTest

@dataclass
class TestInput:
    text: str
    instructions: str
    ground_truth: Optional[str] = None

class SimpleOutputTest(BaseTest):
    def __init__(
        self,
        name: str,
        inputs: List[Dict[str, Any]],
        expected_format: Optional[str] = None,
        description: Optional[str] = None,
        max_retries: int = 3,
        retry_delay: float = 1.0
    ):
        super().__init__(name, description)
        self.inputs = [TestInput(**input_data) for input_data in inputs]
        self.expected_format = expected_format
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.start_time = None
        self.end_time = None
        
    def validate(self) -> bool:
        """
        Validate if the test is properly configured:
        - Must have at least one input
        - Each input must have required fields
        - Expected format must be provided if ground truth exists
        """
        if not self.inputs:
            return False
            
        has_ground_truth = any(input.ground_truth for input in self.inputs)

        if has_ground_truth and not self.expected_format:
            return False
            
        return True

    async def run(self, llm_provider: BaseLLMProvider) -> Dict[str, Any]:
        """
        Run the test with retry mechanism and timing information
        """
        self.start_time = datetime.now()

        results = []

        try:
            for i, input_data in enumerate(self.inputs, 1):
                result = await self._process_single_input(llm_provider, input_data, i)
                results.append(result)
                
        except Exception as e:
            print(e)
        finally:
            self.end_time = datetime.now()

        return {
            'test_type': 'simple_output',
            'test_name': self.name,
            'description': self.description,
            'expected_format': self.expected_format,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat(),
            'duration': (self.end_time - self.start_time).total_seconds(),
            'results': results,
        }

    async def _process_single_input(
        self, 
        llm_provider: BaseLLMProvider, 
        input_data: TestInput, 
        input_number: int
    ) -> Dict[str, Any]:
        """
        Process a single input with retry mechanism
        """
        attempts = 0
        last_error = None

        while attempts < self.max_retries:
            try:
                prompt = self._create_prompt(input_data, input_number)
                response = await llm_provider.generate(prompt)
                
                return {
                    'input_number': input_number,
                    'input_text': input_data.text,
                    'instructions': input_data.instructions,
                    'ground_truth': input_data.ground_truth,
                    'output': response,
                    'attempts': attempts + 1
                }
                
            except Exception as e:
                last_error = str(e)
                attempts += 1
                if attempts < self.max_retries:
                    await asyncio.sleep(self.retry_delay)

        raise Exception(f"Failed after {self.max_retries} attempts. Last error: {last_error}")

    def _create_prompt(self, input_data: TestInput, input_number: int) -> str:
        """
        Create a formatted prompt with improved structure
        """
        components = [
            f"Input {input_number}:",
            input_data.text,
            "\nInstructions:",
            input_data.instructions
        ]
        
        if self.expected_format:
            components.append(f"\nExpected format: {self.expected_format}")
            
        return "\n".join(components)

    @property
    def duration(self) -> Optional[float]:
        """
        Calculate test duration if completed
        """
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None
    
def get_sample():
    simple_test = SimpleOutputTest(
        name="Text Classification",
        description="Classify text sentiment",
        expected_format="POSITIVE, NEGATIVE, or NEUTRAL",
        inputs=[
            {
                "text": "I love this product! It's amazing!",
                "instructions": "Classify the sentiment of this text.",
                "ground_truth": "POSITIVE",
                "metadata": {"source": "product_review", "category": "electronics"}
            },
            {
                "text": "The service was terrible and I want my money back.",
                "instructions": "Classify the sentiment of this text.",
                "ground_truth": "NEGATIVE",
                "metadata": {"source": "customer_feedback", "category": "service"}
            }
        ],
        max_retries=3,
        retry_delay=1.0
    )
    return simple_test    