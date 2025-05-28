"""
Validation tasks for common LLM use cases.

Tasks pair prompts with their corresponding validators to create complete
LLM workflows with validation.
"""

from .base_task import BaseTask
from .code_generation import ClassGenerationTask, CodeGenerationTask, FunctionGenerationTask, ProgramGenerationTask
from .csv_generation import CSVGenerationTask
from .documentation import APIDocumentationTask, ChangelogTask, DocumentationTask, ReadmeTask, TechnicalSpecTask, TutorialTask, UserGuideTask
from .json_generation import PersonJSONTask, ProductCatalogTask
from .story_to_scenes import StoryToScenesTask
from .test_generation import BDDTestGenerationTask, IntegrationTestGenerationTask, TestGenerationTask, UnitTestGenerationTask

__all__ = [
    "BaseTask",
    "APIDocumentationTask",
    "ChangelogTask",
    "ClassGenerationTask",
    "CodeGenerationTask",
    "CSVGenerationTask",
    "DocumentationTask",
    "FunctionGenerationTask",
    "PersonJSONTask",
    "ProductCatalogTask",
    "ProgramGenerationTask",
    "ReadmeTask",
    "StoryToScenesTask",
    "TechnicalSpecTask",
    "TestGenerationTask",
    "TutorialTask",
    "UnitTestGenerationTask",
    "IntegrationTestGenerationTask",
    "BDDTestGenerationTask",
    "UserGuideTask",
]
