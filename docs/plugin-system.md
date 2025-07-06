# Plugin System Documentation

The validated-llm plugin system provides a flexible architecture for extending the framework with custom validators. This system allows developers to create, distribute, and use custom validation plugins without modifying the core codebase.

## Overview

The plugin system consists of several key components:

- **Plugin Registry**: Central repository for managing plugin metadata
- **Plugin Discovery**: Automatic detection and loading of plugins from various sources
- **Plugin Manager**: High-level interface for plugin operations
- **CLI Tools**: Command-line interface for plugin management

## Creating a Plugin

### Basic Plugin Structure

A plugin is a Python module that contains:

1. A validator class that inherits from `BaseValidator`
2. A `PLUGIN_INFO` dictionary with plugin metadata

```python
from validated_llm.base_validator import BaseValidator, ValidationResult
from typing import Any, Dict, Optional

class MyCustomValidator(BaseValidator):
    """My custom validator description."""

    def __init__(self, my_param: str = "default"):
        super().__init__(
            name="my_custom_validator",
            description="Description of what this validator does"
        )
        self.my_param = my_param

    def validate(self, output: str, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """Implement your validation logic here."""
        result = ValidationResult(is_valid=True, errors=[])

        # Your validation logic
        if not output.strip():
            result.add_error("Output cannot be empty")

        return result

# Required plugin metadata
PLUGIN_INFO = {
    "name": "my_custom_validator",
    "version": "1.0.0",
    "description": "My custom validator for specific use cases",
    "author": "Your Name",
    "validator_class": MyCustomValidator,
    "dependencies": [],  # List of required packages
    "tags": ["custom", "validation"],  # Tags for categorization
}
```

### Plugin Metadata

The `PLUGIN_INFO` dictionary must contain:

- **name** (required): Unique plugin name
- **version** (required): Plugin version (semantic versioning recommended)
- **description** (required): Brief description of the plugin
- **author** (required): Plugin author name
- **validator_class** (required): The validator class
- **dependencies** (optional): List of required Python packages
- **tags** (optional): List of tags for categorization

## Plugin Discovery

### Search Paths

The plugin system automatically searches for plugins in:

1. `~/.validated-llm/plugins/` - User-specific plugins
2. `./validated_llm_plugins/` - Project-local plugins
3. Paths specified in `VALIDATED_LLM_PLUGIN_PATH` environment variable
4. Namespace packages under `validated_llm_plugins.*`

### File Organization

Plugins can be organized as:

**Single File Plugin:**

```
my_plugin.py
```

**Package Plugin:**

```
my_plugin/
├── __init__.py  # Contains PLUGIN_INFO
├── validator.py
└── utils.py
```

## Using Plugins

### Programmatic Usage

```python
from validated_llm.plugins import get_manager

# Initialize plugin system
manager = get_manager()
manager.initialize()

# List available plugins
plugins = manager.list_plugins()
for plugin in plugins:
    print(f"{plugin.name} v{plugin.version}")

# Create validator instance
validator = manager.create_validator("my_custom_validator", my_param="custom_value")

# Use validator
result = validator.validate("some output")
print(f"Valid: {result.is_valid}")
```

### CLI Usage

```bash
# List all plugins
validated-llm plugin list

# Show plugin details
validated-llm plugin info my_custom_validator

# Test a plugin
validated-llm plugin test my_custom_validator --args '{"my_param": "test"}'

# Discover plugins from directory
validated-llm plugin discover /path/to/plugins

# Show search paths
validated-llm plugin paths

# Reload all plugins
validated-llm plugin reload
```

## Advanced Features

### Plugin with Dependencies

```python
PLUGIN_INFO = {
    "name": "advanced_validator",
    "version": "1.0.0",
    "description": "Validator with external dependencies",
    "author": "Developer",
    "validator_class": AdvancedValidator,
    "dependencies": ["requests", "beautifulsoup4"],
    "tags": ["web", "scraping"],
}
```

### Plugin with Configuration

```python
class ConfigurableValidator(BaseValidator):
    def __init__(self, config_file: str = None, strict_mode: bool = False):
        super().__init__("configurable", "Configurable validator")
        self.config_file = config_file
        self.strict_mode = strict_mode
        self._load_config()

    def _load_config(self):
        # Load configuration from file
        pass
```

### Plugin with Context Usage

```python
def validate(self, output: str, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
    result = ValidationResult(is_valid=True, errors=[])

    # Use context information
    if context:
        expected_format = context.get("expected_format")
        user_preferences = context.get("user_preferences")

        # Validation logic using context
        if expected_format and not self._matches_format(output, expected_format):
            result.add_error(f"Output does not match expected format: {expected_format}")

    return result
```

## Best Practices

### Validator Design

1. **Single Responsibility**: Each validator should focus on one specific aspect
2. **Clear Feedback**: Provide descriptive error messages and warnings
3. **Context Awareness**: Use context information when available
4. **Performance**: Optimize for common use cases
5. **Documentation**: Include clear docstrings and examples

### Error Handling

```python
def validate(self, output: str, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
    result = ValidationResult(is_valid=True, errors=[])

    try:
        # Validation logic
        pass
    except Exception as e:
        result.add_error(f"Validation failed: {str(e)}")

    return result
```

### Metadata and Warnings

```python
def validate(self, output: str, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
    result = ValidationResult(is_valid=True, errors=[])

    # Add warnings for non-critical issues
    if self._has_minor_issue(output):
        result.add_warning("Minor formatting issue detected")

    # Add metadata for additional information
    result.metadata = {
        "word_count": len(output.split()),
        "validation_time": time.time() - start_time,
        "suggestions": self._get_suggestions(output)
    }

    return result
```

## Plugin Distribution

### Local Development

1. Create plugin in local directory
2. Add to search path or use discovery command
3. Test with CLI tools

### Package Distribution

1. Create Python package with plugin
2. Publish to PyPI
3. Use namespace package `validated_llm_plugins.your_plugin`

### Example Package Structure

```
validated-llm-my-plugin/
├── setup.py
├── README.md
├── validated_llm_plugins/
│   └── my_plugin/
│       ├── __init__.py
│       └── validator.py
└── tests/
    └── test_plugin.py
```

## Testing Plugins

### Unit Testing

```python
import pytest
from validated_llm.base_validator import ValidationResult
from my_plugin import MyCustomValidator

def test_validator_success():
    validator = MyCustomValidator()
    result = validator.validate("valid output")
    assert result.is_valid
    assert len(result.errors) == 0

def test_validator_failure():
    validator = MyCustomValidator()
    result = validator.validate("")
    assert not result.is_valid
    assert "empty" in result.errors[0].lower()
```

### Integration Testing

```python
def test_plugin_registration():
    from validated_llm.plugins import get_manager

    manager = get_manager()
    plugin = manager.register_plugin(
        validator_class=MyCustomValidator,
        name="test_plugin",
        version="1.0.0",
        description="Test plugin",
        author="Test"
    )

    assert plugin.name == "test_plugin"

    validator = manager.create_validator("test_plugin")
    assert isinstance(validator, MyCustomValidator)
```

## Troubleshooting

### Common Issues

1. **Plugin Not Found**

   - Check search paths with `validated-llm plugin paths`
   - Verify `PLUGIN_INFO` dictionary is present
   - Ensure file/package is in correct location

2. **Import Errors**

   - Check dependencies are installed
   - Verify validator class inherits from `BaseValidator`
   - Check for syntax errors in plugin file

3. **Registration Failures**
   - Verify all required metadata fields are present
   - Check for naming conflicts with existing plugins
   - Ensure validator class is properly defined

### Debug Mode

```python
import logging
logging.basicConfig(level=logging.DEBUG)

from validated_llm.plugins import get_manager
manager = get_manager()
manager.initialize()
```

## Example Plugins

See the `examples/plugins/` directory for complete example plugins:

- **credit_card_validator.py**: Validates credit card numbers using Luhn algorithm
- **social_security_validator.py**: Detects and validates SSNs for PII protection

These examples demonstrate various plugin patterns and best practices.
