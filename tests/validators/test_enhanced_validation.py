"""
Comprehensive test suite for enhanced validation features.
Tests the enhanced error messaging system and validation feedback.
"""

import json
from typing import Any, Dict

import pytest

from validated_llm.enhanced_validation import EnhancedValidationResult, ErrorCategory, ErrorMessageEnhancer, ErrorSeverity, ValidationError
from validated_llm.validators.enhanced_json_schema import EnhancedJSONSchemaValidator
from validated_llm.validators.enhanced_range import EnhancedRangeValidator


class TestValidationError:
    """Test ValidationError data structure and functionality."""

    def test_validation_error_creation(self):
        """Test creating ValidationError with all fields."""
        error = ValidationError(
            message="Test error message",
            category=ErrorCategory.SYNTAX,
            severity=ErrorSeverity.HIGH,
            location="line 5",
            suggestion="Fix the syntax error",
            example='{"valid": "json"}',
            code="SYNTAX_001",
            context={"key": "value"},
            fix_actions=["Step 1", "Step 2"],
        )

        assert error.message == "Test error message"
        assert error.category == ErrorCategory.SYNTAX
        assert error.severity == ErrorSeverity.HIGH
        assert error.location == "line 5"
        assert error.suggestion == "Fix the syntax error"
        assert error.example == '{"valid": "json"}'
        assert error.code == "SYNTAX_001"
        assert error.context == {"key": "value"}
        assert error.fix_actions == ["Step 1", "Step 2"]

    def test_validation_error_minimal(self):
        """Test creating ValidationError with minimal required fields."""
        error = ValidationError(message="Minimal error", category=ErrorCategory.CONTENT)

        assert error.message == "Minimal error"
        assert error.category == ErrorCategory.CONTENT
        assert error.severity == ErrorSeverity.HIGH  # default
        assert error.location is None
        assert error.suggestion is None
        assert error.example is None
        assert error.code is None
        assert error.context is None
        assert error.fix_actions == []


class TestEnhancedValidationResult:
    """Test EnhancedValidationResult functionality."""

    def test_enhanced_validation_result_success(self):
        """Test successful validation result."""
        result = EnhancedValidationResult(is_valid=True, errors=[], warnings=[], metadata={"source": "test"})

        assert result.is_valid is True
        assert result.errors == []
        assert result.warnings == []
        assert result.metadata == {"source": "test"}

    def test_enhanced_validation_result_with_errors(self):
        """Test validation result with errors and warnings."""
        errors = [ValidationError("Critical error", ErrorCategory.SYNTAX, ErrorSeverity.CRITICAL), ValidationError("High error", ErrorCategory.SCHEMA, ErrorSeverity.HIGH)]
        warnings = [ValidationError("Warning message", ErrorCategory.FORMAT, ErrorSeverity.LOW)]

        result = EnhancedValidationResult(is_valid=False, errors=errors, warnings=warnings, metadata={"error_count": 2})

        assert result.is_valid is False
        assert len(result.errors) == 2
        assert len(result.warnings) == 1
        assert result.errors[0].severity == ErrorSeverity.CRITICAL
        assert result.warnings[0].severity == ErrorSeverity.LOW

    def test_get_errors_by_category(self):
        """Test filtering errors by category."""
        errors = [ValidationError("Syntax error", ErrorCategory.SYNTAX), ValidationError("Schema error", ErrorCategory.SCHEMA), ValidationError("Another syntax error", ErrorCategory.SYNTAX)]

        result = EnhancedValidationResult(is_valid=False, errors=errors)

        syntax_errors = result.get_errors_by_category(ErrorCategory.SYNTAX)
        assert len(syntax_errors) == 2
        assert all(e.category == ErrorCategory.SYNTAX for e in syntax_errors)

        schema_errors = result.get_errors_by_category(ErrorCategory.SCHEMA)
        assert len(schema_errors) == 1
        assert schema_errors[0].category == ErrorCategory.SCHEMA

    def test_get_errors_by_severity(self):
        """Test filtering errors by severity."""
        errors = [
            ValidationError("Critical", ErrorCategory.SYNTAX, ErrorSeverity.CRITICAL),
            ValidationError("High", ErrorCategory.SCHEMA, ErrorSeverity.HIGH),
            ValidationError("Medium", ErrorCategory.FORMAT, ErrorSeverity.MEDIUM),
            ValidationError("Another critical", ErrorCategory.LOGIC, ErrorSeverity.CRITICAL),
        ]

        result = EnhancedValidationResult(is_valid=False, errors=errors)

        critical_errors = result.get_errors_by_severity(ErrorSeverity.CRITICAL)
        assert len(critical_errors) == 2
        assert all(e.severity == ErrorSeverity.CRITICAL for e in critical_errors)


class TestErrorMessageEnhancer:
    """Test ErrorMessageEnhancer utility functions."""

    def test_enhance_json_syntax_error(self):
        """Test JSON syntax error enhancement."""
        error = ErrorMessageEnhancer.enhance_json_error("Expecting ',' delimiter", '{"test":}')

        assert error.category == ErrorCategory.SYNTAX
        assert error.severity == ErrorSeverity.HIGH
        assert "JSON" in error.message
        assert error.suggestion is not None
        assert len(error.fix_actions) > 0

    def test_enhance_schema_validation_error(self):
        """Test schema validation error enhancement."""
        error = ErrorMessageEnhancer.enhance_schema_error("$.user", "Required field 'name' is missing")

        assert error.category == ErrorCategory.SCHEMA
        assert error.severity == ErrorSeverity.CRITICAL
        assert "$.user" in error.message  # Field path is in the message
        assert error.location == "$.user"
        assert error.suggestion is not None
        assert len(error.fix_actions) > 0

    def test_enhance_range_error(self):
        """Test range validation error enhancement."""
        error = ErrorMessageEnhancer.enhance_range_error(150, 0, 100)

        assert error.category == ErrorCategory.RANGE
        assert error.severity == ErrorSeverity.MEDIUM
        assert "150" in error.message
        assert "0" in error.message
        assert "100" in error.message
        assert error.suggestion is not None
        assert len(error.fix_actions) > 0


class TestEnhancedJSONSchemaValidator:
    """Test EnhancedJSONSchemaValidator functionality."""

    def test_valid_json_validation(self):
        """Test validation of valid JSON against schema."""
        schema = {"type": "object", "properties": {"name": {"type": "string"}, "age": {"type": "integer", "minimum": 0}}, "required": ["name"]}

        validator = EnhancedJSONSchemaValidator(schema)
        result = validator.validate('{"name": "John", "age": 30}')

        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_invalid_json_syntax(self):
        """Test validation of invalid JSON syntax."""
        schema = {"type": "object"}
        validator = EnhancedJSONSchemaValidator(schema)

        result = validator.validate('{"name": "John", "age":}')

        assert result.is_valid is False
        assert len(result.errors) > 0

        # Check that enhanced error information is in metadata
        assert "enhanced_errors" in result.metadata
        enhanced_errors = result.metadata["enhanced_errors"]
        assert len(enhanced_errors) > 0

        # Find syntax error
        syntax_error = next((e for e in enhanced_errors if e["category"] == "syntax"), None)
        assert syntax_error is not None
        assert syntax_error["suggestion"] is not None
        assert len(syntax_error["fix_actions"]) > 0

    def test_schema_validation_failure(self):
        """Test validation failure against schema requirements."""
        schema = {"type": "object", "properties": {"name": {"type": "string"}, "age": {"type": "integer", "minimum": 0}}, "required": ["name", "age"]}

        validator = EnhancedJSONSchemaValidator(schema)
        result = validator.validate('{"name": "John"}')  # missing required 'age'

        assert result.is_valid is False
        assert len(result.errors) > 0

        # Check enhanced errors in metadata
        enhanced_errors = result.metadata["enhanced_errors"]
        schema_error = next((e for e in enhanced_errors if e["category"] == "schema"), None)
        assert schema_error is not None
        assert "required" in schema_error["message"].lower() or "missing" in schema_error["message"].lower()
        assert schema_error["suggestion"] is not None

    def test_type_validation_error(self):
        """Test type validation error with enhanced feedback."""
        schema = {"type": "object", "properties": {"age": {"type": "integer"}}}

        validator = EnhancedJSONSchemaValidator(schema)
        result = validator.validate('{"age": "thirty"}')  # string instead of integer

        assert result.is_valid is False
        assert len(result.errors) > 0

        # Check enhanced errors in metadata
        enhanced_errors = result.metadata["enhanced_errors"]
        type_error = enhanced_errors[0]
        assert "integer" in type_error["message"] or "type" in type_error["message"]
        assert type_error["suggestion"] is not None


class TestEnhancedRangeValidator:
    """Test EnhancedRangeValidator functionality."""

    def test_valid_range_validation(self):
        """Test validation of value within range."""
        validator = EnhancedRangeValidator(min_value=0, max_value=100)
        result = validator.validate("50")

        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_value_below_minimum(self):
        """Test validation of value below minimum with enhanced error."""
        validator = EnhancedRangeValidator(min_value=10, max_value=100)
        result = validator.validate("5")

        assert result.is_valid is False
        assert len(result.errors) == 1

        # Check enhanced errors in metadata
        enhanced_errors = result.metadata["enhanced_errors"]
        error = enhanced_errors[0]
        assert error["category"] == "range"
        assert error["severity"] == "medium"
        assert "5" in error["message"]
        assert "10" in error["message"]
        assert error["suggestion"] is not None
        assert len(error["fix_actions"]) > 0

    def test_value_above_maximum(self):
        """Test validation of value above maximum with enhanced error."""
        validator = EnhancedRangeValidator(min_value=0, max_value=50)
        result = validator.validate("75")

        assert result.is_valid is False
        assert len(result.errors) == 1

        # Check enhanced errors in metadata
        enhanced_errors = result.metadata["enhanced_errors"]
        error = enhanced_errors[0]
        assert error["category"] == "range"
        assert "75" in error["message"]
        assert "50" in error["message"]
        assert error["suggestion"] is not None

    def test_non_numeric_value(self):
        """Test validation of non-numeric value with enhanced error."""
        validator = EnhancedRangeValidator(min_value=0, max_value=100)
        result = validator.validate("not_a_number")

        assert result.is_valid is False
        assert len(result.errors) == 1

        # Check enhanced errors in metadata
        enhanced_errors = result.metadata["enhanced_errors"]
        error = enhanced_errors[0]
        assert error["category"] == "format"
        assert "parse" in error["message"].lower() or "number" in error["message"].lower()
        assert error["suggestion"] is not None


class TestEnhancedValidationIntegration:
    """Integration tests for enhanced validation system."""

    def test_backward_compatibility(self):
        """Test that enhanced validators maintain backward compatibility."""
        # Test that enhanced validators return standard ValidationResult
        schema = {"type": "string"}
        validator = EnhancedJSONSchemaValidator(schema)
        result = validator.validate('"valid string"')

        # Should have basic ValidationResult interface
        assert hasattr(result, "is_valid")
        assert hasattr(result, "errors")
        assert hasattr(result, "warnings")
        assert hasattr(result, "metadata")

        # Enhanced error information should be in metadata
        assert "enhanced_validation" in result.metadata
        assert result.metadata["enhanced_validation"] is True
        assert "enhanced_errors" in result.metadata
        assert "enhanced_warnings" in result.metadata

    def test_complex_validation_scenario(self):
        """Test complex validation scenario with multiple error types."""
        schema = {
            "type": "object",
            "properties": {"name": {"type": "string", "minLength": 2}, "age": {"type": "integer", "minimum": 0, "maximum": 150}, "email": {"type": "string", "format": "email"}},
            "required": ["name", "age", "email"],
        }

        validator = EnhancedJSONSchemaValidator(schema)

        # Invalid JSON with multiple issues
        invalid_json = '{"name": "A", "age": 200, "email": "invalid"}'
        result = validator.validate(invalid_json)

        assert result.is_valid is False
        assert len(result.errors) > 0

        # Check enhanced errors in metadata
        enhanced_errors = result.metadata["enhanced_errors"]
        assert len(enhanced_errors) > 0

        # Should have multiple categories of errors
        categories = {error["category"] for error in enhanced_errors}
        assert len(categories) >= 1  # At least one type of validation error

        # All enhanced errors should have helpful information
        for error in enhanced_errors:
            assert error["message"] is not None
            assert error["category"] is not None
            assert error["severity"] is not None
