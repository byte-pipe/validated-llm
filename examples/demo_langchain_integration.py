#!/usr/bin/env python3
"""
Demo script showing Langchain integration functionality.
This demonstrates the core converter logic without requiring dependencies.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

# Import the core logic directly
import re
from typing import Any, Dict, List


class MockPromptTemplate:
    """Mock Langchain PromptTemplate for demonstration."""

    def __init__(self, template: str, input_variables: List[str]):
        self.template = template
        self.input_variables = input_variables


class PromptAnalyzer:
    """Simplified version of the converter for demonstration."""

    def extract_variables(self, template: str) -> List[str]:
        """Extract variable names from template string."""
        pattern = r"\{(\w+)\}"
        return list(set(re.findall(pattern, template)))

    def analyze_prompt(self, template: str) -> Dict[str, Any]:
        """Analyze a prompt template to infer its purpose."""
        analysis = {"template": template, "variables": self.extract_variables(template), "output_type": "text", "suggested_validators": []}

        template_lower = template.lower()

        if any(word in template_lower for word in ["json", "object", "structure"]):
            analysis["suggested_validators"].append("JSONValidator")
            analysis["output_type"] = "json"
        elif any(word in template_lower for word in ["list", "items", "bullet"]):
            analysis["suggested_validators"].append("ListValidator")
            analysis["output_type"] = "list"
        elif any(word in template_lower for word in ["markdown", "blog", "article"]):
            analysis["suggested_validators"].append("MarkdownValidator")
            analysis["output_type"] = "markdown"
        elif any(word in template_lower for word in ["email", "message"]):
            analysis["suggested_validators"].append("EmailValidator")
            analysis["output_type"] = "email"
        elif any(word in template_lower for word in ["code", "function", "class"]):
            analysis["suggested_validators"].append("SyntaxValidator")
            analysis["output_type"] = "code"
        else:
            analysis["suggested_validators"].append("RegexValidator")
            analysis["output_type"] = "text"

        return analysis

    def generate_task_code(self, analysis: Dict[str, Any], task_name: str) -> str:
        """Generate validated-llm task code from analysis."""
        validator = analysis["suggested_validators"][0] if analysis["suggested_validators"] else "RegexValidator"

        code = f'''"""
Generated task from Langchain PromptTemplate conversion.
"""

from validated_llm.tasks import BaseTask
from validated_llm.validators import {validator}


class {task_name}(BaseTask):
    """
    Converted from Langchain PromptTemplate.

    Expected output type: {analysis["output_type"]}
    Variables: {analysis["variables"]}
    """

    prompt_template = """{analysis["template"]}"""
    validator_class = {validator}

    @classmethod
    def get_prompt_variables(cls):
        """Get the list of variables needed for the prompt."""
        return {analysis["variables"]}
'''
        return code


def demo_conversion():
    """Demonstrate converting various Langchain prompts."""
    print("🔄 Langchain to Validated-LLM Conversion Demo")
    print("=" * 50)

    analyzer = PromptAnalyzer()

    # Example 1: JSON Generation
    print("\n📝 Example 1: JSON Generation")
    print("-" * 30)

    json_prompt = MockPromptTemplate(template="Generate a JSON object with profile information for {name}. Include name, age, occupation, and interests.", input_variables=["name"])

    print(f"Original Langchain template: {json_prompt.template}")
    print(f"Input variables: {json_prompt.input_variables}")

    analysis = analyzer.analyze_prompt(json_prompt.template)
    print(f"✓ Detected output type: {analysis['output_type']}")
    print(f"✓ Suggested validator: {analysis['suggested_validators'][0]}")
    print(f"✓ Extracted variables: {analysis['variables']}")

    task_code = analyzer.generate_task_code(analysis, "PersonProfileTask")
    print("\n📄 Generated validated-llm task:")
    print(task_code)

    # Example 2: Blog Post Generation
    print("\n📝 Example 2: Blog Post Generation")
    print("-" * 30)

    blog_prompt = MockPromptTemplate(template="Write a blog post in markdown format about {topic}. Include an introduction, main content, and conclusion.", input_variables=["topic"])

    print(f"Original Langchain template: {blog_prompt.template}")

    analysis = analyzer.analyze_prompt(blog_prompt.template)
    print(f"✓ Detected output type: {analysis['output_type']}")
    print(f"✓ Suggested validator: {analysis['suggested_validators'][0]}")

    task_code = analyzer.generate_task_code(analysis, "BlogPostTask")
    print("\n📄 Generated validated-llm task:")
    print(task_code)

    # Example 3: List Generation
    print("\n📝 Example 3: List Generation")
    print("-" * 30)

    list_prompt = MockPromptTemplate(template="List the top 5 benefits of {product} for {target_audience}", input_variables=["product", "target_audience"])

    print(f"Original Langchain template: {list_prompt.template}")

    analysis = analyzer.analyze_prompt(list_prompt.template)
    print(f"✓ Detected output type: {analysis['output_type']}")
    print(f"✓ Suggested validator: {analysis['suggested_validators'][0]}")
    print(f"✓ Extracted variables: {analysis['variables']}")

    task_code = analyzer.generate_task_code(analysis, "ProductBenefitsTask")
    print("\n📄 Generated validated-llm task:")
    print(task_code)


def demo_parser_mapping():
    """Demonstrate output parser mapping."""
    print("\n🔗 Output Parser Mapping Demo")
    print("=" * 30)

    parser_mappings = {
        "PydanticOutputParser": "Custom Pydantic validator with schema validation",
        "StructuredOutputParser": "JSONValidator for structured data",
        "ListOutputParser": "Custom ListValidator for list formats",
        "DatetimeOutputParser": "DateTimeValidator for date/time parsing",
        "CommaSeparatedListOutputParser": "Custom CSVValidator for CSV data",
        "OutputFixingParser": "Built into ValidationLoop (automatic retry)",
        "RetryOutputParser": "Built into ValidationLoop (automatic retry)",
    }

    for langchain_parser, validated_llm_equivalent in parser_mappings.items():
        print(f"📋 {langchain_parser}")
        print(f"   → {validated_llm_equivalent}")


def demo_cli_usage():
    """Show CLI usage examples."""
    print("\n💻 CLI Usage Examples")
    print("=" * 25)

    print("# Convert a single Langchain prompt file:")
    print("python -m validated_llm.integrations.langchain.cli convert my_prompts.py")
    print()
    print("# Migrate an entire directory:")
    print("python -m validated_llm.integrations.langchain.cli migrate ./langchain_project --recursive")
    print()
    print("# Show conversion examples:")
    print("python -m validated_llm.integrations.langchain.cli examples")


def main():
    """Run the complete demonstration."""
    demo_conversion()
    demo_parser_mapping()
    demo_cli_usage()

    print("\n" + "=" * 50)
    print("✅ Langchain Integration Demo Complete!")
    print("\nThis integration provides:")
    print("• Automatic prompt analysis and validator suggestion")
    print("• Seamless conversion from Langchain to validated-llm")
    print("• Robust validation with automatic retry on failure")
    print("• Support for all major output formats (JSON, Markdown, Lists, etc.)")
    print("• CLI tools for individual and batch conversion")


if __name__ == "__main__":
    main()
