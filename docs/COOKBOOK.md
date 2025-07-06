# Validated-LLM Cookbook

A comprehensive guide to using the validated-llm framework effectively, with practical examples and best practices.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Core Concepts](#core-concepts)
3. [Common Patterns](#common-patterns)
4. [Validator Selection Guide](#validator-selection-guide)
5. [Task Development](#task-development)
6. [Error Handling](#error-handling)
7. [Performance Optimization](#performance-optimization)
8. [Plugin Development](#plugin-development)
9. [Integration Patterns](#integration-patterns)
10. [Troubleshooting](#troubleshooting)

## Quick Start

### Basic Usage

The simplest way to validate LLM output:

```python
from validated_llm.validation_loop import ValidationLoop
from validated_llm.tasks.json_generation import PersonJSONTask

# Create a task
task = PersonJSONTask()

# Execute with validation
loop = ValidationLoop(task)
result = loop.execute({"name": "Alice", "age": 30})

print(result.validated_output)  # Guaranteed valid JSON
```

### Using Built-in Validators

```python
from validated_llm.validators.email import EmailValidator
from validated_llm.validators.json_schema import JSONSchemaValidator

# Simple validation
email_validator = EmailValidator()
result = email_validator.validate("user@example.com")
print(result.is_valid)  # True

# Complex schema validation
schema = {
    "type": "object",
    "properties": {
        "users": {
            "type": "array",
            "items": {"type": "string", "format": "email"}
        }
    },
    "required": ["users"]
}

json_validator = JSONSchemaValidator(schema=schema)
result = json_validator.validate('{"users": ["alice@example.com", "bob@example.com"]}')
print(result.is_valid)  # True
```

## Core Concepts

### ValidationResult Structure

All validators return a `ValidationResult` object:

```python
from validated_llm.base_validator import ValidationResult

# Understanding the result structure
result = validator.validate(output)

print(result.is_valid)        # Boolean: True if valid
print(result.errors)          # List[str]: Error messages
print(result.warnings)        # List[str]: Warning messages
print(result.metadata)        # Dict[str, Any]: Additional info
print(result.score)           # Optional[float]: Quality score
```

### Task vs Validator Distinction

- **Tasks**: Complete workflows (prompt + validator + data preparation)
- **Validators**: Pure validation logic (no LLM interaction)

```python
# Task: Complete workflow
from validated_llm.tasks.json_generation import PersonJSONTask
task = PersonJSONTask()
result = loop.execute(data)  # Includes LLM generation + validation

# Validator: Pure validation
from validated_llm.validators.json_schema import JSONSchemaValidator
validator = JSONSchemaValidator(schema=schema)
result = validator.validate(json_string)  # Just validation
```

## Common Patterns

### 1. JSON Generation with Schema Validation

Perfect for structured data generation:

```python
from validated_llm.tasks.json_generation import JSONGenerationTask
from validated_llm.validation_loop import ValidationLoop

# Define your schema
user_schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string", "minLength": 1},
        "email": {"type": "string", "format": "email"},
        "age": {"type": "integer", "minimum": 0, "maximum": 150},
        "preferences": {
            "type": "array",
            "items": {"type": "string"},
            "uniqueItems": True
        }
    },
    "required": ["name", "email", "age"],
    "additionalProperties": False
}

# Create task
task = JSONGenerationTask(
    name="user_profile",
    prompt_template="Generate a user profile with name, email, age, and preferences for: {description}",
    schema=user_schema
)

# Execute
loop = ValidationLoop(task)
result = loop.execute({"description": "a software developer who likes coffee and cycling"})
```

### 2. Code Generation with Multi-Language Support

Generate syntactically correct code:

```python
from validated_llm.tasks.code_generation import FunctionGenerationTask
from validated_llm.validation_loop import ValidationLoop

# Python function generation
python_task = FunctionGenerationTask(
    language="python",
    name="binary_search_function",
    prompt_template="Write a binary search function that {requirement}",
    requirements=["handles edge cases", "includes docstring", "uses type hints"]
)

loop = ValidationLoop(python_task)
result = loop.execute({
    "requirement": "searches for a target value in a sorted list"
})

print(result.validated_output)  # Syntactically correct Python function
```

### 3. Document Generation with Structure Validation

Create well-structured documentation:

```python
from validated_llm.tasks.documentation import APIDocumentationTask
from validated_llm.validation_loop import ValidationLoop

# API documentation generation
doc_task = APIDocumentationTask(
    name="rest_api_docs",
    required_sections=["overview", "authentication", "endpoints", "examples"],
    format_style="markdown"
)

loop = ValidationLoop(doc_task)
result = loop.execute({
    "api_name": "User Management API",
    "endpoints": ["/users", "/users/{id}", "/users/{id}/profile"],
    "auth_method": "Bearer token"
})
```

### 4. Composite Validation with Multiple Criteria

Combine multiple validators for complex requirements:

```python
from validated_llm.validators.composite import CompositeValidator
from validated_llm.validators.markdown import MarkdownValidator
from validated_llm.validators.range import RangeValidator

# Create composite validator
composite = CompositeValidator(
    name="article_validator",
    validators=[
        MarkdownValidator(name="format_check"),
        RangeValidator(name="length_check", min_value=500, max_value=2000, unit="words")
    ],
    combination_logic="AND"  # All validators must pass
)

result = composite.validate(article_text)
```

### 5. Email Template Validation

Validate email content for completeness and format:

```python
from validated_llm.tasks.prompt_to_task_generated.email_task import EmailTask
from validated_llm.validation_loop import ValidationLoop

email_task = EmailTask()
loop = ValidationLoop(email_task)

result = loop.execute({
    "recipient": "customer",
    "purpose": "password reset instructions",
    "tone": "professional and helpful"
})

# Result will be a properly formatted email with subject and body
```

## Validator Selection Guide

### When to Use Each Validator

| Use Case              | Recommended Validator                         | Example             |
| --------------------- | --------------------------------------------- | ------------------- |
| User input validation | `EmailValidator`, `PhoneNumberValidator`      | Contact forms       |
| API responses         | `JSONSchemaValidator`                         | REST API validation |
| Configuration files   | `YAMLValidator`, `ConfigValidator`            | App settings        |
| Generated code        | `SyntaxValidator`, `StyleValidator`           | Code generation     |
| Documentation         | `MarkdownValidator`, `DocumentationValidator` | Technical writing   |
| Data files            | `XMLValidator` with XSD                       | Data interchange    |
| Database queries      | `SQLValidator`                                | Query generation    |
| Content moderation    | `RegexValidator`, `RangeValidator`            | Text filtering      |
| Multi-step validation | `CompositeValidator`                          | Complex workflows   |

### Validator Configuration Examples

```python
# Email with custom domain restrictions
email_validator = EmailValidator(
    allowed_domains=["company.com", "partner.org"],
    require_mx_record=True
)

# JSON Schema with strict mode
json_validator = JSONSchemaValidator(
    schema=schema,
    strict_mode=True,  # No additional properties
    validate_formats=True  # Validate format fields
)

# Range validator for different units
word_count = RangeValidator(min_value=100, max_value=500, unit="words")
char_count = RangeValidator(min_value=1000, max_value=5000, unit="characters")
line_count = RangeValidator(min_value=10, max_value=50, unit="lines")

# SQL with specific dialect
sql_validator = SQLValidator(
    dialect="postgresql",
    require_semicolon=True,
    check_syntax_only=False  # Also validate semantics
)
```

## Task Development

### Creating Custom Tasks

Follow this pattern for new tasks:

```python
from validated_llm.tasks.base_task import BaseTask
from validated_llm.validators.your_validator import YourValidator

class CustomTask(BaseTask):
    def __init__(self, name: str = "custom_task", **kwargs):
        # Define your prompt template
        prompt_template = """
        Create a {content_type} that meets the following criteria:
        - Topic: {topic}
        - Length: {length}
        - Style: {style}

        Requirements:
        {requirements}
        """

        # Initialize validator
        validator = YourValidator(**kwargs)

        super().__init__(
            name=name,
            prompt_template=prompt_template,
            validator=validator
        )

    def prepare_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare and validate input data"""
        # Add default values
        data.setdefault("style", "professional")
        data.setdefault("length", "medium")

        # Validate required fields
        required = ["topic", "content_type"]
        for field in required:
            if field not in data:
                raise ValueError(f"Required field missing: {field}")

        return data
```

### Task Best Practices

1. **Clear prompt templates**: Be specific about requirements
2. **Input validation**: Validate data in `prepare_data()`
3. **Sensible defaults**: Provide reasonable default values
4. **Error handling**: Give helpful error messages
5. **Documentation**: Include docstrings and examples

```python
class WellDesignedTask(BaseTask):
    """
    Generate marketing copy for products.

    Args:
        target_audience: Primary audience (required)
        tone: Writing tone ("professional", "casual", "enthusiastic")
        word_limit: Maximum word count (default: 150)

    Example:
        task = MarketingCopyTask()
        result = loop.execute({
            "product": "eco-friendly water bottle",
            "target_audience": "environmentally conscious millennials",
            "tone": "enthusiastic"
        })
    """
    pass
```

## Error Handling

### Understanding Validation Errors

```python
from validated_llm.validation_loop import ValidationLoop
from validated_llm.tasks.json_generation import PersonJSONTask

task = PersonJSONTask()
loop = ValidationLoop(task, max_retries=3)

try:
    result = loop.execute(data)
    if result.success:
        print("Success:", result.validated_output)
    else:
        print("Failed after retries:", result.final_error)
        print("Attempts:", len(result.attempts))

        # Examine each attempt
        for i, attempt in enumerate(result.attempts):
            print(f"Attempt {i+1}:")
            print(f"  Output: {attempt.output}")
            print(f"  Valid: {attempt.validation_result.is_valid}")
            if not attempt.validation_result.is_valid:
                print(f"  Errors: {attempt.validation_result.errors}")

except Exception as e:
    print(f"Unexpected error: {e}")
```

### Custom Error Formatting

```python
from validated_llm.error_formatting import format_validation_errors

# Custom error formatting for better LLM feedback
def format_errors_for_llm(validation_result):
    if validation_result.is_valid:
        return "Output is valid."

    formatted = format_validation_errors(validation_result.errors)

    # Add helpful hints
    hints = []
    if "JSON" in str(validation_result.errors):
        hints.append("Remember to use proper JSON syntax with double quotes.")
    if "required" in str(validation_result.errors):
        hints.append("Make sure all required fields are included.")

    if hints:
        formatted += "nnHints:n" + "n".join(f"- {hint}" for hint in hints)

    return formatted
```

## Performance Optimization

### Caching Validators

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_validator(validator_type: str, **kwargs):
    """Cache validator instances for reuse"""
    if validator_type == "email":
        return EmailValidator(**kwargs)
    elif validator_type == "json_schema":
        return JSONSchemaValidator(**kwargs)
    # ... etc
```

### Batch Processing

```python
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any

def validate_batch(items: List[str], validator) -> List[ValidationResult]:
    """Validate multiple items in parallel"""
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(validator.validate, item) for item in items]
        return [future.result() for future in futures]

# Usage
results = validate_batch(email_list, EmailValidator())
valid_emails = [item for item, result in zip(email_list, results) if result.is_valid]
```

### Timeout Configuration

```python
from validated_llm.validation_loop import ValidationLoop

# Configure timeouts for better performance
loop = ValidationLoop(
    task=task,
    max_retries=3,
    timeout=30,  # 30 second timeout per attempt
    retry_delay=1.0  # 1 second between retries
)
```

## Plugin Development

### Creating a Custom Validator Plugin

```python
# my_plugin.py
from validated_llm.base_validator import BaseValidator, ValidationResult
from typing import Dict, Any, Optional

class CreditCardValidator(BaseValidator):
    """Validates credit card numbers using Luhn algorithm"""

    def __init__(self, name: str = "credit_card_validator"):
        super().__init__(name, "Validates credit card numbers")

    def validate(self, output: str, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        # Remove spaces and dashes
        number = ''.join(output.split()).replace('-', '')

        # Check if all digits
        if not number.isdigit():
            return ValidationResult(
                is_valid=False,
                errors=["Credit card number must contain only digits"]
            )

        # Luhn algorithm
        def luhn_check(card_num):
            digits = [int(d) for d in card_num]
            for i in range(len(digits) - 2, -1, -2):
                digits[i] *= 2
                if digits[i] > 9:
                    digits[i] -= 9
            return sum(digits) % 10 == 0

        is_valid = luhn_check(number)

        return ValidationResult(
            is_valid=is_valid,
            errors=[] if is_valid else ["Invalid credit card number"],
            metadata={"card_type": self._detect_card_type(number)}
        )

    def _detect_card_type(self, number: str) -> str:
        if number.startswith('4'):
            return "Visa"
        elif number.startswith('5'):
            return "Mastercard"
        elif number.startswith('3'):
            return "American Express"
        return "Unknown"

# Plugin metadata (required)
PLUGIN_INFO = {
    "name": "credit_card_validator",
    "version": "1.0.0",
    "description": "Validates credit card numbers using the Luhn algorithm",
    "author": "Your Name",
    "validator_class": CreditCardValidator,
    "dependencies": [],
    "tags": ["finance", "validation", "credit-card"],
}
```

### Using the Plugin System

```python
from validated_llm.plugins.manager import get_manager

# Load and use plugins
manager = get_manager()
manager.initialize()

# List available plugins
plugins = manager.list_plugins()
for plugin in plugins:
    print(f"{plugin.name} v{plugin.version}: {plugin.description}")

# Use a plugin
validator = manager.create_validator("credit_card_validator")
result = validator.validate("4111111111111111")
```

## Integration Patterns

### Flask API Integration

```python
from flask import Flask, request, jsonify
from validated_llm.validation_loop import ValidationLoop
from validated_llm.tasks.json_generation import PersonJSONTask

app = Flask(__name__)

@app.route('/generate-user', methods=['POST'])
def generate_user():
    try:
        data = request.json

        task = PersonJSONTask()
        loop = ValidationLoop(task)
        result = loop.execute(data)

        if result.success:
            return jsonify({
                "success": True,
                "data": result.validated_output,
                "attempts": len(result.attempts)
            })
        else:
            return jsonify({
                "success": False,
                "error": result.final_error,
                "attempts": len(result.attempts)
            }), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500
```

### LangChain Migration

```python
# Convert existing LangChain prompts
from validated_llm.integrations.langchain.converter import PromptTemplateConverter

# If you have a LangChain prompt
langchain_prompt = PromptTemplate(
    input_variables=["topic"],
    template="Write an article about {topic}"
)

# Convert to validated-llm task
converter = PromptTemplateConverter()
task_code = converter.convert_prompt_template(
    prompt=langchain_prompt,
    task_name="ArticleTask"
)

print(task_code)  # Generated BaseTask subclass
```

### Configuration Management

```python
# .validated-llm.yml
validation:
  max_retries: 3
  timeout: 30

validators:
  email:
    require_mx_record: true
    allowed_domains: ["company.com"]

  json_schema:
    strict_mode: true
    validate_formats: true

tasks:
  PersonJSONTask:
    max_retries: 5

# Loading configuration
from validated_llm.config import load_config

config = load_config()
max_retries = config.get_task_setting("PersonJSONTask", "max_retries", default=3)
```

## Troubleshooting

### Common Issues and Solutions

#### 1. "Module not found" errors

```bash
# Ensure proper installation
poetry install

# Or install missing dependencies
poetry add missing-package
```

#### 2. Validation always fails

```python
# Debug the validator output
result = validator.validate(output)
print("Output:", repr(output))
print("Errors:", result.errors)
print("Metadata:", result.metadata)

# Check validator configuration
print("Validator config:", validator.__dict__)
```

#### 3. LLM not responding

```python
# Check ChatBot configuration
from chatbot.chatbot import ChatBot

bot = ChatBot(model="gemma3:27b")
response = bot.chat("Hello")  # Test basic connectivity
```

#### 4. Slow validation

```python
# Profile validation time
import time

start = time.time()
result = validator.validate(output)
print(f"Validation took {time.time() - start:.2f} seconds")

# Consider simpler validators or caching
```

#### 5. Plugin not loading

```python
# Check plugin search paths
from validated_llm.plugins.manager import get_manager

manager = get_manager()
manager.initialize()

print("Search paths:", manager.discovery._search_paths)
print("Available plugins:", [p.name for p in manager.list_plugins()])
```

### Debug Mode

```python
# Enable verbose logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Use debug methods
from validated_llm.validation_loop import ValidationLoop

loop = ValidationLoop(task, debug=True)
result = loop.execute(data)

# Examine detailed execution log
for attempt in result.attempts:
    print(f"Attempt: {attempt.attempt_number}")
    print(f"Prompt sent: {attempt.prompt}")
    print(f"Raw output: {attempt.raw_output}")
    print(f"Extracted: {attempt.output}")
    print(f"Valid: {attempt.validation_result.is_valid}")
```

## Best Practices Summary

1. **Start Simple**: Begin with built-in tasks and validators
2. **Validate Early**: Test validators independently before integration
3. **Clear Prompts**: Be specific about requirements and format
4. **Handle Errors**: Plan for validation failures and retries
5. **Monitor Performance**: Track validation times and success rates
6. **Use Configuration**: Centralize settings in config files
7. **Write Tests**: Test custom validators and tasks thoroughly
8. **Document**: Include examples and docstrings
9. **Version Control**: Tag plugin versions and track changes
10. **Community**: Share useful validators and patterns

## Getting Help

- **Documentation**: Check the README and ROADMAP for updates
- **Examples**: Look in the `examples/` directory for working code
- **Issues**: Report bugs and feature requests on GitHub
- **Community**: Share patterns and best practices

---

_This cookbook is maintained alongside the validated-llm framework. Contributions and improvements are welcome!_
