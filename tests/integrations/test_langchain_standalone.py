#!/usr/bin/env python3
"""
Standalone test for Langchain integration logic.
This test directly includes the converter logic to avoid import issues.
"""

import re
from typing import Any, Dict, List


def extract_variables(template: str) -> List[str]:
    """Extract variable names from template string."""
    pattern = r"\{(\w+)\}"
    return list(set(re.findall(pattern, template)))


def analyze_prompt(template: str) -> Dict[str, Any]:
    """Analyze a prompt template to infer its purpose and suggest validators."""
    analysis = {"template": template, "variables": extract_variables(template), "output_type": "text", "suggested_validators": []}

    # Analyze template content for validator suggestions
    template_lower = template.lower()

    if any(word in template_lower for word in ["json", "object", "structure"]):
        analysis["suggested_validators"].append("JSONValidator")
        analysis["output_type"] = "json"
    elif any(word in template_lower for word in ["list", "items", "bullet"]):
        analysis["suggested_validators"].append("ListValidator")
        analysis["output_type"] = "list"
    elif any(word in template_lower for word in ["markdown", "blog", "article"]):
        analysis["suggested_validators"].append("MarkdownValidator")
        analysis["output_type"] = "markdown"
    elif any(word in template_lower for word in ["email", "message"]):
        analysis["suggested_validators"].append("EmailValidator")
        analysis["output_type"] = "email"
    elif any(word in template_lower for word in ["code", "function", "class"]):
        analysis["suggested_validators"].append("SyntaxValidator")
        analysis["output_type"] = "code"
    else:
        analysis["suggested_validators"].append("RegexValidator")
        analysis["output_type"] = "text"

    return analysis


def test_extract_variables():
    """Test variable extraction."""
    # Single variable
    assert extract_variables("Hello {name}") == ["name"]

    # Multiple variables
    vars = extract_variables("Generate a {format} report about {topic} for {audience}")
    assert set(vars) == {"format", "topic", "audience"}

    # Duplicate variables
    assert extract_variables("Compare {item} with another {item}") == ["item"]

    # No variables
    assert extract_variables("Hello world") == []

    print("✓ Variable extraction tests passed")


def test_analyze_prompt():
    """Test prompt analysis."""
    # JSON detection
    result = analyze_prompt("Generate a JSON object with name and age for {person}")
    assert result["output_type"] == "json"
    assert "JSONValidator" in result["suggested_validators"]
    assert result["variables"] == ["person"]

    # Markdown detection
    result = analyze_prompt("Write a blog post in markdown about {topic}")
    assert result["output_type"] == "markdown"
    assert "MarkdownValidator" in result["suggested_validators"]

    # List detection
    result = analyze_prompt("List 5 benefits of {product}")
    assert result["output_type"] == "list"
    assert "ListValidator" in result["suggested_validators"]

    # Email detection
    result = analyze_prompt("Write an email message to {recipient}")
    assert result["output_type"] == "email"
    assert "EmailValidator" in result["suggested_validators"]

    # Code detection
    result = analyze_prompt("Write a Python function to {task}")
    assert result["output_type"] == "code"
    assert "SyntaxValidator" in result["suggested_validators"]

    # Default text
    result = analyze_prompt("Tell me about {topic}")
    assert result["output_type"] == "text"
    assert "RegexValidator" in result["suggested_validators"]

    print("✓ Prompt analysis tests passed")


def test_list_validator():
    """Test list validation logic."""

    def validate_list(output: str) -> tuple[bool, List[str]]:
        """Simple list validator."""
        lines = output.strip().split("\n")

        # Check if it looks like a list
        is_list = all(line.strip().startswith(("-", "*", "•", "1", "2", "3", "4", "5", "6", "7", "8", "9")) for line in lines if line.strip())

        if is_list and len(lines) > 0:
            items = [line.strip().lstrip("-*•0123456789. ") for line in lines]
            return True, items
        else:
            return False, []

    # Valid lists
    is_valid, items = validate_list("- Item 1\n- Item 2\n- Item 3")
    assert is_valid
    assert items == ["Item 1", "Item 2", "Item 3"]

    is_valid, items = validate_list("1. First\n2. Second\n3. Third")
    assert is_valid
    assert items == ["First", "Second", "Third"]

    is_valid, items = validate_list("* Apple\n* Banana\n* Orange")
    assert is_valid
    assert items == ["Apple", "Banana", "Orange"]

    # Invalid output
    is_valid, _ = validate_list("Not a list format")
    assert not is_valid

    print("✓ List validator tests passed")


def test_csv_validator():
    """Test CSV validation logic."""

    def validate_csv(output: str) -> tuple[bool, List[str]]:
        """Simple CSV validator."""
        items = [item.strip() for item in output.split(",")]

        if len(items) > 0 and all(items):
            return True, items
        else:
            return False, []

    # Valid CSV
    is_valid, items = validate_csv("apple, banana, orange")
    assert is_valid
    assert items == ["apple", "banana", "orange"]

    # Single item
    is_valid, items = validate_csv("single")
    assert is_valid
    assert items == ["single"]

    # Empty CSV
    is_valid, _ = validate_csv("")
    assert not is_valid

    # CSV with empty items
    is_valid, _ = validate_csv("apple, , orange")
    assert not is_valid

    print("✓ CSV validator tests passed")


def main():
    """Run all tests."""
    print("Running Langchain Integration Tests")
    print("=" * 40)

    test_extract_variables()
    test_analyze_prompt()
    test_list_validator()
    test_csv_validator()

    print("\n✅ All tests passed!")


if __name__ == "__main__":
    main()
