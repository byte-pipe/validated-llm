"""
Simple tests for Langchain integration converter that don't require full imports.
"""

import os
import sys
from unittest.mock import Mock, patch

import pytest

# Add the specific module path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../src"))


class TestPromptTemplateConverterSimple:
    """Test the PromptTemplateConverter class without full imports."""

    def test_analyze_prompt_json_detection(self):
        """Test that JSON prompts are correctly detected."""
        # Import just what we need
        with patch.dict(
            "sys.modules",
            {
                "validated_llm.integrations.langchain": Mock(LANGCHAIN_AVAILABLE=True),
                "validated_llm.base_validator": Mock(),
                "validated_llm.tasks": Mock(),
                "validated_llm.validators": Mock(),
                "chatbot": Mock(),
                "chatbot.chatbot": Mock(),
            },
        ):
            from validated_llm.integrations.langchain.converter import PromptTemplateConverter

            converter = PromptTemplateConverter()

            template = "Generate a JSON object with name and age for {person}"
            analysis = converter.analyze_prompt(template)

            assert analysis["output_type"] == "json"
            assert "JSONValidator" in analysis["suggested_validators"]
            assert analysis["variables"] == ["person"]

    def test_extract_variables(self):
        """Test variable extraction from templates."""
        with patch.dict(
            "sys.modules",
            {
                "validated_llm.integrations.langchain": Mock(LANGCHAIN_AVAILABLE=True),
                "validated_llm.base_validator": Mock(),
                "validated_llm.tasks": Mock(),
                "validated_llm.validators": Mock(),
                "chatbot": Mock(),
                "chatbot.chatbot": Mock(),
            },
        ):
            from validated_llm.integrations.langchain.converter import PromptTemplateConverter

            converter = PromptTemplateConverter()

            template = "Generate a {format} report about {topic} for {audience}"
            variables = converter._extract_variables(template)

            assert set(variables) == {"format", "topic", "audience"}

    def test_parser_mapper_initialization(self):
        """Test that parser map is properly initialized."""
        with patch.dict("sys.modules", {"validated_llm.base_validator": Mock(), "validated_llm.validators": Mock(DateTimeValidator=Mock(), EmailValidator=Mock(), RegexValidator=Mock())}):
            from validated_llm.integrations.langchain.parser_mapping import OutputParserMapper

            mapper = OutputParserMapper()
            assert "PydanticOutputParser" in mapper.parser_map
            assert "DatetimeOutputParser" in mapper.parser_map
            assert "OutputFixingParser" in mapper.parser_map

    def test_list_validator_basic(self):
        """Test basic list validator functionality."""

        # Create a mock ValidationResult class
        class MockValidationResult:
            def __init__(self, is_valid, errors, warnings, metadata=None):
                self.is_valid = is_valid
                self.errors = errors
                self.warnings = warnings
                self.metadata = metadata or {}

        # Create a mock BaseValidator
        class MockBaseValidator:
            def __init__(self):
                pass

        with patch.dict("sys.modules", {"validated_llm.base_validator": Mock(BaseValidator=MockBaseValidator, ValidationResult=MockValidationResult), "validated_llm.validators": Mock()}):
            from validated_llm.integrations.langchain.parser_mapping import OutputParserMapper

            mapper = OutputParserMapper()
            ListValidator = mapper._create_list_validator()

            validator = ListValidator()

            # Test valid list
            valid_output = "- Item 1\n- Item 2\n- Item 3"
            result = validator.validate(valid_output)
            assert result.is_valid
            assert result.metadata["items"] == ["Item 1", "Item 2", "Item 3"]
