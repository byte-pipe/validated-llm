#!/usr/bin/env python3
"""
Demo script for Code Import/Export formats.

This demo shows how to:
1. Import code from various sources (Jupyter, Markdown, Docstrings)
2. Export code to different formats (Tests, Documentation, Snippets)
3. Convert between formats
"""

import json
import tempfile
from pathlib import Path

from validated_llm.code_formats import CodeExporter, CodeFormatter, CodeImporter


def demo_markdown_import_export():
    """Demo importing from and exporting to Markdown."""
    print("\n" + "=" * 60)
    print("Demo 1: Markdown Import/Export")
    print("=" * 60)

    # Sample markdown with code blocks
    markdown_content = """
# Data Processing Functions

Here's a function to calculate statistics:

```python
def calculate_stats(data):
    '''Calculate mean and standard deviation.'''
    mean = sum(data) / len(data)
    variance = sum((x - mean) ** 2 for x in data) / len(data)
    std_dev = variance ** 0.5
    return {'mean': mean, 'std_dev': std_dev}
```

And here's how to use it:

```python
data = [1, 2, 3, 4, 5]
stats = calculate_stats(data)
print(f"Mean: {stats['mean']}, Std Dev: {stats['std_dev']}")
```
"""

    print("\nOriginal Markdown:")
    print(markdown_content[:200] + "...")

    # Import code blocks
    blocks = CodeImporter.from_markdown(markdown_content)
    print(f"\nFound {len(blocks)} code blocks")

    for i, block in enumerate(blocks, 1):
        print(f"\nBlock {i} ({block['language']}):")
        print(block["code"][:100] + "..." if len(block["code"]) > 100 else block["code"])

    # Export first block back to markdown with a title
    if blocks:
        exported = CodeFormatter.to_markdown(blocks[0]["code"], language="python", title="Statistical Functions")
        print("\nExported to Markdown:")
        print(exported)


def demo_jupyter_format():
    """Demo Jupyter notebook format conversion."""
    print("\n" + "=" * 60)
    print("Demo 2: Jupyter Notebook Format")
    print("=" * 60)

    # Create cells
    code_cell = CodeFormatter.to_jupyter_cell(
        """import numpy as np
import matplotlib.pyplot as plt

# Generate data
x = np.linspace(0, 10, 100)
y = np.sin(x)

# Plot
plt.plot(x, y)
plt.title('Sine Wave')
plt.show()""",
        cell_type="code",
    )

    markdown_cell = CodeFormatter.to_jupyter_cell(
        """# Data Visualization Example

This notebook demonstrates basic plotting with matplotlib.""",
        cell_type="markdown",
    )

    # Create a simple notebook structure
    notebook = {"cells": [markdown_cell, code_cell], "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}}, "nbformat": 4, "nbformat_minor": 4}

    print("\nCreated Jupyter notebook structure:")
    print(json.dumps(notebook, indent=2)[:300] + "...")

    # Save and re-import
    with tempfile.NamedTemporaryFile(suffix=".ipynb", mode="w", delete=False) as f:
        json.dump(notebook, f)
        temp_path = f.name

    # Import from saved notebook
    imported_cells = CodeImporter.from_jupyter(temp_path)
    print(f"\nImported {len(imported_cells)} code cells from notebook")

    # Clean up
    Path(temp_path).unlink()


def demo_test_generation():
    """Demo generating test code from functions."""
    print("\n" + "=" * 60)
    print("Demo 3: Test Code Generation")
    print("=" * 60)

    # Sample function
    function_code = """def fibonacci(n):
    '''Calculate the nth Fibonacci number.'''
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)"""

    # Test cases
    test_cases = [{"input": "0", "expected": "0"}, {"input": "1", "expected": "1"}, {"input": "5", "expected": "5"}, {"input": "10", "expected": "55"}]

    print("\nOriginal function:")
    print(function_code)

    # Generate Python tests
    python_tests = CodeExporter.to_test_format(function_code, test_cases, "python")
    print("\nGenerated Python tests:")
    print(python_tests)

    # JavaScript version
    js_function = """function fibonacci(n) {
    if (n <= 1) return n;
    return fibonacci(n-1) + fibonacci(n-2);
}"""

    js_tests = CodeExporter.to_test_format(js_function, test_cases, "javascript")
    print("\n\nGenerated JavaScript tests:")
    print(js_tests)


def demo_snippet_format():
    """Demo code snippet format with metadata."""
    print("\n" + "=" * 60)
    print("Demo 4: Code Snippet Format")
    print("=" * 60)

    # Create a snippet with full metadata
    code = """class BinarySearchTree:
    def __init__(self):
        self.root = None

    def insert(self, value):
        if not self.root:
            self.root = TreeNode(value)
        else:
            self._insert_recursive(self.root, value)

    def _insert_recursive(self, node, value):
        if value < node.value:
            if node.left is None:
                node.left = TreeNode(value)
            else:
                self._insert_recursive(node.left, value)
        else:
            if node.right is None:
                node.right = TreeNode(value)
            else:
                self._insert_recursive(node.right, value)"""

    snippet = CodeFormatter.to_snippet_format(
        code,
        language="python",
        title="Binary Search Tree Implementation",
        description="A simple BST with insert functionality",
        tags=["data-structures", "tree", "algorithm"],
        metadata={"author": "Demo User", "complexity": "O(log n) average, O(n) worst case", "requires": ["TreeNode class definition"]},
    )

    print("\nCode Snippet with Metadata:")
    print(json.dumps(snippet, indent=2))


def demo_gist_format():
    """Demo GitHub Gist format."""
    print("\n" + "=" * 60)
    print("Demo 5: GitHub Gist Format")
    print("=" * 60)

    # Multiple files for a gist
    files = {
        "utils.py": """def format_number(n):
    '''Format number with commas.'''
    return f"{n:,}"

def parse_date(date_str):
    '''Parse date string to datetime.'''
    from datetime import datetime
    return datetime.strptime(date_str, '%Y-%m-%d')""",
        "main.py": """from utils import format_number, parse_date

# Example usage
print(format_number(1000000))
print(parse_date('2024-01-15'))""",
        "README.md": """# Utility Functions

Simple Python utilities for formatting and parsing.""",
    }

    gist = CodeFormatter.to_gist_format(files, description="Python utility functions example", public=True)

    print("\nGist format structure:")
    print(json.dumps(gist, indent=2)[:500] + "...")


def demo_docstring_extraction():
    """Demo extracting code examples from docstrings."""
    print("\n" + "=" * 60)
    print("Demo 6: Docstring Code Extraction")
    print("=" * 60)

    # Python code with doctest examples
    python_code = '''
def quadratic_solver(a, b, c):
    """Solve quadratic equation ax² + bx + c = 0.

    Args:
        a: Coefficient of x²
        b: Coefficient of x
        c: Constant term

    Returns:
        Tuple of solutions (x1, x2)

    Examples:
        >>> quadratic_solver(1, -5, 6)
        (3.0, 2.0)

        >>> quadratic_solver(1, 0, -4)
        (2.0, -2.0)

        >>> quadratic_solver(1, 2, 1)
        (-1.0, -1.0)
    """
    discriminant = b**2 - 4*a*c
    if discriminant < 0:
        return None

    x1 = (-b + discriminant**0.5) / (2*a)
    x2 = (-b - discriminant**0.5) / (2*a)
    return (x1, x2)

class MathUtils:
    """Mathematical utility functions.

    Example:
        >>> utils = MathUtils()
        >>> utils.factorial(5)
        120
    """

    def factorial(self, n):
        """Calculate factorial.

        Example:
            >>> MathUtils().factorial(4)
            24
        """
        if n <= 1:
            return 1
        return n * self.factorial(n - 1)
'''

    print("Python code with doctest examples:")
    print(python_code[:200] + "...")

    # Extract examples
    examples = CodeImporter.from_docstrings(python_code)
    print(f"\nExtracted {len(examples)} code examples:")

    for ex in examples:
        print(f"\nFrom {ex['context']}:")
        print(f"Code: {ex['code']}")


def demo_documentation_export():
    """Demo exporting code structure as documentation."""
    print("\n" + "=" * 60)
    print("Demo 7: Documentation Export")
    print("=" * 60)

    # Sample module code
    code = '''
"""
A module for data validation utilities.
"""

import re
from typing import List, Optional

# Constants
EMAIL_REGEX = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

def validate_email(email: str) -> bool:
    """Validate email address format.

    Args:
        email: Email address to validate

    Returns:
        True if valid, False otherwise
    """
    return bool(re.match(EMAIL_REGEX, email))

def validate_phone(phone: str) -> bool:
    """Validate phone number format.

    Supports formats: (123) 456-7890, 123-456-7890, 1234567890
    """
    # Remove non-digits
    digits = re.sub(r'\\D', '', phone)
    return len(digits) == 10

class DataValidator:
    """A comprehensive data validation class."""

    def __init__(self, strict: bool = False):
        """Initialize validator.

        Args:
            strict: Whether to use strict validation rules
        """
        self.strict = strict
        self.errors: List[str] = []

    def validate_dataset(self, data: List[dict]) -> bool:
        """Validate a dataset.

        Returns:
            True if all data is valid
        """
        self.errors.clear()
        for i, record in enumerate(data):
            if not self._validate_record(record):
                self.errors.append(f"Invalid record at index {i}")
        return len(self.errors) == 0

    def _validate_record(self, record: dict) -> bool:
        """Validate a single record."""
        # Implementation here
        return True

# Example usage
if __name__ == "__main__":
    print(validate_email("test@example.com"))
    validator = DataValidator(strict=True)
'''

    # Export documentation
    doc = CodeExporter.to_documentation_format(code, "python", include_comments=True)

    print("\nExtracted Documentation Structure:")
    print(f"Language: {doc['language']}")
    print(f"\nImports ({len(doc['imports'])}):")
    for imp in doc["imports"][:5]:
        print(f"  - {imp}")

    print(f"\nFunctions ({len(doc['functions'])}):")
    for func in doc["functions"]:
        print(f"  - {func['name']}({', '.join(func['args'])})")
        if func["docstring"]:
            docstring_first_line = func["docstring"].split("\n")[0]
            print(f"    {docstring_first_line}")

    print(f"\nClasses ({len(doc['classes'])}):")
    for cls in doc["classes"]:
        print(f"  - {cls['name']}")
        print(f"    Methods: {', '.join(cls['methods'])}")

    print(f"\nComments ({len(doc['comments'])}):")
    for comment in doc["comments"][:3]:
        print(f"  Line {comment['line_number']}: {comment['text']}")


def main():
    """Run all demos."""
    print("Code Import/Export Formats Demo")
    print("This demo shows various code format conversions")

    demos = [demo_markdown_import_export, demo_jupyter_format, demo_test_generation, demo_snippet_format, demo_gist_format, demo_docstring_extraction, demo_documentation_export]

    for demo in demos:
        demo()

    print("\n" + "=" * 60)
    print("All demos completed!")
    print("\nCode formats enable:")
    print("- Importing code from notebooks, markdown, and docstrings")
    print("- Exporting to test formats, documentation, and snippets")
    print("- Converting between different code representations")


if __name__ == "__main__":
    main()
