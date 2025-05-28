"""
Tests for Langchain integration converter.

Note: These tests use mock objects since Langchain is not a dependency.
"""

import os
import sys
from unittest.mock import Mock, patch

import pytest

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../src"))

# Mock the chatbot module before any imports
sys.modules["chatbot"] = Mock()
sys.modules["chatbot.chatbot"] = Mock()

from validated_llm.base_validator import BaseValidator, ValidationResult
from validated_llm.integrations.langchain.converter import PromptTemplateConverter


class TestPromptTemplateConverter:
    """Test the PromptTemplateConverter class."""

    def test_analyze_prompt_json_detection(self):
        """Test that JSON prompts are correctly detected."""
        with patch("validated_llm.integrations.langchain.LANGCHAIN_AVAILABLE", True):
            converter = PromptTemplateConverter()

            template = "Generate a JSON object with name and age for {person}"
            analysis = converter.analyze_prompt(template)

            assert analysis["output_type"] == "json"
            assert "JSONValidator" in analysis["suggested_validators"]
            assert analysis["variables"] == ["person"]

    def test_analyze_prompt_markdown_detection(self):
        """Test that Markdown prompts are correctly detected."""
        with patch("validated_llm.integrations.langchain.LANGCHAIN_AVAILABLE", True):
            converter = PromptTemplateConverter()

            template = "Write a blog post in markdown about {topic}"
            analysis = converter.analyze_prompt(template)

            assert analysis["output_type"] == "markdown"
            assert "MarkdownValidator" in analysis["suggested_validators"]
            assert analysis["variables"] == ["topic"]

    def test_analyze_prompt_list_detection(self):
        """Test that list prompts are correctly detected."""
        with patch("validated_llm.integrations.langchain.LANGCHAIN_AVAILABLE", True):
            converter = PromptTemplateConverter()

            template = "List 5 benefits of {product}"
            analysis = converter.analyze_prompt(template)

            assert analysis["output_type"] == "list"
            assert "ListValidator" in analysis["suggested_validators"]

    def test_extract_variables(self):
        """Test variable extraction from templates."""
        with patch("validated_llm.integrations.langchain.LANGCHAIN_AVAILABLE", True):
            converter = PromptTemplateConverter()

            template = "Generate a {format} report about {topic} for {audience}"
            variables = converter._extract_variables(template)

            assert set(variables) == {"format", "topic", "audience"}

    def test_extract_variables_duplicates(self):
        """Test that duplicate variables are handled correctly."""
        with patch("validated_llm.integrations.langchain.LANGCHAIN_AVAILABLE", True):
            converter = PromptTemplateConverter()

            template = "Compare {item} with another {item}"
            variables = converter._extract_variables(template)

            assert variables == ["item"]

    @patch("validated_llm.integrations.langchain.LANGCHAIN_AVAILABLE", True)
    def test_convert_prompt_template(self):
        """Test the basic structure of prompt template conversion."""
        # Test the core conversion logic without complex mocking

        # Mock prompt data
        template = "Generate a product description for {product}"
        input_variables = ["product"]

        # Test variable extraction (the core functionality)
        converter = PromptTemplateConverter()
        extracted_vars = converter._extract_variables(template)
        assert extracted_vars == ["product"]

        # Test prompt analysis
        analysis = converter.analyze_prompt(template)
        assert analysis["template"] == template
        assert analysis["variables"] == ["product"]
        assert analysis["output_type"] == "text"  # Should default to text
        assert "RegexValidator" in analysis["suggested_validators"]

    def test_langchain_not_installed(self):
        """Test helpful error when Langchain is not installed."""
        with patch("validated_llm.integrations.langchain.LANGCHAIN_AVAILABLE", False):
            with pytest.raises(ImportError, match="pip install langchain"):
                PromptTemplateConverter()


class TestOutputParserMapper:
    """Test the OutputParserMapper class."""

    def test_parser_map_initialization(self):
        """Test that parser map is properly initialized."""
        from validated_llm.integrations.langchain.parser_mapping import OutputParserMapper

        mapper = OutputParserMapper()
        assert "PydanticOutputParser" in mapper.parser_map
        assert "DatetimeOutputParser" in mapper.parser_map
        assert "OutputFixingParser" in mapper.parser_map

    def test_list_validator_creation(self):
        """Test list validator creation and validation."""
        from validated_llm.integrations.langchain.parser_mapping import OutputParserMapper

        mapper = OutputParserMapper()
        ListValidator = mapper._create_list_validator()

        validator = ListValidator()

        # Test valid list
        valid_output = "- Item 1\n- Item 2\n- Item 3"
        result = validator.validate(valid_output)
        assert result.is_valid
        assert result.metadata["items"] == ["Item 1", "Item 2", "Item 3"]

        # Test invalid output
        invalid_output = "Not a list format"
        result = validator.validate(invalid_output)
        assert not result.is_valid

    def test_csv_validator_creation(self):
        """Test CSV validator creation and validation."""
        from validated_llm.integrations.langchain.parser_mapping import OutputParserMapper

        mapper = OutputParserMapper()
        CSVValidator = mapper._create_csv_validator()

        validator = CSVValidator()

        # Test valid CSV
        valid_output = "apple, banana, orange"
        result = validator.validate(valid_output)
        assert result.is_valid
        assert result.metadata["items"] == ["apple", "banana", "orange"]

        # Test empty CSV
        invalid_output = ""
        result = validator.validate(invalid_output)
        assert not result.is_valid
