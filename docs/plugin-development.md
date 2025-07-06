# Plugin Development Workflow Guide

This guide walks you through the complete process of developing, testing, and distributing custom validators as plugins for the validated-llm framework.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Plugin Architecture](#plugin-architecture)
3. [Development Workflow](#development-workflow)
4. [Testing Your Plugin](#testing-your-plugin)
5. [Plugin Packaging](#plugin-packaging)
6. [Distribution Strategies](#distribution-strategies)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)

## Quick Start

### 1. Create Your First Plugin

```python
# my_validator_plugin.py
from validated_llm.base_validator import BaseValidator, ValidationResult
from typing import Dict, Any, Optional
import re

class URLValidator(BaseValidator):
    """Validates URLs with customizable schemes and requirements"""

    def __init__(self,
                 name: str = "url_validator",
                 allowed_schemes: list = None,
                 require_tld: bool = True):
        super().__init__(name, "Validates URL format and accessibility")
        self.allowed_schemes = allowed_schemes or ["http", "https"]
        self.require_tld = require_tld

    def validate(self, output: str, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """Validate URL format"""
        url = output.strip()

        # Basic URL pattern
        url_pattern = r'^(https?|ftp)://[^s/.?#].[^s]*'

        if not re.match(url_pattern, url, re.IGNORECASE):
            return ValidationResult(
                is_valid=False,
                errors=["Invalid URL format"]
            )

        # Check allowed schemes
        scheme = url.split('://')[0].lower()
        if scheme not in self.allowed_schemes:
            return ValidationResult(
                is_valid=False,
                errors=[f"Scheme '{scheme}' not allowed. Allowed: {self.allowed_schemes}"]
            )

        # Additional validation can go here
        return ValidationResult(
            is_valid=True,
            metadata={"scheme": scheme, "url_length": len(url)}
        )

# Plugin metadata (REQUIRED)
PLUGIN_INFO = {
    "name": "url_validator",
    "version": "1.0.0",
    "description": "Validates URL format with customizable scheme restrictions",
    "author": "Your Name <your.email@example.com>",
    "validator_class": URLValidator,
    "dependencies": [],  # List any required packages
    "tags": ["url", "web", "validation"],
}
```

### 2. Test Your Plugin

```python
# test_my_plugin.py
from my_validator_plugin import URLValidator

def test_url_validator():
    validator = URLValidator()

    # Test valid URLs
    valid_urls = [
        "https://example.com",
        "http://subdomain.example.co.uk",
        "https://example.com/path?query=1"
    ]

    for url in valid_urls:
        result = validator.validate(url)
        assert result.is_valid, f"URL should be valid: {url}"

    # Test invalid URLs
    invalid_urls = [
        "not-a-url",
        "ftp://example.com",  # Not in allowed schemes
        "https://",
    ]

    for url in invalid_urls:
        result = validator.validate(url)
        assert not result.is_valid, f"URL should be invalid: {url}"

if __name__ == "__main__":
    test_url_validator()
    print("All tests passed!")
```

### 3. Use Your Plugin

```python
# Using the plugin system
from validated_llm.plugins.manager import get_manager

# Load plugin
manager = get_manager()
manager.add_search_path(Path("."))  # Current directory
manager.initialize()

# Create validator from plugin
validator = manager.create_validator("url_validator", allowed_schemes=["https"])
result = validator.validate("https://example.com")
print(f"Valid: {result.is_valid}")
```

## Plugin Architecture

### Plugin Structure

Every plugin must have:

1. **Validator Class**: Inherits from `BaseValidator`
2. **PLUGIN_INFO Dictionary**: Contains metadata
3. **Optional Dependencies**: Listed in requirements

```
my_plugin/
├── __init__.py          # Plugin module
├── validator.py         # Main validator implementation
├── tests/               # Test files
│   ├── __init__.py
│   └── test_validator.py
├── requirements.txt     # Plugin dependencies
└── README.md           # Plugin documentation
```

### PLUGIN_INFO Schema

```python
PLUGIN_INFO = {
    # Required fields
    "name": "unique_plugin_name",           # Unique identifier
    "version": "1.0.0",                     # Semantic version
    "description": "What this plugin does", # Brief description
    "author": "Name <email@example.com>",   # Author info
    "validator_class": YourValidatorClass,   # Validator class reference

    # Optional fields
    "dependencies": ["requests", "lxml"],    # Required packages
    "tags": ["web", "api", "validation"],   # Searchable tags
    "minimum_python": "3.8",               # Minimum Python version
    "homepage": "https://github.com/...",   # Project homepage
    "documentation": "https://docs...",     # Documentation URL
    "license": "MIT",                       # License identifier
}
```

### Validator Implementation Requirements

```python
class MyValidator(BaseValidator):
    def __init__(self, name: str = "my_validator", **kwargs):
        # Call parent constructor
        super().__init__(name, "Validator description")

        # Store configuration
        self.config = kwargs

    def validate(self, output: str, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """
        Main validation method - REQUIRED

        Args:
            output: The string to validate
            context: Optional context dictionary

        Returns:
            ValidationResult with is_valid, errors, warnings, metadata, score
        """
        # Your validation logic here

        return ValidationResult(
            is_valid=True,  # or False
            errors=[],      # List of error messages
            warnings=[],    # List of warning messages
            metadata={},    # Additional info dictionary
            score=1.0       # Optional quality score (0.0-1.0)
        )

    def get_validation_instructions(self) -> str:
        """
        Optional: Provide instructions for LLM

        Returns:
            String with validation requirements
        """
        return "Output must meet the following criteria: ..."
```

## Development Workflow

### 1. Setup Development Environment

```bash
# Clone the validated-llm repository
git clone https://github.com/your-org/validated-llm.git
cd validated-llm

# Install in development mode
poetry install

# Create plugin directory
mkdir -p plugins/my_plugin
cd plugins/my_plugin
```

### 2. Plugin Development Steps

#### Step 1: Define Requirements

Create a specification document:

```markdown
# My Plugin Specification

## Purpose

Validate social security numbers with format checking and verification.

## Requirements

- Support multiple SSN formats (XXX-XX-XXXX, XXXXXXXXX)
- Validate format correctness
- Optional: Check against known invalid patterns
- Configurable strict mode

## Input/Output

- Input: String containing potential SSN
- Output: ValidationResult with format validation

## Configuration

- strict_mode: Enable additional checks
- allow_dashes: Accept dashed format
- mask_output: Mask SSN in metadata for security
```

#### Step 2: Implement Core Logic

```python
# ssn_validator.py
import re
from typing import Dict, Any, Optional
from validated_llm.base_validator import BaseValidator, ValidationResult

class SSNValidator(BaseValidator):
    """Social Security Number validator with format checking"""

    def __init__(self,
                 name: str = "ssn_validator",
                 strict_mode: bool = False,
                 allow_dashes: bool = True,
                 mask_output: bool = True):
        super().__init__(name, "Validates Social Security Number format")
        self.strict_mode = strict_mode
        self.allow_dashes = allow_dashes
        self.mask_output = mask_output

        # Known invalid SSN patterns
        self.invalid_patterns = [
            "000-00-0000", "111-11-1111", "222-22-2222",
            "333-33-3333", "444-44-4444", "555-55-5555",
            "666-66-6666", "777-77-7777", "888-88-8888",
            "999-99-9999"
        ]

    def validate(self, output: str, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        ssn = output.strip()
        errors = []
        warnings = []

        # Normalize SSN (remove dashes/spaces)
        normalized_ssn = re.sub(r'[^d]', '', ssn)

        # Check length
        if len(normalized_ssn) != 9:
            errors.append(f"SSN must be 9 digits, got {len(normalized_ssn)}")
            return ValidationResult(is_valid=False, errors=errors)

        # Check format
        if self.allow_dashes:
            dash_pattern = r'^d{3}-d{2}-d{4}'
            no_dash_pattern = r'^d{9}'

            if not (re.match(dash_pattern, ssn) or re.match(no_dash_pattern, ssn)):
                errors.append("SSN format must be XXX-XX-XXXX or XXXXXXXXX")
        else:
            if not re.match(r'^d{9}', ssn):
                errors.append("SSN format must be XXXXXXXXX (no dashes allowed)")

        # Strict mode checks
        if self.strict_mode:
            # Check for sequential numbers
            if self._is_sequential(normalized_ssn):
                warnings.append("SSN appears to be sequential (may be test data)")

            # Check against known invalid patterns
            formatted_ssn = f"{normalized_ssn[:3]}-{normalized_ssn[3:5]}-{normalized_ssn[5:]}"
            if formatted_ssn in self.invalid_patterns:
                errors.append("SSN matches known invalid pattern")

        # Prepare metadata
        metadata = {
            "format": "dashed" if "-" in ssn else "no_dashes",
            "area_number": normalized_ssn[:3]
        }

        if self.mask_output:
            metadata["masked_ssn"] = f"XXX-XX-{normalized_ssn[5:]}"
        else:
            metadata["ssn"] = formatted_ssn

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            metadata=metadata
        )

    def _is_sequential(self, ssn: str) -> bool:
        """Check if SSN contains sequential digits"""
        for i in range(len(ssn) - 2):
            if (int(ssn[i]) + 1 == int(ssn[i+1]) and
                int(ssn[i+1]) + 1 == int(ssn[i+2])):
                return True
        return False

    def get_validation_instructions(self) -> str:
        instructions = [
            "Social Security Number must be in format XXX-XX-XXXX or XXXXXXXXX",
            "Must contain exactly 9 digits"
        ]

        if self.strict_mode:
            instructions.extend([
                "Avoid sequential numbers (123-45-6789)",
                "Avoid known invalid patterns (000-00-0000, etc.)"
            ])

        return "n".join(f"- {instruction}" for instruction in instructions)

# Plugin metadata
PLUGIN_INFO = {
    "name": "ssn_validator",
    "version": "1.0.0",
    "description": "Validates Social Security Number format with security features",
    "author": "Your Name <your.email@example.com>",
    "validator_class": SSNValidator,
    "dependencies": [],
    "tags": ["ssn", "security", "personal-data", "validation"],
    "minimum_python": "3.8",
    "license": "MIT"
}
```

#### Step 3: Write Comprehensive Tests

```python
# tests/test_ssn_validator.py
import pytest
from ssn_validator import SSNValidator

class TestSSNValidator:

    @pytest.fixture
    def validator(self):
        return SSNValidator()

    @pytest.fixture
    def strict_validator(self):
        return SSNValidator(strict_mode=True)

    def test_valid_ssn_formats(self, validator):
        """Test valid SSN formats"""
        valid_ssns = [
            "123-45-6789",
            "123456789",
            "987-65-4321"
        ]

        for ssn in valid_ssns:
            result = validator.validate(ssn)
            assert result.is_valid, f"SSN should be valid: {ssn}"
            assert len(result.errors) == 0

    def test_invalid_ssn_formats(self, validator):
        """Test invalid SSN formats"""
        invalid_ssns = [
            "12-345-6789",    # Wrong format
            "123-4-56789",    # Wrong format
            "123-45-67890",   # Too many digits
            "123-45-678",     # Too few digits
            "abc-de-fghi",    # Non-numeric
            ""                # Empty
        ]

        for ssn in invalid_ssns:
            result = validator.validate(ssn)
            assert not result.is_valid, f"SSN should be invalid: {ssn}"
            assert len(result.errors) > 0

    def test_strict_mode_validation(self, strict_validator):
        """Test strict mode features"""
        # Sequential SSN should trigger warning
        result = strict_validator.validate("123-45-6789")
        assert result.is_valid  # Format is valid
        assert len(result.warnings) > 0  # But has warning

        # Known invalid pattern should fail
        result = strict_validator.validate("000-00-0000")
        assert not result.is_valid
        assert "invalid pattern" in str(result.errors).lower()

    def test_configuration_options(self):
        """Test validator configuration"""
        # No dashes allowed
        no_dash_validator = SSNValidator(allow_dashes=False)

        result = no_dash_validator.validate("123-45-6789")
        assert not result.is_valid  # Dashes not allowed

        result = no_dash_validator.validate("123456789")
        assert result.is_valid  # No dashes OK

        # Masking disabled
        no_mask_validator = SSNValidator(mask_output=False)
        result = no_mask_validator.validate("123-45-6789")
        assert "ssn" in result.metadata
        assert "masked_ssn" not in result.metadata

    def test_metadata_content(self, validator):
        """Test metadata extraction"""
        result = validator.validate("123-45-6789")

        assert result.is_valid
        assert result.metadata["format"] == "dashed"
        assert result.metadata["area_number"] == "123"
        assert "masked_ssn" in result.metadata
        assert result.metadata["masked_ssn"] == "XXX-XX-6789"

    def test_validation_instructions(self, validator):
        """Test instruction generation"""
        instructions = validator.get_validation_instructions()
        assert "XXX-XX-XXXX" in instructions
        assert "9 digits" in instructions

    @pytest.mark.parametrize("ssn,expected_format", [
        ("123-45-6789", "dashed"),
        ("123456789", "no_dashes"),
        (" 123-45-6789 ", "dashed"),  # With whitespace
    ])
    def test_format_detection(self, validator, ssn, expected_format):
        """Test format detection"""
        result = validator.validate(ssn)
        if result.is_valid:
            assert result.metadata["format"] == expected_format
```

#### Step 4: Add Integration Tests

```python
# tests/test_integration.py
from validated_llm.plugins.manager import get_manager
from pathlib import Path

def test_plugin_loading():
    """Test that plugin loads correctly"""
    manager = get_manager()
    manager.add_search_path(Path(__file__).parent.parent)
    manager.initialize()

    # Check plugin is discovered
    plugins = manager.list_plugins()
    ssn_plugins = [p for p in plugins if p.name == "ssn_validator"]
    assert len(ssn_plugins) == 1

    plugin = ssn_plugins[0]
    assert plugin.version == "1.0.0"
    assert "ssn" in plugin.tags

def test_plugin_usage():
    """Test using plugin through manager"""
    manager = get_manager()
    manager.add_search_path(Path(__file__).parent.parent)
    manager.initialize()

    # Create validator instance
    validator = manager.create_validator("ssn_validator", strict_mode=True)

    # Test validation
    result = validator.validate("123-45-6789")
    assert result.is_valid
    assert result.metadata["area_number"] == "123"
```

### 3. Development Best Practices

#### Error Handling

```python
def validate(self, output: str, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
    try:
        # Validation logic here
        pass
    except Exception as e:
        # Log the error but don't crash
        return ValidationResult(
            is_valid=False,
            errors=[f"Validation error: {str(e)}"],
            metadata={"exception": type(e).__name__}
        )
```

#### Performance Considerations

```python
class OptimizedValidator(BaseValidator):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Pre-compile regex patterns
        self.pattern = re.compile(r'^[a-zA-Z0-9]+')

        # Cache expensive operations
        self._cache = {}

    def validate(self, output: str, context=None) -> ValidationResult:
        # Use cached results when possible
        if output in self._cache:
            return self._cache[output]

        # Perform validation
        result = self._do_validation(output)

        # Cache result (with size limit)
        if len(self._cache) < 1000:
            self._cache[output] = result

        return result
```

#### Security Considerations

```python
class SecureValidator(BaseValidator):
    def validate(self, output: str, context=None) -> ValidationResult:
        # Input sanitization
        if len(output) > 10000:  # Reasonable size limit
            return ValidationResult(
                is_valid=False,
                errors=["Input too large"]
            )

        # Avoid logging sensitive data
        metadata = {
            "length": len(output),
            "has_special_chars": bool(re.search(r'[^a-zA-Z0-9]', output))
            # Don't include the actual content
        }

        return ValidationResult(
            is_valid=True,
            metadata=metadata
        )
```

## Testing Your Plugin

### 1. Unit Testing Strategy

```python
# Complete test suite structure
tests/
├── __init__.py
├── test_basic_validation.py     # Basic functionality
├── test_edge_cases.py          # Edge cases and error conditions
├── test_configuration.py       # Configuration options
├── test_performance.py         # Performance benchmarks
├── test_integration.py         # Plugin system integration
└── test_security.py           # Security considerations
```

### 2. Test Coverage

```bash
# Install coverage tools
pip install pytest-cov

# Run tests with coverage
pytest --cov=your_plugin --cov-report=html tests/

# View coverage report
open htmlcov/index.html
```

### 3. Performance Testing

```python
# test_performance.py
import time
import pytest
from your_plugin import YourValidator

class TestPerformance:

    @pytest.fixture
    def validator(self):
        return YourValidator()

    def test_validation_speed(self, validator):
        """Ensure validation completes quickly"""
        test_input = "sample input for testing"

        times = []
        for _ in range(100):
            start = time.time()
            validator.validate(test_input)
            times.append(time.time() - start)

        avg_time = sum(times) / len(times)
        assert avg_time < 0.01  # Less than 10ms average

    def test_memory_usage(self, validator):
        """Check memory usage doesn't grow excessively"""
        import tracemalloc

        tracemalloc.start()

        # Validate many inputs
        for i in range(1000):
            validator.validate(f"test input {i}")

        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        # Should not use more than 10MB
        assert peak < 10 * 1024 * 1024
```

## Plugin Packaging

### 1. Package Structure

```
my_plugin_package/
├── setup.py                    # Package setup
├── pyproject.toml             # Modern Python packaging
├── README.md                  # Package documentation
├── LICENSE                    # License file
├── CHANGELOG.md              # Version history
├── my_plugin/                # Package directory
│   ├── __init__.py           # Package init
│   ├── validator.py          # Main validator
│   └── utils.py              # Helper functions
├── tests/                    # Test suite
│   ├── __init__.py
│   └── test_validator.py
└── examples/                 # Usage examples
    └── basic_usage.py
```

### 2. Setup Configuration

```python
# setup.py
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="validated-llm-my-plugin",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A custom validator plugin for validated-llm",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/validated-llm-my-plugin",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Linguistic",
    ],
    python_requires=">=3.8",
    install_requires=[
        "validated-llm>=1.0.0",
        # Add your dependencies here
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "mypy>=0.900",
        ],
        "test": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
        ],
    },
    entry_points={
        "validated_llm.plugins": [
            "my_validator = my_plugin.validator:PLUGIN_INFO",
        ],
    },
)
```

### 3. Modern Packaging with pyproject.toml

```toml
# pyproject.toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "validated-llm-my-plugin"
version = "1.0.0"
description = "A custom validator plugin for validated-llm"
readme = "README.md"
license = {file = "LICENSE"}
authors = [
    {name = "Your Name", email = "your.email@example.com"},
]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
]
requires-python = ">=3.8"
dependencies = [
    "validated-llm>=1.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=6.0",
    "pytest-cov>=2.0",
    "black>=21.0",
    "mypy>=0.900",
]
test = [
    "pytest>=6.0",
    "pytest-cov>=2.0",
]

[project.urls]
Homepage = "https://github.com/yourusername/validated-llm-my-plugin"
Documentation = "https://validated-llm-my-plugin.readthedocs.io/"
Repository = "https://github.com/yourusername/validated-llm-my-plugin.git"
"Bug Tracker" = "https://github.com/yourusername/validated-llm-my-plugin/issues"

[project.entry-points."validated_llm.plugins"]
my_validator = "my_plugin.validator:PLUGIN_INFO"

[tool.setuptools.packages.find]
where = ["."]
include = ["my_plugin*"]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]

[tool.mypy]
python_version = "3.8"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true

[tool.black]
line-length = 88
target-version = ['py38']
```

## Distribution Strategies

### 1. PyPI Distribution

```bash
# Build package
python -m build

# Upload to TestPyPI first
python -m twine upload --repository testpypi dist/*

# Test installation
pip install --index-url https://test.pypi.org/simple/ validated-llm-my-plugin

# Upload to PyPI
python -m twine upload dist/*
```

### 2. GitHub Package Registry

```yaml
# .github/workflows/publish.yml
name: Publish Package

on:
  release:
    types: [published]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install build twine
      - name: Build package
        run: python -m build
      - name: Publish to PyPI
        uses: pypa/gh-action-pypi-publish@release/v1
        with:
          password: { { secrets.PYPI_API_TOKEN } }
```

### 3. Direct Installation

```bash
# Install from Git repository
pip install git+https://github.com/yourusername/validated-llm-my-plugin.git

# Install from local development
pip install -e .

# Install specific version
pip install git+https://github.com/yourusername/validated-llm-my-plugin.git@v1.0.0
```

### 4. Private Package Distribution

```python
# For private/enterprise plugins
# setup.py with private index
setup(
    # ... other setup parameters
    index_url="https://your-private-pypi.com/simple/",
    dependency_links=[
        "https://your-private-repo.com/packages/",
    ],
)
```

## Best Practices

### 1. Documentation

Create comprehensive documentation:

````markdown
# My Plugin Documentation

## Installation

```bash
pip install validated-llm-my-plugin
```
````

## Quick Start

```python
from validated_llm.plugins.manager import get_manager

manager = get_manager()
manager.initialize()

validator = manager.create_validator("my_validator")
result = validator.validate("test input")
```

## Configuration Options

| Option        | Type | Default | Description              |
| ------------- | ---- | ------- | ------------------------ |
| `strict_mode` | bool | False   | Enable strict validation |
| `timeout`     | int  | 30      | Timeout in seconds       |

## Examples

### Basic Usage

[Include working examples]

### Advanced Configuration

[Include advanced examples]

## API Reference

### MyValidator Class

[Document all methods and parameters]

## Changelog

### Version 1.0.0

- Initial release
- Basic validation functionality

````

### 2. Version Management

Follow semantic versioning:

```python
# version.py
__version__ = "1.0.0"

# Major.Minor.Patch
# Major: Breaking changes
# Minor: New features (backward compatible)
# Patch: Bug fixes
````

### 3. Continuous Integration

```yaml
# .github/workflows/test.yml
name: Test Suite

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, '3.10', 3.11]

    steps:
      - uses: actions/checkout@v3
      - name: Set up Python {{ matrix.python-version }}
        uses: actions/setup-python@v4
        with:
          python-version: { { matrix.python-version } }

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -e .[dev]

      - name: Run tests
        run: |
          pytest --cov=my_plugin --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml

      - name: Type checking
        run: mypy my_plugin/

      - name: Code formatting
        run: black --check my_plugin/ tests/
```

### 4. Security Guidelines

```python
# Security best practices
class SecureValidator(BaseValidator):
    def validate(self, output: str, context=None) -> ValidationResult:
        # 1. Input validation
        if not isinstance(output, str):
            return ValidationResult(
                is_valid=False,
                errors=["Input must be a string"]
            )

        # 2. Size limits
        if len(output) > self.MAX_INPUT_SIZE:
            return ValidationResult(
                is_valid=False,
                errors=["Input too large"]
            )

        # 3. Sanitize logging
        safe_preview = output[:50] + "..." if len(output) > 50 else output
        logger.debug(f"Validating input: {safe_preview}")

        # 4. No sensitive data in metadata
        metadata = {
            "input_length": len(output),
            "validation_time": time.time()
            # Don't include actual content
        }

        return ValidationResult(is_valid=True, metadata=metadata)
```

## Troubleshooting

### Common Issues

#### 1. Plugin Not Found

```python
# Check plugin search paths
from validated_llm.plugins.manager import get_manager

manager = get_manager()
print("Search paths:", manager.discovery._search_paths)

# Add your plugin directory
manager.add_search_path(Path("/path/to/your/plugin"))
manager.initialize()
```

#### 2. Import Errors

```python
# Check plugin info
try:
    from your_plugin import PLUGIN_INFO
    print("Plugin info:", PLUGIN_INFO)
except ImportError as e:
    print("Import error:", e)

# Check validator class
try:
    validator_class = PLUGIN_INFO["validator_class"]
    instance = validator_class()
    print("Validator created successfully")
except Exception as e:
    print("Validation creation error:", e)
```

#### 3. Validation Issues

```python
# Debug validation
validator = your_validator_instance

try:
    result = validator.validate("test")
    print("Validation result:", result)
    print("Valid:", result.is_valid)
    print("Errors:", result.errors)
    print("Metadata:", result.metadata)
except Exception as e:
    print("Validation error:", e)
    import traceback
    traceback.print_exc()
```

#### 4. Performance Problems

```python
# Profile your validator
import cProfile
import pstats

def profile_validation():
    validator = your_validator_instance
    for i in range(1000):
        validator.validate(f"test input {i}")

cProfile.run('profile_validation()', 'profile_stats')
stats = pstats.Stats('profile_stats')
stats.sort_stats('cumulative').print_stats(10)
```

### Getting Help

1. **Check Documentation**: Review this guide and the main validated-llm docs
2. **Search Issues**: Look for similar problems in the GitHub issues
3. **Debug Step by Step**: Use the debugging techniques above
4. **Community Support**: Ask questions in discussions or issues
5. **Professional Support**: Consider consulting for complex custom validators

---

This comprehensive guide should help you develop, test, and distribute high-quality validator plugins for the validated-llm framework. Remember to follow best practices for security, performance, and maintainability.
