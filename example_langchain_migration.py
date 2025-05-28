#!/usr/bin/env python3
"""
Real example of migrating from Langchain to validated-llm.
"""

import os
import sys

# Mock imports for demo
from unittest.mock import MagicMock, Mock

# Create a proper mock module
chatbot_mock = MagicMock()
chatbot_mock.chatbot = MagicMock()
chatbot_mock.chatbot.ChatBot = Mock()

sys.modules["chatbot"] = chatbot_mock
sys.modules["chatbot.chatbot"] = chatbot_mock.chatbot
sys.modules["langchain"] = Mock()
sys.modules["langchain.prompts"] = Mock()

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

print("🔄 LANGCHAIN TO VALIDATED-LLM MIGRATION EXAMPLE\n")

# ============================================================
# STEP 1: Your existing Langchain code
# ============================================================
print("📌 STEP 1: Your existing Langchain code")
print("-" * 40)
print(
    """
# OLD CODE:
from langchain.prompts import PromptTemplate

product_prompt = PromptTemplate(
    input_variables=["product", "audience"],
    template='''Generate a marketing description for {product}.
    Target audience: {audience}
    Format as JSON with title, tagline, and benefits.'''
)

# Using without validation - risky!
result = llm(product_prompt.format(product="Smart Watch", audience="Fitness enthusiasts"))
"""
)

# ============================================================
# STEP 2: Convert using our tool
# ============================================================
print("\n📌 STEP 2: Convert using our converter")
print("-" * 40)

# Simulate the conversion
from validated_llm.integrations.langchain.converter import PromptTemplateConverter

# Create converter
converter = PromptTemplateConverter()

# Analyze the prompt
template = """Generate a marketing description for {product}.
Target audience: {audience}
Format as JSON with title, tagline, and benefits."""

analysis = converter.analyze_prompt(template)
print(f"✅ Detected output type: {analysis['output_type']}")
print(f"✅ Suggested validator: {analysis['suggested_validators']}")
print(f"✅ Variables found: {analysis['variables']}")

# ============================================================
# STEP 3: Generated validated-llm task
# ============================================================
print("\n📌 STEP 3: Your new validated-llm task")
print("-" * 40)
print(
    """
# NEW CODE:
from validated_llm.tasks import BaseTask
from validated_llm.validators import JSONValidator
from validated_llm.validation_loop import ValidationLoop

class MarketingDescriptionTask(BaseTask):
    '''Generate validated marketing descriptions.'''

    prompt_template = '''Generate a marketing description for {product}.
    Target audience: {audience}
    Format as JSON with title, tagline, and benefits.'''

    validator_class = JSONValidator

    # Add JSON schema validation
    validator_config = {
        "required_fields": ["title", "tagline", "benefits"],
        "schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "maxLength": 100},
                "tagline": {"type": "string", "maxLength": 200},
                "benefits": {
                    "type": "array",
                    "items": {"type": "string"},
                    "minItems": 3,
                    "maxItems": 5
                }
            },
            "required": ["title", "tagline", "benefits"]
        }
    }
"""
)

# ============================================================
# STEP 4: Use with automatic validation
# ============================================================
print("\n📌 STEP 4: Use with automatic validation & retry")
print("-" * 40)
print(
    """
# Create task instance
task = MarketingDescriptionTask()

# Create validation loop with retry
loop = ValidationLoop(
    task=task,
    max_retries=3,  # Will retry up to 3 times if validation fails
    llm_backend="your_llm"
)

# Execute with guaranteed valid output
result = loop.execute(
    product="Smart Watch",
    audience="Fitness enthusiasts"
)

# Result is GUARANTEED to be valid JSON with all required fields!
print(result)
# {
#   "title": "FitTrack Pro Smart Watch",
#   "tagline": "Your Personal Fitness Coach on Your Wrist",
#   "benefits": [
#     "24/7 heart rate monitoring",
#     "GPS tracking for outdoor workouts",
#     "Sleep quality analysis",
#     "Water resistance for swimming"
#   ]
# }
"""
)

# ============================================================
# Benefits Summary
# ============================================================
print("\n✨ MIGRATION BENEFITS:")
print("-" * 40)
print("❌ Before: Hope the LLM returns valid JSON")
print("✅ After: GUARANTEED valid JSON output")
print()
print("❌ Before: Manual parsing and error handling")
print("✅ After: Automatic validation with retry")
print()
print("❌ Before: Inconsistent output format")
print("✅ After: Schema-validated structure")
print()
print("❌ Before: Silent failures")
print("✅ After: Clear error messages for debugging")

# ============================================================
# CLI Migration
# ============================================================
print("\n🛠️  BULK MIGRATION WITH CLI:")
print("-" * 40)
print(
    """
# Convert all Langchain prompts in your project:
$ python -m validated_llm.integrations.langchain.cli migrate ./my_project --recursive

# This will:
1. Find all Python files with PromptTemplate usage
2. Analyze each prompt and suggest validators
3. Generate corresponding validated-llm tasks
4. Create a migration report

# Example output:
✅ Converted 15 prompts across 8 files
📄 Generated: my_project/tasks/converted_tasks.py
📊 Migration report: migration_report.md
"""
)

print("\n🎉 Migration Complete! Your LLM outputs are now validated and reliable!")
