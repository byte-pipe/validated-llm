"""Tests for enhanced error message formatting."""

import pytest

from validated_llm.error_formatting import ContextExtractor, EnhancedValidationError, ErrorCategory, ErrorFormatter, ErrorLocation, ErrorSeverity, create_enhanced_error


class TestErrorLocation:
    """Test ErrorLocation functionality."""

    def test_str_with_line_and_column(self):
        location = ErrorLocation(line=5, column=10)
        assert str(location) == " at line 5, column 10"

    def test_str_with_path(self):
        location = ErrorLocation(path="$.users[0].email")
        assert str(location) == " at path '$.users[0].email'"

    def test_str_with_all_fields(self):
        location = ErrorLocation(line=5, column=10, position=42, path="$.test")
        assert str(location) == " at line 5, column 10, path '$.test'"

    def test_str_empty(self):
        location = ErrorLocation()
        assert str(location) == ""


class TestEnhancedValidationError:
    """Test EnhancedValidationError functionality."""

    def test_basic_creation(self):
        error = EnhancedValidationError(category=ErrorCategory.SYNTAX, message="Test error")
        assert error.category == ErrorCategory.SYNTAX
        assert error.message == "Test error"
        assert error.severity == ErrorSeverity.ERROR
        assert error.suggestions == []
        assert error.examples == []

    def test_with_all_fields(self):
        location = ErrorLocation(line=5, column=10)
        error = EnhancedValidationError(
            category=ErrorCategory.TYPE_MISMATCH,
            message="Type error",
            severity=ErrorSeverity.WARNING,
            location=location,
            context="some context",
            expected="string",
            actual="number",
            suggestions=["Fix the type"],
            examples=["'hello'"],
            documentation_url="https://example.com",
        )

        assert error.category == ErrorCategory.TYPE_MISMATCH
        assert error.severity == ErrorSeverity.WARNING
        assert error.location == location
        assert error.expected == "string"
        assert error.actual == "number"
        assert error.suggestions == ["Fix the type"]
        assert error.examples == ["'hello'"]


class TestErrorFormatter:
    """Test ErrorFormatter functionality."""

    def test_format_basic_error(self):
        error = EnhancedValidationError(category=ErrorCategory.SYNTAX, message="Test error")

        formatted = ErrorFormatter.format_error(error, include_context=False)
        assert "❌ Test error" in formatted
        assert "Context:" not in formatted

    def test_format_error_with_location(self):
        location = ErrorLocation(line=5, column=10)
        error = EnhancedValidationError(category=ErrorCategory.SYNTAX, message="Test error", location=location)

        formatted = ErrorFormatter.format_error(error, include_context=False)
        assert "❌ Test error at line 5, column 10" in formatted

    def test_format_error_with_context(self):
        error = EnhancedValidationError(category=ErrorCategory.SYNTAX, message="Test error", context="line 1\nline 2\nline 3")

        formatted = ErrorFormatter.format_error(error, include_context=True)
        assert "📍 Context:" in formatted
        assert "line 1" in formatted
        assert "line 2" in formatted
        assert "line 3" in formatted

    def test_format_error_with_expected_actual(self):
        error = EnhancedValidationError(category=ErrorCategory.TYPE_MISMATCH, message="Type error", expected="string", actual="number")

        formatted = ErrorFormatter.format_error(error)
        assert "✅ Expected: string" in formatted
        assert "🔍 Actual:   number" in formatted

    def test_format_error_with_suggestions(self):
        error = EnhancedValidationError(category=ErrorCategory.SYNTAX, message="Test error", suggestions=["Fix this", "Try that"])

        formatted = ErrorFormatter.format_error(error, include_context=True)
        assert "💡 Suggestions:" in formatted
        assert "1. Fix this" in formatted
        assert "2. Try that" in formatted

    def test_format_error_with_examples(self):
        error = EnhancedValidationError(category=ErrorCategory.FORMAT_ERROR, message="Format error", examples=["example1", "example2", "example3", "example4"])

        formatted = ErrorFormatter.format_error(error, include_context=True)
        assert "📝 Valid Examples:" in formatted
        assert "example1" in formatted
        assert "example2" in formatted
        assert "example3" in formatted
        assert "example4" not in formatted  # Should limit to 3

    def test_format_error_with_documentation(self):
        error = EnhancedValidationError(category=ErrorCategory.SYNTAX, message="Test error", documentation_url="https://example.com/docs")

        formatted = ErrorFormatter.format_error(error, include_context=True)
        assert "📚 Documentation: https://example.com/docs" in formatted

    def test_format_error_severity_symbols(self):
        error_error = EnhancedValidationError(category=ErrorCategory.SYNTAX, message="Error message", severity=ErrorSeverity.ERROR)

        warning_error = EnhancedValidationError(category=ErrorCategory.SYNTAX, message="Warning message", severity=ErrorSeverity.WARNING)

        info_error = EnhancedValidationError(category=ErrorCategory.SYNTAX, message="Info message", severity=ErrorSeverity.INFO)

        assert "❌" in ErrorFormatter.format_error(error_error, include_context=False)
        assert "⚠️" in ErrorFormatter.format_error(warning_error, include_context=False)
        assert "ℹ️" in ErrorFormatter.format_error(info_error, include_context=False)

    def test_format_multiple_errors_single(self):
        error = EnhancedValidationError(category=ErrorCategory.SYNTAX, message="Single error")

        formatted = ErrorFormatter.format_multiple_errors([error])
        assert "❌ Single error" in formatted
        assert "Found 1 validation" not in formatted

    def test_format_multiple_errors_multiple(self):
        errors = [EnhancedValidationError(category=ErrorCategory.SYNTAX, message="Error 1"), EnhancedValidationError(category=ErrorCategory.TYPE_MISMATCH, message="Error 2")]

        formatted = ErrorFormatter.format_multiple_errors(errors)
        assert "Found 2 validation errors:" in formatted
        assert "Error 1:" in formatted
        assert "Error 2:" in formatted

    def test_format_multiple_errors_with_limit(self):
        errors = [EnhancedValidationError(category=ErrorCategory.SYNTAX, message=f"Error {i}") for i in range(1, 8)]  # 7 errors

        formatted = ErrorFormatter.format_multiple_errors(errors, max_errors=3)
        assert "Found 7 validation errors:" in formatted
        assert "Error 1:" in formatted
        assert "Error 2:" in formatted
        assert "Error 3:" in formatted
        assert "... and 4 more errors" in formatted
        assert "Error categories:" in formatted

    def test_wrap_line_simple(self):
        line = "This is a short line"
        wrapped = ErrorFormatter._wrap_line(line, 50)
        assert wrapped == [line]

    def test_wrap_line_long(self):
        line = "This is a very long line that definitely exceeds the maximum width and should be wrapped"
        wrapped = ErrorFormatter._wrap_line(line, 30)
        assert len(wrapped) > 1
        assert all(len(l) <= 32 for l in wrapped)  # Allow for indentation

    def test_wrap_line_with_indentation(self):
        line = "    This is an indented line that is too long and needs wrapping"
        wrapped = ErrorFormatter._wrap_line(line, 30)
        assert len(wrapped) > 1
        assert all(l.startswith("    ") for l in wrapped)  # Preserve indentation


class TestContextExtractor:
    """Test ContextExtractor functionality."""

    def test_extract_text_context_simple(self):
        text = "The quick brown fox jumps over the lazy dog"
        position = 20  # Around "jumps"

        context = ContextExtractor.extract_text_context(text, position, window=10)
        assert "fox jumps over" in context
        assert "^" in context

    def test_extract_text_context_multiline(self):
        text = "Line 1\nLine 2 with error\nLine 3"
        position = 15  # In "Line 2"

        context = ContextExtractor.extract_text_context(text, position, window=20)
        assert "Line 2" in context
        assert "^" in context

    def test_extract_text_context_edge_cases(self):
        # Empty text
        assert ContextExtractor.extract_text_context("", 0) == ""

        # Negative position
        assert ContextExtractor.extract_text_context("test", -1) == ""

        # Position beyond text
        context = ContextExtractor.extract_text_context("test", 10, window=5)
        assert context == ""  # Returns empty string for position beyond text

    def test_extract_line_context(self):
        text = "Line 1\nLine 2\nLine 3\nLine 4\nLine 5"

        context = ContextExtractor.extract_line_context(text, 3, context_lines=1)
        assert "  2: Line 2" in context
        assert ">>>   3: Line 3" in context  # Note the extra spaces
        assert "  4: Line 4" in context
        assert "Line 1" not in context
        assert "Line 5" not in context

    def test_extract_line_context_edge_cases(self):
        text = "Line 1\nLine 2\nLine 3"

        # Line number too high
        assert ContextExtractor.extract_line_context(text, 10) == ""

        # Line number too low
        assert ContextExtractor.extract_line_context(text, 0) == ""

        # First line
        context = ContextExtractor.extract_line_context(text, 1, context_lines=1)
        assert ">>>   1: Line 1" in context  # Note the extra spaces
        assert "      2: Line 2" in context

    def test_extract_json_path_context(self):
        data = {"users": [{"name": "John", "email": "john@example.com"}, {"name": "Jane", "email": "jane@example.com"}]}

        context = ContextExtractor.extract_json_path_context(data, "$.users[0]")
        # The function navigates to $.users[0] but since we only go to parent path,
        # it will show the keys at $.users level (which is ['users'])
        assert "Available keys:" in context

    def test_extract_json_path_context_array(self):
        data = {"items": [1, 2, 3, 4, 5]}

        context = ContextExtractor.extract_json_path_context(data, "$.items")
        # The function goes to parent path which is root, showing available keys
        assert "Available keys:" in context

    def test_extract_json_path_context_invalid(self):
        data = {"test": "value"}

        context = ContextExtractor.extract_json_path_context(data, "$.invalid.path")
        assert "Unable to extract context" in context


class TestCreateEnhancedError:
    """Test create_enhanced_error convenience function."""

    def test_create_basic_error(self):
        error = create_enhanced_error(category=ErrorCategory.SYNTAX, message="Test error")

        assert isinstance(error, EnhancedValidationError)
        assert error.category == ErrorCategory.SYNTAX
        assert error.message == "Test error"
        assert error.severity == ErrorSeverity.ERROR

    def test_create_error_with_text_position(self):
        text = "Some text with error here"
        error = create_enhanced_error(category=ErrorCategory.SYNTAX, message="Test error", text=text, position=15)

        assert error.context is not None
        assert "error here" in error.context
        assert "^" in error.context

    def test_create_error_with_line_number(self):
        text = "Line 1\nLine 2\nLine 3"
        error = create_enhanced_error(category=ErrorCategory.SYNTAX, message="Test error", text=text, line=2)

        assert error.context is not None
        assert ">>>   2: Line 2" in error.context  # Note the extra spaces
        assert error.location is not None
        assert error.location.line == 2

    def test_create_error_with_all_params(self):
        error = create_enhanced_error(
            category=ErrorCategory.TYPE_MISMATCH,
            message="Type error",
            line=5,
            column=10,
            path="$.test",
            expected="string",
            actual="number",
            suggestions=["Fix it"],
            examples=["'hello'"],
            documentation_url="https://example.com",
            severity=ErrorSeverity.WARNING,
        )

        assert error.category == ErrorCategory.TYPE_MISMATCH
        assert error.severity == ErrorSeverity.WARNING
        assert error.location.line == 5
        assert error.location.column == 10
        assert error.location.path == "$.test"
        assert error.expected == "string"
        assert error.actual == "number"
        assert error.suggestions == ["Fix it"]
        assert error.examples == ["'hello'"]
        assert error.documentation_url == "https://example.com"


if __name__ == "__main__":
    pytest.main([__file__])
