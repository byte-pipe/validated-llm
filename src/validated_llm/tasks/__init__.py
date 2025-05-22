"""
Validation tasks for common LLM use cases.

Tasks pair prompts with their corresponding validators to create complete
LLM workflows with validation.
"""

from .base_task import BaseTask
from .csv_generation import CSVGenerationTask
from .json_generation import PersonJSONTask, ProductCatalogTask
from .story_to_scenes import StoryToScenesTask

__all__ = [
    "BaseTask",
    "CSVGenerationTask",
    "PersonJSONTask",
    "ProductCatalogTask",
    "StoryToScenesTask",
]
