# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

`validated-llm` is a Python package that provides robust LLM output validation with automatic retry loops. It uses the ChatBot library for LLM communication and implements a validation-first approach where LLM responses are automatically validated and improved through feedback loops.

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

# Run tests (integration tests require actual LLM access)
poetry run pytest

# Run with coverage
poetry run pytest --cov=src tests/

# Run specific integration test (may timeout if LLM unavailable)
poetry run pytest tests/test_llm_validation_integration.py

# Format code (line length 222 per pyproject.toml)
poetry run black src/ tests/
poetry run isort src/ tests/

# Type checking
poetry run mypy src/

# Lint code
poetry run flake8 src/ tests/

# Build package
poetry build
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

### Validation Architecture
- Validators can include their source code in prompts using `get_source_code()`
- ValidationResult provides structured feedback (`errors`, `warnings`, `metadata`)
- FunctionValidator allows wrapping simple functions as full validators

### Task-Based Design
- Tasks are complete workflows (prompt + validator) rather than separate components
- Built-in tasks handle common patterns (JSON schema, CSV, story processing)
- Tasks can customize prompt data preparation and validator configuration

## Testing Approach

- Single comprehensive integration test file: `tests/test_llm_validation_integration.py`
- Tests actual LLM integration using ChatBot with real model calls
- Validates both successful generation and proper error handling/feedback
- Performance and error handling edge case testing included

## Important Configuration Notes

- Line length: 222 characters (configured in pyproject.toml)
- Python version: 3.11+ (MyPy configured for 3.9 compatibility)
- ChatBot dependency is a local development dependency from parallel project
- No exceptions.py file exists - exceptions defined in `__init__.py`
- MyPy ignores missing imports for `chatbot.chatbot` and `pytest`

## Fixed Issues

- Added missing `jsonschema` dependency for JSON schema validation
- Added type stubs: `types-jsonschema`, `types-PyYAML`
- Fixed all import errors (`llm_validation` → `validated_llm`)
- Added `integration` marker to pytest configuration
- Fixed MyPy type annotations throughout codebase
- `poetry run pytest` now works (though tests require actual LLM access)
