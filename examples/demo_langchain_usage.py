#!/usr/bin/env python3
"""
Complete demonstration of how to use the Langchain to validated-llm converter.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

# Mock the dependencies for demo purposes
from unittest.mock import Mock

sys.modules["chatbot"] = Mock()
sys.modules["chatbot.chatbot"] = Mock()
sys.modules["langchain"] = Mock()
sys.modules["langchain.prompts"] = Mock()

# Now we can import our converter
from validated_llm.integrations.langchain.converter import PromptTemplateConverter
from validated_llm.integrations.langchain.parser_mapping import OutputParserMapper


def demo_basic_conversion():
    """Demo 1: Convert a simple Langchain prompt to validated-llm task."""
    print("=" * 60)
    print("DEMO 1: Basic Prompt Conversion")
    print("=" * 60)

    # Simulate a Langchain PromptTemplate
    class LangchainPromptTemplate:
        def __init__(self, template, input_variables):
            self.template = template
            self.input_variables = input_variables

    # 1. Create a Langchain prompt (what users currently have)
    langchain_prompt = LangchainPromptTemplate(template="Write a product description for {product_name}. The description should highlight its key features: {features}", input_variables=["product_name", "features"])

    print("\n📝 Original Langchain Prompt:")
    print(f"Template: {langchain_prompt.template}")
    print(f"Variables: {langchain_prompt.input_variables}")

    # 2. Use our converter to analyze the prompt
    converter = PromptTemplateConverter()
    analysis = converter.analyze_prompt(langchain_prompt.template)

    print("\n🔍 Analysis Results:")
    print(f"Output type detected: {analysis['output_type']}")
    print(f"Suggested validator: {analysis['suggested_validators']}")
    print(f"Variables extracted: {analysis['variables']}")

    # 3. Generate the validated-llm task code
    print("\n📄 Generated validated-llm Task:")
    print("-" * 40)

    task_code = f'''from validated_llm.tasks import BaseTask
from validated_llm.validators import {analysis['suggested_validators'][0]}


class ProductDescriptionTask(BaseTask):
    """
    Auto-generated from Langchain PromptTemplate.
    This task generates product descriptions with automatic validation.
    """

    prompt_template = """{langchain_prompt.template}"""

    validator_class = {analysis['suggested_validators'][0]}

    @classmethod
    def get_prompt_variables(cls):
        return {langchain_prompt.input_variables}
'''
    print(task_code)

    # 4. Show how to use the generated task
    print("\n🚀 How to use the generated task:")
    print("-" * 40)
    print(
        """
# In your code:
from your_tasks import ProductDescriptionTask
from validated_llm.validation_loop import ValidationLoop

# Create the task
task = ProductDescriptionTask()

# Run with validation
loop = ValidationLoop(task=task, max_retries=3)
result = loop.execute(
    product_name="Smart Water Bottle",
    features="Temperature tracking, LED indicators, Mobile app sync"
)

print(result)  # Guaranteed to be valid!
"""
    )


def demo_json_conversion():
    """Demo 2: Convert a JSON-generating Langchain prompt."""
    print("\n" + "=" * 60)
    print("DEMO 2: JSON Output Conversion")
    print("=" * 60)

    # Langchain prompt that generates JSON
    class LangchainJSONPrompt:
        def __init__(self):
            self.template = """Generate a JSON object for a user profile with the following details:
- Name: {name}
- Age: {age}
- Occupation: {occupation}

The JSON should include these fields: id, name, age, occupation, email, created_at"""
            self.input_variables = ["name", "age", "occupation"]

    json_prompt = LangchainJSONPrompt()

    print("\n📝 Langchain JSON Prompt:")
    print(json_prompt.template)

    # Analyze and convert
    converter = PromptTemplateConverter()
    analysis = converter.analyze_prompt(json_prompt.template)

    print("\n🔍 Analysis Results:")
    print(f"Output type: {analysis['output_type']} ✅")
    print(f"Validator: {analysis['suggested_validators']} ✅")

    # Generate task with JSON validation
    print("\n📄 Generated Task with JSON Validation:")
    print("-" * 40)
    print(
        """
class UserProfileTask(BaseTask):
    prompt_template = \"\"\"Generate a JSON object for a user profile...\"\"\"

    validator_class = JSONValidator

    # Can add JSON schema validation
    validator_config = {
        "required_fields": ["id", "name", "age", "occupation", "email", "created_at"],
        "schema": {
            "type": "object",
            "properties": {
                "id": {"type": "string"},
                "name": {"type": "string"},
                "age": {"type": "integer", "minimum": 0},
                "occupation": {"type": "string"},
                "email": {"type": "string", "format": "email"},
                "created_at": {"type": "string", "format": "date-time"}
            },
            "required": ["id", "name", "age", "occupation", "email", "created_at"]
        }
    }
"""
    )


def demo_list_conversion():
    """Demo 3: Convert a list-generating prompt."""
    print("\n" + "=" * 60)
    print("DEMO 3: List Output Conversion")
    print("=" * 60)

    list_template = "List the top 5 benefits of {product} for {target_audience}. Format as a bulleted list."

    converter = PromptTemplateConverter()
    analysis = converter.analyze_prompt(list_template)

    print(f"\n📝 List Prompt: {list_template}")
    print(f"\n🔍 Detected: {analysis['output_type']} format")
    print(f"✅ Will use: {analysis['suggested_validators'][0]}")

    print("\n📄 The ListValidator will ensure:")
    print("- Output is formatted as a proper list")
    print("- Each item starts with -, *, •, or numbers")
    print("- Empty lines are handled correctly")
    print("- Returns parsed list items for further processing")


def demo_parser_mapping():
    """Demo 4: Show how Langchain parsers map to validators."""
    print("\n" + "=" * 60)
    print("DEMO 4: Output Parser Mapping")
    print("=" * 60)

    print("\n🔄 Langchain Parser → Validated-LLM Validator Mapping:\n")

    mappings = [
        ("PydanticOutputParser", "→", "Custom validator with Pydantic model validation"),
        ("StructuredOutputParser", "→", "JSONValidator with schema"),
        ("ListOutputParser", "→", "ListValidator (validates list formats)"),
        ("DatetimeOutputParser", "→", "DateTimeValidator"),
        ("CommaSeparatedListOutputParser", "→", "CSVValidator"),
        ("OutputFixingParser", "→", "Built into ValidationLoop (automatic retry)"),
        ("RetryOutputParser", "→", "Built into ValidationLoop (automatic retry)"),
    ]

    for langchain, arrow, validated in mappings:
        print(f"  {langchain:<30} {arrow} {validated}")

    print("\n💡 Key advantage: validated-llm automatically retries on validation failure!")


def demo_cli_usage():
    """Demo 5: Show CLI usage for batch conversion."""
    print("\n" + "=" * 60)
    print("DEMO 5: CLI Usage for Batch Conversion")
    print("=" * 60)

    print("\n🛠️  Command Line Interface:\n")

    print("1️⃣  Convert a single file:")
    print("   $ python -m validated_llm.integrations.langchain.cli convert prompts.py")
    print("   ✅ Generates: prompts_tasks.py with all converted tasks\n")

    print("2️⃣  Migrate entire project:")
    print("   $ python -m validated_llm.integrations.langchain.cli migrate ./my_project --recursive")
    print("   ✅ Finds all Langchain prompts and converts them\n")

    print("3️⃣  See examples:")
    print("   $ python -m validated_llm.integrations.langchain.cli examples")
    print("   ✅ Shows conversion examples and best practices\n")

    print("4️⃣  Convert with specific validator:")
    print("   $ python -m validated_llm.integrations.langchain.cli convert prompts.py --validator EmailValidator")
    print("   ✅ Forces specific validator instead of auto-detection")


def demo_real_world_example():
    """Demo 6: Complete real-world example."""
    print("\n" + "=" * 60)
    print("DEMO 6: Real-World Migration Example")
    print("=" * 60)

    print("\n📋 Scenario: You have Langchain code for generating emails\n")

    print("🔴 OLD Langchain Code:")
    print("-" * 40)
    print(
        '''
from langchain.prompts import PromptTemplate
from langchain.llms import OpenAI

# Define prompt
email_prompt = PromptTemplate(
    input_variables=["recipient", "subject", "tone"],
    template="""Write a professional email to {recipient} about {subject}.
    Use a {tone} tone. Include a greeting, body, and signature."""
)

# Generate without validation
llm = OpenAI()
email = llm(email_prompt.format(
    recipient="John Doe",
    subject="Project Update",
    tone="friendly"
))
print(email)  # Hope it's formatted correctly! 🤞
'''
    )

    print("\n🟢 NEW validated-llm Code:")
    print("-" * 40)
    print(
        '''
from validated_llm.tasks import BaseTask
from validated_llm.validators import EmailValidator
from validated_llm.validation_loop import ValidationLoop

# Converted task with validation
class ProfessionalEmailTask(BaseTask):
    prompt_template = """Write a professional email to {recipient} about {subject}.
    Use a {tone} tone. Include a greeting, body, and signature."""

    validator_class = EmailValidator
    validator_config = {
        "require_greeting": True,
        "require_signature": True,
        "min_length": 100
    }

# Generate with guaranteed validation
task = ProfessionalEmailTask()
loop = ValidationLoop(task=task, max_retries=3)

email = loop.execute(
    recipient="John Doe",
    subject="Project Update",
    tone="friendly"
)
print(email)  # Guaranteed to be properly formatted! ✅
'''
    )

    print("\n✨ Benefits of Migration:")
    print("• ✅ Automatic validation of email format")
    print("• ✅ Retry on failure with error feedback")
    print("• ✅ Consistent output quality")
    print("• ✅ Better error handling")
    print("• ✅ Type safety and documentation")


def main():
    """Run all demonstrations."""
    print("\n🚀 LANGCHAIN TO VALIDATED-LLM CONVERTER DEMO\n")

    demo_basic_conversion()
    demo_json_conversion()
    demo_list_conversion()
    demo_parser_mapping()
    demo_cli_usage()
    demo_real_world_example()

    print("\n" + "=" * 60)
    print("🎉 Migration Complete!")
    print("=" * 60)
    print("\nYour Langchain prompts now have:")
    print("✅ Automatic validation")
    print("✅ Retry on failure")
    print("✅ Structured error feedback")
    print("✅ Better reliability")
    print("✅ Type safety\n")


if __name__ == "__main__":
    main()
