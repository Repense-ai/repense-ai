from typing import List, Dict, Any

from repenseai.genai.benchmark.core.base_provider import BaseagentProvider
from repenseai.genai.benchmark.core.base_test import BaseTest

class OpenQuestionExamTest(BaseTest):
    def __init__(
        self,
        name: str,
        questions: List[Dict[str, Any]],
        description: str = None,
        max_tokens_per_answer: int = 500
    ):
        super().__init__(name, description)
        self.questions = questions
        self.max_tokens_per_answer = max_tokens_per_answer

    def validate(self) -> bool:
        """
        Validate if the test is properly configured:
        - Each question must have a text
        - Each question must have evaluation criteria
        """
        for question in self.questions:
            if not all(key in question for key in ['text', 'evaluation_criteria']):
                return False
            if not isinstance(question['evaluation_criteria'], list):
                return False
        return True

    async def run(self, agent_provider: BaseagentProvider) -> Dict[str, Any]:
        results = []
        
        for i, question in enumerate(self.questions, 1):
            prompt = self._create_prompt(question, i)
            response = await agent_provider.generate(prompt)
            
            results.append({
                'question_number': i,
                'question': question['text'],
                'evaluation_criteria': question['evaluation_criteria'],
                'agent_answer': response,
            })
        
        return {
            'test_type': 'open_exam',
            'results': results
        }

    def _create_prompt(self, question: Dict[str, Any], question_number: int) -> str:

        prompt = (
            f"Question {question_number}:\n"
            f"{question['text']}\n\n"
            "Please provide a detailed answer to this question. "
            "Be specific and thorough in your response.\n"
            "Your answer should address the main points and demonstrate understanding of the topic."
        )

        return prompt
    

def get_sample():
    
    open_test = OpenQuestionExamTest(
        name="History Essay Test",
        description="World War II essay questions",
        questions=[
            {
                'text': "Explain the main causes of World War II.",
                'evaluation_criteria': [
                    "Mentions Treaty of Versailles",
                    "Discusses rise of fascism",
                    "Explains economic factors",
                    "Describes immediate triggers"
                ]
            }
        ]
    )

    return open_test    
