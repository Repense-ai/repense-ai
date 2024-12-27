from typing import TypedDict, List, Dict, Any

from repenseai.genai.benchmark.core.base_provider import BaseLLMProvider
from repenseai.genai.benchmark.core.base_test import BaseTest

class Question(TypedDict):
    text: str
    options: List[str]
    correct_answer: str

class TestValidationError(Exception):
    pass

class OptionQuestionTest(BaseTest):
    def __init__(
        self,
        name: str,
        questions: List[Question],
        description: str = None,
        prompt_template: str = None
    ):
        super().__init__(name, description)
        self.questions = questions

        DEFAULT_PROMPT_TEMPLATE = (
            "Question {question_number}:\n"
            "{question_text}\n\n"
            "Options:\n"
            "{options_text}\n\n"
            "Please respond with only the letter of the correct option (A, B, C, etc.).\n"
            "Do not explain your answer or add any additional text."
        )

        self.prompt_template = prompt_template or DEFAULT_PROMPT_TEMPLATE

    def validate(self) -> bool:
        try:
            self._validate_questions()
            return True
        except TestValidationError as e:
            print(e)
            return False
            
    def _validate_questions(self) -> None:
        for i, question in enumerate(self.questions, 1):
            if not all(key in question for key in ['text', 'options', 'correct_answer']):
                raise TestValidationError(f"Question {i} is missing required fields")
            if not isinstance(question['options'], list) or len(question['options']) < 2:
                raise TestValidationError(f"Question {i} must have at least 2 options")
            if not any(question['correct_answer'] in option for option in question['options']):
                raise TestValidationError(f"Question {i}'s correct answer must be in options")

    async def run(self, llm_provider: BaseLLMProvider) -> Dict[str, Any]:
        results = []
        
        for i, question in enumerate(self.questions, 1):
            prompt = self._create_prompt(question, i)
            response = await llm_provider.generate(prompt)
            
            results.append({
                'question_number': i,
                'question': question['text'],
                'options': question['options'],
                'correct_answer': question['correct_answer'],
                'llm_answer': response,
            })
        
        return {
            'test_type': 'options_exam',
            'results': results
        }

    def _create_prompt(self, question: Question, question_number: int) -> str:
        options_text = "\n".join(
            f"{chr(65 + i)}. {option}" 
            for i, option in enumerate(question['options'])
        )

        return self.prompt_template.format(
            question_number=question_number,
            question_text=question['text'],
            options_text=options_text
        )