"""
validated-llm: LLM output validation with retry loops

A robust framework for validating language model outputs with automatic retry mechanisms.
Designed for applications where you need reliable, structured responses from LLMs.
"""

from .base_validator import BaseValidator

# Import specific task classes
from .tasks.base_task import BaseTask
from .tasks.csv_generation import CSVGenerationTask
from .tasks.json_generation import PersonJSONTask, ProductCatalogTask
from .tasks.story_to_scenes import StoryToScenesTask
from .validation_loop import ValidationLoop


# Define exceptions (will be moved to separate module later)
class ValidationError(Exception):
    """Raised when validation fails"""


class MaxRetriesExceeded(Exception):
    """Raised when maximum retry attempts are exceeded"""


class LLMError(Exception):
    """Raised when LLM API calls fail"""


__version__ = "0.1.0"
__author__ = "validated-llm contributors"
__email__ = "contact@example.com"

__all__ = [
    # Core classes
    "ValidationLoop",
    "BaseTask",
    "BaseValidator",
    # Exceptions
    "ValidationError",
    "MaxRetriesExceeded",
    "LLMError",
    # Tasks
    "CSVGenerationTask",
    "PersonJSONTask",
    "ProductCatalogTask",
    "StoryToScenesTask",
    # Metadata
    "__version__",
]
