# Tests for prompt-to-task Tool

This directory contains comprehensive tests for the prompt-to-task conversion tool.

## Test Coverage

- **test_analyzer.py**: Tests for the PromptAnalyzer class
  - Template variable extraction
  - Output format detection (JSON, CSV, list, text)
  - Validation hint extraction
  - Edge cases and special characters

- **test_code_generator.py**: Tests for the TaskCodeGenerator class
  - Task code generation with various formats
  - Validator code generation (built-in and custom)
  - Class name conversion
  - Example usage generation

- **test_validator_suggester.py**: Tests for the ValidatorSuggester class
  - Validator suggestions for different formats
  - Built-in validator detection
  - Custom validator generation
  - Confidence scoring

- **test_cli_click.py**: Tests for the CLI interface
  - Help command
  - Basic conversion workflow
  - Interactive mode
  - Analyze-only mode
  - Validator-only mode
  - Error handling

## Running Tests

```bash
# Run all tests
poetry run pytest tools/tests/

# Run with coverage
poetry run pytest tools/tests/ --cov=tools --cov-report=term-missing

# Run specific test file
poetry run pytest tools/tests/test_analyzer.py -v
```

## Current Status

- All 41 tests passing ✅
- 86% code coverage
- Key functionality well-tested
- Edge cases covered
