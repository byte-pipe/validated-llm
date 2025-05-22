#!/usr/bin/env python3
"""
Integration tests for the LLM validation system.

Tests different prompt/validator combinations to ensure the system can
successfully generate valid output within reasonable attempt limits.
"""

import logging

# Import the LLM validation system
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import pytest
import yaml

sys.path.append(str(Path(__file__).parent.parent / "src"))

from validated_llm import ValidationLoop
from validated_llm.base_validator import ValidationResult
from validated_llm.tasks import CSVGenerationTask, PersonJSONTask, ProductCatalogTask, StoryToScenesTask

# Test configuration - using ChatBot instead of direct Ollama
MAX_ATTEMPTS = 5
DEFAULT_MODEL = "gemma3:27b"

logger = logging.getLogger(__name__)


class LLMValidationTestCase:
    """Represents a single test case for the LLM validation system."""

    def __init__(
        self,
        name: str,
        task_or_prompt: Any,
        validator_class: Optional[Any] = None,
        input_data: Optional[Dict[str, Any]] = None,
        validator_config: Optional[Dict[str, Any]] = None,
        max_attempts: int = MAX_ATTEMPTS,
        temperature: float = 0.7,
    ) -> None:
        self.name = name

        # Support both new task-based and legacy prompt/validator style
        if hasattr(task_or_prompt, "prompt_template"):
            # New task-based approach
            self.task = task_or_prompt
            self.prompt_template = task_or_prompt.prompt_template
            self.validator_class = task_or_prompt.validator_class
        else:
            # Legacy approach
            self.task = None
            self.prompt_template = task_or_prompt
            self.validator_class = validator_class

        self.input_data = input_data or {}
        self.validator_config = validator_config or {}
        self.max_attempts = max_attempts
        self.temperature = temperature


class TestLLMValidationIntegration:
    """Integration tests for the LLM validation system."""

    @pytest.fixture(scope="class")
    def validation_loop(self) -> ValidationLoop:
        """Create validation loop for testing with ChatBot."""
        return ValidationLoop(model_name=DEFAULT_MODEL, default_max_retries=MAX_ATTEMPTS)

    @staticmethod
    def get_test_cases() -> List[LLMValidationTestCase]:
        """Define test cases for different prompt/validator combinations."""

        test_cases = []

        # Test Case 1: Story-to-Scenes with simple story (using new task-based approach)
        test_cases.append(
            LLMValidationTestCase(
                name="story_to_scenes_simple",
                task_or_prompt=StoryToScenesTask(),
                input_data={
                    "story": """
                A young astronaut lands on a mysterious planet covered in crystal formations.
                She discovers that the crystals sing in harmony when touched by sunlight.
                As she explores deeper, she finds an ancient alien city built entirely from these musical crystals.
                """
                },
            )
        )

        # Test Case 2: Story-to-Scenes with complex narrative (using new task-based approach)
        test_cases.append(
            LLMValidationTestCase(
                name="story_to_scenes_complex",
                task_or_prompt=StoryToScenesTask(),
                input_data={
                    "story": """
                Dr. Elena Rodriguez had spent three years preparing for this moment. The quantum computer hummed
                behind reinforced glass as she input the final sequence. The calculations were perfect, but the
                implications terrifying. If her theory was correct, they had just opened a doorway to parallel
                dimensions. The screen flickered, showing impossible geometries. Through the lab's speakers came
                a voice - her own voice - speaking words she had never said: "Elena, you need to stop the experiment.
                In my dimension, this destroyed everything."
                """
                },
            )
        )

        # Test Case 3: Story-to-Scenes with minimal content (edge case)
        test_cases.append(LLMValidationTestCase(name="story_to_scenes_minimal", task_or_prompt=StoryToScenesTask(), input_data={"story": "A cat sat on a mat. It was a red mat. The cat was happy."}))

        # Test Case 4: Story-to-Scenes with dialogue-heavy content
        test_cases.append(
            LLMValidationTestCase(
                name="story_to_scenes_dialogue",
                task_or_prompt=StoryToScenesTask(),
                input_data={
                    "story": """
                "Are you sure this is the right address?" Maria asked, staring at the abandoned warehouse.
                "According to the map, yes," David replied, checking his phone again.
                They approached the rusty door. A sign read 'AUTHORIZED PERSONNEL ONLY.'
                "Well, we're not authorized," Maria laughed nervously.
                "But we're definitely personnel," David grinned, pushing open the door.
                Inside, rows of computers hummed quietly in the darkness.
                """
                },
            )
        )

        # Test Case 5: Story-to-Scenes validation fix test (style separation)
        test_cases.append(
            LLMValidationTestCase(
                name="story_to_scenes_style_validation",
                task_or_prompt=StoryToScenesTask(),
                input_data={
                    "story": """
                Sarah walked through the ancient forest, her footsteps muffled by the thick carpet of fallen leaves.
                As she ventured deeper, she discovered a small clearing where wildflowers bloomed in vibrant colors.
                In the center stood an old stone well, its weathered surface covered with moss and mysterious symbols.
                """
                },
                max_attempts=3,  # Should succeed quickly with fixed validation
            )
        )

        # Test Case 6: JSON Schema Validation - Person data (using new task-based approach)
        test_cases.append(
            LLMValidationTestCase(
                name="json_person_validation",
                task_or_prompt=PersonJSONTask(),
                input_data={"input_text": "Sarah Chen is a 28-year-old data scientist from Seattle who loves rock climbing, machine learning, and playing violin."},
            )
        )

        # Test Case 7: CSV Validation - Sales report (using new task-based approach)
        test_cases.append(
            LLMValidationTestCase(
                name="csv_sales_report",
                task_or_prompt=CSVGenerationTask(),
                input_data={"data_description": "Q1 2024 sales data showing daily sales figures for tech products across different regions"},
                validator_config={"required_columns": ["Date", "Product", "Sales_Rep", "Amount", "Region"], "min_rows": 3, "max_rows": 20},
            )
        )

        # Test Case 8: Complex JSON - Product catalog (using new task-based approach)
        test_cases.append(
            LLMValidationTestCase(
                name="json_complex_product_catalog",
                task_or_prompt=ProductCatalogTask(),
                input_data={"product_descriptions": "Wireless Bluetooth headphones - premium noise canceling, 30-hour battery. Smart fitness tracker - heart rate monitor, GPS, waterproof design."},
            )
        )

        return test_cases

    @pytest.mark.integration
    def test_llm_validation_success(self, validation_loop: ValidationLoop) -> None:
        """Test that each prompt/validator combination succeeds within max attempts."""

        test_cases = self.get_test_cases()

        for test_case in test_cases:
            logger.info(f"Running integration test: {test_case.name}")

            # Create validator instance
            if test_case.task:
                # New task-based approach
                validator = test_case.task.create_validator(**test_case.validator_config)
            else:
                # Legacy approach
                validator = test_case.validator_class(**test_case.validator_config)

            # Execute validation loop
            result = validation_loop.execute(prompt_template=test_case.prompt_template, validator=validator, input_data=test_case.input_data, max_retries=test_case.max_attempts, debug=True)

            # Assertions
            assert result["success"], (
                f"Test '{test_case.name}' failed after {result['attempts']} attempts. " f"Last validation errors: {result.get('validation_result', ValidationResult(is_valid=False, errors=[], warnings=[])).errors}"
            )

            assert result["attempts"] <= test_case.max_attempts, f"Test '{test_case.name}' took {result['attempts']} attempts, " f"exceeding max of {test_case.max_attempts}"

            assert result["execution_time"] > 0, "Execution time should be positive"

            assert result["output"], "Output should not be empty"

            # Log success metrics
            logger.info(f"✅ Test '{test_case.name}' succeeded in {result['attempts']} attempts " f"({result['execution_time']:.2f}s)")

            # Additional validation-specific checks
            from validated_llm.tasks.story_to_scenes import StoryToScenesValidator

            if test_case.validator_class == StoryToScenesValidator or isinstance(test_case.task, StoryToScenesTask):
                # Ensure output contains scenes
                assert "- id:" in result["output"], "Output should contain scene definitions"
                assert "image:" in result["output"], "Output should contain image sections"
                assert "audio:" in result["output"], "Output should contain audio sections"
                assert "caption:" in result["output"], "Output should contain caption sections"

                # Test specific fixes: style field separation and no markdown
                assert "```yaml" not in result["output"], "Output should not contain markdown code blocks"
                assert "```" not in result["output"], "Output should not contain markdown backticks"

                # Parse as YAML and validate structure
                try:
                    scenes = yaml.safe_load(result["output"])
                    assert isinstance(scenes, list), "Output should be a list of scenes"
                    assert len(scenes) > 0, "Should contain at least one scene"

                    for i, scene in enumerate(scenes):
                        assert "image" in scene, f"Scene {i+1} should have image section"
                        assert "audio" in scene, f"Scene {i+1} should have audio section"
                        assert "caption" in scene, f"Scene {i+1} should have caption section"

                        # Critical fix validation: style field separation
                        assert "style" in scene["image"], f"Scene {i+1} image should have required 'style' field"
                        assert scene["image"]["style"] in ["photorealistic", "cinematic", "artistic"], f"Scene {i+1} image style should be one of the valid enum values"

                        # Ensure style info is NOT embedded in prompt
                        prompt = scene["image"]["prompt"].lower()
                        style_keywords = ["photorealistic", "cinematic", "artistic", "realistic", "style"]
                        embedded_style = any(keyword in prompt for keyword in style_keywords)
                        if embedded_style:
                            logger.warning(f"Scene {i+1} may have style info embedded in prompt: {scene['image']['prompt']}")

                except yaml.YAMLError as e:
                    pytest.fail(f"Output should be valid YAML: {e}")
                except Exception as e:
                    pytest.fail(f"Error validating scene structure: {e}")

            elif hasattr(test_case.validator_class, "__name__") and "JSON" in test_case.validator_class.__name__:
                # Ensure output is valid JSON
                import json

                try:
                    json.loads(result["output"])
                except json.JSONDecodeError:
                    pytest.fail("Output should be valid JSON")

            elif hasattr(test_case.validator_class, "__name__") and "CSV" in test_case.validator_class.__name__:
                # Ensure output contains CSV structure
                lines = result["output"].strip().split("\n")
                assert len(lines) >= 2, "CSV should have header + at least one data row"
                assert "," in lines[0], "CSV should contain commas"

    @pytest.mark.integration
    def test_validation_loop_performance_metrics(self, validation_loop: ValidationLoop) -> None:
        """Test performance characteristics of the validation loop."""

        # Simple test case for performance measurement
        task = StoryToScenesTask()
        validator = task.create_validator()
        simple_story = "A dog ran through the park. It was a sunny day."

        result = validation_loop.execute(prompt_template=task.prompt_template, validator=validator, input_data={"story": simple_story}, max_retries=3, debug=True)

        # Performance assertions
        assert result["execution_time"] < 60, "Simple validation should complete within 60 seconds"
        assert result["attempts"] <= 3, "Simple validation should succeed quickly"

        logger.info(f"Performance test completed in {result['execution_time']:.2f}s")

    @pytest.mark.integration
    def test_validation_loop_error_handling(self, validation_loop: ValidationLoop) -> None:
        """Test error handling in the validation loop."""

        # Test with invalid prompt template
        task = StoryToScenesTask()
        validator = task.create_validator()

        # This should handle the error gracefully
        result = validation_loop.execute(prompt_template="Invalid prompt: {nonexistent_key}", validator=validator, input_data={"story": "Test story"}, max_retries=1, debug=True)

        # Should handle template errors gracefully
        assert not result["success"]
        assert "error" in result or "validation_result" in result

    @pytest.mark.integration
    def test_story_to_scenes_validation_fix(self, validation_loop: ValidationLoop) -> None:
        """Test that story-to-scenes validation now works correctly with style field separation."""

        task = StoryToScenesTask()
        validator = task.create_validator()

        # Test the exact story from our debugging session
        test_story = """
        Sarah walked through the ancient forest, her footsteps muffled by the thick carpet of fallen leaves.
        As she ventured deeper, she discovered a small clearing where wildflowers bloomed in vibrant colors.
        In the center stood an old stone well, its weathered surface covered with moss and mysterious symbols.
        Sarah approached the well and peered into its depths, discovering it was a portal to other worlds.
        """

        result = validation_loop.execute(prompt_template=task.prompt_template, validator=validator, input_data={"story": test_story}, max_retries=3, debug=True)

        # Should succeed with the fixed validation
        assert result["success"], f"Validation should succeed after fix. Errors: {result.get('validation_result', {}).get('errors', [])}"
        assert result["attempts"] <= 3, "Should succeed quickly with fixed validation"

        # Parse and validate the specific fix
        scenes = yaml.safe_load(result["output"])
        assert isinstance(scenes, list) and len(scenes) > 0, "Should generate valid scenes"

        for i, scene in enumerate(scenes):
            # Critical validation: separate style field
            assert "style" in scene["image"], f"Scene {i+1} missing required style field"
            assert scene["image"]["style"] in ["photorealistic", "cinematic", "artistic"], f"Scene {i+1} has invalid style: {scene['image']['style']}"

            # Ensure no markdown wrapping
            assert "```" not in result["output"], "Output should not contain markdown"

        logger.info(f"✅ Story-to-scenes validation fix test passed with {len(scenes)} scenes")

    @pytest.mark.integration
    def test_validator_feedback_loop(self, validation_loop: ValidationLoop) -> None:
        """Test that validation feedback actually improves LLM output."""

        # Create a mock validator that fails the first few times with specific feedback
        from validated_llm.base_validator import BaseValidator

        class TestFeedbackValidator(BaseValidator):
            def __init__(self) -> None:
                super().__init__(name="test_feedback_validator", description="Tests feedback loop mechanism")
                self.attempt_count = 0

            def validate(self, output: str, context: Optional[Dict[str, Any]] = None) -> "ValidationResult":
                from validated_llm.base_validator import ValidationResult

                self.attempt_count += 1

                if self.attempt_count == 1:
                    return ValidationResult(is_valid=False, errors=["Output must start with 'CORRECTED:' prefix"], warnings=[])
                elif self.attempt_count == 2 and not output.startswith("CORRECTED:"):
                    return ValidationResult(is_valid=False, errors=["Still missing 'CORRECTED:' prefix at the beginning"], warnings=[])
                else:
                    return ValidationResult(is_valid=True, errors=[], warnings=[])

        feedback_validator = TestFeedbackValidator()

        result = validation_loop.execute(prompt_template="Please respond with: {test_input}", validator=feedback_validator, input_data={"test_input": "Hello world"}, max_retries=5, debug=True)

        # Should succeed after receiving feedback
        assert result["success"], "Validation should succeed after feedback"
        assert result["attempts"] >= 2, "Should take multiple attempts due to feedback"
        assert "CORRECTED:" in result["output"], "Final output should incorporate feedback"


# Test runners and utilities
def run_integration_tests() -> None:
    """Run integration tests with proper setup."""

    # Configure logging
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # Run tests - ChatBot handles its own connection
    pytest.main([__file__, "-v", "-m", "integration", "--tb=short"])


if __name__ == "__main__":
    run_integration_tests()
