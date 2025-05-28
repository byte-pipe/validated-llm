"""
Tests for the TestValidator.
"""

import pytest

from validated_llm.validators.test import TestValidator


class TestTestValidator:
    """Test suite for TestValidator."""

    def test_valid_python_unittest(self):
        """Test validation of proper Python unittest code."""
        validator = TestValidator(language="python")

        valid_test_code = """import unittest

class TestCalculator(unittest.TestCase):

    def test_addition(self):
        self.assertEqual(2 + 3, 5)
        self.assertEqual(0 + 0, 0)
        self.assertEqual(-1 + 1, 0)

    def test_subtraction(self):
        self.assertEqual(5 - 3, 2)
        self.assertEqual(0 - 0, 0)

    def test_division_by_zero(self):
        with self.assertRaises(ZeroDivisionError):
            1 / 0

if __name__ == '__main__':
    unittest.main()
"""

        result = validator.validate(valid_test_code)
        assert result.is_valid
        assert result.metadata["test_functions"] >= 3
        assert result.metadata["has_test_framework"] is True

    def test_valid_python_pytest(self):
        """Test validation of proper pytest code."""
        validator = TestValidator(language="python")

        pytest_code = """import pytest

def test_factorial():
    assert factorial(0) == 1
    assert factorial(1) == 1
    assert factorial(5) == 120

def test_factorial_negative():
    with pytest.raises(ValueError):
        factorial(-1)

def test_factorial_edge_cases():
    assert factorial(0) == 1  # Edge case: zero
    assert factorial(1) == 1  # Edge case: one
"""

        result = validator.validate(pytest_code)
        assert result.is_valid
        assert result.metadata["test_functions"] >= 3

    def test_insufficient_test_functions(self):
        """Test detection of insufficient test functions."""
        validator = TestValidator(language="python", min_test_functions=3)

        insufficient_code = """import unittest

def test_only_one():
    assert True
"""

        result = validator.validate(insufficient_code)
        assert not result.is_valid
        assert any("Insufficient test functions" in e for e in result.errors)

    def test_no_assertions(self):
        """Test detection of tests without assertions."""
        validator = TestValidator(language="python")

        no_assertions_code = """def test_something():
    x = 1 + 1
    print("This test does nothing")
"""

        result = validator.validate(no_assertions_code)
        # Should warn about low assertion count
        assert len(result.warnings) > 0

    def test_naming_convention_validation(self):
        """Test validation of test naming conventions."""
        validator = TestValidator(language="python", check_naming=True)

        bad_naming_code = """import unittest

def calculate_something():  # Not a test function name
    assert 2 + 2 == 4

def another_function():  # Not a test function name
    assert True
"""

        result = validator.validate(bad_naming_code)
        assert result.metadata["test_functions"] == 0  # No properly named test functions

    def test_edge_case_requirement(self):
        """Test requirement for edge case testing."""
        validator = TestValidator(language="python", require_edge_cases=True)

        no_edge_cases_code = """import unittest

def test_normal_case():
    assert add(2, 3) == 5
"""

        result = validator.validate(no_edge_cases_code)
        assert any("edge case" in w for w in result.warnings)

    def test_error_test_requirement(self):
        """Test requirement for error testing."""
        validator = TestValidator(language="python", require_error_tests=True)

        no_error_tests_code = """import unittest

def test_normal_operation():
    assert calculate(5) == 25
"""

        result = validator.validate(no_error_tests_code)
        assert not result.is_valid
        assert any("error" in e or "exception" in e for e in result.errors)

    def test_javascript_jest_validation(self):
        """Test validation of JavaScript Jest tests."""
        validator = TestValidator(language="javascript")

        jest_code = """describe('Calculator', () => {
    test('should add two numbers', () => {
        expect(add(2, 3)).toBe(5);
        expect(add(0, 0)).toBe(0);
    });

    test('should handle negative numbers', () => {
        expect(add(-1, 1)).toBe(0);
        expect(add(-5, -3)).toBe(-8);
    });

    test('should throw error for invalid input', () => {
        expect(() => add('a', 'b')).toThrow();
    });
});
"""

        result = validator.validate(jest_code)
        assert result.is_valid
        assert result.metadata["test_blocks"] >= 3
        assert result.metadata["assertions"] >= 5

    def test_java_junit_validation(self):
        """Test validation of Java JUnit tests."""
        validator = TestValidator(language="java")

        junit_code = """import org.junit.Test;
import static org.junit.Assert.*;

public class CalculatorTest {

    @Test
    public void testAddition() {
        assertEquals(5, Calculator.add(2, 3));
        assertEquals(0, Calculator.add(0, 0));
    }

    @Test
    public void testDivisionByZero() {
        assertThrows(ArithmeticException.class, () -> {
            Calculator.divide(10, 0);
        });
    }

    @Test
    public void testNullInput() {
        assertThrows(IllegalArgumentException.class, () -> {
            Calculator.process(null);
        });
    }
}
"""

        result = validator.validate(junit_code)
        assert result.is_valid
        assert result.metadata["test_methods"] >= 3

    def test_go_testing_validation(self):
        """Test validation of Go testing code."""
        validator = TestValidator(language="go")

        go_test_code = """package calculator

import (
    "testing"
)

func TestAdd(t *testing.T) {
    result := Add(2, 3)
    if result != 5 {
        t.Errorf("Expected 5, got %d", result)
    }
}

func TestAddZero(t *testing.T) {
    result := Add(0, 0)
    if result != 0 {
        t.Errorf("Expected 0, got %d", result)
    }
}

func TestDivideByZero(t *testing.T) {
    defer func() {
        if r := recover(); r == nil {
            t.Errorf("Expected panic for division by zero")
        }
    }()

    Divide(10, 0)
}
"""

        result = validator.validate(go_test_code)
        assert result.is_valid
        assert result.metadata["test_functions"] >= 3

    def test_documentation_requirement(self):
        """Test requirement for test documentation."""
        validator = TestValidator(language="python", check_documentation=True)

        undocumented_test = '''import unittest

def test_something():
    assert True

def test_another_thing():
    """This test has documentation."""
    assert True
'''

        result = validator.validate(undocumented_test)
        # Should warn about missing documentation
        assert any("documentation" in w for w in result.warnings)

    def test_setup_teardown_requirement(self):
        """Test requirement for setup/teardown methods."""
        validator = TestValidator(language="python", require_setup_teardown=True)

        no_setup_code = """import unittest

def test_something():
    assert True
"""

        result = validator.validate(no_setup_code)
        assert any("setup" in w for w in result.warnings)
        assert any("teardown" in w for w in result.warnings)

    def test_minimum_assertions_per_test(self):
        """Test minimum assertions per test requirement."""
        validator = TestValidator(language="python", min_assertions_per_test=2)

        few_assertions_code = """import unittest

def test_insufficient_assertions():
    assert True  # Only one assertion
"""

        result = validator.validate(few_assertions_code)
        assert any("assertions" in w for w in result.warnings)

    def test_unsupported_language(self):
        """Test handling of unsupported languages."""
        with pytest.raises(ValueError) as exc_info:
            TestValidator(language="pascal")

        assert "Unsupported language" in str(exc_info.value)

    def test_syntax_error_handling(self):
        """Test handling of syntax errors in test code."""
        validator = TestValidator(language="python")

        invalid_code = """def test_broken(
    assert True  # Missing closing parenthesis
"""

        result = validator.validate(invalid_code)
        assert not result.is_valid
        assert any("syntax" in e.lower() for e in result.errors)

    def test_empty_code(self):
        """Test validation of empty test code."""
        validator = TestValidator(language="python")

        result = validator.validate("")
        assert not result.is_valid
        assert any("Insufficient test functions" in e for e in result.errors)

    def test_comprehensive_test_validation(self):
        """Test comprehensive validation with all requirements."""
        validator = TestValidator(language="python", min_test_functions=2, min_assertions_per_test=2, require_edge_cases=True, require_error_tests=True, check_documentation=True)

        comprehensive_code = '''import unittest
import pytest

class TestMathOperations(unittest.TestCase):
    """Test suite for mathematical operations."""

    def test_addition_normal_cases(self):
        """Test addition with normal inputs."""
        self.assertEqual(add(2, 3), 5)
        self.assertEqual(add(10, 20), 30)

    def test_addition_edge_cases(self):
        """Test addition with edge cases."""
        self.assertEqual(add(0, 0), 0)  # Zero edge case
        self.assertEqual(add(-1, 1), 0)  # Negative edge case

    def test_division_error_cases(self):
        """Test division error handling."""
        with self.assertRaises(ZeroDivisionError):
            divide(10, 0)
        with self.assertRaises(TypeError):
            divide("10", "2")
'''

        result = validator.validate(comprehensive_code)
        assert result.is_valid
        assert result.metadata["test_functions"] >= 2
        assert result.metadata["has_test_framework"] is True
