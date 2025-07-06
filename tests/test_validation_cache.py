"""
Tests for validation caching functionality.
"""

import time
from typing import Any, Dict

import pytest

from validated_llm.base_validator import BaseValidator, ValidationResult
from validated_llm.cached_validator import CachedValidatorMixin, make_cached_validator
from validated_llm.validation_cache import ValidationCache, clear_global_cache, configure_global_cache, get_global_cache


class SimpleTestValidator(BaseValidator):
    """Simple test validator for cache testing."""

    def __init__(self, sleep_duration: float = 0.0, fail_validation: bool = False):
        super().__init__(name="TestValidator", description="A test validator")
        self.sleep_duration = sleep_duration
        self.fail_validation = fail_validation
        self.call_count = 0

    def validate(self, output: str, context=None) -> ValidationResult:
        """Validate with optional delay to simulate expensive operations."""
        self.call_count += 1

        if self.sleep_duration > 0:
            time.sleep(self.sleep_duration)

        if self.fail_validation:
            return ValidationResult(is_valid=False, errors=[f"Test error for: {output}"], warnings=[], metadata={"test": True})

        return ValidationResult(is_valid=True, errors=[], warnings=[], metadata={"test": True, "call_count": self.call_count})


class TestValidationCache:
    """Test ValidationCache functionality."""

    def test_cache_creation(self):
        """Test basic cache creation and configuration."""
        cache = ValidationCache(max_size=100, ttl_seconds=30.0)

        assert cache.max_size == 100
        assert cache.ttl_seconds == 30.0

        stats = cache.get_stats()
        assert stats["size"] == 0
        assert stats["hits"] == 0
        assert stats["misses"] == 0

    def test_cache_basic_operations(self):
        """Test basic cache put/get operations."""
        cache = ValidationCache(max_size=10)

        result = ValidationResult(is_valid=True, errors=[], warnings=[], metadata={})

        # Cache miss
        cached_result = cache.get("validator1", "input1")
        assert cached_result is None

        # Store in cache
        cache.put("validator1", "input1", result)

        # Cache hit
        cached_result = cache.get("validator1", "input1")
        assert cached_result is not None
        assert cached_result.is_valid == result.is_valid

        stats = cache.get_stats()
        assert stats["hits"] == 1
        assert stats["misses"] == 1

    def test_cache_ttl_expiration(self):
        """Test that cache entries expire based on TTL."""
        cache = ValidationCache(max_size=10, ttl_seconds=0.1)  # 100ms TTL

        result = ValidationResult(is_valid=True, errors=[], warnings=[], metadata={})
        cache.put("validator1", "input1", result)

        # Should be cached immediately
        cached_result = cache.get("validator1", "input1")
        assert cached_result is not None

        # Wait for expiration
        time.sleep(0.15)

        # Should be expired
        cached_result = cache.get("validator1", "input1")
        assert cached_result is None

    def test_cache_size_limit(self):
        """Test cache size limits and eviction."""
        cache = ValidationCache(max_size=3)

        result = ValidationResult(is_valid=True, errors=[], warnings=[], metadata={})

        # Fill cache to capacity
        cache.put("validator1", "input1", result)
        cache.put("validator1", "input2", result)
        cache.put("validator1", "input3", result)

        stats = cache.get_stats()
        assert stats["size"] == 3

        # Add one more - should trigger eviction
        cache.put("validator1", "input4", result)

        # Should have evicted some entries
        stats = cache.get_stats()
        assert stats["size"] <= 3
        assert stats["evictions"] > 0

    def test_cache_context_handling(self):
        """Test that context is properly included in cache keys."""
        cache = ValidationCache(max_size=10)

        result1 = ValidationResult(is_valid=True, errors=[], warnings=[], metadata={"context": "1"})
        result2 = ValidationResult(is_valid=True, errors=[], warnings=[], metadata={"context": "2"})

        # Same validator and input, different context
        cache.put("validator1", "input1", result1, {"mode": "strict"})
        cache.put("validator1", "input1", result2, {"mode": "lenient"})

        # Should get different results based on context
        cached1 = cache.get("validator1", "input1", {"mode": "strict"})
        cached2 = cache.get("validator1", "input1", {"mode": "lenient"})

        assert cached1.metadata["context"] == "1"
        assert cached2.metadata["context"] == "2"

    def test_global_cache_functions(self):
        """Test global cache management functions."""
        # Configure global cache
        cache = configure_global_cache(max_size=50, ttl_seconds=60.0)
        assert cache.max_size == 50
        assert cache.ttl_seconds == 60.0

        # Get global cache
        global_cache = get_global_cache()
        assert global_cache is cache

        # Clear global cache
        result = ValidationResult(is_valid=True, errors=[], warnings=[], metadata={})
        global_cache.put("test", "input", result)
        assert global_cache.get("test", "input") is not None

        clear_global_cache()
        assert global_cache.get("test", "input") is None


class TestCachedValidatorMixin:
    """Test CachedValidatorMixin functionality."""

    def test_cached_validator_creation(self):
        """Test creating a cached validator."""

        class CachedTestValidator(CachedValidatorMixin, SimpleTestValidator):
            def __init__(self, sleep_duration: float = 0.0, use_cache: bool = True):
                SimpleTestValidator.__init__(self, sleep_duration=sleep_duration)
                CachedValidatorMixin.__init__(self, use_cache=use_cache)

            def _validate_uncached(self, output: str, context=None):
                return SimpleTestValidator.validate(self, output, context)

        validator = CachedTestValidator(sleep_duration=0.01)
        assert validator._use_cache is True

        # First call should execute validation
        result1 = validator.validate("test input")
        assert result1.is_valid is True
        assert validator.call_count == 1

        # Second call should use cache
        result2 = validator.validate("test input")
        assert result2.is_valid is True
        assert validator.call_count == 1  # No additional call

        # Different input should execute validation
        result3 = validator.validate("different input")
        assert result3.is_valid is True
        assert validator.call_count == 2

    def test_cache_disabled(self):
        """Test validator with caching disabled."""

        class CachedTestValidator(CachedValidatorMixin, SimpleTestValidator):
            def __init__(self, use_cache: bool = True):
                SimpleTestValidator.__init__(self)
                CachedValidatorMixin.__init__(self, use_cache=use_cache)

            def _validate_uncached(self, output: str, context=None):
                return SimpleTestValidator.validate(self, output, context)

        validator = CachedTestValidator(use_cache=False)

        # Both calls should execute validation
        validator.validate("test input")
        validator.validate("test input")

        assert validator.call_count == 2

    def test_performance_improvement(self):
        """Test that caching provides measurable performance improvement."""

        class CachedTestValidator(CachedValidatorMixin, SimpleTestValidator):
            def __init__(self, sleep_duration: float = 0.0):
                SimpleTestValidator.__init__(self, sleep_duration=sleep_duration)
                CachedValidatorMixin.__init__(self, use_cache=True)

            def _validate_uncached(self, output: str, context=None):
                return SimpleTestValidator.validate(self, output, context)

        validator = CachedTestValidator(sleep_duration=0.05)  # 50ms delay

        # Time first call (should be slow)
        start_time = time.time()
        result1 = validator.validate("test input")
        first_call_time = time.time() - start_time

        # Time second call (should be fast due to cache)
        start_time = time.time()
        result2 = validator.validate("test input")
        second_call_time = time.time() - start_time

        # Verify the calls worked
        assert result1.is_valid is True
        assert result2.is_valid is True
        assert validator.call_count == 1  # Only one actual validation

        # Second call should be significantly faster
        assert second_call_time < first_call_time / 2, f"Expected {second_call_time} < {first_call_time/2}"
        assert first_call_time > 0.04, f"Expected first call > 40ms, got {first_call_time*1000:.1f}ms"
        assert second_call_time < 0.01, f"Expected second call < 10ms, got {second_call_time*1000:.1f}ms"

    def test_cache_stats(self):
        """Test cache statistics tracking."""

        class CachedTestValidator(CachedValidatorMixin, SimpleTestValidator):
            def __init__(self):
                SimpleTestValidator.__init__(self)
                CachedValidatorMixin.__init__(self, use_cache=True)

            def _validate_uncached(self, output: str, context=None):
                return SimpleTestValidator.validate(self, output, context)

        validator = CachedTestValidator()

        # Initial stats
        stats = validator.get_cache_stats()
        assert stats["validator_hits"] == 0
        assert stats["validator_misses"] == 0

        # First call - cache miss
        validator.validate("input1")
        stats = validator.get_cache_stats()
        assert stats["validator_misses"] == 1
        assert stats["validator_hit_rate"] == 0.0

        # Second call - cache hit
        validator.validate("input1")
        stats = validator.get_cache_stats()
        assert stats["validator_hits"] == 1
        assert stats["validator_misses"] == 1
        assert stats["validator_hit_rate"] == 0.5

    def test_validator_id_generation(self):
        """Test that validator IDs are generated correctly."""

        class CachedTestValidator1(CachedValidatorMixin, SimpleTestValidator):
            def __init__(self):
                SimpleTestValidator.__init__(self)
                CachedValidatorMixin.__init__(self, use_cache=True)

            def _validate_uncached(self, output: str, context=None):
                return SimpleTestValidator.validate(self, output, context)

        class CachedTestValidator2(CachedValidatorMixin, SimpleTestValidator):
            def __init__(self):
                SimpleTestValidator.__init__(self)
                CachedValidatorMixin.__init__(self, use_cache=True)

            def _validate_uncached(self, output: str, context=None):
                return SimpleTestValidator.validate(self, output, context)

        validator1 = CachedTestValidator1()
        validator2 = CachedTestValidator2()

        id1 = validator1._get_validator_id()
        id2 = validator2._get_validator_id()

        # Should have different IDs for different validator classes
        assert id1 != id2
        assert "CachedTestValidator1" in id1
        assert "CachedTestValidator2" in id2


class TestMakeCachedValidator:
    """Test the make_cached_validator factory function."""

    def test_factory_function(self):
        """Test creating cached validators using factory function."""
        CachedTestValidator = make_cached_validator(SimpleTestValidator, use_cache=True)

        validator = CachedTestValidator(sleep_duration=0.01)

        # Should behave like a cached validator
        validator.validate("test input")
        validator.validate("test input")

        assert validator.call_count == 1  # Second call should be cached

    def test_factory_preserves_functionality(self):
        """Test that factory-created validators preserve original functionality."""
        CachedTestValidator = make_cached_validator(SimpleTestValidator)

        validator = CachedTestValidator(fail_validation=True)
        result = validator.validate("test input")

        assert result.is_valid is False
        assert len(result.errors) > 0

    def test_factory_class_naming(self):
        """Test that factory creates properly named classes."""
        CachedTestValidator = make_cached_validator(SimpleTestValidator)

        assert CachedTestValidator.__name__ == "CachedSimpleTestValidator"

        # Test with a different validator class
        from validated_llm.validators.range import RangeValidator

        CachedRangeValidator = make_cached_validator(RangeValidator)

        assert CachedRangeValidator.__name__ == "CachedRangeValidator"


class TestCacheIntegration:
    """Integration tests for caching with real validators."""

    def test_cached_json_schema_validator(self):
        """Test caching with JSON schema validator."""
        from validated_llm.validators import FastJSONSchemaValidator

        schema = {"type": "object", "properties": {"name": {"type": "string"}, "age": {"type": "integer"}}, "required": ["name"]}

        validator = FastJSONSchemaValidator(schema, use_cache=True)

        # Valid JSON
        json_input = '{"name": "John", "age": 30}'

        # First validation
        result1 = validator.validate(json_input)
        assert result1.is_valid is True

        # Second validation (should be cached)
        result2 = validator.validate(json_input)
        assert result2.is_valid is True

        # Should have cache hits
        stats = validator.get_cache_stats()
        assert stats["validator_hits"] > 0

    def test_cached_regex_validator(self):
        """Test caching with regex validator."""
        from validated_llm.validators import FastRegexValidator

        validator = FastRegexValidator(r"^\d{3}-\d{2}-\d{4}$", use_cache=True)

        # Valid pattern
        valid_input = "123-45-6789"

        # First validation
        result1 = validator.validate(valid_input)
        assert result1.is_valid is True

        # Second validation (should be cached)
        result2 = validator.validate(valid_input)
        assert result2.is_valid is True

        # Should have cache hits
        stats = validator.get_cache_stats()
        assert stats["validator_hits"] > 0
