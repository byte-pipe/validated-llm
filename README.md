# validated-llm

[![PyPI version](https://badge.fury.io/py/validated-llm.svg)](https://badge.fury.io/py/validated-llm)
[![Python Support](https://img.shields.io/pypi/pyversions/validated-llm.svg)](https://pypi.org/project/validated-llm/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

LLM output validation with retry loops - ensure your language model responses meet requirements.

## Overview

`validated-llm` provides a robust framework for validating language model outputs with automatic retry mechanisms. It's designed for applications where you need reliable, structured responses from LLMs.

## Key Features

- **Automatic Retry Logic**: Handles failed validations with configurable retry attempts
- **Flexible Validation**: Support for JSON schema, custom validators, and Pydantic models
- **Multiple LLM Providers**: Works with OpenAI, Anthropic, and other OpenAI-compatible APIs
- **Task-Based Architecture**: Organize validation logic into reusable task classes
- **Comprehensive Logging**: Track validation attempts and failures for debugging

## Quick Start

### Installation

```bash
pip install validated-llm
```

### Basic Usage

```python
from validated_llm import ValidationLoop, BaseTask
from pydantic import BaseModel
from typing import List

class StoryScene(BaseModel):
    title: str
    description: str
    characters: List[str]

class StoryToScenesTask(BaseTask):
    def get_prompt(self, story_text: str) -> str:
        return f"""
        Convert this story into 3-5 scenes:
        {story_text}

        Return as JSON with scenes array containing title, description, and characters.
        """

    def validate_response(self, response_text: str) -> bool:
        try:
            data = json.loads(response_text)
            scenes = [StoryScene(**scene) for scene in data['scenes']]
            return len(scenes) >= 3
        except:
            return False

# Use the task
validator = ValidationLoop(
    model="gpt-4",
    max_retries=3,
    temperature=0.7
)

task = StoryToScenesTask()
result = validator.run_task(task, "Once upon a time...")
print(result)  # Validated JSON response
```

### Built-in Tasks

The package includes several pre-built validation tasks:

#### JSON Generation
```python
from validated_llm.tasks import JSONGenerationTask

task = JSONGenerationTask(
    schema={
        "type": "object",
        "properties": {
            "scenes": {
                "type": "array",
                "items": {"type": "object"}
            }
        },
        "required": ["scenes"]
    }
)
```

#### CSV Generation
```python
from validated_llm.tasks import CSVGenerationTask

task = CSVGenerationTask(
    required_columns=["name", "age", "role"],
    min_rows=3
)
```

## Architecture

### Core Components

1. **ValidationLoop**: Main orchestrator that handles the retry logic
2. **BaseTask**: Abstract base class for creating validation tasks
3. **BaseValidator**: Pluggable validation system for different response types

### Creating Custom Tasks

```python
class CustomTask(BaseTask):
    def get_prompt(self, input_data: str) -> str:
        # Return the prompt for the LLM
        return f"Process this data: {input_data}"

    def validate_response(self, response: str) -> bool:
        # Return True if response is valid
        return len(response) > 10

    def parse_response(self, response: str) -> dict:
        # Optional: transform the response
        return {"processed": response}
```

## Configuration

### LLM Provider Setup

```python
# OpenAI (default)
validator = ValidationLoop(
    model="gpt-4",
    api_key="your-api-key"
)

# Custom endpoint (e.g., local LLM)
validator = ValidationLoop(
    model="llama2",
    base_url="http://localhost:11434/v1/",
    api_key="not-needed"
)
```

### Retry Configuration

```python
validator = ValidationLoop(
    model="gpt-4",
    max_retries=5,           # Maximum retry attempts
    temperature=0.7,         # LLM temperature
    timeout=30,              # Request timeout in seconds
    backoff_factor=1.5       # Exponential backoff multiplier
)
```

## Advanced Usage

### Custom Validators

```python
from validated_llm import BaseValidator

class SchemaValidator(BaseValidator):
    def __init__(self, schema: dict):
        self.schema = schema

    def validate(self, response: str) -> tuple[bool, str]:
        try:
            data = json.loads(response)
            # Validate against schema
            return True, "Valid JSON"
        except Exception as e:
            return False, f"Invalid: {e}"
```

### Error Handling

```python
from validated_llm.exceptions import ValidationError, MaxRetriesExceeded

try:
    result = validator.run_task(task, input_data)
except MaxRetriesExceeded:
    print("Failed after maximum retries")
except ValidationError as e:
    print(f"Validation failed: {e}")
```

## Testing

Run the test suite:

```bash
poetry run pytest
```

With coverage:

```bash
poetry run pytest --cov=src tests/
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make changes and add tests
4. Run tests: `poetry run pytest`
5. Format code: `poetry run black . && poetry run isort .`
6. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Examples

See the `examples/` directory for more detailed usage examples:

- `basic_validation.py` - Simple validation example
- `custom_task.py` - Creating custom validation tasks
- `multiple_providers.py` - Using different LLM providers
- `story_to_scenes.py` - Real-world story processing example
