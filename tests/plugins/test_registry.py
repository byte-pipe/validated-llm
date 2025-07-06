"""
Tests for the plugin registry system.
"""

from typing import Any, Dict, Optional

import pytest

from validated_llm.base_validator import BaseValidator, ValidationResult
from validated_llm.plugins.exceptions import PluginRegistrationError, PluginValidationError
from validated_llm.plugins.registry import PluginRegistry, ValidationPlugin


class MockValidator(BaseValidator):
    """Mock validator for testing."""

    def __init__(self, name: str = "mock", description: str = "Mock validator"):
        super().__init__(name, description)

    def validate(self, output: str, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        return ValidationResult(is_valid=True, errors=[])


class MockValidatorWithArgs(BaseValidator):
    """Mock validator that requires arguments."""

    def __init__(self, required_arg: str, optional_arg: str = "default"):
        super().__init__("mock_with_args", "Mock validator with arguments")
        self.required_arg = required_arg
        self.optional_arg = optional_arg

    def validate(self, output: str, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        return ValidationResult(is_valid=True, errors=[])


class InvalidValidator:
    """Not a BaseValidator - should fail validation."""

    pass


class TestPluginRegistry:
    """Test cases for PluginRegistry."""

    def test_register_plugin_success(self) -> None:
        """Test successful plugin registration."""
        registry = PluginRegistry()

        plugin = ValidationPlugin(name="test_plugin", version="1.0.0", description="Test plugin", author="Test Author", validator_class=MockValidator)

        registry.register_plugin(plugin)

        # Check plugin was registered
        retrieved = registry.get_plugin("test_plugin")
        assert retrieved is not None
        assert retrieved.name == "test_plugin"
        assert retrieved.version == "1.0.0"

    def test_register_plugin_duplicate_name(self) -> None:
        """Test registration fails with duplicate names."""
        registry = PluginRegistry()

        plugin1 = ValidationPlugin(name="duplicate", version="1.0.0", description="First plugin", author="Author 1", validator_class=MockValidator)

        plugin2 = ValidationPlugin(name="duplicate", version="2.0.0", description="Second plugin", author="Author 2", validator_class=MockValidator)

        registry.register_plugin(plugin1)

        with pytest.raises(PluginRegistrationError, match="already registered"):
            registry.register_plugin(plugin2)

    def test_register_validator_class_direct(self) -> None:
        """Test registering a validator class directly."""
        registry = PluginRegistry()

        plugin = registry.register_validator_class(validator_class=MockValidator, name="direct_plugin", version="1.0.0", description="Directly registered plugin", author="Test Author", tags=["test", "mock"])

        assert plugin.name == "direct_plugin"
        assert plugin.validator_class == MockValidator
        assert "test" in plugin.tags

        # Check it's in registry
        retrieved = registry.get_plugin("direct_plugin")
        assert retrieved is not None
        assert retrieved.name == "direct_plugin"

    def test_plugin_validation_missing_name(self) -> None:
        """Test plugin validation fails with missing name."""
        registry = PluginRegistry()

        plugin = ValidationPlugin(name="", version="1.0.0", description="Test plugin", author="Test Author", validator_class=MockValidator)  # Empty name

        with pytest.raises(PluginValidationError, match="name is required"):
            registry.register_plugin(plugin)

    def test_plugin_validation_missing_version(self) -> None:
        """Test plugin validation fails with missing version."""
        registry = PluginRegistry()

        plugin = ValidationPlugin(name="test_plugin", version="", description="Test plugin", author="Test Author", validator_class=MockValidator)  # Empty version

        with pytest.raises(PluginValidationError, match="version is required"):
            registry.register_plugin(plugin)

    def test_plugin_validation_invalid_validator_class(self) -> None:
        """Test plugin validation fails with invalid validator class."""
        registry = PluginRegistry()

        plugin = ValidationPlugin(name="test_plugin", version="1.0.0", description="Test plugin", author="Test Author", validator_class=InvalidValidator)  # type: ignore

        with pytest.raises(PluginValidationError, match="inherit from BaseValidator"):
            registry.register_plugin(plugin)

    def test_create_validator_success(self) -> None:
        """Test creating validator instance from plugin."""
        registry = PluginRegistry()

        plugin = ValidationPlugin(name="test_plugin", version="1.0.0", description="Test plugin", author="Test Author", validator_class=MockValidator)

        registry.register_plugin(plugin)

        # Create validator instance
        validator = registry.create_validator("test_plugin")
        assert isinstance(validator, MockValidator)
        assert validator.name == "mock"

    def test_create_validator_with_args(self) -> None:
        """Test creating validator with constructor arguments."""
        registry = PluginRegistry()

        plugin = ValidationPlugin(name="test_plugin_args", version="1.0.0", description="Test plugin with args", author="Test Author", validator_class=MockValidatorWithArgs)

        registry.register_plugin(plugin)

        # Create validator with required argument
        validator = registry.create_validator("test_plugin_args", required_arg="test_value", optional_arg="custom_value")

        assert isinstance(validator, MockValidatorWithArgs)
        assert validator.required_arg == "test_value"
        assert validator.optional_arg == "custom_value"

    def test_create_validator_not_found(self) -> None:
        """Test creating validator fails when plugin not found."""
        registry = PluginRegistry()

        from validated_llm.plugins.exceptions import PluginError

        with pytest.raises(PluginError, match="not found"):
            registry.create_validator("nonexistent_plugin")

    def test_list_plugins(self) -> None:
        """Test listing plugins."""
        registry = PluginRegistry()

        # Register multiple plugins
        plugin1 = ValidationPlugin(name="plugin1", version="1.0.0", description="First plugin", author="Author 1", validator_class=MockValidator, tags=["tag1", "common"])

        plugin2 = ValidationPlugin(name="plugin2", version="1.0.0", description="Second plugin", author="Author 2", validator_class=MockValidator, tags=["tag2", "common"])

        registry.register_plugin(plugin1)
        registry.register_plugin(plugin2)

        # List all plugins
        all_plugins = registry.list_plugins()
        assert len(all_plugins) == 2

        # List plugins by tag
        common_plugins = registry.list_plugins(tag="common")
        assert len(common_plugins) == 2

        tag1_plugins = registry.list_plugins(tag="tag1")
        assert len(tag1_plugins) == 1
        assert tag1_plugins[0].name == "plugin1"

    def test_unregister_plugin(self) -> None:
        """Test unregistering plugins."""
        registry = PluginRegistry()

        plugin = ValidationPlugin(name="test_plugin", version="1.0.0", description="Test plugin", author="Test Author", validator_class=MockValidator)

        registry.register_plugin(plugin)
        assert registry.get_plugin("test_plugin") is not None

        # Unregister existing plugin
        result = registry.unregister_plugin("test_plugin")
        assert result is True
        assert registry.get_plugin("test_plugin") is None

        # Unregister non-existent plugin
        result = registry.unregister_plugin("nonexistent")
        assert result is False

    def test_get_plugin_info(self) -> None:
        """Test getting plugin information."""
        registry = PluginRegistry()

        plugin = ValidationPlugin(
            name="info_test", version="2.0.0", description="Plugin for info testing", author="Info Author", validator_class=MockValidator, dependencies=["dep1", "dep2"], tags=["info", "test"], plugin_module="test.module"
        )

        registry.register_plugin(plugin)

        info = registry.get_plugin_info("info_test")
        assert info is not None
        assert info["name"] == "info_test"
        assert info["version"] == "2.0.0"
        assert info["description"] == "Plugin for info testing"
        assert info["author"] == "Info Author"
        assert info["dependencies"] == ["dep1", "dep2"]
        assert info["tags"] == ["info", "test"]
        assert info["validator_class"] == "MockValidator"
        assert info["module"] == "test.module"

        # Test non-existent plugin
        info = registry.get_plugin_info("nonexistent")
        assert info is None

    def test_clear_registry(self) -> None:
        """Test clearing the registry."""
        registry = PluginRegistry()

        plugin = ValidationPlugin(name="test_plugin", version="1.0.0", description="Test plugin", author="Test Author", validator_class=MockValidator)

        registry.register_plugin(plugin)
        assert len(registry.list_plugins()) == 1

        registry.clear()
        assert len(registry.list_plugins()) == 0
        assert registry.get_plugin("test_plugin") is None
