"""Tests for configuration management."""

import os
import tempfile
from pathlib import Path

import pytest
import yaml

from validated_llm.config import ConfigLoader, ValidatedLLMConfig, create_sample_config, get_config, get_task_config, get_validator_config, load_config
from validated_llm.validators.config import ConfigValidator


class TestValidatedLLMConfig:
    """Test cases for ValidatedLLMConfig."""

    def test_default_config(self):
        """Test default configuration values."""
        config = ValidatedLLMConfig()

        assert config.llm_model == "gemma3:27b"
        assert config.llm_temperature == 0.7
        assert config.llm_max_tokens is None
        assert config.max_retries == 3
        assert config.timeout_seconds == 60
        assert config.show_progress is True
        assert config.code_language == "python"
        assert config.code_style_formatter == "black"
        assert config.output_format == "markdown"
        assert config.verbose is False

    def test_merge_configs(self):
        """Test merging configurations."""
        config1 = ValidatedLLMConfig()
        config2 = ValidatedLLMConfig()

        # Modify config2
        config2.llm_model = "gpt-4"
        config2.max_retries = 5
        config2.validator_defaults = {"EmailValidator": {"check_dns": True}}
        config2.plugin_paths = ["/path/to/plugins"]

        # Merge
        config1.merge(config2)

        assert config1.llm_model == "gpt-4"
        assert config1.max_retries == 5
        assert config1.validator_defaults == {"EmailValidator": {"check_dns": True}}
        assert config1.plugin_paths == ["/path/to/plugins"]

    def test_merge_nested_dicts(self):
        """Test merging nested dictionaries."""
        config1 = ValidatedLLMConfig()
        config1.validator_defaults = {"EmailValidator": {"allow_smtputf8": True}, "JSONValidator": {"strict": False}}

        config2 = ValidatedLLMConfig()
        config2.validator_defaults = {"EmailValidator": {"check_dns": True}, "XMLValidator": {"validate_schema": True}}

        config1.merge(config2)

        # EmailValidator should have both settings
        assert config1.validator_defaults["EmailValidator"] == {"allow_smtputf8": True, "check_dns": True}
        # JSONValidator should remain unchanged
        assert config1.validator_defaults["JSONValidator"] == {"strict": False}
        # XMLValidator should be added
        assert config1.validator_defaults["XMLValidator"] == {"validate_schema": True}


class TestConfigLoader:
    """Test cases for ConfigLoader."""

    def test_load_default_config(self):
        """Test loading default configuration when no files exist."""
        loader = ConfigLoader()
        config = loader.load_config("/nonexistent/path")

        assert config.llm_model == "gemma3:27b"
        assert config.max_retries == 3

    def test_load_project_config(self):
        """Test loading project configuration file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create config file
            config_path = Path(tmpdir) / ".validated-llm.yml"
            config_data = {"llm_model": "custom-model", "max_retries": 5, "code_language": "javascript"}
            with open(config_path, "w") as f:
                yaml.dump(config_data, f)

            # Load config
            loader = ConfigLoader()
            config = loader.load_config(tmpdir)

            assert config.llm_model == "custom-model"
            assert config.max_retries == 5
            assert config.code_language == "javascript"

    def test_load_nested_project_config(self):
        """Test loading config from parent directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create nested directory structure
            root_dir = Path(tmpdir)
            sub_dir = root_dir / "src" / "project"
            sub_dir.mkdir(parents=True)

            # Create config in root
            config_path = root_dir / ".validated-llm.yml"
            config_data = {"llm_model": "parent-model"}
            with open(config_path, "w") as f:
                yaml.dump(config_data, f)

            # Load from subdirectory
            loader = ConfigLoader()
            config = loader.load_config(sub_dir)

            assert config.llm_model == "parent-model"

    def test_load_env_config(self):
        """Test loading configuration from environment variables."""
        # Set environment variables
        env_vars = {"VALIDATED_LLM_MODEL": "env-model", "VALIDATED_LLM_TEMPERATURE": "0.5", "VALIDATED_LLM_MAX_RETRIES": "7", "VALIDATED_LLM_VERBOSE": "true"}

        for key, value in env_vars.items():
            os.environ[key] = value

        try:
            loader = ConfigLoader()
            config = loader.load_config()

            assert config.llm_model == "env-model"
            assert config.llm_temperature == 0.5
            assert config.max_retries == 7
            assert config.verbose is True
        finally:
            # Clean up
            for key in env_vars:
                os.environ.pop(key, None)

    def test_config_precedence(self):
        """Test configuration precedence (env > project > global > default)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create project config
            config_path = Path(tmpdir) / ".validated-llm.yml"
            config_data = {"llm_model": "project-model", "max_retries": 4, "code_language": "go"}
            with open(config_path, "w") as f:
                yaml.dump(config_data, f)

            # Set environment variable (should override project)
            os.environ["VALIDATED_LLM_MODEL"] = "env-model"

            try:
                loader = ConfigLoader()
                config = loader.load_config(tmpdir)

                # Environment should override project
                assert config.llm_model == "env-model"
                # Project value should be used
                assert config.max_retries == 4
                assert config.code_language == "go"
            finally:
                os.environ.pop("VALIDATED_LLM_MODEL", None)

    def test_invalid_config_file(self):
        """Test handling of invalid configuration file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create invalid YAML
            config_path = Path(tmpdir) / ".validated-llm.yml"
            with open(config_path, "w") as f:
                f.write("invalid: yaml: content:")

            loader = ConfigLoader()
            with pytest.raises(ValueError, match="Invalid config"):
                loader.load_config(tmpdir)

    def test_config_caching(self):
        """Test that config files are cached."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / ".validated-llm.yml"
            config_data = {"llm_model": "cached-model"}
            with open(config_path, "w") as f:
                yaml.dump(config_data, f)

            loader = ConfigLoader()

            # Load twice
            config1 = loader.load_config(tmpdir)
            config2 = loader.load_config(tmpdir)

            # Should use cache (same config object)
            assert config1 is config2

    def test_get_validator_config(self):
        """Test getting validator-specific configuration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / ".validated-llm.yml"
            config_data = {"validator_defaults": {"EmailValidator": {"check_dns": True, "allow_smtputf8": False}, "JSONValidator": {"strict_mode": True}}}
            with open(config_path, "w") as f:
                yaml.dump(config_data, f)

            loader = ConfigLoader()
            loader.load_config(tmpdir)

            email_config = loader.get_validator_config("EmailValidator")
            assert email_config == {"check_dns": True, "allow_smtputf8": False}

            json_config = loader.get_validator_config("JSONValidator")
            assert json_config == {"strict_mode": True}

            # Non-existent validator
            other_config = loader.get_validator_config("OtherValidator")
            assert other_config == {}


class TestConfigValidator:
    """Test cases for ConfigValidator."""

    def test_valid_config(self):
        """Test validation of valid configuration."""
        config_content = """
llm_model: gpt-4
llm_temperature: 0.8
max_retries: 5
timeout_seconds: 120

code_language: python
code_style_formatter: black

validator_defaults:
  EmailValidator:
    check_dns: true

task_defaults:
  CodeGenerationTask:
    language: python
"""

        validator = ConfigValidator()
        result = validator.validate(config_content)

        assert result.is_valid
        assert len(result.errors) == 0

    def test_empty_config(self):
        """Test validation of empty configuration."""
        validator = ConfigValidator()
        result = validator.validate("")

        assert not result.is_valid
        assert "Configuration file is empty" in result.errors[0]

    def test_invalid_yaml(self):
        """Test validation of invalid YAML syntax."""
        config_content = "invalid: yaml: content:"

        validator = ConfigValidator()
        result = validator.validate(config_content)

        assert not result.is_valid
        assert "Invalid YAML syntax" in result.errors[0]

    def test_invalid_types(self):
        """Test validation with incorrect types."""
        config_content = """
llm_temperature: "not a number"
max_retries: 3.5
show_progress: "yes"
validator_defaults: "not a dict"
"""

        validator = ConfigValidator()
        result = validator.validate(config_content)

        assert not result.is_valid
        assert any("llm_temperature must be a number" in error for error in result.errors)
        assert any("max_retries must be an integer" in error for error in result.errors)
        assert any("show_progress must be a boolean" in error for error in result.errors)
        assert any("validator_defaults must be a dictionary" in error for error in result.errors)

    def test_out_of_range_values(self):
        """Test validation with out-of-range values."""
        config_content = """
llm_temperature: 5.0
max_retries: -1
timeout_seconds: 0
doc_min_sections: 0
"""

        validator = ConfigValidator()
        result = validator.validate(config_content)

        assert not result.is_valid
        assert any("temperature 5.0 is outside typical range" in warning for warning in result.warnings)
        assert any("max_retries must be non-negative" in error for error in result.errors)
        assert any("timeout_seconds must be positive" in error for error in result.errors)
        assert any("doc_min_sections must be at least 1" in error for error in result.errors)

    def test_unknown_keys_lenient(self):
        """Test handling of unknown keys in lenient mode."""
        config_content = """
llm_model: gpt-4
unknown_key: some_value
another_unknown: 123
"""

        validator = ConfigValidator(strict_mode=False)
        result = validator.validate(config_content)

        assert result.is_valid  # Should be valid in lenient mode
        assert any("Unknown configuration keys" in warning for warning in result.warnings)

    def test_unknown_keys_strict(self):
        """Test handling of unknown keys in strict mode."""
        config_content = """
llm_model: gpt-4
unknown_key: some_value
"""

        validator = ConfigValidator(strict_mode=True)
        result = validator.validate(config_content)

        assert not result.is_valid  # Should be invalid in strict mode
        assert any("Unknown configuration keys" in error for error in result.errors)

    def test_sample_config_is_valid(self):
        """Test that the sample configuration is valid."""
        sample_config = create_sample_config()

        validator = ConfigValidator()
        result = validator.validate(sample_config)

        assert result.is_valid
        assert len(result.errors) == 0


def test_module_functions():
    """Test module-level convenience functions."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create config
        config_path = Path(tmpdir) / ".validated-llm.yml"
        config_data = {"llm_model": "test-model", "validator_defaults": {"TestValidator": {"setting": "value"}}}
        with open(config_path, "w") as f:
            yaml.dump(config_data, f)

        # Test load_config
        config = load_config(tmpdir)
        assert config.llm_model == "test-model"

        # Test get_config (should return cached)
        config2 = get_config()
        assert config2.llm_model == "test-model"

        # Test get_validator_config
        validator_config = get_validator_config("TestValidator")
        assert validator_config == {"setting": "value"}

        # Test get_task_config
        task_config = get_task_config("NonExistentTask")
        assert task_config == {}


if __name__ == "__main__":
    pytest.main([__file__])
