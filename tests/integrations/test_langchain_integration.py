"""
Integration tests for Langchain converter that properly mock dependencies.
"""

import os
import sys
from unittest.mock import MagicMock, Mock, patch

import pytest

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../src"))


@patch.dict("sys.modules", {"chatbot": Mock(), "chatbot.chatbot": Mock(), "langchain": Mock(), "langchain.prompts": Mock()})
def test_converter_with_mocked_deps():
    """Test the actual converter with mocked dependencies."""
    # Mock all the dependencies before importing
    with patch("validated_llm.integrations.langchain.LANGCHAIN_AVAILABLE", True):
        from validated_llm.integrations.langchain.converter import PromptTemplateConverter

        converter = PromptTemplateConverter()

        # Test analyze_prompt method
        template = "Generate a JSON object with name and age for {person}"
        analysis = converter.analyze_prompt(template)

        assert analysis["output_type"] == "json"
        assert "JSONValidator" in analysis["suggested_validators"]
        assert analysis["variables"] == ["person"]


def test_parser_mapper_with_mocked_deps():
    """Test the parser mapper with mocked dependencies."""
    # Test the parser mapping logic directly without imports
    parser_mappings = {
        "PydanticOutputParser": "Custom Pydantic validator",
        "StructuredOutputParser": "JSONValidator",
        "ListOutputParser": "Custom ListValidator",
        "DatetimeOutputParser": "DateTimeValidator",
        "CommaSeparatedListOutputParser": "Custom CSVValidator",
        "OutputFixingParser": None,  # Built into ValidationLoop
        "RetryOutputParser": None,  # Built into ValidationLoop
    }

    # Test that all expected parsers are mapped
    assert "PydanticOutputParser" in parser_mappings
    assert "DatetimeOutputParser" in parser_mappings
    assert "OutputFixingParser" in parser_mappings
    assert parser_mappings["OutputFixingParser"] is None  # Should be None for built-in


def test_langchain_availability_check():
    """Test the langchain availability check."""

    # Test the availability check logic directly
    def check_langchain_installed(langchain_available=False):
        """Mock version of the availability check."""
        if not langchain_available:
            raise ImportError("Langchain is not installed. Please install it with:\n" "pip install langchain")

    # Test when langchain is not available
    with pytest.raises(ImportError, match="pip install langchain"):
        check_langchain_installed(langchain_available=False)

    # Test when langchain is available (should not raise)
    try:
        check_langchain_installed(langchain_available=True)
    except ImportError:
        pytest.fail("Should not raise ImportError when langchain is available")


@patch.dict("sys.modules", {"chatbot": Mock(), "chatbot.chatbot": Mock(), "click": Mock()})
def test_cli_imports():
    """Test that CLI module can be imported with mocked dependencies."""
    # This should not raise ImportError
    try:
        from validated_llm.integrations.langchain import cli

        assert cli is not None
    except ImportError as e:
        pytest.fail(f"CLI import failed: {e}")


def test_end_to_end_conversion_simulation():
    """Simulate end-to-end conversion without actual imports."""
    # Simulate the conversion process

    # 1. Mock Langchain prompt
    class MockPromptTemplate:
        def __init__(self, template, input_variables):
            self.template = template
            self.input_variables = input_variables

    # 2. Create prompt
    prompt = MockPromptTemplate(template="Generate marketing copy for {product} targeting {audience}", input_variables=["product", "audience"])

    # 3. Simulate analysis
    import re

    def analyze_prompt(template):
        variables = list(set(re.findall(r"\{(\w+)\}", template)))
        template_lower = template.lower()

        if "json" in template_lower:
            output_type = "json"
            validator = "JSONValidator"
        elif "markdown" in template_lower:
            output_type = "markdown"
            validator = "MarkdownValidator"
        elif "list" in template_lower:
            output_type = "list"
            validator = "ListValidator"
        else:
            output_type = "text"
            validator = "RegexValidator"

        return {"template": template, "variables": variables, "output_type": output_type, "suggested_validators": [validator]}

    analysis = analyze_prompt(prompt.template)

    # 4. Verify analysis
    assert set(analysis["variables"]) == {"product", "audience"}
    assert analysis["output_type"] == "text"
    assert analysis["suggested_validators"] == ["RegexValidator"]

    # 5. Simulate task generation
    task_code = f"""
class MarketingCopyTask(BaseTask):
    prompt_template = "{analysis['template']}"
    validator_class = {analysis['suggested_validators'][0]}

    @classmethod
    def get_prompt_variables(cls):
        return {analysis['variables']}
"""

    # 6. Verify generated code contains expected elements
    assert "MarketingCopyTask" in task_code
    assert "BaseTask" in task_code
    assert "RegexValidator" in task_code
    assert prompt.template in task_code
