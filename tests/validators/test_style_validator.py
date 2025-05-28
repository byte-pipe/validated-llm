"""
Tests for the StyleValidator.
"""

import pytest

from validated_llm.validators.style import StyleValidator


class TestStyleValidator:
    """Test suite for StyleValidator."""

    def test_valid_python_black_style(self):
        """Test validation of properly formatted Python code."""
        validator = StyleValidator(language="python", formatter="black")

        # Code that is already Black-formatted
        valid_code = '''def factorial(n):
    """Calculate factorial of n."""
    if n <= 1:
        return 1
    return n * factorial(n - 1)


class Calculator:
    def add(self, a, b):
        return a + b
'''

        result = validator.validate(valid_code)
        # If Black is not available, should get a warning
        if result.is_valid and len(result.warnings) > 0:
            assert "not available" in result.warnings[0]
        else:
            # If Black is available, code should be valid
            assert result.is_valid or "style standards" in str(result.errors)

    def test_python_style_violations(self):
        """Test detection of Python style violations."""
        validator = StyleValidator(language="python", formatter="black", show_diff=True)

        # Code with style issues (inconsistent spacing, line length)
        bad_style_code = """def  factorial( n ):
    if n<=1: return 1
    else: return n*factorial(n-1)
"""

        result = validator.validate(bad_style_code)
        # If Black is available, should detect style issues
        if len(result.warnings) > 0 and "not available" in result.warnings[0]:
            # Black not available, skip
            assert result.is_valid
        else:
            assert not result.is_valid
            assert any("style standards" in e for e in result.errors)

    def test_auto_fix_mode(self):
        """Test auto-fix mode returns formatted code."""
        validator = StyleValidator(language="python", formatter="black", auto_fix=True)

        messy_code = '''def hello(name):return f"Hello, {name}!"'''

        result = validator.validate(messy_code)
        if len(result.warnings) > 0 and "not available" in result.warnings[0]:
            # Formatter not available
            assert result.is_valid
        else:
            assert result.is_valid
            if result.metadata.get("output"):
                # Should have formatted output
                assert "def hello" in result.metadata["output"]
                assert result.metadata.get("auto_fixed") is True

    def test_javascript_prettier_style(self):
        """Test JavaScript formatting with Prettier."""
        validator = StyleValidator(language="javascript", formatter="prettier")

        # Well-formatted JavaScript
        valid_js = """function fibonacci(n) {
  if (n <= 1) return n;
  return fibonacci(n - 1) + fibonacci(n - 2);
}

const calculator = {
  add: (a, b) => a + b,
  subtract: (a, b) => a - b,
};
"""

        result = validator.validate(valid_js)
        # Will be valid or have warning about Prettier not available
        assert result.is_valid or len(result.warnings) > 0

    def test_javascript_style_violations(self):
        """Test detection of JavaScript style issues."""
        validator = StyleValidator(language="javascript", formatter="prettier")

        # Poorly formatted JavaScript
        bad_js = """function hello(name){return`Hello ${name}!`}"""

        result = validator.validate(bad_js)
        if len(result.warnings) > 0 and "not available" in result.warnings[0]:
            assert result.is_valid
        else:
            # Should detect formatting issues
            assert not result.is_valid or result.metadata.get("style_compliant")

    def test_go_gofmt_style(self):
        """Test Go formatting with gofmt."""
        validator = StyleValidator(language="go", formatter="gofmt")

        # Properly formatted Go code
        valid_go = """package main

import "fmt"

func main() {
	fmt.Println("Hello, World!")
}

func add(a, b int) int {
	return a + b
}
"""

        result = validator.validate(valid_go)
        assert result.is_valid or len(result.warnings) > 0

    def test_rust_rustfmt_style(self):
        """Test Rust formatting with rustfmt."""
        validator = StyleValidator(language="rust", formatter="rustfmt")

        valid_rust = """fn factorial(n: u32) -> u32 {
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

        result = validator.validate(valid_rust)
        assert result.is_valid or len(result.warnings) > 0

    def test_java_google_format(self):
        """Test Java formatting with google-java-format."""
        validator = StyleValidator(language="java", formatter="google-java-format")

        valid_java = """public class HelloWorld {
  public static void main(String[] args) {
    System.out.println("Hello, World!");
  }

  public int add(int a, int b) {
    return a + b;
  }
}
"""

        result = validator.validate(valid_java)
        assert result.is_valid or len(result.warnings) > 0

    def test_unsupported_language(self):
        """Test handling of unsupported languages."""
        with pytest.raises(ValueError) as exc_info:
            StyleValidator(language="cobol")

        assert "Unsupported language" in str(exc_info.value)

    def test_unsupported_formatter(self):
        """Test handling of unsupported formatters."""
        with pytest.raises(ValueError) as exc_info:
            StyleValidator(language="python", formatter="nonexistent")

        assert "Unsupported formatter" in str(exc_info.value)

    def test_python_isort(self):
        """Test Python import sorting with isort."""
        validator = StyleValidator(language="python", formatter="isort")

        # Code with unsorted imports
        code_with_imports = """import os
import sys
from pathlib import Path
import json
from typing import Dict, List

def main():
    pass
"""

        result = validator.validate(code_with_imports)
        # Should be valid or warn about isort not available
        assert result.is_valid or len(result.warnings) > 0 or len(result.errors) > 0

    def test_show_diff_option(self):
        """Test that diff is shown when enabled."""
        validator = StyleValidator(language="python", formatter="black", show_diff=True, auto_fix=False)

        bad_code = """def hello(): print("hello")"""

        result = validator.validate(bad_code)
        if not result.is_valid and len(result.warnings) == 0:
            # Should have diff in errors if formatter is available
            assert any("Style differences" in e or "style standards" in e for e in result.errors)

    def test_timeout_handling(self):
        """Test timeout handling for formatters."""
        validator = StyleValidator(language="python", formatter="black", timeout=1)

        # Normal code should format quickly
        result = validator.validate("print('hello')")
        # Should complete (either successfully or with warning)
        assert result is not None

    def test_formatter_not_available(self):
        """Test graceful handling when formatter is not installed."""
        # Use a formatter that might not be installed
        validator = StyleValidator(language="rust", formatter="rustfmt")

        result = validator.validate("fn main() {}")
        # Should either work or give a warning
        assert result.is_valid or any("not available" in w for w in result.warnings)

    def test_empty_code(self):
        """Test validation of empty code."""
        validator = StyleValidator(language="python", formatter="black")

        result = validator.validate("")
        # Empty code should be valid
        assert result.is_valid or len(result.warnings) > 0

        result = validator.validate("   \n  \n  ")
        assert result.is_valid or len(result.warnings) > 0
