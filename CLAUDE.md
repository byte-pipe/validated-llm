# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

`validated-llm` is a Python package that provides robust LLM output validation with automatic retry loops. It uses the ChatBot library for LLM communication and implements a validation-first approach where responses are automatically validated and improved through feedback loops.

## Key Architecture Components

### ValidationLoop (`src/validated_llm/validation_loop.py`)

- Main orchestrator handling retry logic and LLM communication
- Uses ChatBot library (dependency from `/Users/a/data/projects/1-ai/chatbot`) instead of direct OpenAI calls
- Builds comprehensive system prompts with validation instructions
- Implements feedback loops where validation errors are sent back to LLM for correction

### BaseValidator (`src/validated_llm/base_validator.py`)

- Abstract base for all validators with standardized ValidationResult
- Includes source code introspection - validators can include their own code in LLM prompts
- FunctionValidator wrapper allows using standalone functions as validators
- ValidationResult provides structured error/warning feedback for LLM correction

### Task System (`src/validated_llm/tasks/`)

- BaseTask abstract class pairs prompt templates with their validators
- Built-in tasks: StoryToScenesTask, JSONGenerationTask (PersonJSONTask, ProductCatalogTask), CSVGenerationTask
- Tasks encapsulate both the prompt template and corresponding validator class

## Common Development Commands

```bash
# Install dependencies
poetry install

# Run tests
poetry run pytest                                           # Run all tests
poetry run pytest tests/test_llm_validation_integration.py  # Run specific test (may timeout if LLM unavailable)
poetry run pytest -k test_specific_function                 # Run specific test function
poetry run pytest --cov=src tests/                         # Run with coverage
poetry run pytest -m "not integration"                     # Skip integration tests

# Code quality checks (required after changes)
poetry run mypy .                    # Type checking
poetry run black src/ tests/ tools/  # Format code (line length 222)
poetry run isort src/ tests/ tools/  # Sort imports
poetry run flake8 src/ tests/       # Lint code (if enabled)
pre-commit run --all-files           # Run all pre-commit hooks

# Build and package
poetry build                         # Build package

# CLI tools testing
poetry run validated-llm-prompt2task --help  # Test prompt converter CLI
poetry run validated-llm-config --help       # Test config CLI
```

## Core Data Flow

1. Task defines prompt_template and validator_class
2. ValidationLoop.execute() builds comprehensive system prompt including validator source code
3. ChatBot initialized with system prompt including validation instructions
4. LLM generates response, ValidationLoop extracts and validates output
5. If validation fails, errors are sent back as feedback for retry
6. Process repeats until success or max_retries exceeded

## Key Implementation Details

### LLM Integration

- Uses ChatBot library instead of direct API calls
- Default model: "gemma3:27b" (Ollama model)
- ChatBot handles system prompts and conversational context for feedback loops
- Local chatbot dependency at `/Users/a/data/projects/1-ai/chatbot`

### Validation Architecture

- Validators can include their source code in prompts using `get_source_code()`
- ValidationResult provides structured feedback (`errors`, `warnings`, `metadata`)
- FunctionValidator allows wrapping simple functions as full validators
- 16 built-in validators: JSON Schema, XML, YAML, Email, Phone, URL, Markdown, DateTime, Range, Regex, SQL, Syntax, Style, Test, Composite, Documentation

### Task-Based Design

- Tasks are complete workflows (prompt + validator) rather than separate components
- Built-in tasks handle common patterns (JSON schema, CSV, story processing)
- Tasks can customize prompt data preparation and validator configuration
- Template library with 29 pre-built templates across 6 categories

### Plugin System

- Custom validators can be loaded as plugins
- Plugin discovery from directories
- Validation and testing tools for plugins

## Testing Approach

- Main integration test: `tests/test_llm_validation_integration.py`
- Tool tests in `tools/tests/` directory
- Tests actual LLM integration using ChatBot with real model calls
- Validates both successful generation and proper error handling/feedback
- Performance and error handling edge case testing included
- Use `pytest -m "not integration"` to skip LLM-dependent tests

## Important Configuration Notes

- Line length: 222 characters (configured in pyproject.toml)
- Python version: 3.11+ (MyPy configured for 3.9 compatibility)
- ChatBot dependency is a local development dependency from parallel project
- No exceptions.py file exists - exceptions defined in `__init__.py`
- MyPy ignores missing imports for `chatbot.chatbot` and `pytest`
- Pre-commit hooks run mypy, black, and isort (flake8 commented out)

## Fixed Issues

- Added missing `jsonschema` dependency for JSON schema validation
- Added type stubs: `types-jsonschema`, `types-PyYAML`, `types-lxml`, `lxml-stubs`
- Fixed all import errors (`llm_validation` → `validated_llm`)
- Added `integration` marker to pytest configuration
- Fixed MyPy type annotations throughout codebase
- `poetry run pytest` now works (though tests require actual LLM access)
