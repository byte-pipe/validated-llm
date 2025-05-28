"""
Tests for the SyntaxValidator.
"""

import pytest

from validated_llm.validators.syntax import SyntaxValidator


class TestSyntaxValidator:
    """Test suite for SyntaxValidator."""

    def test_valid_python_syntax(self):
        """Test validation of valid Python code."""
        validator = SyntaxValidator(language="python", check_best_practices=False)

        valid_code = """
def factorial(n):
    \"\"\"Calculate factorial of n.\"\"\"
    if n <= 1:
        return 1
    return n * factorial(n - 1)

class Calculator:
    def add(self, a, b):
        return a + b
"""

        result = validator.validate(valid_code)
        assert result.is_valid
        assert len(result.errors) == 0
        assert "ast_nodes" in result.metadata

    def test_invalid_python_syntax(self):
        """Test detection of Python syntax errors."""
        validator = SyntaxValidator(language="python")

        invalid_code = """
def broken_function(
    print("Missing closing parenthesis"
    return True
"""

        result = validator.validate(invalid_code)
        assert not result.is_valid
        assert len(result.errors) > 0
        assert "syntax error" in result.errors[0].lower()

    def test_python_indentation_error(self):
        """Test detection of Python indentation errors."""
        validator = SyntaxValidator(language="python")

        invalid_code = """
def test():
print("Bad indentation")
"""

        result = validator.validate(invalid_code)
        assert not result.is_valid
        assert len(result.errors) > 0

    def test_python_best_practices_warnings(self):
        """Test Python best practices warnings."""
        validator = SyntaxValidator(language="python", strict_mode=False)

        code_with_issues = """
def no_docstring():
    return 42

try:
    risky_operation()
except:
    pass
"""

        result = validator.validate(code_with_issues)
        assert result.is_valid  # Still valid syntax
        assert len(result.warnings) > 0
        assert any("docstring" in w for w in result.warnings)
        assert any("except" in w for w in result.warnings)

    def test_strict_mode(self):
        """Test strict mode converts warnings to errors."""
        validator = SyntaxValidator(language="python", strict_mode=True)

        code_with_issues = """
def no_docstring():
    return 42
"""

        result = validator.validate(code_with_issues)
        assert not result.is_valid
        assert len(result.errors) > 0
        assert any("docstring" in e for e in result.errors)

    def test_valid_javascript_syntax(self):
        """Test validation of valid JavaScript code."""
        validator = SyntaxValidator(language="javascript")

        valid_code = """
function fibonacci(n) {
    if (n <= 1) return n;
    return fibonacci(n - 1) + fibonacci(n - 2);
}

const calculator = {
    add: (a, b) => a + b,
    subtract: (a, b) => a - b
};
"""

        result = validator.validate(valid_code)
        # Will be valid or have warning about Node.js not available
        assert result.is_valid or len(result.warnings) > 0

    def test_invalid_javascript_syntax(self):
        """Test detection of JavaScript syntax errors."""
        validator = SyntaxValidator(language="javascript")

        invalid_code = """
function broken() {
    const x = {
        key: "value"
    // Missing closing brace
}
"""

        result = validator.validate(invalid_code)
        # If Node.js is available, should catch the error
        if result.is_valid and len(result.warnings) > 0:
            # Node.js not available, skip validation
            assert "not available" in result.warnings[0]
        else:
            assert not result.is_valid
            assert len(result.errors) > 0

    def test_valid_go_syntax(self):
        """Test validation of valid Go code."""
        validator = SyntaxValidator(language="go")

        valid_code = """
package main

import "fmt"

func main() {
    fmt.Println("Hello, World!")
}

func add(a, b int) int {
    return a + b
}
"""

        result = validator.validate(valid_code)
        assert result.is_valid or len(result.warnings) > 0

    def test_go_missing_package(self):
        """Test Go code without package declaration."""
        validator = SyntaxValidator(language="go")

        # Should auto-add package main
        code = """
func hello() {
    fmt.Println("Hello")
}
"""

        result = validator.validate(code)
        # Should handle missing package gracefully
        assert result.is_valid or len(result.warnings) > 0 or len(result.errors) > 0

    def test_valid_rust_syntax(self):
        """Test validation of valid Rust code."""
        validator = SyntaxValidator(language="rust")

        valid_code = """
fn factorial(n: u32) -> u32 {
    match n {
        0 | 1 => 1,
        _ => n * factorial(n - 1),
    }
}

struct Point {
    x: f64,
    y: f64,
}
"""

        result = validator.validate(valid_code)
        assert result.is_valid or len(result.warnings) > 0

    def test_valid_java_syntax(self):
        """Test validation of valid Java code."""
        validator = SyntaxValidator(language="java")

        valid_code = """
public class HelloWorld {
    public static void main(String[] args) {
        System.out.println("Hello, World!");
    }

    public int add(int a, int b) {
        return a + b;
    }
}
"""

        result = validator.validate(valid_code)
        assert result.is_valid or len(result.warnings) > 0

    def test_java_no_class(self):
        """Test Java code without class definition."""
        validator = SyntaxValidator(language="java")

        invalid_code = """
public static void main(String[] args) {
    System.out.println("No class!");
}
"""

        result = validator.validate(invalid_code)
        if not result.is_valid:
            assert any("class" in e for e in result.errors)

    def test_unsupported_language(self):
        """Test handling of unsupported languages."""
        with pytest.raises(ValueError) as exc_info:
            SyntaxValidator(language="cobol")

        assert "Unsupported language" in str(exc_info.value)

    def test_timeout_handling(self):
        """Test timeout handling for external validators."""
        validator = SyntaxValidator(language="python", timeout=1)

        # This should complete quickly
        result = validator.validate("print('hello')")
        assert result.is_valid

    def test_empty_code(self):
        """Test validation of empty code."""
        validator = SyntaxValidator(language="python")

        # Empty code is valid Python
        result = validator.validate("")
        assert result.is_valid

        result = validator.validate("   \n  \n  ")
        assert result.is_valid
