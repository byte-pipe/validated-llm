"""
Tests for JSONSchemaValidator.
"""

import pytest

from validated_llm.validators.json_schema import JSONSchemaValidator


class TestJSONSchemaValidator:
    """Test JSONSchemaValidator functionality."""

    def test_valid_json_simple_schema(self):
        """Test validation of valid JSON against a simple schema."""
        schema = {"type": "object", "properties": {"name": {"type": "string"}, "age": {"type": "integer"}}, "required": ["name", "age"]}

        validator = JSONSchemaValidator(schema)
        result = validator.validate('{"name": "John Doe", "age": 30}')

        assert result.is_valid
        assert len(result.errors) == 0
        assert result.metadata["validated_data"] == {"name": "John Doe", "age": 30}

    def test_invalid_json_syntax(self):
        """Test validation of invalid JSON syntax."""
        schema = {"type": "object"}
        validator = JSONSchemaValidator(schema)

        result = validator.validate('{"name": "John", "age":}')

        assert not result.is_valid
        assert len(result.errors) == 1
        assert "Invalid JSON" in result.errors[0]

    def test_missing_required_field(self):
        """Test validation when required field is missing."""
        schema = {"type": "object", "properties": {"name": {"type": "string"}, "email": {"type": "string"}}, "required": ["name", "email"]}

        validator = JSONSchemaValidator(schema)
        result = validator.validate('{"name": "John"}')

        assert not result.is_valid
        assert len(result.errors) == 1
        assert "email" in result.errors[0]
        assert "required" in result.errors[0].lower()

    def test_type_mismatch(self):
        """Test validation when field has wrong type."""
        schema = {"type": "object", "properties": {"count": {"type": "integer"}, "active": {"type": "boolean"}}}

        validator = JSONSchemaValidator(schema)
        result = validator.validate('{"count": "five", "active": "yes"}')

        assert not result.is_valid
        assert len(result.errors) == 2
        # Check that both type errors are reported
        error_messages = " ".join(result.errors)
        assert "count" in error_messages
        assert "active" in error_messages

    def test_nested_object_validation(self):
        """Test validation of nested objects."""
        schema = {
            "type": "object",
            "properties": {
                "user": {
                    "type": "object",
                    "properties": {"name": {"type": "string"}, "contact": {"type": "object", "properties": {"email": {"type": "string", "format": "email"}, "phone": {"type": "string"}}, "required": ["email"]}},
                    "required": ["name", "contact"],
                }
            },
            "required": ["user"],
        }

        validator = JSONSchemaValidator(schema)

        # Valid nested object
        valid_json = """
        {
            "user": {
                "name": "John Doe",
                "contact": {
                    "email": "john@example.com",
                    "phone": "+1234567890"
                }
            }
        }
        """
        result = validator.validate(valid_json)
        assert result.is_valid

        # Missing nested required field
        invalid_json = """
        {
            "user": {
                "name": "John Doe",
                "contact": {
                    "phone": "+1234567890"
                }
            }
        }
        """
        result = validator.validate(invalid_json)
        assert not result.is_valid
        assert "email" in result.errors[0]

    def test_array_validation(self):
        """Test validation of arrays."""
        schema = {"type": "object", "properties": {"tags": {"type": "array", "items": {"type": "string"}, "minItems": 1, "maxItems": 5}}}

        validator = JSONSchemaValidator(schema)

        # Valid array
        result = validator.validate('{"tags": ["python", "json", "validation"]}')
        assert result.is_valid

        # Empty array (violates minItems)
        result = validator.validate('{"tags": []}')
        assert not result.is_valid

        # Array with wrong type
        result = validator.validate('{"tags": ["valid", 123, "string"]}')
        assert not result.is_valid

    def test_format_validation(self):
        """Test format validation (email, uri, etc.)."""
        schema = {"type": "object", "properties": {"email": {"type": "string", "format": "email"}, "website": {"type": "string", "format": "uri"}, "birthdate": {"type": "string", "format": "date"}}}

        validator = JSONSchemaValidator(schema, format_checker=True)

        # Valid formats
        valid_json = """
        {
            "email": "user@example.com",
            "website": "https://example.com",
            "birthdate": "1990-01-01"
        }
        """
        result = validator.validate(valid_json)
        assert result.is_valid

        # Invalid email format
        invalid_json = """
        {
            "email": "not-an-email",
            "website": "https://example.com",
            "birthdate": "1990-01-01"
        }
        """
        result = validator.validate(invalid_json)
        assert not result.is_valid
        assert "email" in str(result.errors)

    def test_strict_mode_vs_non_strict(self):
        """Test behavior difference between strict and non-strict modes."""
        schema = {"type": "object", "properties": {"name": {"type": "string"}}, "additionalProperties": False}

        json_with_extra = '{"name": "John", "extra": "field"}'

        # Strict mode - additional properties are errors
        validator_strict = JSONSchemaValidator(schema, strict_mode=True)
        result = validator_strict.validate(json_with_extra)
        assert not result.is_valid
        assert len(result.errors) > 0

        # Non-strict mode - additional properties are warnings
        validator_lenient = JSONSchemaValidator(schema, strict_mode=False)
        result = validator_lenient.validate(json_with_extra)
        assert result.is_valid  # Still valid in non-strict mode
        assert len(result.warnings) > 0

    def test_validator_description(self):
        """Test that validator provides helpful description."""
        schema = {"type": "object", "properties": {"id": {"type": "integer"}, "name": {"type": "string"}}, "required": ["id"]}

        validator = JSONSchemaValidator(schema)
        description = validator.get_validator_description()

        assert "JSON Schema Validator" in description
        assert '"type": "object"' in description
        assert '"required"' in description
        assert '"id"' in description
