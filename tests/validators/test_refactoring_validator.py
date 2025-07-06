"""
Tests for the RefactoringValidator.
"""

import pytest

from validated_llm.validators.refactoring import RefactoringValidator


class TestRefactoringValidator:
    """Test the RefactoringValidator."""

    def test_validator_initialization(self):
        """Test validator initialization with default parameters."""
        validator = RefactoringValidator()

        assert validator.language == "python"
        assert validator.original_code is None
        assert validator.check_complexity is True
        assert validator.check_naming is True
        assert validator.check_structure is True
        assert validator.check_imports is True
        assert validator.max_complexity == 10

    def test_validator_with_original_code(self):
        """Test validator initialization with original code."""
        original = "def foo(): return 42"
        validator = RefactoringValidator(original_code=original)

        assert validator.original_code == original

    def test_validate_syntax_error(self):
        """Test validation fails on syntax errors."""
        validator = RefactoringValidator(language="python")

        result = validator.validate("def foo( invalid syntax")

        assert not result.is_valid
        assert len(result.errors) > 0
        assert any("syntax" in error.lower() for error in result.errors)

    def test_validate_valid_python_refactoring(self):
        """Test validation of valid Python refactoring."""
        validator = RefactoringValidator(language="python")

        refactored_code = """
def calculate_total(items):
    \"\"\"Calculate total price for items.\"\"\"
    return sum(item.price * item.quantity
               for item in items
               if item.price > 0 and item.quantity > 0)
"""

        result = validator.validate(refactored_code)

        assert result.is_valid
        assert "improvements" in result.metadata
        assert len(result.metadata["improvements"]) > 0

    def test_validate_with_complexity_check(self):
        """Test validation with complexity checking."""
        validator = RefactoringValidator(language="python", check_complexity=True, max_complexity=3)

        # High complexity code
        complex_code = """
def process_data(data):
    if data:
        if data.type == "A":
            if data.value > 10:
                return "high"
            else:
                return "low"
        elif data.type == "B":
            if data.value > 20:
                return "very high"
            else:
                return "medium"
        else:
            return "unknown"
    return None
"""

        result = validator.validate(complex_code)

        assert result.is_valid  # Still valid, but with warnings
        assert len(result.warnings) > 0
        assert any("complexity" in warning for warning in result.warnings)

    def test_validate_naming_conventions(self):
        """Test validation of naming conventions."""
        validator = RefactoringValidator(language="python", check_naming=True)

        # Bad naming
        bad_naming_code = """
def ProcessData(dataList):
    class data_processor:
        pass
    return dataList
"""

        result = validator.validate(bad_naming_code)

        assert result.is_valid  # Valid syntax but warnings
        assert len(result.warnings) > 0
        assert any("naming" in str(result.warnings) or "convention" in str(result.warnings) for warning in result.warnings)

    def test_validate_with_structure_improvements(self):
        """Test validation detects structure improvements."""
        validator = RefactoringValidator(language="python", check_structure=True)

        well_structured_code = '''
def calculate_average(numbers: list[float]) -> float:
    """Calculate the average of a list of numbers.

    Args:
        numbers: List of numbers to average.

    Returns:
        The average value.
    """
    if not numbers:
        return 0.0
    return sum(numbers) / len(numbers)
'''

        result = validator.validate(well_structured_code)

        assert result.is_valid
        assert "improvements" in result.metadata
        improvements = result.metadata["improvements"]
        assert any("docstring" in imp for imp in improvements)
        assert any("type hints" in imp for imp in improvements)

    def test_validate_javascript_refactoring(self):
        """Test validation of JavaScript refactoring."""
        validator = RefactoringValidator(language="javascript")

        modern_js = """
const calculateTotal = (items) => {
    return items
        .filter(item => item.price > 0 && item.quantity > 0)
        .reduce((total, item) => total + item.price * item.quantity, 0);
};

const { name, price } = product;
"""

        result = validator.validate(modern_js)

        assert result.is_valid
        assert "improvements" in result.metadata
        improvements = result.metadata["improvements"]
        assert any("arrow functions" in imp for imp in improvements)
        assert any("destructuring" in imp for imp in improvements)

    def test_validate_with_original_comparison(self):
        """Test validation with original code comparison."""
        original_code = """
def add(a, b):
    return a + b

def multiply(x, y):
    return x * y
"""

        validator = RefactoringValidator(language="python", original_code=original_code)

        # Refactored code missing multiply function
        refactored_code = """
def add(a: int, b: int) -> int:
    \"\"\"Add two numbers together.\"\"\"
    return a + b
"""

        result = validator.validate(refactored_code)

        assert not result.is_valid
        assert len(result.errors) > 0
        assert any("multiply" in error for error in result.errors)

    def test_validate_preserves_functionality(self):
        """Test validation ensures functionality is preserved."""
        original_code = """
def process_items(items):
    total = 0
    for item in items:
        total += item
    return total
"""

        validator = RefactoringValidator(language="python", original_code=original_code)

        # Refactored with same functionality
        refactored_code = """
def process_items(items):
    \"\"\"Calculate sum of items.\"\"\"
    return sum(items)
"""

        result = validator.validate(refactored_code)

        assert result.is_valid
        assert result.metadata.get("preserved_functionality", False) is True

    def test_extract_signatures(self):
        """Test signature extraction for different languages."""
        validator = RefactoringValidator(language="python")

        python_code = """
def function_one():
    pass

class MyClass:
    def method(self):
        pass

def function_two(x, y):
    return x + y
"""

        signatures = validator._extract_signatures(python_code)

        assert "function_one" in signatures
        assert "MyClass" in signatures
        assert "function_two" in signatures

    def test_source_code_description(self):
        """Test source code description for LLM context."""
        source = RefactoringValidator.get_source_code()

        assert "RefactoringValidator" in source
        assert "syntactic correctness" in source
        assert "functionality preservation" in source
        assert "quality improvements" in source

    def test_validate_import_organization(self):
        """Test validation of import organization."""
        validator = RefactoringValidator(language="python", check_imports=True)

        # Well-organized imports
        good_imports = """
import os
import sys
from typing import List, Dict

import numpy as np
import pandas as pd

from my_module import helper


def process_data(data: pd.DataFrame) -> Dict:
    return {}
"""

        result = validator.validate(good_imports)

        assert result.is_valid
        assert any("imports" in imp for imp in result.metadata["improvements"])

    def test_validate_typescript_refactoring(self):
        """Test validation of TypeScript refactoring."""
        validator = RefactoringValidator(language="typescript")

        ts_code = """
interface Item {
    isValid: boolean;
    value: number;
}

const processData = (items: Item[]): number => {
    return items
        .filter(item => item.isValid)
        .map(item => item.value)
        .reduce((sum, val) => sum + val, 0);
};
"""

        result = validator.validate(ts_code)

        assert result.is_valid
