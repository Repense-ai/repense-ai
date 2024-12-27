from typing import TypedDict, Dict, Any

from datetime import datetime

from repenseai.genai.benchmark.core.base_evaluator import BaseEvaluator

class EvaluationResult(TypedDict):
    question_number: int
    is_correct: bool
    given_answer: str
    correct_answer: str
    confidence: float

class OptionQuestionEvaluator(BaseEvaluator):
    def __init__(self, name: str):
        super().__init__(name)
        self.total_questions = 0
        self.correct_answers = 0

    async def evaluate(self, test_results: Dict[str, Any]) -> Dict[str, Any]:
        if test_results.get('test_type') != 'options_exam':
            raise ValueError("Invalid test type for OptionsEvaluator")
            
        evaluation = []

        self.total_questions = len(test_results['results'])
        self.correct_answers = 0

        for result in test_results['results']:
            try:
                evaluation_result = self._evaluate_single_answer(result)
                evaluation.append(evaluation_result)
                if evaluation_result['is_correct']:
                    self.correct_answers += 1
            except Exception as e:
                evaluation.append({
                    'question_number': result['question_number'],
                    'error': str(e),
                    'is_correct': False
                })

        return {
            'evaluation_details': evaluation,
            'total_questions': self.total_questions,
            'correct_answers': self.correct_answers,
            'accuracy': self.get_score(),
            'metadata': {
                'evaluator_name': self.name,
                'evaluation_timestamp': datetime.now().isoformat()
            }
        }

    def _evaluate_single_answer(self, result: Dict[str, Any]) -> EvaluationResult:

        llm_answer = result['llm_answer'].strip().upper()[0]
        correct_answer = result['correct_answer'].strip().upper()[0]
        
        return {
            'question_number': result['question_number'],
            'is_correct': llm_answer == correct_answer,
            'given_answer': llm_answer,
            'correct_answer': correct_answer,
            'confidence': 1.0
        }

    def get_score(self) -> float:
        return self.correct_answers / self.total_questions if self.total_questions > 0 else 0.0