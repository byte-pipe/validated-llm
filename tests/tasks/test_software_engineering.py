"""
Tests for software engineering tasks.
"""

import json
from typing import Any, Dict

import pytest

from validated_llm.tasks.software_engineering import AnalysisType, CodebaseAnalysisTask, RequirementsTask, RequirementType, UserStoryTask


class TestCodebaseAnalysisTask:
    """Test cases for CodebaseAnalysisTask."""

    def test_task_initialization(self):
        """Test task initialization with default parameters."""
        task = CodebaseAnalysisTask()

        assert task.name == "CodebaseAnalysisTask"
        assert "codebase analysis" in task.description.lower()
        assert task.project_language == "python"
        assert task.project_type == "web_application"
        assert AnalysisType.ARCHITECTURE in task.analysis_types
        assert AnalysisType.SECURITY in task.analysis_types
        assert task.include_dependencies is True
        assert task.include_metrics is True
        assert task.include_recommendations is True

    def test_task_initialization_custom_parameters(self):
        """Test task initialization with custom parameters."""
        analysis_types = [AnalysisType.SECURITY, AnalysisType.PERFORMANCE]

        task = CodebaseAnalysisTask(analysis_types=analysis_types, project_language="javascript", project_type="mobile_app", include_dependencies=False, max_issues_per_category=5)

        assert task.analysis_types == analysis_types
        assert task.project_language == "javascript"
        assert task.project_type == "mobile_app"
        assert task.include_dependencies is False
        assert task.max_issues_per_category == 5

    def test_prompt_template_content(self):
        """Test that prompt template contains required elements."""
        task = CodebaseAnalysisTask(analysis_types=[AnalysisType.SECURITY, AnalysisType.ARCHITECTURE], project_language="python")

        prompt = task.prompt_template

        # Check basic structure
        assert "software architect" in prompt.lower()
        assert "codebase" in prompt.lower()
        assert "analysis" in prompt.lower()

        # Check project information
        assert "python" in prompt
        assert "security" in prompt.lower()
        assert "architecture" in prompt.lower()

        # Check output requirements
        assert "json" in prompt.lower()
        assert "project_overview" in prompt
        assert "analysis_results" in prompt
        assert "recommendations" in prompt

        # Check placeholder for codebase content
        assert "{codebase_content}" in prompt

    def test_validator_creation(self):
        """Test validator creation and configuration."""
        task = CodebaseAnalysisTask()
        validator = task.create_validator()

        assert validator is not None
        assert hasattr(validator, "validate")

    def test_schema_validation_structure(self):
        """Test that the analysis schema has required structure."""
        task = CodebaseAnalysisTask()
        schema = task._build_analysis_schema()

        # Check top-level structure
        assert "type" in schema
        assert schema["type"] == "object"
        assert "properties" in schema
        assert "required" in schema

        properties = schema["properties"]

        # Check required sections
        assert "project_overview" in properties
        assert "analysis_results" in properties
        assert "summary" in properties

        # Check project overview structure
        project_props = properties["project_overview"]["properties"]
        assert "name" in project_props
        assert "language" in project_props
        assert "type" in project_props
        assert "description" in project_props

        # Check analysis results structure
        analysis_props = properties["analysis_results"]["properties"]
        assert "architecture" in analysis_props
        assert "security" in analysis_props
        assert "quality" in analysis_props

    def test_analysis_types_enum(self):
        """Test AnalysisType enum values."""
        assert AnalysisType.ARCHITECTURE.value == "architecture"
        assert AnalysisType.SECURITY.value == "security"
        assert AnalysisType.PERFORMANCE.value == "performance"
        assert AnalysisType.MAINTAINABILITY.value == "maintainability"
        assert AnalysisType.QUALITY.value == "quality"
        assert AnalysisType.DEPENDENCIES.value == "dependencies"
        assert AnalysisType.TESTING.value == "testing"
        assert AnalysisType.DOCUMENTATION.value == "documentation"


class TestRequirementsTask:
    """Test cases for RequirementsTask."""

    def test_task_initialization(self):
        """Test task initialization with default parameters."""
        task = RequirementsTask()

        assert task.name == "RequirementsTask"
        assert "requirements" in task.description.lower()
        assert task.project_type == "web_application"
        assert RequirementType.FUNCTIONAL in task.requirement_types
        assert RequirementType.NON_FUNCTIONAL in task.requirement_types
        assert RequirementType.TECHNICAL in task.requirement_types
        assert task.include_acceptance_criteria is True
        assert task.include_priorities is True
        assert task.include_traceability is True

    def test_task_initialization_custom_parameters(self):
        """Test task initialization with custom parameters."""
        req_types = [RequirementType.FUNCTIONAL, RequirementType.BUSINESS]
        stakeholders = ["customer", "developer"]
        compliance = ["GDPR", "SOX"]

        task = RequirementsTask(requirement_types=req_types, project_type="enterprise_system", stakeholders=stakeholders, compliance_standards=compliance, include_acceptance_criteria=False, min_requirements_per_type=5)

        assert task.requirement_types == req_types
        assert task.project_type == "enterprise_system"
        assert task.stakeholders == stakeholders
        assert task.compliance_standards == compliance
        assert task.include_acceptance_criteria is False
        assert task.min_requirements_per_type == 5

    def test_prompt_template_content(self):
        """Test that prompt template contains required elements."""
        task = RequirementsTask(requirement_types=[RequirementType.FUNCTIONAL, RequirementType.TECHNICAL], stakeholders=["user", "admin"], compliance_standards=["HIPAA"])

        prompt = task.prompt_template

        # Check basic structure
        assert "business analyst" in prompt.lower()
        assert "requirements" in prompt.lower()

        # Check project information
        assert "functional" in prompt.lower()
        assert "technical" in prompt.lower()
        assert "user, admin" in prompt
        assert "HIPAA" in prompt

        # Check output requirements
        assert "json" in prompt.lower()
        assert "document_info" in prompt
        assert "functional_requirements" in prompt
        assert "technical_requirements" in prompt

        # Check placeholder for project description
        assert "{project_description}" in prompt

    def test_validator_creation(self):
        """Test validator creation and configuration."""
        task = RequirementsTask()
        validator = task.create_validator()

        assert validator is not None
        assert hasattr(validator, "validate")

    def test_schema_validation_structure(self):
        """Test that the requirements schema has required structure."""
        task = RequirementsTask()
        schema = task._build_requirements_schema()

        # Check top-level structure
        assert "type" in schema
        assert schema["type"] == "object"
        assert "properties" in schema
        assert "required" in schema

        properties = schema["properties"]

        # Check required sections
        assert "document_info" in properties
        assert "functional_requirements" in properties

        # Check functional requirements structure
        func_req = properties["functional_requirements"]
        assert func_req["type"] == "array"
        assert "minItems" in func_req
        assert func_req["minItems"] == 1

        # Check requirement item structure
        req_item = func_req["items"]["properties"]
        assert "id" in req_item
        assert "title" in req_item
        assert "description" in req_item
        assert "priority" in req_item
        assert "acceptance_criteria" in req_item

    def test_requirement_types_enum(self):
        """Test RequirementType enum values."""
        assert RequirementType.FUNCTIONAL.value == "functional"
        assert RequirementType.NON_FUNCTIONAL.value == "non_functional"
        assert RequirementType.TECHNICAL.value == "technical"
        assert RequirementType.BUSINESS.value == "business"
        assert RequirementType.USER.value == "user"
        assert RequirementType.SYSTEM.value == "system"


class TestUserStoryTask:
    """Test cases for UserStoryTask."""

    def test_task_initialization(self):
        """Test task initialization with default parameters."""
        task = UserStoryTask()

        assert task.name == "UserStoryTask"
        assert "user stories" in task.description.lower()
        assert task.story_format == "standard"
        assert task.include_acceptance_criteria is True
        assert task.include_story_points is True
        assert task.include_dependencies is True
        assert task.include_business_value is True
        assert task.epic_organization is True
        assert task.min_stories == 5
        assert task.max_stories == 20

    def test_task_initialization_custom_parameters(self):
        """Test task initialization with custom parameters."""
        personas = ["developer", "tester"]

        task = UserStoryTask(story_format="job_story", include_acceptance_criteria=False, include_story_points=False, persona_types=personas, epic_organization=False, min_stories=3, max_stories=10)

        assert task.story_format == "job_story"
        assert task.include_acceptance_criteria is False
        assert task.include_story_points is False
        assert task.persona_types == personas
        assert task.epic_organization is False
        assert task.min_stories == 3
        assert task.max_stories == 10

    def test_prompt_template_content(self):
        """Test that prompt template contains required elements."""
        task = UserStoryTask(persona_types=["user", "admin"], include_acceptance_criteria=True, epic_organization=True)

        prompt = task.prompt_template

        # Check basic structure
        assert "product owner" in prompt.lower()
        assert "user stories" in prompt.lower()
        assert "agile" in prompt.lower()

        # Check format information
        assert "As a [persona]" in prompt
        assert "I want [functionality]" in prompt
        assert "so that [benefit" in prompt

        # Check conditional content
        assert "given-when-then" in prompt.lower()
        assert "epics" in prompt.lower()

        # Check output requirements
        assert "json" in prompt.lower()
        assert "user_stories" in prompt
        assert "acceptance_criteria" in prompt

        # Check placeholder for requirements
        assert "{product_requirements}" in prompt

    def test_validator_creation(self):
        """Test validator creation and configuration."""
        task = UserStoryTask()
        validator = task.create_validator()

        assert validator is not None
        assert hasattr(validator, "validate")

    def test_schema_validation_structure(self):
        """Test that the user story schema has required structure."""
        task = UserStoryTask()
        schema = task._build_story_schema()

        # Check top-level structure
        assert "type" in schema
        assert schema["type"] == "object"
        assert "properties" in schema
        assert "required" in schema

        properties = schema["properties"]

        # Check required sections
        assert "backlog_info" in properties
        assert "user_stories" in properties

        # Check user stories structure
        stories = properties["user_stories"]
        assert stories["type"] == "array"
        assert "minItems" in stories
        assert stories["minItems"] == 1

        # Check story item structure
        story_item = stories["items"]["properties"]
        assert "id" in story_item
        assert "title" in story_item
        assert "story" in story_item
        assert "persona" in story_item
        assert "priority" in story_item
        assert "acceptance_criteria" in story_item

        # Check acceptance criteria structure
        ac_item = story_item["acceptance_criteria"]["items"]["properties"]
        assert "scenario" in ac_item
        assert "given" in ac_item
        assert "when" in ac_item
        assert "then" in ac_item

    def test_story_points_validation(self):
        """Test story points validation range."""
        task = UserStoryTask()
        schema = task._build_story_schema()

        story_points = schema["properties"]["user_stories"]["items"]["properties"]["story_points"]
        assert story_points["type"] == "integer"
        assert story_points["minimum"] == 1
        assert story_points["maximum"] == 21  # Common Fibonacci sequence max

    def test_priority_enum_validation(self):
        """Test priority enum validation."""
        task = UserStoryTask()
        schema = task._build_story_schema()

        priority = schema["properties"]["user_stories"]["items"]["properties"]["priority"]
        assert priority["type"] == "string"
        assert "enum" in priority
        assert "critical" in priority["enum"]
        assert "high" in priority["enum"]
        assert "medium" in priority["enum"]
        assert "low" in priority["enum"]


class TestSoftwareEngineeringTasksIntegration:
    """Integration tests for software engineering tasks."""

    def test_all_tasks_have_consistent_interface(self):
        """Test that all tasks implement the required interface consistently."""
        tasks = [CodebaseAnalysisTask(), RequirementsTask(), UserStoryTask()]

        for task in tasks:
            # Check required properties
            assert hasattr(task, "name")
            assert hasattr(task, "description")
            assert hasattr(task, "prompt_template")
            assert hasattr(task, "validator_class")

            # Check required methods
            assert hasattr(task, "create_validator")
            assert callable(task.create_validator)

            # Check that properties return appropriate types
            assert isinstance(task.name, str)
            assert isinstance(task.description, str)
            assert isinstance(task.prompt_template, str)
            assert len(task.name) > 0
            assert len(task.description) > 0
            assert len(task.prompt_template) > 0

    def test_validator_creation_consistency(self):
        """Test that all tasks create valid validators."""
        tasks = [CodebaseAnalysisTask(), RequirementsTask(), UserStoryTask()]

        for task in tasks:
            validator = task.create_validator()

            # Check validator interface
            assert hasattr(validator, "validate")
            assert callable(validator.validate)

    def test_prompt_template_placeholders(self):
        """Test that prompt templates contain expected placeholders."""
        test_cases = [(CodebaseAnalysisTask(), "{codebase_content}"), (RequirementsTask(), "{project_description}"), (UserStoryTask(), "{product_requirements}")]

        for task, expected_placeholder in test_cases:
            prompt = task.prompt_template
            assert expected_placeholder in prompt, f"Missing placeholder in {task.name}"

    def test_json_output_requirements(self):
        """Test that all tasks require JSON output."""
        tasks = [CodebaseAnalysisTask(), RequirementsTask(), UserStoryTask()]

        for task in tasks:
            prompt = task.prompt_template
            assert "json" in prompt.lower(), f"Missing JSON requirement in {task.name}"
            assert "```json" in prompt, f"Missing JSON example in {task.name}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
