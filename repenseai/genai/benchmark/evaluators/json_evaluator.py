from typing import Dict, Any

from repenseai.genai.benchmark.core.base_evaluator import BaseEvaluator

import json
import jsonschema


class SchemaEvaluator(BaseEvaluator):
    def __init__(self, name: str):
        super().__init__(name)
        self.valid_responses = 0
        self.total_responses = 0

    async def evaluate(self, test_results: Dict[str, Any]) -> Dict[str, Any]:
        evaluation = []
        schema = test_results['schema']

        self.total_responses = len(test_results['results'])
        self.valid_responses = 0

        for result in test_results['results']:
            try:
                jsonschema.validate(result['extracted_data'], schema)

                is_valid = True
                self.valid_responses += 1

            except jsonschema.ValidationError:
                is_valid = False

            evaluation.append(
                {
                    'input_number': result['input_number'],
                    'is_valid': is_valid,
                    'extracted_data': result['extracted_data']
                }
            )

        return {
            'evaluation_details': evaluation,
            'total_responses': self.total_responses,
            'valid_responses': self.valid_responses
        }

    def get_score(self) -> float:
        return self.valid_responses / self.total_responses if self.total_responses > 0 else 0.0
    

class DataEvaluator(BaseEvaluator):
    def __init__(self, name: str):
        super().__init__(name)
        self.correct_fields = 0
        self.total_fields = 0
        
    def _compare_values(self, expected: Any, actual: Any) -> bool:
        """Compare expected and actual values with type flexibility"""
        if isinstance(expected, (int, float)) and isinstance(actual, (int, float)):
            return abs(float(expected) - float(actual)) < 0.0001
        return str(expected).lower() == str(actual).lower()
    
    def _evaluate_field_accuracy(self, expected: Dict[str, Any], actual: Dict[str, Any]) -> Dict[str, bool]:
        """Evaluate accuracy for each field in the data"""
        field_results = {}
        for key in expected:
            if key not in actual:
                field_results[key] = False
            else:
                field_results[key] = self._compare_values(expected[key], actual[key])
        return field_results
    
    async def evaluate(self, test_results: Dict[str, Any]) -> Dict[str, Any]:
        evaluation = []

        self.correct_fields = 0
        self.total_fields = 0
        
        for result in test_results['results']:

            json_result = json.loads(result['extracted_data'])

            expected_data = json_result['expected_data']
            extracted_data = json_result['extracted_data']
            
            field_accuracy = self._evaluate_field_accuracy(expected_data, extracted_data)
            
            correct_in_sample = sum(1 for x in field_accuracy.values() if x)
            total_in_sample = len(field_accuracy)
            
            self.correct_fields += correct_in_sample
            self.total_fields += total_in_sample
            
            evaluation.append({
                'input_number': json_result['input_number'],
                'field_accuracy': field_accuracy,
                'accuracy_score': correct_in_sample / total_in_sample if total_in_sample > 0 else 0.0,
                'extracted_data': extracted_data,
                'expected_data': expected_data
            })
        
        return {
            'evaluation_details': evaluation,
            'total_fields': self.total_fields,
            'correct_fields': self.correct_fields,
            'overall_accuracy': self.get_score()
        }
    
    def get_score(self) -> float:
        return self.correct_fields / self.total_fields if self.total_fields > 0 else 0.0