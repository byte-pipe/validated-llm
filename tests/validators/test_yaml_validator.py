"""
Tests for YAMLValidator.
"""

import pytest

from validated_llm.validators.yaml import YAMLValidator


class TestYAMLValidator:
    """Test YAMLValidator functionality."""

    def test_valid_yaml_basic(self):
        """Test validation of basic valid YAML."""
        validator = YAMLValidator()
        yaml_content = """
name: John Doe
age: 30
active: true
"""

        result = validator.validate(yaml_content)

        assert result.is_valid
        assert len(result.errors) == 0
        assert result.metadata["parsed_data"] == {"name": "John Doe", "age": 30, "active": True}
        assert result.metadata["root_type"] == "dict"

    def test_invalid_yaml_syntax(self):
        """Test validation of YAML with syntax errors."""
        validator = YAMLValidator()

        # Invalid indentation
        result = validator.validate(
            """
name: John
  age: 30
    active: true
"""
        )
        assert not result.is_valid
        assert "YAML syntax error" in result.errors[0]

        # Unclosed quote
        result = validator.validate(
            """
name: "John Doe
age: 30
"""
        )
        assert not result.is_valid

    def test_yaml_lists(self):
        """Test validation of YAML lists."""
        validator = YAMLValidator()
        yaml_content = """
fruits:
  - apple
  - banana
  - orange
numbers: [1, 2, 3, 4, 5]
"""

        result = validator.validate(yaml_content)

        assert result.is_valid
        data = result.metadata["parsed_data"]
        assert data["fruits"] == ["apple", "banana", "orange"]
        assert data["numbers"] == [1, 2, 3, 4, 5]

    def test_required_keys(self):
        """Test validation with required keys."""
        validator = YAMLValidator(required_keys=["name", "email", "age"])

        # All required keys present
        result = validator.validate(
            """
name: John Doe
email: john@example.com
age: 30
city: New York
"""
        )
        assert result.is_valid

        # Missing required key
        result = validator.validate(
            """
name: John Doe
email: john@example.com
"""
        )
        assert not result.is_valid
        assert "Missing required keys: age" in result.errors[0]

    def test_type_constraints(self):
        """Test validation with type constraints."""
        validator = YAMLValidator(type_constraints={"name": str, "age": int, "scores": list, "active": bool})

        # Correct types
        result = validator.validate(
            """
name: John Doe
age: 30
scores: [85, 90, 78]
active: true
"""
        )
        assert result.is_valid

        # Wrong types
        result = validator.validate(
            """
name: 123
age: "thirty"
scores: "not a list"
active: "yes"
"""
        )
        assert not result.is_valid
        # Should have 4 type errors
        assert len(result.errors) == 4

    def test_nested_yaml_structure(self):
        """Test validation of nested YAML structures."""
        validator = YAMLValidator(allow_duplicate_keys=True)
        yaml_content = """
company:
  name: Tech Corp
  employees:
    - name: John Doe
      position: Developer
      skills:
        - Python
        - JavaScript
    - name: Jane Smith
      position: Designer
      skills:
        - Photoshop
        - Illustrator
"""

        result = validator.validate(yaml_content)

        assert result.is_valid
        data = result.metadata["parsed_data"]
        assert len(data["company"]["employees"]) == 2
        assert data["company"]["employees"][0]["skills"][0] == "Python"

    def test_yaml_anchors_and_aliases(self):
        """Test YAML with anchors and aliases."""
        validator = YAMLValidator(allow_duplicate_keys=True)
        yaml_content = """
defaults: &defaults
  timeout: 30
  retries: 3

development:
  <<: *defaults
  debug: true

production:
  <<: *defaults
  debug: false
"""

        result = validator.validate(yaml_content)

        assert result.is_valid
        data = result.metadata["parsed_data"]
        assert data["development"]["timeout"] == 30
        assert data["production"]["retries"] == 3
        assert data["development"]["debug"] is True
        assert data["production"]["debug"] is False

    def test_max_depth_validation(self):
        """Test validation with maximum depth constraint."""
        validator = YAMLValidator(max_depth=3)  # Changed from 2 to 3 for the test data

        # Within depth limit
        result = validator.validate(
            """
level1:
  level2:
    value: test
"""
        )
        assert result.is_valid
        assert len(result.warnings) == 0

        # Exceeds depth limit
        result = validator.validate(
            """
level1:
  level2:
    level3:
      level4:
        value: too deep
"""
        )
        assert result.is_valid  # Still valid, but with warning
        assert len(result.warnings) == 1
        assert "exceeds maximum" in result.warnings[0]
        assert result.metadata["max_depth"] == 5  # This has 5 levels of nesting

    def test_duplicate_keys_detection(self):
        """Test detection of duplicate keys."""
        validator = YAMLValidator(allow_duplicate_keys=False)

        # YAML with duplicate keys
        yaml_content = """
name: John
age: 30
name: Jane
email: jane@example.com
"""

        result = validator.validate(yaml_content)

        # Should detect the duplicate 'name' key
        assert not result.is_valid
        assert any("Duplicate key 'name'" in error for error in result.errors)

    def test_non_dict_root(self):
        """Test validation when root is not a dictionary."""
        # When no required keys, any valid YAML is accepted
        validator = YAMLValidator()

        # List at root
        result = validator.validate("- item1\n- item2\n- item3")
        assert result.is_valid
        assert result.metadata["root_type"] == "list"
        assert result.metadata["length"] == 3

        # Scalar at root
        result = validator.validate("just a string")
        assert result.is_valid
        assert result.metadata["root_type"] == "str"

        # But with required keys, must be a dict
        validator = YAMLValidator(required_keys=["name"])
        result = validator.validate("- item1\n- item2")
        assert not result.is_valid
        assert "Expected YAML object/mapping" in result.errors[0]

    def test_strict_vs_non_strict_mode(self):
        """Test difference between strict and non-strict modes."""
        yaml_content = """
name: John Doe
age: 30
"""

        # Strict mode - missing required key is an error
        validator_strict = YAMLValidator(required_keys=["name", "email"], strict_mode=True)
        result = validator_strict.validate(yaml_content)
        assert not result.is_valid
        assert len(result.errors) == 1

        # Non-strict mode - missing required key is a warning
        validator_lenient = YAMLValidator(required_keys=["name", "email"], strict_mode=False)
        result = validator_lenient.validate(yaml_content)
        assert result.is_valid
        assert len(result.warnings) == 1

    def test_validator_description(self):
        """Test that validator provides helpful description."""
        # Basic validator
        validator = YAMLValidator()
        description = validator.get_validator_description()
        assert "YAML Validator" in description
        assert "valid YAML" in description

        # With constraints
        validator = YAMLValidator(required_keys=["name", "age"], type_constraints={"age": int}, max_depth=3)
        description = validator.get_validator_description()
        assert "Required keys" in description
        assert "name, age" in description
        assert "Type constraints" in description
        assert "age: int" in description
        assert "Maximum nesting depth: 3" in description
