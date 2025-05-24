"""
Core LLM Validation Loop implementation.
This module provides the main LLMValidationLoop class that orchestrates
the iterative generation and validation process.
"""

import json
import logging
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union

from chatbot.chatbot import ChatBot

from .base_validator import BaseValidator, FunctionValidator, ValidationResult

logger = logging.getLogger(__name__)


class ValidationLoop:
    """
    Generic LLM validation loop that can be reused for various tasks.
    This class orchestrates the process of:
    1. Sending prompts to LLM with validation instructions
    2. Validating LLM responses
    3. Providing feedback for improvement
    4. Retrying until valid output or max attempts reached
    """

    def __init__(
        self,
        model_name: str = "gemma3:27b",
        default_max_retries: int = 3,
    ):
        """
        Initialize the validation loop.
        Args:
            model_name: Name of the Ollama model to use (e.g., "gemma3:27b")
            default_max_retries: Default maximum number of retry attempts
        """
        self.model_name = model_name
        self.default_max_retries = default_max_retries
        self.validator_registry: Dict[str, BaseValidator] = {}

    def register_validator(self, name: str, validator: Union[BaseValidator, Callable]) -> None:
        """
        Register a validator for reuse across different tasks.
        Args:
            name: Unique name for the validator
            validator: BaseValidator instance or callable function
        """
        if callable(validator) and not isinstance(validator, BaseValidator):
            validator = FunctionValidator(validator, name)
        self.validator_registry[name] = validator
        logger.info(f"Registered validator: {name}")

    def get_validator(self, name: str) -> BaseValidator:
        """Get a registered validator by name."""
        if name not in self.validator_registry:
            raise ValueError(f"Validator '{name}' not found. Available: {list(self.validator_registry.keys())}")
        validator = self.validator_registry[name]
        if not isinstance(validator, BaseValidator):
            raise TypeError(f"Expected BaseValidator, got {type(validator)}")
        return validator

    def execute(
        self,
        prompt_template: str,
        validator: Union[str, BaseValidator, Callable],
        input_data: Dict[str, Any],
        max_retries: Optional[int] = None,
        context: Optional[Dict[str, Any]] = None,
        debug: bool = False,
    ) -> Dict[str, Any]:
        """
        Execute the LLM validation loop.
        Args:
            prompt_template: Base prompt template with placeholders
            validator: Validator instance, function, or registered validator name
            input_data: Data to fill prompt template placeholders
            max_retries: Maximum retry attempts (uses default if None)
            context: Additional context for validation
            debug: Enable debug logging and output preservation
        Returns:
            Dictionary with execution results:
            {
                'success': bool,
                'output': str,
                'attempts': int,
                'validation_result': ValidationResult,
                'execution_time': float,
                'debug_info': Dict (if debug=True)
            }
        """
        start_time = time.time()
        max_retries = max_retries or self.default_max_retries
        debug_info: Optional[List[Dict[str, Any]]] = [] if debug else None
        # Resolve validator
        if isinstance(validator, str):
            validator = self.get_validator(validator)
        elif callable(validator) and not isinstance(validator, BaseValidator):
            validator = FunctionValidator(validator)
        logger.info(f"Starting LLM validation loop with validator: {validator.name}")
        # Create ChatBot instance with comprehensive system prompt
        system_prompt = self._build_system_prompt(prompt_template, validator, input_data)
        chatbot = ChatBot(prompt=system_prompt, model=self.model_name)
        # Initialize validation_result for proper scoping
        validation_result: Optional[ValidationResult] = None
        cleaned_output = ""
        for attempt in range(max_retries):
            logger.info(f"Attempt {attempt + 1}/{max_retries}")
            try:
                # For first attempt, ask for the initial task
                if attempt == 0:
                    task_prompt = prompt_template.format(**input_data)
                    llm_response = chatbot.ask(task_prompt)
                else:
                    # For subsequent attempts, provide feedback
                    if validation_result is not None:
                        feedback_text = validation_result.get_feedback_text()
                        retry_prompt = f"""Your previous response had validation errors:
{feedback_text}
Please provide a corrected response that addresses these issues."""
                    else:
                        retry_prompt = "Please provide a corrected response."
                    llm_response = chatbot.ask(retry_prompt)
                if debug and debug_info is not None:
                    debug_info.append(
                        {
                            "attempt": attempt + 1,
                            "prompt": task_prompt if attempt == 0 else retry_prompt,
                            "raw_response": llm_response,
                            "timestamp": time.time(),
                        }
                    )
                # Extract and clean the output
                cleaned_output = self._extract_output(llm_response)
                # Validate the output
                validation_result = validator.validate(cleaned_output, context)
                if validation_result.is_valid:
                    execution_time = time.time() - start_time
                    logger.info(f"Validation successful after {attempt + 1} attempt(s)")
                    result = {
                        "success": True,
                        "output": cleaned_output,
                        "attempts": attempt + 1,
                        "validation_result": validation_result,
                        "execution_time": execution_time,
                    }
                    if debug:
                        result["debug_info"] = debug_info
                    return result
                # Log validation failure for next iteration
                logger.warning(f"Validation failed on attempt {attempt + 1}: {len(validation_result.errors)} errors")
            except Exception as e:
                logger.error(f"Error on attempt {attempt + 1}: {str(e)}")
                if debug and debug_info is not None:
                    debug_info.append(
                        {
                            "attempt": attempt + 1,
                            "error": str(e),
                            "timestamp": time.time(),
                        }
                    )
        # All attempts failed
        execution_time = time.time() - start_time
        logger.error(f"Validation failed after {max_retries} attempts")
        result = {
            "success": False,
            "output": cleaned_output if "cleaned_output" in locals() else "",
            "attempts": max_retries,
            "validation_result": validation_result if "validation_result" in locals() else None,
            "execution_time": execution_time,
        }
        if debug:
            result["debug_info"] = debug_info
        return result

    def _build_system_prompt(self, prompt_template: str, validator: BaseValidator, input_data: Dict[str, Any]) -> str:
        """Build comprehensive system prompt for ChatBot initialization."""
        # Get validation instructions
        validation_instructions = validator.get_validation_instructions()
        # Create comprehensive system prompt
        system_prompt = f"""You are an expert assistant that provides precise, well-formatted responses according to the given instructions.
{validation_instructions}
IMPORTANT: Your responses will be automatically validated. Please ensure they exactly match the required format.
When I ask you to correct previous errors, please analyze the feedback carefully and provide an improved response that addresses all the validation issues."""
        return system_prompt

    def _extract_output(self, llm_response: str) -> str:
        """Extract the raw output from LLM response with minimal processing."""
        # Only strip whitespace - let the validator handle formatting validation
        return llm_response.strip()

    def save_execution_log(self, result: Dict[str, Any], output_path: Path) -> None:
        """Save detailed execution log for debugging and analysis."""
        log_data = {
            "timestamp": time.time(),
            "success": result["success"],
            "attempts": result["attempts"],
            "execution_time": result["execution_time"],
            "model_name": self.model_name,
        }
        if "debug_info" in result:
            log_data["debug_info"] = result["debug_info"]
        if result["validation_result"]:
            log_data["final_validation"] = {
                "is_valid": result["validation_result"].is_valid,
                "errors": result["validation_result"].errors,
                "warnings": result["validation_result"].warnings,
            }
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(log_data, f, indent=2, ensure_ascii=False)
        logger.info(f"Execution log saved to: {output_path}")
