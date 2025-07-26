#!/usr/bin/env python3
"""
Simplified integration tests for the LLM validation system.
Tests only the most essential functionality to verify the system works.
"""
import logging
import sys
from pathlib import Path
from typing import Any, Dict

import pytest

sys.path.append(str(Path(__file__).parent.parent / "src"))
from validated_llm import ValidationLoop
from validated_llm.tasks import StoryToScenesTask

logger = logging.getLogger(__name__)


class TestLLMValidationIntegrationSimple:
    """Simplified integration tests for faster execution."""

    @pytest.fixture(scope="class")
    def validation_loop(self) -> ValidationLoop:
        """Create validation loop for testing with ChatBot."""
        return ValidationLoop(vendor="ollama", model="gemma3:27b", default_max_retries=2)

    @pytest.mark.integration
    @pytest.mark.timeout(180)  # 3 minute timeout
    def test_basic_story_to_scenes(self, validation_loop: ValidationLoop) -> None:
        """Test basic story to scenes conversion."""
        # Simple task
        task = StoryToScenesTask()
        validator = task.create_validator()

        # Very simple story for quick testing
        story = "A cat sat on a mat. The sun was shining. The cat was happy."

        logger.info("Running basic story-to-scenes test")

        # Execute validation loop
        result = validation_loop.execute(prompt_template=task.prompt_template, validator=validator, input_data={"story": story}, max_retries=2, debug=True)

        # Basic assertions
        assert result["success"], f"Validation failed: {result.get('validation_result')}"
        assert result["output"], "Output should not be empty"
        assert result["attempts"] <= 2, "Should succeed within 2 attempts"
        assert result["execution_time"] > 0, "Execution time should be positive"

        logger.info(f"✅ Test succeeded in {result['attempts']} attempts ({result['execution_time']:.2f}s)")

    @pytest.mark.integration
    @pytest.mark.timeout(60)  # 1 minute timeout
    def test_validation_error_handling(self, validation_loop: ValidationLoop) -> None:
        """Test that validation errors are handled gracefully."""
        task = StoryToScenesTask()
        validator = task.create_validator()

        # Invalid prompt template
        result = validation_loop.execute(prompt_template="Invalid prompt: {nonexistent_key}", validator=validator, input_data={"story": "Test story"}, max_retries=1, debug=True)

        # Should handle the error gracefully
        assert not result["success"]
        assert result["attempts"] == 1


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    # Run tests
    pytest.main([__file__, "-v", "-m", "integration", "--tb=short"])
