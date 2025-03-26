from typing import Dict, Any

from repenseai.genai.benchmark.core.base_evaluator import BaseEvaluator
from repenseai.genai.benchmark.core.base_provider import BaseagentProvider


class OpenQuestionEvaluator(BaseEvaluator):
    def __init__(self, name: str, agent_provider: BaseagentProvider = None):
        super().__init__(name)
        self.agent_provider = agent_provider
        self.total_score = 0.0
        self.max_score = 0.0

    async def evaluate(self, test_results: Dict[str, Any]) -> Dict[str, Any]:
        evaluation = []
        self.total_score = 0.0
        self.max_score = 0.0

        for result in test_results["results"]:
            criteria_scores = []
            for criterion in result["evaluation_criteria"]:
                # If we have an agent provider, use it to evaluate the criterion
                if self.agent_provider:
                    score = await self._evaluate_criterion_with_Agent(
                        result["agent_answer"], criterion
                    )
                else:
                    # Manual evaluation needed
                    score = None

                criteria_scores.append({"criterion": criterion, "score": score})

            question_score = sum(
                s["score"] for s in criteria_scores if s["score"] is not None
            )
            max_possible = len(criteria_scores)

            self.total_score += question_score
            self.max_score += max_possible

            evaluation.append(
                {
                    "question_number": result["question_number"],
                    "criteria_scores": criteria_scores,
                    "question_score": question_score,
                    "max_possible": max_possible,
                }
            )

        return {
            "evaluation_details": evaluation,
            "total_score": self.total_score,
            "max_score": self.max_score,
        }

    async def _evaluate_criterion_with_Agent(
        self, answer: str, criterion: str
    ) -> float:
        prompt = (
            f'Evaluate if the following answer meets this criterion: "{criterion}"\n'
            f"Answer: {answer}\n\n"
            "Rate on a scale of 0 to 1 how well the answer meets the criterion.\n"
            "Respond with only a number between 0 and 1."
        )

        response = await self.agent_provider.generate(prompt)

        try:
            return float(response)
        except ValueError:
            return 0.0

    def get_score(self) -> float:
        return self.total_score / self.max_score if self.max_score > 0 else 0.0
