from repenseai.genai.benchmark.core.base_provider import BaseLLMProvider

from repenseai.genai.benchmark.tests.option_question import OptionQuestionTest
from repenseai.genai.benchmark.tests.json_extraction import DataExtractionTest
from repenseai.genai.benchmark.tests.simple_output import SimpleOutputTest

from repenseai.genai.benchmark.evaluators.option_evaluator import OptionQuestionEvaluator
from repenseai.genai.benchmark.evaluators.json_evaluator import SchemaEvaluator
from repenseai.genai.benchmark.evaluators.simple_evaluator import SimpleOutputEvaluator, MatchType

from repenseai.genai.benchmark.core.base_benchmark import Benchmark



# Create providers
openai_provider = BaseLLMProvider(
    name="OpenAI",
    model="gpt-4o",
)

anthropic_provider = BaseLLMProvider(
    name="Anthropic",
    model="claude-3-5-haiku-20241022",
)


# options_test = OptionQuestionTest(
#     name="Basic Knowledge Test",
#     description="Test basic knowledge across different topics",
#     questions=[
#         {
#             'text': "What is the capital of France?",
#             'options': ['a: London', 'b: Paris', 'c: Berlin', 'd: Madrid'],
#             'correct_answer': 'b'
#         },
#         {
#             'text': "What is 7 x 8?",
#             'options': ['a: 54', 'b: 58', 'c: 56', 'd: 62'],
#             'correct_answer': 'c'
#         }
#     ]
# )

# data_test = DataExtractionTest(
#     name="Contact Information Extraction",
#     description="Extract contact details from text",
#     schema={
#         "type": "object",
#         "properties": {
#             "name": {"type": "string"},
#             "email": {"type": "string"},
#             "phone": {"type": "string"}
#         },
#         "required": ["name"]
#     },
#     inputs=[
#         {
#             "text": "My name is John Smith and you can reach me at john@email.com or call 555-0123."
#         },
#         {
#             "text": "Contact Sarah Wilson at wilson.s@company.org, phone number: 555-9876"
#         }
#     ]
# )

simple_test = SimpleOutputTest(
    name="Text Classification",
    description="Classify text sentiment",
    expected_format="POSITIVE, NEGATIVE, or NEUTRAL",
    inputs=[
        {
            "text": "I love this product! It's amazing!",
            "instructions": "Classify the sentiment of this text.",
            "ground_truth": "POSITIVE",
        },
        {
            "text": "The service was terrible and I want my money back.",
            "instructions": "Classify the sentiment of this text.",
            "ground_truth": "NEGATIVE",
        }
    ],
    max_retries=3,
    retry_delay=1.0
)


# options_evaluator = OptionQuestionEvaluator(name="Basic Knowledge Test")
# schema_evaluator = SchemaEvaluator(name="JSON Schema Evaluator")

sentiment_evaluator = SimpleOutputEvaluator(
    name="Text Classification",
    validation_rules={
        'allowed_values': ['POSITIVE', 'NEGATIVE', 'NEUTRAL']
    },
    metrics=["accuracy", "f1", "precision", "recall"],
    match_type=MatchType.EXACT
)


benchmark = Benchmark()

# Add providers
benchmark.add_provider(openai_provider)
benchmark.add_provider(anthropic_provider)

# Add tests
# benchmark.add_test(options_test)
# benchmark.add_test(data_test)
benchmark.add_test(simple_test)

# Add evaluators
# benchmark.add_evaluator("Basic Knowledge Test", options_evaluator)
# benchmark.add_evaluator("Contact Information Extraction", schema_evaluator)
benchmark.add_evaluator("Text Classification", sentiment_evaluator)

results = benchmark.run_sync()
print(results)