"""
Tests for the plugin manager.
"""

import tempfile
from pathlib import Path
from typing import Any, Dict, Optional

import pytest

from validated_llm.base_validator import BaseValidator, ValidationResult
from validated_llm.plugins.exceptions import PluginError
from validated_llm.plugins.manager import PluginManager
from validated_llm.plugins.registry import PluginRegistry, ValidationPlugin


class DummyValidator(BaseValidator):
    """Test validator for plugin manager tests."""

    def __init__(self, validator_name: str = "test_validator"):
        super().__init__(validator_name, "Test validator for manager tests")

    def validate(self, output: str, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        return ValidationResult(is_valid=len(output) > 0, errors=[] if output else ["Empty output"])


class TestPluginManager:
    """Test cases for PluginManager."""

    def test_manager_initialization(self) -> None:
        """Test plugin manager initialization."""
        registry = PluginRegistry()
        manager = PluginManager(registry)

        assert manager.registry is registry
        assert not manager._initialized

        manager.initialize()
        assert manager._initialized

        # Second initialization should be no-op
        manager.initialize()
        assert manager._initialized

    def test_register_plugin_direct(self) -> None:
        """Test registering a plugin directly with the manager."""
        manager = PluginManager(PluginRegistry())

        plugin = manager.register_plugin(validator_class=DummyValidator, name="direct_test", version="1.0.0", description="Directly registered test plugin", author="Test Suite", tags=["test", "direct"])

        assert plugin.name == "direct_test"
        assert plugin.validator_class == DummyValidator
        assert "test" in plugin.tags

        # Verify it's accessible through manager
        retrieved = manager.get_plugin("direct_test")
        assert retrieved is not None
        assert retrieved.name == "direct_test"

    def test_create_validator_with_initialization(self) -> None:
        """Test creating validator automatically initializes manager."""
        manager = PluginManager(PluginRegistry())

        # Register a plugin
        manager.register_plugin(validator_class=DummyValidator, name="auto_init_test", version="1.0.0", description="Auto-initialization test", author="Test Suite")

        # Creating validator should auto-initialize
        assert not manager._initialized
        validator = manager.create_validator("auto_init_test")
        assert manager._initialized

        assert isinstance(validator, DummyValidator)

    def test_create_validator_with_args(self) -> None:
        """Test creating validator with constructor arguments."""
        manager = PluginManager(PluginRegistry())

        manager.register_plugin(validator_class=DummyValidator, name="args_test", version="1.0.0", description="Arguments test", author="Test Suite")

        validator = manager.create_validator("args_test", validator_name="custom_name")
        assert isinstance(validator, DummyValidator)
        assert validator.name == "custom_name"

    def test_create_validator_not_found(self) -> None:
        """Test creating validator fails when plugin not found."""
        manager = PluginManager(PluginRegistry())

        with pytest.raises(PluginError, match="not found"):
            manager.create_validator("nonexistent_plugin")

    def test_list_plugins(self) -> None:
        """Test listing plugins through manager."""
        manager = PluginManager(PluginRegistry())

        # Register multiple plugins
        manager.register_plugin(validator_class=DummyValidator, name="list_test1", version="1.0.0", description="First list test", author="Test Suite", tags=["list", "test"])

        manager.register_plugin(validator_class=DummyValidator, name="list_test2", version="1.0.0", description="Second list test", author="Test Suite", tags=["list", "example"])

        # List all plugins
        all_plugins = manager.list_plugins()
        assert len(all_plugins) == 2

        # List by tag
        test_plugins = manager.list_plugins(tag="test")
        assert len(test_plugins) == 1
        assert test_plugins[0].name == "list_test1"

    def test_get_plugin_info(self) -> None:
        """Test getting plugin info through manager."""
        manager = PluginManager(PluginRegistry())

        manager.register_plugin(validator_class=DummyValidator, name="info_test", version="2.1.0", description="Info test plugin", author="Test Suite", dependencies=["pytest"], tags=["info", "test"])

        info = manager.get_plugin_info("info_test")
        assert info is not None
        assert info["name"] == "info_test"
        assert info["version"] == "2.1.0"
        assert info["dependencies"] == ["pytest"]

        # Test non-existent plugin
        info = manager.get_plugin_info("nonexistent")
        assert info is None

    def test_add_search_path(self) -> None:
        """Test adding search paths."""
        manager = PluginManager(PluginRegistry())

        with tempfile.TemporaryDirectory() as tmpdir:
            search_path = Path(tmpdir)

            # Should start with no custom paths
            initial_paths = len(manager.discovery._search_paths)

            manager.add_search_path(search_path)

            # Should have added the path
            assert len(manager.discovery._search_paths) == initial_paths + 1
            assert search_path in manager.discovery._search_paths

    def test_reload_plugins(self) -> None:
        """Test reloading plugins."""
        manager = PluginManager(PluginRegistry())

        # Register initial plugin
        manager.register_plugin(validator_class=DummyValidator, name="reload_test", version="1.0.0", description="Reload test", author="Test Suite")

        assert len(manager.list_plugins()) == 1

        # Reload should clear and rediscover
        plugins = manager.reload_plugins()

        # Registry should be cleared (no plugins from search paths in test)
        assert len(plugins) == 0
        assert len(manager.list_plugins()) == 0

    def test_discover_from_directory(self) -> None:
        """Test discovering plugins from a directory."""
        manager = PluginManager(PluginRegistry())

        with tempfile.TemporaryDirectory() as tmpdir:
            plugin_dir = Path(tmpdir)

            # Create a test plugin file
            plugin_file = plugin_dir / "test_plugin.py"
            plugin_content = """
from validated_llm.base_validator import BaseValidator, ValidationResult
from typing import Any, Dict, Optional

class TestDiscoveryValidator(BaseValidator):
    def __init__(self):
        super().__init__("discovery_test", "Test discovery validator")

    def validate(self, output: str, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        return ValidationResult(is_valid=True, errors=[])

PLUGIN_INFO = {
    "name": "discovery_test",
    "version": "1.0.0",
    "description": "Test plugin for discovery",
    "author": "Test Suite",
    "validator_class": TestDiscoveryValidator,
    "dependencies": [],
    "tags": ["test", "discovery"],
}
"""
            plugin_file.write_text(plugin_content)

            # Discover plugins from directory
            discovered = list(manager.discovery.discover_from_directory(plugin_dir))

            assert len(discovered) == 1
            assert discovered[0].name == "discovery_test"
            assert discovered[0].version == "1.0.0"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
