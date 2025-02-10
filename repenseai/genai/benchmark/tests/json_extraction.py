from typing import List, Dict, Any

import json

from repenseai.genai.benchmark.core.base_provider import BaseagentProvider
from repenseai.genai.benchmark.core.base_test import BaseTest


class DataExtractionTest(BaseTest):
    def __init__(
        self,
        name: str,
        inputs: List[Dict[str, Any]],
        schema: Dict[str, Any],
        description: str = None
    ):
        super().__init__(name, description)
        self.inputs = inputs
        self.schema = schema

    def validate(self) -> bool:
        """
        Validate if the test is properly configured:
        - Each input must have a text
        - Schema must be a valid JSON schema
        """
        if not self.inputs or not self.schema:
            return False
        
        for input_data in self.inputs:
            if 'text' not in input_data:
                return False
        
        # Basic schema validation
        required_schema_fields = ['type', 'properties']
        if not all(field in self.schema for field in required_schema_fields):
            return False
            
        return True

    async def run(self, agent_provider: BaseagentProvider) -> Dict[str, Any]:
        results = []
        
        for i, input_data in enumerate(self.inputs, 1):
            prompt = self._create_prompt(input_data, i)
            response = await agent_provider.generate(prompt)
            
            try:
                parsed_response = json.loads(response)
            except json.JSONDecodeError:
                parsed_response = response

            results.append(
                {
                    'input_number': i,
                    'input_text': input_data['text'],
                    'extracted_data': parsed_response,
                }
            )
        
        return {
            'test_type': 'data_extraction',
            'schema': self.schema,
            'results': results
        }

    def _create_prompt(self, input_data: Dict[str, Any], input_number: int) -> str:
        schema_str = json.dumps(self.schema, indent=2)

        prompt = (
            "Extract information from the following text according to the schema below.\n"
            "Respond ONLY with a valid JSON object matching the schema. Do not include any additional text.\n\n"
            f"Schema:\n{schema_str}\n\n"
            f"Input {input_number}:\n{input_data['text']}"
        )
        
        return prompt
    
    
def get_sample():
    data_test = DataExtractionTest(
        name="Person Information Extraction",
        description="Extract person details from text",
        schema={
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"},
                "occupation": {"type": "string"},
                "location": {"type": "string"}
            },
            "required": ["name", "age"]
        },
        inputs=[
            {
                "text": "John Smith is a 35-year-old software engineer living in New York."
            },
            {
                "text": "Mary Johnson, 42, works as a teacher in Chicago."
            }
        ]
    )

    return data_test    