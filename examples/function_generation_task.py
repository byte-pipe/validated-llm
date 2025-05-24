"""
Example: Function Generation Task

This example demonstrates using the validated-LLM framework for code generation.
It shows both the potential and limitations of applying validation patterns to coding tasks.

Key considerations for coding validation:
- Syntax validation is universal and valuable
- Logic validation requires specific test cases (less flexible)
- Style validation can be somewhat generic
- Execution validation needs sandboxing and specific inputs

This example tries to balance flexibility with usefulness.
"""

import ast
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Type

# Add the src directory to Python path so we can import validated_llm
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from validated_llm.base_validator import BaseValidator, ValidationResult
from validated_llm.tasks.base_task import BaseTask


class FunctionGenerationTask(BaseTask):
    """
    Task for generating Python functions with validation.

    This task demonstrates how validation can work for code generation:
    - Flexible enough to generate different types of functions
    - Specific enough to catch common coding errors
    - Practical for real-world use cases
    """

    @property
    def name(self) -> str:
        return "Python Function Generation"

    @property
    def description(self) -> str:
        return "Generate Python functions with syntax, style, and basic logic validation"

    @property
    def prompt_template(self) -> str:
        return """
Generate a Python function based on the following specification:

FUNCTION SPECIFICATION:
Function Name: {function_name}
Description: {description}
Parameters: {parameters}
Return Type: {return_type}
Requirements: {requirements}

CODING STANDARDS:
- Use descriptive variable names
- Include proper type hints
- Add comprehensive docstring with Args and Returns sections
- Follow PEP 8 style guidelines
- Handle edge cases appropriately
- Add input validation where appropriate

EXAMPLE FORMAT:
```python
def function_name(param1: type1, param2: type2) -> return_type:
    \"\"\"
    Brief description of what the function does.

    Args:
        param1 (type1): Description of param1
        param2 (type2): Description of param2

    Returns:
        return_type: Description of return value

    Raises:
        ExceptionType: When this exception occurs
    \"\"\"
    # Implementation here
    pass
```

ADDITIONAL CONTEXT:
{additional_context}

Generate ONLY the function code (no additional explanation):"""

    @property
    def validator_class(self) -> Type[BaseValidator]:
        return PythonFunctionValidator

    def get_prompt_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Prepare and enrich the prompt data."""
        # Convert parameters list to string if needed
        parameters = kwargs.get("parameters", [])
        if isinstance(parameters, list):
            parameters = ", ".join(parameters)

        return {
            "function_name": kwargs.get("function_name", "unnamed_function"),
            "description": kwargs.get("description", "No description provided"),
            "parameters": parameters,
            "return_type": kwargs.get("return_type", "Any"),
            "requirements": kwargs.get("requirements", "No specific requirements"),
            "additional_context": kwargs.get("additional_context", ""),
        }


class PythonFunctionValidator(BaseValidator):
    """
    Validator for Python functions that balances flexibility with usefulness.

    This validator demonstrates how coding validation can be:
    - Generic enough to apply to many functions
    - Specific enough to catch real issues
    - Configurable for different requirements
    """

    def __init__(
        self,
        required_function_name: Optional[str] = None,
        require_type_hints: bool = True,
        require_docstring: bool = True,
        min_lines: int = 3,
        max_lines: int = 100,
        test_cases: Optional[List[Dict[str, Any]]] = None,
        allow_external_imports: bool = False,
    ):
        """
        Initialize the Python function validator.

        Args:
            required_function_name: Expected function name (if specified)
            require_type_hints: Whether type hints are required
            require_docstring: Whether docstring is required
            min_lines: Minimum lines of code
            max_lines: Maximum lines of code
            test_cases: Optional test cases to validate function behavior
            allow_external_imports: Whether to allow imports beyond standard library
        """
        super().__init__(name="python_function_validator", description=f"Validates Python functions (type hints: {require_type_hints}, docstring: {require_docstring})")

        self.required_function_name = required_function_name
        self.require_type_hints = require_type_hints
        self.require_docstring = require_docstring
        self.min_lines = min_lines
        self.max_lines = max_lines
        self.test_cases = test_cases or []
        self.allow_external_imports = allow_external_imports

    def validate(self, content: str, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """Validate the generated Python function."""
        errors = []
        warnings = []
        metadata = {}

        # Clean the content (remove markdown code blocks if present)
        clean_content = self._extract_code_from_markdown(content)

        # 1. Syntax validation (universal and valuable)
        syntax_errors = self._validate_syntax(clean_content)
        errors.extend(syntax_errors)

        if syntax_errors:
            # If syntax is invalid, skip other validations
            return ValidationResult(is_valid=False, errors=errors, warnings=warnings, metadata={"syntax_valid": False})

        # Parse the AST for further analysis
        try:
            tree = ast.parse(clean_content)
            metadata["syntax_valid"] = True
        except SyntaxError as e:
            errors.append(f"Syntax error: {e}")
            return ValidationResult(is_valid=False, errors=errors, warnings=warnings, metadata=metadata)

        # 2. Structure validation
        structure_errors, structure_warnings = self._validate_structure(tree, clean_content)
        errors.extend(structure_errors)
        warnings.extend(structure_warnings)

        # 3. Style validation (somewhat generic)
        style_warnings = self._validate_style(clean_content)
        warnings.extend(style_warnings)

        # 4. Documentation validation
        doc_errors, doc_warnings = self._validate_documentation(tree, clean_content)
        errors.extend(doc_errors)
        warnings.extend(doc_warnings)

        # 5. Import validation
        import_warnings = self._validate_imports(tree)
        warnings.extend(import_warnings)

        # 6. Execution validation (if test cases provided)
        if self.test_cases:
            exec_errors, exec_warnings = self._validate_execution(clean_content)
            errors.extend(exec_errors)
            warnings.extend(exec_warnings)

        # Calculate metadata
        lines = clean_content.strip().split("\n")
        metadata.update(
            {
                "line_count": len(lines),
                "function_count": len([node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]),
                "has_docstring": self._has_docstring(tree),
                "has_type_hints": self._has_type_hints(tree),
            }
        )

        return ValidationResult(is_valid=len(errors) == 0, errors=errors, warnings=warnings, metadata=metadata)

    def _extract_code_from_markdown(self, content: str) -> str:
        """Extract Python code from markdown code blocks."""
        # Look for ```python code blocks
        python_pattern = r"```python\s*\n(.*?)\n```"
        matches = re.findall(python_pattern, content, re.DOTALL)
        if matches:
            return matches[0].strip()

        # Look for ``` code blocks
        generic_pattern = r"```\s*\n(.*?)\n```"
        matches = re.findall(generic_pattern, content, re.DOTALL)
        if matches:
            return matches[0].strip()

        # Return content as-is if no code blocks found
        return content.strip()

    def _validate_syntax(self, content: str) -> List[str]:
        """Validate Python syntax - universal validation."""
        errors = []
        try:
            ast.parse(content)
        except SyntaxError as e:
            errors.append(f"Syntax error on line {e.lineno}: {e.msg}")
        except Exception as e:
            errors.append(f"Parse error: {str(e)}")
        return errors

    def _validate_structure(self, tree: ast.AST, content: str) -> tuple[List[str], List[str]]:
        """Validate function structure and requirements."""
        errors = []
        warnings = []

        # Find function definitions
        functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]

        if not functions:
            errors.append("No function definition found")
            return errors, warnings

        if len(functions) > 1:
            warnings.append(f"Multiple functions found ({len(functions)}), expected only one")

        main_function = functions[0]

        # Check function name if specified
        if self.required_function_name and main_function.name != self.required_function_name:
            errors.append(f"Function name '{main_function.name}' does not match required '{self.required_function_name}'")

        # Check line count
        lines = content.strip().split("\n")
        line_count = len(lines)

        if line_count < self.min_lines:
            errors.append(f"Function too short: {line_count} lines (minimum: {self.min_lines})")
        elif line_count > self.max_lines:
            warnings.append(f"Function quite long: {line_count} lines (recommended max: {self.max_lines})")

        # Check for empty function
        if len(main_function.body) == 1 and isinstance(main_function.body[0], ast.Expr) and isinstance(main_function.body[0].value, ast.Constant) and main_function.body[0].value.value is Ellipsis:
            errors.append("Function contains only '...' placeholder")
        elif len(main_function.body) == 1 and isinstance(main_function.body[0], ast.Pass):
            errors.append("Function contains only 'pass' statement")

        return errors, warnings

    def _validate_style(self, content: str) -> List[str]:
        """Validate basic style guidelines - somewhat generic."""
        warnings = []

        lines = content.split("\n")

        # Check line length (PEP 8)
        for i, line in enumerate(lines, 1):
            if len(line) > 88:  # Black's line length
                warnings.append(f"Line {i} exceeds 88 characters ({len(line)} chars)")

        # Check for naming conventions
        if re.search(r"\bdef [A-Z]", content):
            warnings.append("Function name should be lowercase with underscores (PEP 8)")

        # Check for common anti-patterns
        if "eval(" in content:
            warnings.append("Consider avoiding 'eval()' for security and clarity")

        if "exec(" in content:
            warnings.append("Consider avoiding 'exec()' for security and clarity")

        # Check variable naming
        var_pattern = r"\b[A-Z]{2,}\b"
        if re.search(var_pattern, content):
            warnings.append("Consider using lowercase for variable names (avoid ALL_CAPS unless constants)")

        return warnings

    def _validate_documentation(self, tree: ast.AST, content: str) -> tuple[List[str], List[str]]:
        """Validate function documentation."""
        errors = []
        warnings = []

        functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        if not functions:
            return errors, warnings

        main_function = functions[0]

        # Check for docstring
        has_docstring = main_function.body and isinstance(main_function.body[0], ast.Expr) and isinstance(main_function.body[0].value, ast.Constant) and isinstance(main_function.body[0].value.value, str)

        if self.require_docstring and not has_docstring:
            errors.append("Function must include a docstring")
        elif has_docstring:
            docstring = main_function.body[0].value.value

            # Check docstring quality
            if len(docstring.strip()) < 10:
                warnings.append("Docstring seems too brief, consider adding more detail")

            if "Args:" not in docstring and main_function.args.args:
                warnings.append("Consider documenting function parameters in docstring")

            if "Returns:" not in docstring and main_function.returns:
                warnings.append("Consider documenting return value in docstring")

        return errors, warnings

    def _validate_imports(self, tree: ast.AST) -> List[str]:
        """Validate import statements."""
        warnings = []

        if not self.allow_external_imports:
            imports = [node for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))]

            # List of standard library modules (simplified)
            stdlib_modules = {"os", "sys", "json", "math", "random", "re", "datetime", "collections", "itertools", "functools", "operator", "pathlib", "typing", "dataclasses"}

            for imp in imports:
                if isinstance(imp, ast.Import):
                    for alias in imp.names:
                        if alias.name.split(".")[0] not in stdlib_modules:
                            warnings.append(f"External import '{alias.name}' - ensure it's necessary")
                elif isinstance(imp, ast.ImportFrom):
                    if imp.module and imp.module.split(".")[0] not in stdlib_modules:
                        warnings.append(f"External import from '{imp.module}' - ensure it's necessary")

        return warnings

    def _validate_execution(self, content: str) -> tuple[List[str], List[str]]:
        """Validate function execution with test cases - specific validation."""
        errors = []
        warnings = []

        if not self.test_cases:
            return errors, warnings

        try:
            # Create a temporary file and execute the function
            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
                # Write the function code
                f.write(content)
                f.write("\n\n")

                # Add test code
                for i, test_case in enumerate(self.test_cases):
                    args = test_case.get("args", [])
                    kwargs = test_case.get("kwargs", {})
                    expected = test_case.get("expected")

                    # Generate test call
                    args_str = ", ".join(str(arg) for arg in args)
                    kwargs_str = ", ".join(f"{k}={v}" for k, v in kwargs.items())
                    call_args = ", ".join(filter(None, [args_str, kwargs_str]))

                    f.write(f"\n# Test case {i+1}\n")
                    f.write(f"try:\n")
                    f.write(f'    result = {self.required_function_name or "generated_function"}({call_args})\n')
                    f.write(f"    expected = {repr(expected)}\n")
                    f.write(f"    if result != expected:\n")
                    f.write(f'        print(f"Test {i+1} FAILED: got {{result}}, expected {{expected}}")\n')
                    f.write(f"    else:\n")
                    f.write(f'        print(f"Test {i+1} PASSED")\n')
                    f.write(f"except Exception as e:\n")
                    f.write(f'    print(f"Test {i+1} ERROR: {{e}}")\n')

                temp_file = f.name

            # Execute the test file
            try:
                result = subprocess.run([sys.executable, temp_file], capture_output=True, text=True, timeout=10)

                if result.returncode != 0:
                    errors.append(f"Execution failed: {result.stderr}")
                else:
                    output_lines = result.stdout.strip().split("\n")
                    for line in output_lines:
                        if "FAILED" in line:
                            errors.append(f"Test case failed: {line}")
                        elif "ERROR" in line:
                            errors.append(f"Test case error: {line}")

            except subprocess.TimeoutExpired:
                warnings.append("Function execution timed out (10s limit)")

        except Exception as e:
            warnings.append(f"Could not execute function tests: {str(e)}")
        finally:
            # Clean up temp file
            try:
                Path(temp_file).unlink()
            except:
                pass

        return errors, warnings

    def _has_docstring(self, tree: ast.AST) -> bool:
        """Check if function has a docstring."""
        functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        if not functions:
            return False

        main_function = functions[0]
        return main_function.body and isinstance(main_function.body[0], ast.Expr) and isinstance(main_function.body[0].value, ast.Constant) and isinstance(main_function.body[0].value.value, str)

    def _has_type_hints(self, tree: ast.AST) -> bool:
        """Check if function has type hints."""
        functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        if not functions:
            return False

        main_function = functions[0]

        # Check return type annotation
        has_return_hint = main_function.returns is not None

        # Check parameter type annotations
        has_param_hints = any(arg.annotation is not None for arg in main_function.args.args)

        return has_return_hint or has_param_hints


def example_usage() -> None:
    """
    Example of using the FunctionGenerationTask for code generation.

    This demonstrates both the strengths and limitations of applying
    the validated-LLM framework to coding tasks.
    """
    from validated_llm.validation_loop import ValidationLoop

    # Create the function generation task
    task = FunctionGenerationTask()

    print("🔧 Testing Function Generation Task")
    print("=" * 50)

    # Example 1: Basic function with syntax validation only
    print("\n📝 Example 1: Basic function (syntax validation only)")
    validator_basic = task.create_validator(required_function_name="calculate_fibonacci", require_type_hints=False, require_docstring=False, test_cases=None)

    input_data_basic = {
        "function_name": "calculate_fibonacci",
        "description": "Calculate the nth Fibonacci number",
        "parameters": ["n: int"],
        "return_type": "int",
        "requirements": "Handle n=0 and n=1 as base cases",
        "additional_context": "Use iterative approach for efficiency",
    }

    loop = ValidationLoop(default_max_retries=2)

    try:
        result = loop.execute(prompt_template=task.prompt_template, validator=validator_basic, input_data=input_data_basic)

        if result["success"]:
            print("✅ Basic validation passed")
            print(f"Generated function (first 5 lines):")
            lines = result["output"].split("\n")[:5]
            for line in lines:
                print(f"  {line}")
        else:
            print("❌ Basic validation failed")
            if result["validation_result"]:
                for error in result["validation_result"].errors[:3]:
                    print(f"  - {error}")

    except Exception as e:
        print(f"❌ Error: {e}")

    # Example 2: Strict function with execution validation
    print("\n📝 Example 2: Strict function (with test cases)")
    validator_strict = task.create_validator(
        required_function_name="is_prime",
        require_type_hints=True,
        require_docstring=True,
        test_cases=[{"args": [2], "expected": True}, {"args": [4], "expected": False}, {"args": [17], "expected": True}, {"args": [1], "expected": False}],
    )

    input_data_strict = {
        "function_name": "is_prime",
        "description": "Check if a number is prime",
        "parameters": ["n: int"],
        "return_type": "bool",
        "requirements": "Return True if n is prime, False otherwise. Handle edge cases like n <= 1",
        "additional_context": "A prime number is only divisible by 1 and itself",
    }

    try:
        result = loop.execute(prompt_template=task.prompt_template, validator=validator_strict, input_data=input_data_strict)

        if result["success"]:
            print("✅ Strict validation passed")
            print(f"Attempts: {result['attempts']}")
            metadata = result["validation_result"].metadata
            print(f"Metadata: {metadata}")
        else:
            print("❌ Strict validation failed")
            if result["validation_result"]:
                print("Errors:")
                for error in result["validation_result"].errors:
                    print(f"  - {error}")
                if result["validation_result"].warnings:
                    print("Warnings:")
                    for warning in result["validation_result"].warnings[:3]:
                        print(f"  - {warning}")

    except Exception as e:
        print(f"❌ Error: {e}")

    print("\n🤔 Framework Analysis for Coding:")
    print("✅ Strengths:")
    print("  - Universal syntax validation")
    print("  - Generic style checking")
    print("  - Configurable requirements")
    print("  - Automatic retry with feedback")
    print("\n⚠️  Limitations:")
    print("  - Test cases are highly specific (less flexible)")
    print("  - Logic validation requires domain knowledge")
    print("  - Execution sandbox complexity")
    print("  - Performance overhead for simple tasks")


if __name__ == "__main__":
    example_usage()
