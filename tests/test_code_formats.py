"""
Tests for code import/export formats.
"""

import json
import tempfile
from pathlib import Path

import pytest

from validated_llm.code_formats import CodeExporter, CodeFormatter, CodeImporter


class TestCodeFormatter:
    """Test the CodeFormatter class."""

    def test_extract_markdown_code_blocks(self):
        """Test extracting code blocks from markdown."""
        markdown = """
# Example Code

Here's a Python function:

```python
def hello():
    print("Hello, World!")
```

And here's some JavaScript:

```javascript
const greet = (name) => {
    console.log(`Hello, ${name}!`);
};
```
"""

        blocks = CodeFormatter.extract_code_blocks(markdown)

        assert len(blocks) == 2
        assert blocks[0]["language"] == "python"
        assert "def hello()" in blocks[0]["code"]
        assert blocks[1]["language"] == "javascript"
        assert "const greet" in blocks[1]["code"]

    def test_extract_code_blocks_with_language_filter(self):
        """Test extracting only specific language blocks."""
        markdown = """
```python
def foo():
    pass
```

```javascript
function bar() {}
```
"""

        python_blocks = CodeFormatter.extract_code_blocks(markdown, language="python")

        assert len(python_blocks) == 1
        assert python_blocks[0]["language"] == "python"
        assert "def foo()" in python_blocks[0]["code"]

    def test_extract_indented_code_blocks(self):
        """Test extracting indented code blocks."""
        text = """
Here's an example:

    def calculate(x, y):
        return x + y

    result = calculate(10, 20)

That's the code.
"""

        blocks = CodeFormatter.extract_code_blocks(text)

        # The function might be split into multiple blocks
        all_code = " ".join(block["code"] for block in blocks)
        assert "def calculate" in all_code
        assert "result = calculate" in all_code

    def test_to_markdown(self):
        """Test converting code to markdown format."""
        code = "def hello():\n    print('Hello')"

        markdown = CodeFormatter.to_markdown(code, language="python", title="Greeting Function")

        assert "## Greeting Function" in markdown
        assert "```python" in markdown
        assert code in markdown
        assert "```" in markdown

    def test_to_jupyter_cell(self):
        """Test converting code to Jupyter cell format."""
        code = "print('Hello, Jupyter!')"

        cell = CodeFormatter.to_jupyter_cell(code, cell_type="code")

        assert cell["cell_type"] == "code"
        assert cell["source"] == ["print('Hello, Jupyter!')"]
        assert "outputs" in cell
        assert cell["execution_count"] is None

    def test_to_jupyter_markdown_cell(self):
        """Test converting markdown to Jupyter cell."""
        markdown = "# Title\n\nThis is markdown content."

        cell = CodeFormatter.to_jupyter_cell(markdown, cell_type="markdown")

        assert cell["cell_type"] == "markdown"
        assert cell["source"] == ["# Title", "", "This is markdown content."]

    def test_to_gist_format(self):
        """Test converting to GitHub Gist format."""
        files = {"main.py": 'def main():\n    print("Hello")', "utils.py": "def helper():\n    return 42"}

        gist = CodeFormatter.to_gist_format(files, description="Example gist", public=True)

        assert gist["description"] == "Example gist"
        assert gist["public"] is True
        assert "main.py" in gist["files"]
        assert gist["files"]["main.py"]["content"] == files["main.py"]

    def test_to_snippet_format(self):
        """Test converting to snippet format."""
        code = "def factorial(n):\n    return 1 if n <= 1 else n * factorial(n-1)"

        snippet = CodeFormatter.to_snippet_format(code, language="python", title="Factorial Function", description="Recursive factorial implementation", tags=["recursion", "math"], metadata={"author": "test"})

        assert snippet["title"] == "Factorial Function"
        assert snippet["language"] == "python"
        assert snippet["tags"] == ["recursion", "math"]
        assert snippet["metrics"]["lines"] == 2
        assert snippet["metadata"]["author"] == "test"


class TestCodeImporter:
    """Test the CodeImporter class."""

    def test_from_jupyter(self, tmp_path):
        """Test importing from Jupyter notebook."""
        # Create a simple notebook
        notebook = {
            "cells": [
                {"cell_type": "code", "execution_count": 1, "metadata": {}, "outputs": [], "source": ["print('Hello')\n", "x = 42"]},
                {"cell_type": "markdown", "metadata": {}, "source": ["# Title"]},
                {"cell_type": "code", "execution_count": 2, "metadata": {"tags": ["test"]}, "outputs": [], "source": ["def foo():\n", "    return 'bar'"]},
            ],
            "metadata": {"kernelspec": {"language": "python"}},
        }

        notebook_path = tmp_path / "test.ipynb"
        with open(notebook_path, "w") as f:
            json.dump(notebook, f)

        cells = CodeImporter.from_jupyter(notebook_path)

        assert len(cells) == 2  # Only code cells
        assert cells[0]["code"] == "print('Hello')\nx = 42"
        assert cells[0]["language"] == "python"
        assert cells[1]["code"] == "def foo():\n    return 'bar'"
        assert cells[1]["metadata"]["tags"] == ["test"]

    def test_from_markdown(self):
        """Test importing from markdown."""
        markdown = """
# Code Examples

```python
def add(a, b):
    return a + b
```

Some text here.

```javascript
const multiply = (x, y) => x * y;
```
"""

        blocks = CodeImporter.from_markdown(markdown)

        assert len(blocks) == 2
        assert blocks[0]["language"] == "python"
        assert "def add" in blocks[0]["code"]
        assert blocks[1]["language"] == "javascript"

    def test_from_docstrings(self):
        """Test extracting examples from docstrings."""
        python_code = '''
def add(a, b):
    """Add two numbers.

    Examples:
        >>> add(2, 3)
        5
        >>> add(-1, 1)
        0
        >>> result = add(10, 20)
        >>> print(result)
        30
    """
    return a + b

class Calculator:
    """A simple calculator.

    Example:
        >>> calc = Calculator()
        >>> calc.compute(5)
        5
    """
    def compute(self, x):
        return x
'''

        examples = CodeImporter.from_docstrings(python_code)

        assert len(examples) >= 3
        assert any("add(2, 3)" in ex["code"] for ex in examples)
        assert all(ex["type"] == "doctest" for ex in examples)
        assert any("FunctionDef: add" in ex["context"] for ex in examples)


class TestCodeExporter:
    """Test the CodeExporter class."""

    def test_to_test_format_python(self):
        """Test exporting Python code with tests."""
        function_code = """def add(a, b):
    return a + b"""

        test_cases = [{"input": "2, 3", "expected": "5"}, {"input": "-1, 1", "expected": "0"}, {"input": "0, 0", "expected": "0"}]

        test_code = CodeExporter.to_test_format(function_code, test_cases, "python")

        assert "def add(a, b):" in test_code
        assert "def test_function():" in test_code
        assert "assert add(2, 3) == 5" in test_code
        assert "assert add(-1, 1) == 0" in test_code
        assert "if __name__ == '__main__':" in test_code

    def test_to_test_format_javascript(self):
        """Test exporting JavaScript code with tests."""
        function_code = """const multiply = (x, y) => x * y;"""

        test_cases = [{"input": "2, 3", "expected": "6"}, {"input": "5, 0", "expected": "0"}]

        test_code = CodeExporter.to_test_format(function_code, test_cases, "javascript")

        assert "const multiply" in test_code
        assert "function testMultiply()" in test_code
        assert "console.assert(multiply(2, 3) === 6" in test_code
        assert "testMultiply();" in test_code

    def test_to_documentation_format(self):
        """Test exporting code with documentation."""
        code = '''
import math
from typing import List

def calculate_mean(numbers: List[float]) -> float:
    """Calculate the arithmetic mean of a list of numbers.

    Args:
        numbers: List of numbers

    Returns:
        The mean value
    """
    if not numbers:
        return 0.0
    return sum(numbers) / len(numbers)

class Statistics:
    """A class for statistical calculations."""

    def __init__(self):
        self.data = []

    def add_data(self, value: float):
        """Add a data point."""
        self.data.append(value)

# This is a comment
result = calculate_mean([1, 2, 3])
'''

        doc = CodeExporter.to_documentation_format(code, "python", include_comments=True)

        assert doc["language"] == "python"
        # Find the calculate_mean function (skip class methods)
        functions = [f for f in doc["functions"] if f["name"] == "calculate_mean"]
        assert len(functions) == 1
        assert functions[0]["name"] == "calculate_mean"
        assert "Calculate the arithmetic mean" in functions[0]["docstring"]
        assert functions[0]["args"] == ["numbers"]

        assert len(doc["classes"]) == 1
        assert doc["classes"][0]["name"] == "Statistics"
        assert "add_data" in doc["classes"][0]["methods"]

        assert "math" in doc["imports"]
        assert any("typing" in imp for imp in doc["imports"])

        assert len(doc["comments"]) >= 1
        assert any("This is a comment" in c["text"] for c in doc["comments"])

    def test_to_documentation_format_no_comments(self):
        """Test documentation export without comments."""
        code = """
def foo():
    # Internal comment
    pass
"""

        doc = CodeExporter.to_documentation_format(code, "python", include_comments=False)

        assert len(doc["comments"]) == 0
