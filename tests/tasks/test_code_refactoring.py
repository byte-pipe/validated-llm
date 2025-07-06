"""
Tests for the CodeRefactoringTask.
"""

import pytest

from validated_llm.tasks.code_refactoring import CleanCodeRefactoringTask, CodeRefactoringTask, ModernizationRefactoringTask, PerformanceRefactoringTask
from validated_llm.validators.refactoring import RefactoringValidator


class TestCodeRefactoringTask:
    """Test the CodeRefactoringTask."""

    def test_task_initialization(self):
        """Test task initialization with default parameters."""
        task = CodeRefactoringTask()

        assert task.name == "Python Code Refactoring"
        assert task.description == "Refactor python code to improve quality while preserving functionality"
        assert task.language == "python"
        assert task.check_complexity is True
        assert task.check_naming is True
        assert task.check_structure is True
        assert task.max_complexity == 10
        assert task.refactoring_style == "clean_code"

    def test_task_with_custom_language(self):
        """Test task initialization with custom language."""
        task = CodeRefactoringTask(language="javascript")

        assert task.name == "Javascript Code Refactoring"
        assert task.language == "javascript"

    def test_validator_class(self):
        """Test that the correct validator class is used."""
        task = CodeRefactoringTask()
        assert task.validator_class == RefactoringValidator

    def test_prompt_template_structure(self):
        """Test the structure of the prompt template."""
        task = CodeRefactoringTask()
        template = task.prompt_template

        # Check for key sections
        assert "Refactor the following python code" in template
        assert "REFACTORING REQUIREMENTS:" in template
        assert "SPECIFIC IMPROVEMENTS TO FOCUS ON:" in template
        assert "CONSTRAINTS:" in template
        assert "Maximum cyclomatic complexity: 10" in template

    def test_prepare_prompt_data_basic(self):
        """Test basic prompt data preparation."""
        task = CodeRefactoringTask()

        original_code = """
def calculate_total(items):
    total = 0
    for item in items:
        if item.price > 0:
            if item.quantity > 0:
                total = total + item.price * item.quantity
    return total
"""

        data = task.prepare_prompt_data(original_code=original_code, refactoring_goals="reduce complexity, improve readability")

        assert data["original_code"] == original_code
        assert data["refactoring_goals"] == "reduce complexity, improve readability"
        assert "improvement_focus" in data
        assert "additional_constraints" in data

    def test_prepare_prompt_data_with_list_goals(self):
        """Test prompt data with list of refactoring goals."""
        task = CodeRefactoringTask()

        data = task.prepare_prompt_data(original_code="def foo(): pass", refactoring_goals=["reduce complexity", "improve naming", "add type hints"])

        assert data["refactoring_goals"] == "reduce complexity, improve naming, add type hints"

    def test_improvement_focus_generation(self):
        """Test generation of improvement focus based on configuration."""
        task = CodeRefactoringTask(check_complexity=True, check_naming=True, check_structure=True)

        data = task.prepare_prompt_data(original_code="def foo(): pass", focus_performance=True, focus_readability=True, extract_functions=True)

        focus = data["improvement_focus"]
        assert "Reduce cyclomatic complexity" in focus
        assert "clear, descriptive names" in focus
        assert "Optimize for performance" in focus
        assert "Prioritize readability" in focus
        assert "Extract complex logic" in focus

    def test_additional_constraints(self):
        """Test generation of additional constraints."""
        task = CodeRefactoringTask()

        data = task.prepare_prompt_data(original_code="def foo(): pass", preserve_api=True, preserve_imports=True, preserve_comments=True, target_complexity=5)

        constraints = data["additional_constraints"]
        assert "Preserve all public function/class interfaces" in constraints
        assert "Keep the same imports" in constraints
        assert "Preserve existing comments" in constraints
        assert "Target complexity: 5" in constraints

    def test_clean_code_style(self):
        """Test clean code refactoring style."""
        task = CodeRefactoringTask(refactoring_style="clean_code")
        template = task.prompt_template

        assert "CLEAN CODE PRINCIPLES:" in template
        assert "Single Responsibility" in template
        assert "DRY (Don't Repeat Yourself)" in template
        assert "KISS (Keep It Simple)" in template

    def test_performance_style(self):
        """Test performance refactoring style."""
        task = CodeRefactoringTask(refactoring_style="performance")
        template = task.prompt_template

        assert "PERFORMANCE OPTIMIZATION:" in template
        assert "Minimize computational complexity" in template
        assert "efficient data structures" in template

    def test_functional_style(self):
        """Test functional programming refactoring style."""
        task = CodeRefactoringTask(refactoring_style="functional")
        template = task.prompt_template

        assert "FUNCTIONAL PROGRAMMING STYLE:" in template
        assert "immutability" in template
        assert "pure functions" in template
        assert "map/filter/reduce" in template

    def test_configure_validator(self):
        """Test validator configuration."""
        task = CodeRefactoringTask(language="javascript", check_complexity=False, max_complexity=15)

        config = task.configure_validator()

        assert config["language"] == "javascript"
        assert config["check_complexity"] is False
        assert config["max_complexity"] == 15

    def test_configure_validator_with_original_code(self):
        """Test validator configuration includes original code."""
        task = CodeRefactoringTask()

        # Prepare prompt data first to set original code
        task.prepare_prompt_data(original_code="def original(): pass")

        config = task.configure_validator()
        assert config["original_code"] == "def original(): pass"


class TestSpecializedRefactoringTasks:
    """Test specialized refactoring task variants."""

    def test_performance_refactoring_task(self):
        """Test PerformanceRefactoringTask."""
        task = PerformanceRefactoringTask()

        assert task.refactoring_style == "performance"
        assert task.check_complexity is True
        assert "PERFORMANCE OPTIMIZATION:" in task.prompt_template

    def test_clean_code_refactoring_task(self):
        """Test CleanCodeRefactoringTask."""
        task = CleanCodeRefactoringTask()

        assert task.refactoring_style == "clean_code"
        assert task.check_naming is True
        assert task.check_structure is True
        assert task.max_complexity == 8
        assert "CLEAN CODE PRINCIPLES:" in task.prompt_template

    def test_modernization_refactoring_task(self):
        """Test ModernizationRefactoringTask."""
        task = ModernizationRefactoringTask()

        assert task.refactoring_style == "modern"
        assert task.check_structure is True

        template = task.prompt_template
        assert "MODERN CODE STYLE:" in template
        assert "latest language features" in template

    def test_specialized_task_custom_params(self):
        """Test specialized tasks with custom parameters."""
        task = PerformanceRefactoringTask(language="go", max_complexity=5)

        assert task.language == "go"
        assert task.max_complexity == 5
        assert task.refactoring_style == "performance"
