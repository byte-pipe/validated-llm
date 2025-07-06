"""
Tests for async validation functionality.
"""

import asyncio
import json
import time
from typing import Any, Dict, Optional

import pytest

from validated_llm.async_validation_loop import AsyncValidationLoop
from validated_llm.async_validator import AsyncBaseValidator, AsyncCompositeValidator, AsyncFunctionValidator, AsyncValidatorAdapter
from validated_llm.base_validator import ValidationResult
from validated_llm.validators.async_json_schema import AsyncJSONSchemaValidator
from validated_llm.validators.async_range import AsyncRangeValidator
from validated_llm.validators.json_schema import JSONSchemaValidator
from validated_llm.validators.range import RangeValidator


class MockAsyncValidator(AsyncBaseValidator):
    """Mock async validator for testing."""

    def __init__(self, name: str = "MockAsyncValidator", should_pass: bool = True, delay: float = 0.1):
        super().__init__(name=name, description="Mock async validator for testing")
        self.should_pass = should_pass
        self.delay = delay
        self.validation_count = 0

    async def validate_async(self, output: str, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """Mock async validation with configurable delay."""
        self.validation_count += 1
        await asyncio.sleep(self.delay)

        if self.should_pass:
            return ValidationResult(is_valid=True, errors=[], metadata={"mock_validator": True, "validation_count": self.validation_count})
        else:
            return ValidationResult(is_valid=False, errors=[f"Mock validation failed on attempt {self.validation_count}"], metadata={"mock_validator": True, "validation_count": self.validation_count})


class TestAsyncBaseValidator:
    """Test cases for AsyncBaseValidator."""

    @pytest.mark.asyncio
    async def test_mock_validator_success(self):
        """Test mock validator with successful validation."""
        validator = MockAsyncValidator(should_pass=True)
        result = await validator.validate_async("test output")

        assert result.is_valid
        assert len(result.errors) == 0
        assert result.metadata["mock_validator"] is True
        assert result.metadata["validation_count"] == 1

    @pytest.mark.asyncio
    async def test_mock_validator_failure(self):
        """Test mock validator with failed validation."""
        validator = MockAsyncValidator(should_pass=False)
        result = await validator.validate_async("test output")

        assert not result.is_valid
        assert len(result.errors) == 1
        assert "Mock validation failed" in result.errors[0]

    def test_validation_instructions(self):
        """Test validation instructions generation."""
        validator = MockAsyncValidator()
        instructions = validator.get_validation_instructions()

        assert "MockAsyncValidator" in instructions
        assert "validation criteria" in instructions


class TestAsyncValidatorAdapter:
    """Test cases for AsyncValidatorAdapter."""

    @pytest.mark.asyncio
    async def test_sync_validator_adaptation(self):
        """Test wrapping synchronous validator in async adapter."""
        # Create a sync validator
        sync_validator = RangeValidator(min_value=1, max_value=10, value_type="integer")

        # Wrap in async adapter
        async_adapter = AsyncValidatorAdapter(sync_validator)

        # Test valid input
        result = await async_adapter.validate_async("5")
        assert result.is_valid

        # Test invalid input
        result = await async_adapter.validate_async("15")
        assert not result.is_valid
        assert len(result.errors) > 0

    def test_adapter_name_delegation(self):
        """Test that adapter properly delegates name and instructions."""
        sync_validator = RangeValidator(min_value=1, max_value=10)
        async_adapter = AsyncValidatorAdapter(sync_validator)

        assert "Async(" in async_adapter.name
        assert "RangeValidator" in async_adapter.name

        instructions = async_adapter.get_validation_instructions()
        assert "RANGE VALIDATION" in instructions


class TestAsyncCompositeValidator:
    """Test cases for AsyncCompositeValidator."""

    @pytest.mark.asyncio
    async def test_and_logic_all_pass(self):
        """Test AND logic with all validators passing."""
        validators = [
            MockAsyncValidator("validator1", should_pass=True, delay=0.1),
            MockAsyncValidator("validator2", should_pass=True, delay=0.1),
        ]

        composite = AsyncCompositeValidator(validators, operator="AND", concurrent=True)

        start_time = time.time()
        result = await composite.validate_async("test")
        execution_time = time.time() - start_time

        assert result.is_valid
        assert len(result.errors) == 0
        # Should run concurrently, so total time < sum of delays
        assert execution_time < 0.3

    @pytest.mark.asyncio
    async def test_and_logic_one_fails(self):
        """Test AND logic with one validator failing."""
        validators = [
            MockAsyncValidator("validator1", should_pass=True, delay=0.1),
            MockAsyncValidator("validator2", should_pass=False, delay=0.1),
        ]

        composite = AsyncCompositeValidator(validators, operator="AND", concurrent=True)
        result = await composite.validate_async("test")

        assert not result.is_valid
        assert len(result.errors) > 0
        assert "[validator2]" in result.errors[0]

    @pytest.mark.asyncio
    async def test_or_logic_one_passes(self):
        """Test OR logic with one validator passing."""
        validators = [
            MockAsyncValidator("validator1", should_pass=False, delay=0.1),
            MockAsyncValidator("validator2", should_pass=True, delay=0.1),
        ]

        composite = AsyncCompositeValidator(validators, operator="OR", concurrent=True)
        result = await composite.validate_async("test")

        assert result.is_valid

    @pytest.mark.asyncio
    async def test_sequential_execution(self):
        """Test sequential execution mode."""
        validators = [
            MockAsyncValidator("validator1", should_pass=True, delay=0.1),
            MockAsyncValidator("validator2", should_pass=True, delay=0.1),
        ]

        composite = AsyncCompositeValidator(validators, operator="AND", concurrent=False)

        start_time = time.time()
        result = await composite.validate_async("test")
        execution_time = time.time() - start_time

        assert result.is_valid
        # Should run sequentially, so total time >= sum of delays
        assert execution_time >= 0.2

    @pytest.mark.asyncio
    async def test_mixed_sync_async_validators(self):
        """Test composite validator with mixed sync and async validators."""
        validators = [
            MockAsyncValidator("async_validator", should_pass=True, delay=0.1),
            RangeValidator(min_value=1, max_value=10, value_type="integer"),  # Sync validator
        ]

        composite = AsyncCompositeValidator(validators, operator="AND", concurrent=True)
        result = await composite.validate_async("5")

        assert result.is_valid


class TestAsyncFunctionValidator:
    """Test cases for AsyncFunctionValidator."""

    @pytest.mark.asyncio
    async def test_async_function_validator(self):
        """Test validator with async function."""

        async def async_validation_func(output: str) -> bool:
            await asyncio.sleep(0.1)
            return "valid" in output.lower()

        validator = AsyncFunctionValidator(async_validation_func, name="test_async")

        result = await validator.validate_async("This is valid")
        assert result.is_valid

        result = await validator.validate_async("This is bad")
        assert not result.is_valid

    @pytest.mark.asyncio
    async def test_sync_function_validator(self):
        """Test validator with sync function (run in thread pool)."""

        def sync_validation_func(output: str) -> bool:
            return len(output) > 5

        validator = AsyncFunctionValidator(sync_validation_func, name="test_sync")

        result = await validator.validate_async("short")
        assert not result.is_valid

        result = await validator.validate_async("long enough")
        assert result.is_valid

    @pytest.mark.asyncio
    async def test_function_validator_exception(self):
        """Test function validator with exception handling."""

        def failing_function(output: str) -> bool:
            raise ValueError("Test exception")

        validator = AsyncFunctionValidator(failing_function)
        result = await validator.validate_async("test")

        assert not result.is_valid
        assert "Test exception" in result.errors[0]


class TestAsyncJSONSchemaValidator:
    """Test cases for AsyncJSONSchemaValidator."""

    @pytest.mark.asyncio
    async def test_valid_json_schema(self):
        """Test async JSON schema validation with valid input."""
        schema = {"type": "object", "properties": {"name": {"type": "string"}, "age": {"type": "integer", "minimum": 0}}, "required": ["name", "age"]}

        validator = AsyncJSONSchemaValidator(schema)
        result = await validator.validate_async('{"name": "John", "age": 30}')

        assert result.is_valid
        assert len(result.errors) == 0
        assert result.metadata["async_validation"] is True

    @pytest.mark.asyncio
    async def test_invalid_json_schema(self):
        """Test async JSON schema validation with invalid input."""
        schema = {"type": "object", "properties": {"name": {"type": "string"}, "age": {"type": "integer", "minimum": 0}}, "required": ["name", "age"]}

        validator = AsyncJSONSchemaValidator(schema)

        # Missing required field
        result = await validator.validate_async('{"name": "John"}')
        assert not result.is_valid
        assert "age" in str(result.errors)

    @pytest.mark.asyncio
    async def test_invalid_json_syntax(self):
        """Test async JSON schema validation with invalid JSON syntax."""
        schema = {"type": "object"}
        validator = AsyncJSONSchemaValidator(schema)

        result = await validator.validate_async('{"name": "John",}')  # Trailing comma
        assert not result.is_valid
        assert "Invalid JSON" in result.errors[0]


class TestAsyncRangeValidator:
    """Test cases for AsyncRangeValidator."""

    @pytest.mark.asyncio
    async def test_number_in_range(self):
        """Test async range validation with number in range."""
        validator = AsyncRangeValidator(min_value=1, max_value=10, value_type="number")

        result = await validator.validate_async("5.5")
        assert result.is_valid
        assert result.metadata["async_validation"] is True

    @pytest.mark.asyncio
    async def test_number_out_of_range(self):
        """Test async range validation with number out of range."""
        validator = AsyncRangeValidator(min_value=1, max_value=10, value_type="number")

        result = await validator.validate_async("15")
        assert not result.is_valid
        assert "out of range" in result.errors[0]

    @pytest.mark.asyncio
    async def test_integer_validation(self):
        """Test async range validation with integer type."""
        validator = AsyncRangeValidator(min_value=1, max_value=10, value_type="integer")

        result = await validator.validate_async("5")
        assert result.is_valid

        result = await validator.validate_async("0")
        assert not result.is_valid


# Note: AsyncValidationLoop tests would require a ChatBot mock, which is more complex
# For now, we'll focus on the validator tests above


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
