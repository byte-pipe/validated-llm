#!/usr/bin/env python3
"""
Demo script showing how to use configuration files with validated-llm.

This example demonstrates:
1. Loading configuration from .validated-llm.yml
2. Using config defaults in validators and tasks
3. Environment variable overrides
"""

import os
import tempfile
from pathlib import Path

from validated_llm import ValidationLoop
from validated_llm.config import get_config, load_config
from validated_llm.tasks import CodeGenerationTask
from validated_llm.validators import EmailValidator


def demo_config_loading():
    """Demonstrate configuration loading and precedence."""
    print("=== Configuration Loading Demo ===\n")

    # Load configuration
    config = load_config()

    print(f"Current configuration:")
    print(f"  LLM Model: {config.llm_model}")
    print(f"  Temperature: {config.llm_temperature}")
    print(f"  Max Retries: {config.max_retries}")
    print(f"  Code Language: {config.code_language}")
    print()

    # Show validator defaults
    print("EmailValidator defaults from config:")
    email_defaults = config.validator_defaults.get("EmailValidator", {})
    print(f"  allow_smtputf8: {email_defaults.get('allow_smtputf8', 'not set')}")
    print(f"  check_deliverability: {email_defaults.get('check_deliverability', 'not set')}")
    print()


def demo_validator_with_config():
    """Demonstrate how validators use configuration defaults."""
    print("=== Validator Using Config Defaults ===\n")

    # Create validator without specifying allow_smtputf8 or check_deliverability
    # It will use values from config file
    validator = EmailValidator()

    print(f"EmailValidator settings:")
    print(f"  allow_smtputf8: {validator.allow_smtputf8} (from config)")
    print(f"  check_deliverability: {validator.check_deliverability} (from config)")
    print()

    # Test validation
    result = validator.validate("john.doe@example.com")
    print(f"Validation result for 'john.doe@example.com': {result.is_valid}")
    print()


def demo_task_with_config():
    """Demonstrate how tasks use configuration defaults."""
    print("=== Task Using Config Defaults ===\n")

    # Create task without specifying language
    # It will use value from config file
    task = CodeGenerationTask()

    print(f"CodeGenerationTask settings:")
    print(f"  language: {task.language} (from config)")
    print()


def demo_env_override():
    """Demonstrate environment variable overrides."""
    print("=== Environment Variable Override Demo ===\n")

    # Save original env
    original_model = os.environ.get("VALIDATED_LLM_MODEL")

    try:
        # Set environment variable
        os.environ["VALIDATED_LLM_MODEL"] = "gpt-4"

        # Reload config
        config = load_config()

        print(f"After setting VALIDATED_LLM_MODEL=gpt-4:")
        print(f"  LLM Model: {config.llm_model} (overridden by env var)")
        print()

    finally:
        # Restore original env
        if original_model is None:
            os.environ.pop("VALIDATED_LLM_MODEL", None)
        else:
            os.environ["VALIDATED_LLM_MODEL"] = original_model


def demo_validation_loop_with_config():
    """Demonstrate ValidationLoop using configuration."""
    print("=== ValidationLoop Using Config ===\n")

    # Create ValidationLoop without specifying model_name or max_retries
    # It will use values from config
    loop = ValidationLoop()

    print(f"ValidationLoop settings:")
    print(f"  model_name: {loop.model_name} (from config)")
    print(f"  default_max_retries: {loop.default_max_retries} (from config)")
    print()


def demo_custom_config_file():
    """Demonstrate loading from a custom config file."""
    print("=== Custom Config File Demo ===\n")

    # Create a temporary config file
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / ".validated-llm.yml"

        # Write custom config
        with open(config_path, "w") as f:
            f.write(
                """
# Custom configuration for demo
llm_model: custom-model
llm_temperature: 0.5
max_retries: 5

validator_defaults:
  EmailValidator:
    allow_smtputf8: false
    check_deliverability: true
"""
            )

        # Load config from custom location
        config = load_config(tmpdir)

        print(f"Custom config loaded from {config_path}:")
        print(f"  LLM Model: {config.llm_model}")
        print(f"  Temperature: {config.llm_temperature}")
        print(f"  Max Retries: {config.max_retries}")
        print()


def main():
    """Run all configuration demos."""
    print("Validated-LLM Configuration Demo")
    print("=" * 50)
    print()

    # Check if config file exists
    config_path = Path.cwd() / ".validated-llm.yml"
    if config_path.exists():
        print(f"Using configuration from: {config_path}")
    else:
        print("No .validated-llm.yml found, using defaults")
    print()

    # Run demos
    demo_config_loading()
    demo_validator_with_config()
    demo_task_with_config()
    demo_env_override()
    demo_validation_loop_with_config()
    demo_custom_config_file()

    print("Demo complete!")


if __name__ == "__main__":
    main()
