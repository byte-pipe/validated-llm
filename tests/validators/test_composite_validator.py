"""Tests for CompositeValidator and ValidationChain."""

from typing import Any, Dict, Optional
from unittest.mock import Mock

import pytest

from src.validated_llm.base_validator import ValidationResult
from src.validated_llm.validators.composite import CompositeValidator, LogicOperator, ValidationChain


class MockValidator:
    """Mock validator for testing."""

    def __init__(self, is_valid: bool, errors: list = None, warnings: list = None, metadata: dict = None, description: str = "Mock validator"):
        self.result = ValidationResult(is_valid=is_valid, errors=errors or [], warnings=warnings or [], metadata=metadata or {})
        self.description = description
        self.validate_calls = 0

    def validate(self, output: str, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        self.validate_calls += 1
        return self.result

    def get_description(self) -> str:
        return self.description


class TestCompositeValidator:
    """Test cases for CompositeValidator."""

    def test_and_all_valid(self):
        """Test AND operation with all validators passing."""
        validator1 = MockValidator(True, description="Validator 1")
        validator2 = MockValidator(True, description="Validator 2")

        composite = CompositeValidator([validator1, validator2], LogicOperator.AND)
        result = composite.validate("test content")

        assert result.is_valid
        assert len(result.errors) == 0
        assert len(result.warnings) == 0
        assert validator1.validate_calls == 1
        assert validator2.validate_calls == 1

    def test_and_one_invalid(self):
        """Test AND operation with one validator failing."""
        validator1 = MockValidator(True, description="Validator 1")
        validator2 = MockValidator(False, errors=["Error from validator 2"], description="Validator 2")

        composite = CompositeValidator([validator1, validator2], LogicOperator.AND)
        result = composite.validate("test content")

        assert not result.is_valid
        assert "Validator 2: Error from validator 2" in result.errors
        assert validator1.validate_calls == 1
        assert validator2.validate_calls == 1

    def test_and_short_circuit(self):
        """Test AND operation with short-circuit enabled."""
        validator1 = MockValidator(False, errors=["Error from validator 1"], description="Validator 1")
        validator2 = MockValidator(True, description="Validator 2")

        composite = CompositeValidator([validator1, validator2], LogicOperator.AND, short_circuit=True)
        result = composite.validate("test content")

        assert not result.is_valid
        assert "Validator 1: Error from validator 1" in result.errors
        assert validator1.validate_calls == 1
        assert validator2.validate_calls == 0  # Should not be called due to short-circuit

    def test_and_no_short_circuit(self):
        """Test AND operation with short-circuit disabled."""
        validator1 = MockValidator(False, errors=["Error from validator 1"], description="Validator 1")
        validator2 = MockValidator(False, errors=["Error from validator 2"], description="Validator 2")

        composite = CompositeValidator([validator1, validator2], LogicOperator.AND, short_circuit=False)
        result = composite.validate("test content")

        assert not result.is_valid
        assert "Validator 1: Error from validator 1" in result.errors
        assert "Validator 2: Error from validator 2" in result.errors
        assert validator1.validate_calls == 1
        assert validator2.validate_calls == 1

    def test_or_one_valid(self):
        """Test OR operation with one validator passing."""
        validator1 = MockValidator(False, errors=["Error from validator 1"], description="Validator 1")
        validator2 = MockValidator(True, description="Validator 2")

        composite = CompositeValidator([validator1, validator2], LogicOperator.OR)
        result = composite.validate("test content")

        assert result.is_valid
        assert validator1.validate_calls == 1
        assert validator2.validate_calls == 1

    def test_or_all_invalid(self):
        """Test OR operation with all validators failing."""
        validator1 = MockValidator(False, errors=["Error from validator 1"], description="Validator 1")
        validator2 = MockValidator(False, errors=["Error from validator 2"], description="Validator 2")

        composite = CompositeValidator([validator1, validator2], LogicOperator.OR)
        result = composite.validate("test content")

        assert not result.is_valid
        assert "Validator 1: Error from validator 1" in result.errors
        assert "Validator 2: Error from validator 2" in result.errors
        assert validator1.validate_calls == 1
        assert validator2.validate_calls == 1

    def test_or_short_circuit(self):
        """Test OR operation with short-circuit enabled."""
        validator1 = MockValidator(True, description="Validator 1")
        validator2 = MockValidator(False, errors=["Error from validator 2"], description="Validator 2")

        composite = CompositeValidator([validator1, validator2], LogicOperator.OR, short_circuit=True)
        result = composite.validate("test content")

        assert result.is_valid
        assert validator1.validate_calls == 1
        assert validator2.validate_calls == 0  # Should not be called due to short-circuit

    def test_warnings_aggregation(self):
        """Test that warnings are properly aggregated."""
        validator1 = MockValidator(True, warnings=["Warning 1"], description="Validator 1")
        validator2 = MockValidator(True, warnings=["Warning 2"], description="Validator 2")

        composite = CompositeValidator([validator1, validator2], LogicOperator.AND)
        result = composite.validate("test content")

        assert result.is_valid
        assert "Validator 1: Warning 1" in result.warnings
        assert "Validator 2: Warning 2" in result.warnings

    def test_metadata_aggregation(self):
        """Test that metadata is properly aggregated."""
        validator1 = MockValidator(True, metadata={"key1": "value1"}, description="Validator 1")
        validator2 = MockValidator(True, metadata={"key2": "value2"}, description="Validator 2")

        composite = CompositeValidator([validator1, validator2], LogicOperator.AND, aggregate_metadata=True)
        result = composite.validate("test content")

        assert result.is_valid
        assert result.metadata["validator_1"]["key1"] == "value1"
        assert result.metadata["validator_2"]["key2"] == "value2"
        assert result.metadata["operation"]["operator"] == "AND"

    def test_exception_handling(self):
        """Test handling of exceptions from validators."""
        validator1 = MockValidator(True, description="Validator 1")
        validator2 = Mock()
        validator2.validate.side_effect = Exception("Test exception")

        composite = CompositeValidator([validator1, validator2], LogicOperator.AND)
        result = composite.validate("test content")

        assert not result.is_valid
        assert any("Validator 2 failed with exception: Test exception" in error for error in result.errors)

    def test_create_and_classmethod(self):
        """Test create_and class method."""
        validator1 = MockValidator(True, description="Validator 1")
        validator2 = MockValidator(True, description="Validator 2")

        composite = CompositeValidator.create_and(validator1, validator2)

        assert composite.operator == LogicOperator.AND
        assert len(composite.validators) == 2

    def test_create_or_classmethod(self):
        """Test create_or class method."""
        validator1 = MockValidator(True, description="Validator 1")
        validator2 = MockValidator(True, description="Validator 2")

        composite = CompositeValidator.create_or(validator1, validator2)

        assert composite.operator == LogicOperator.OR
        assert len(composite.validators) == 2

    def test_empty_validators_list(self):
        """Test that empty validators list raises ValueError."""
        with pytest.raises(ValueError, match="At least one validator must be provided"):
            CompositeValidator([])

    def test_get_description(self):
        """Test get_description method."""
        validator1 = MockValidator(True, description="Validator 1")
        validator2 = MockValidator(True, description="Validator 2")

        composite = CompositeValidator([validator1, validator2], LogicOperator.AND)
        description = composite.get_description()

        assert "Composite validator combining 2 validators with AND logic" in description
        assert "Validator 1" in description
        assert "Validator 2" in description


class TestValidationChain:
    """Test cases for ValidationChain."""

    def test_simple_and_chain(self):
        """Test simple AND chain."""
        validator1 = MockValidator(True, description="Validator 1")
        validator2 = MockValidator(True, description="Validator 2")

        chain = ValidationChain().add(validator1).and_().add(validator2)
        composite = chain.build()

        result = composite.validate("test content")
        assert result.is_valid
        assert composite.operator == LogicOperator.AND

    def test_simple_or_chain(self):
        """Test simple OR chain."""
        validator1 = MockValidator(False, errors=["Error 1"], description="Validator 1")
        validator2 = MockValidator(True, description="Validator 2")

        chain = ValidationChain().add(validator1).or_().add(validator2)
        composite = chain.build()

        result = composite.validate("test content")
        assert result.is_valid
        assert composite.operator == LogicOperator.OR

    def test_single_validator_chain(self):
        """Test chain with single validator."""
        validator1 = MockValidator(True, description="Validator 1")

        chain = ValidationChain().add(validator1)
        composite = chain.build()

        result = composite.validate("test content")
        assert result.is_valid
        assert len(composite.validators) == 1

    def test_complex_mixed_chain(self):
        """Test complex chain with mixed operators."""
        validator1 = MockValidator(True, description="Validator 1")
        validator2 = MockValidator(True, description="Validator 2")
        validator3 = MockValidator(False, errors=["Error 3"], description="Validator 3")

        # (validator1 AND validator2) OR validator3
        chain = ValidationChain().add(validator1).and_().add(validator2).or_().add(validator3)
        composite = chain.build()

        result = composite.validate("test content")
        assert result.is_valid  # First two validators pass, so overall should pass

    def test_operator_without_validators_error(self):
        """Test that adding operator without validators raises error."""
        chain = ValidationChain()

        with pytest.raises(ValueError, match="Cannot add operator without validators"):
            chain.and_()

        with pytest.raises(ValueError, match="Cannot add operator without validators"):
            chain.or_()

    def test_empty_chain_build_error(self):
        """Test that building empty chain raises error."""
        chain = ValidationChain()

        with pytest.raises(ValueError, match="No validators in chain"):
            chain.build()

    def test_fluent_api(self):
        """Test that chain methods return self for fluent API."""
        validator1 = MockValidator(True, description="Validator 1")
        validator2 = MockValidator(True, description="Validator 2")

        chain = ValidationChain()
        result_chain = chain.add(validator1).and_().add(validator2)

        assert result_chain is chain  # Should return same instance


if __name__ == "__main__":
    pytest.main([__file__])
