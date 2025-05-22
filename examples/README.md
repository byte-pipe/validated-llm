# Examples: Creating Custom Tasks

This directory contains examples of how to create your own custom tasks and validators for the `validated-llm` package.

## Overview

While the package comes with built-in tasks (JSON generation, CSV generation, story-to-scenes), you can easily create custom tasks tailored to your specific needs by:

1. **Creating a custom Task class** that inherits from `BaseTask`
2. **Creating a custom Validator class** that inherits from `BaseValidator`
3. **Defining your prompt template** with placeholders for dynamic data
4. **Implementing validation logic** specific to your output format

## Examples

### 1. Simple Email Generation Task

See [`custom_email_task.py`](./custom_email_task.py) for a straightforward example that:

- Generates professional emails with customizable tone and purpose
- Validates email structure (subject, greeting, closing, word count)
- Provides detailed error messages and warnings for LLM improvement

### 2. Complex Data Analysis Report Task

See [`complex_data_analysis_task.py`](./complex_data_analysis_task.py) for an advanced example that demonstrates:

- **Multi-section structured output** with 7 required sections
- **Statistical validation** - validates calculated statistics against actual data
- **Context-aware validation** - uses input data to verify calculations
- **Content depth validation** - ensures minimum insights, recommendations, visualizations
- **Professional language validation** - checks tone and actionability
- **Complex prompt engineering** - detailed formatting and requirements
- **Rich metadata** - tracks insights count, word count, validation metrics

This example generates comprehensive data analysis reports from raw datasets and validates:
- ✅ Required section structure (Executive Summary, Statistical Analysis, etc.)
- ✅ Statistical accuracy (mean, median, std dev calculations)
- ✅ Content quality (minimum 3 insights, 4 recommendations)
- ✅ Professional language and actionable recommendations
- ✅ Data visualization suggestions

### 3. Using Built-in Story-to-Scenes Task

See [`builtin_story_to_scenes_demo.py`](./builtin_story_to_scenes_demo.py) for an example of using the pre-built task:

- **Shows task structure** - How to use existing validated-llm tasks
- **Demonstrates integration** - ValidationLoop with built-in tasks
- **Expected output format** - YAML scenes for video generation
- **Complex validation** - Multi-section YAML validation with style rules

Additional story-to-scenes examples:
- [`builtin_story_to_scenes_full.py`](./builtin_story_to_scenes_full.py) - Complete working example with multiple stories (takes 30-60 seconds)
- [`builtin_story_to_scenes_simple.py`](./builtin_story_to_scenes_simple.py) - Minimal test case for quick validation

## Creating Your Own Custom Task

### Step 1: Define Your Task Class

```python
from validated_llm.tasks.base_task import BaseTask
from validated_llm.base_validator import BaseValidator
from typing import Type

class MyCustomTask(BaseTask):
    @property
    def name(self) -> str:
        return "My Custom Task"

    @property
    def description(self) -> str:
        return "Description of what this task does"

    @property
    def prompt_template(self) -> str:
        return """
        Your custom prompt template here with {placeholders}

        Clear instructions for the LLM about:
        - What to generate
        - Output format requirements
        - Any constraints or guidelines

        Your response:"""

    @property
    def validator_class(self) -> Type[BaseValidator]:
        return MyCustomValidator
```

### Step 2: Define Your Validator Class

```python
from validated_llm.base_validator import BaseValidator, ValidationResult
from typing import Any, Dict, Optional

class MyCustomValidator(BaseValidator):
    def __init__(self, **kwargs):
        super().__init__(
            name="my_custom_validator",
            description="Validates my custom output format"
        )
        # Store any configuration parameters

    def validate(self, content: str, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        errors = []
        warnings = []

        # Your validation logic here
        # Check format, structure, content quality, etc.

        if some_error_condition:
            errors.append("Specific error message for LLM feedback")

        if some_warning_condition:
            warnings.append("Warning message about potential issues")

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            metadata={"additional": "info"}
        )
```

### Step 3: Use Your Custom Task

```python
from validated_llm.validation_loop import ValidationLoop
from your_module import MyCustomTask

# Create task instance
task = MyCustomTask()

# Create validator (optionally with custom settings)
validator = task.create_validator()

# Create validation loop
loop = ValidationLoop(default_max_retries=3)

# Prepare input data
input_data = {
    "placeholder1": "value1",
    "placeholder2": "value2"
}

# Execute with your data
result = loop.execute(
    prompt_template=task.prompt_template,
    validator=validator,
    input_data=input_data
)

if result["success"]:
    print("Generated output:", result["output"])
    print(f"Success after {result['attempts']} attempts")
else:
    print("Failed to generate valid output")
    if result["validation_result"]:
        for error in result["validation_result"].errors:
            print(f"  - {error}")
```

## Key Design Principles

### 1. **Clear Prompt Templates**
- Use descriptive placeholders like `{recipient}`, `{tone}`, `{data_description}`
- Provide clear output format requirements
- Include examples when helpful
- Specify constraints and guidelines

### 2. **Comprehensive Validation**
- Check both format/structure AND content quality
- Provide specific error messages that help the LLM improve
- Use warnings for non-critical issues
- Include metadata for debugging

### 3. **Flexible Configuration**
- Allow validator parameters to be customized
- Support optional context data
- Make validators reusable across similar tasks

### 4. **Error-Driven Improvement**
- Validation errors become feedback for LLM retry attempts
- Focus on actionable error messages
- Help the LLM understand what needs to be fixed

## Built-in Tasks for Reference

Look at the built-in tasks in `src/validated_llm/tasks/` for more examples:

- **`json_generation.py`**: JSON schema validation with complex nested structures
- **`csv_generation.py`**: Tabular data validation with row/column checks
- **`story_to_scenes.py`**: Complex YAML validation with multiple sections

## Running the Examples

```bash
# Simple email generation example
poetry run python examples/custom_email_task.py

# Complex data analysis report example
poetry run python examples/complex_data_analysis_task.py

# Built-in story-to-scenes demo (shows structure, no LLM calls)
poetry run python examples/builtin_story_to_scenes_demo.py

# Built-in story-to-scenes full example (actually converts stories, takes 30-60s)
poetry run python examples/builtin_story_to_scenes_full.py

# Built-in story-to-scenes simple test (quick validation test)
poetry run python examples/builtin_story_to_scenes_simple.py
```

This will demonstrate the email generation task in action with the validation loop.

## Best Practices

1. **Start Simple**: Begin with basic format validation, then add content quality checks
2. **Test Iteratively**: Run your task with various inputs to refine the prompt and validation
3. **Provide Good Feedback**: Validation errors should guide the LLM toward the correct output
4. **Handle Edge Cases**: Consider malformed inputs, missing data, and unexpected formats
5. **Use Type Hints**: Follow the patterns in built-in tasks for consistency

## Need Help?

- Check the built-in tasks for patterns and examples
- Review `BaseTask` and `BaseValidator` base classes for available methods
- Look at `ValidationResult` for the expected return format
- See the main README for overall package documentation
