from enum import Enum
from typing import Any, Dict, List, Optional
import re

from repenseai.genai.benchmark.core.base_evaluator import BaseEvaluator
from repenseai.genai.benchmark.core.base_provider import BaseLLMProvider


class MatchType(Enum):
    EXACT = "exact"                 # Correspondência exata
    NORMALIZED = "normalized"       # Normalizado (case, pontuação, espaços)
    CONTAINS = "contains"          # Contém a resposta
    SEMANTIC = "semantic"          # Similaridade semântica
    REGEX = "regex"                # Expressão regular
    CUSTOM = "custom"              # Função customizada


class SimpleOutputEvaluator(BaseEvaluator):
    def __init__(
        self, 
        name: str, 
        validation_rules: Dict[str, Any] = None,
        metrics: List[str] = None,
        match_type: MatchType = MatchType.NORMALIZED,
        similarity_threshold: float = 0.85,
        llm_provider: Optional[BaseLLMProvider] = None  # Para matching semântico
    ):
        super().__init__(name)

        self.validation_rules = validation_rules or {}
        self.metrics = metrics or ["accuracy"]
        self.match_type = match_type
        self.similarity_threshold = similarity_threshold
        self.llm_provider = llm_provider
        self.valid_outputs = 0
        self.total_outputs = 0
        self.correct_outputs = 0
        self.metrics_results = {}

    def _normalize_text(self, text: str) -> str:
        """Normaliza o texto removendo pontuação extra, espaços e case"""
        text = text.lower().strip()
        text = re.sub(r'[^\w\s]', '', text)
        text = re.sub(r'\s+', ' ', text)
        return text

    async def _check_semantic_similarity(self, output: str, ground_truth: str) -> bool:
        """Verifica similaridade semântica usando LLM"""
        if not self.llm_provider:
            return False
        
        prompt = (
            "Compare these two answers and determine if they have the same meaning:\n"
            f"Answer 1: {output}\n"
            f"Answer 2: {ground_truth}\n\n"
            "Respond with only 'True' if they mean the same thing, or 'False' if they don't."
        )

        response = await self.llm_provider.generate(prompt)
        return response.strip().lower() == 'true'

    async def _compare_outputs(self, output: str, ground_truth: str) -> bool:
        """Compara outputs baseado no tipo de matching configurado"""
        if not ground_truth:
            return False

        match self.match_type:
            case MatchType.EXACT:
                return output == ground_truth
            
            case MatchType.NORMALIZED:
                return self._normalize_text(output) == self._normalize_text(ground_truth)
            
            case MatchType.CONTAINS:
                return self._normalize_text(ground_truth) in self._normalize_text(output)
            
            case MatchType.SEMANTIC:
                return await self._check_semantic_similarity(output, ground_truth)
            
            case MatchType.REGEX:
                pattern = self.validation_rules.get('regex_pattern', ground_truth)
                return bool(re.match(pattern, output))
            
            case MatchType.CUSTOM:
                custom_func = self.validation_rules.get('custom_comparator')
                return custom_func(output, ground_truth) if custom_func else False
            
    def _calculate_metrics(self, predictions: List[str], ground_truth: List[str]) -> Dict[str, float]:
        metrics_results = {}
        
        for metric in self.metrics:
            if metric == "accuracy":
                correct = sum(p == g for p, g in zip(predictions, ground_truth))
                metrics_results["accuracy"] = correct / len(predictions)
            
            elif metric == "f1":
                from sklearn.metrics import f1_score
                # Assuming binary classification for simplicity
                metrics_results["f1"] = f1_score(
                    ground_truth, 
                    predictions, 
                    average='weighted',
                    zero_division=0
                )
            
            elif metric == "precision":
                from sklearn.metrics import precision_score
                metrics_results["precision"] = precision_score(
                    ground_truth, 
                    predictions, 
                    average='weighted',
                    zero_division=0
                )
            
            elif metric == "recall":
                from sklearn.metrics import recall_score
                metrics_results["recall"] = recall_score(
                    ground_truth, 
                    predictions, 
                    average='weighted',
                    zero_division=0
                )

        return metrics_results

    def _validate_output(self, output: str) -> bool:
        """
        Validates the output based on validation rules.
        
        Validation rules can include:
        - allowed_values: List of allowed values
        - min_length: Minimum length of output
        - max_length: Maximum length of output
        - regex_pattern: Regular expression pattern to match
        - required_format: Format specification (e.g., 'number', 'date', 'email')
        - custom_validator: Custom validation function
        """
        if not self.validation_rules:
            return True

        # Check if output is None or empty
        if output is None or not isinstance(output, str):
            return False

        # Check allowed values
        if 'allowed_values' in self.validation_rules:
            if output not in self.validation_rules['allowed_values']:
                return False

        # Check length constraints
        if 'min_length' in self.validation_rules:
            if len(output) < self.validation_rules['min_length']:
                return False

        if 'max_length' in self.validation_rules:
            if len(output) > self.validation_rules['max_length']:
                return False

        # Check regex pattern
        if 'regex_pattern' in self.validation_rules:
            pattern = self.validation_rules['regex_pattern']
            if not re.match(pattern, output):
                return False

        # Check required format
        if 'required_format' in self.validation_rules:
            format_type = self.validation_rules['required_format']
            
            if format_type == 'number':
                try:
                    float(output)
                except ValueError:
                    return False
            
            elif format_type == 'date':
                try:
                    from datetime import datetime
                    datetime.strptime(output, self.validation_rules.get('date_format', '%Y-%m-%d'))
                except ValueError:
                    return False
            
            elif format_type == 'email':
                email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                if not re.match(email_pattern, output):
                    return False

        # Custom validation
        if 'custom_validator' in self.validation_rules:
            custom_validator = self.validation_rules['custom_validator']
            try:
                if not custom_validator(output):
                    return False
            except Exception:
                return False

        return True     

    async def evaluate(self, test_results: Dict[str, Any]) -> Dict[str, Any]:
        evaluation = []

        self.total_outputs = len(test_results['results'])
        self.valid_outputs = 0
        self.correct_outputs = 0
        
        predictions = []
        ground_truth = []

        for result in test_results['results']:
            output = result['output'].upper()
            ground_truth_value = result.get('ground_truth').upper()
            
            # Valida formato se houver regras
            is_valid = self._validate_output(output)

            if is_valid:
                self.valid_outputs += 1
            
            # Compara com ground truth se existir
            is_correct = False

            if ground_truth_value is not None:
                is_correct = await self._compare_outputs(output, ground_truth_value)

            predictions.append(is_correct)
            ground_truth.append(True)

            evaluation.append(
                {
                    'input_number': result['input_number'],
                    'is_valid': is_valid,
                    'output': output,
                    'ground_truth': ground_truth_value,
                    'correct': is_correct,
                    'normalized_output': self._normalize_text(output),
                    'normalized_ground_truth': self._normalize_text(ground_truth_value) if ground_truth_value else None
                }
            )

        if ground_truth:
            self.metrics_results = self._calculate_metrics(predictions, ground_truth)

        return {
            'evaluation_details': evaluation,
            'total_outputs': self.total_outputs,
            'valid_outputs': self.valid_outputs,
            'metrics': self.metrics_results,
            'match_type': self.match_type.value
        }
    
    def get_score(self) -> float:
        if self.metrics_results:
            return self.metrics_results
        return self.valid_outputs / self.total_outputs if self.total_outputs > 0 else 0.0