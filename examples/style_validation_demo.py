#!/usr/bin/env python3
"""
Style Validation Demo

This script demonstrates how the StyleValidator can be used to ensure
generated code follows proper formatting standards.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from validated_llm.validators.style import StyleValidator


def demo_python_style_validation():
    """Demonstrate Python code style validation with Black."""
    print("\n" + "=" * 60)
    print("PYTHON STYLE VALIDATION (Black)")
    print("=" * 60)

    # Example 1: Poorly formatted code
    print("\n1. Checking poorly formatted code:")
    messy_code = """def  factorial( n ):
    if n<=1: return 1
    else: return n*factorial(n-1)
class MyClass: pass"""

    validator = StyleValidator(language="python", formatter="black", show_diff=True)
    result = validator.validate(messy_code)

    if result.is_valid:
        if result.warnings:
            print(f"   ⚠️  Warning: {result.warnings[0]}")
        else:
            print("   ✅ Code is properly formatted")
    else:
        print("   ❌ Style violations found:")
        for error in result.errors:
            print(f"      {error}")

    # Example 2: Auto-fix mode
    print("\n2. Using auto-fix mode:")
    auto_validator = StyleValidator(language="python", formatter="black", auto_fix=True)

    result = auto_validator.validate(messy_code)

    if result.is_valid and result.metadata.get("output"):
        print("   ✅ Code automatically formatted:")
        print("   " + "-" * 50)
        for line in result.metadata["output"].split("\n"):
            print(f"   {line}")
        print("   " + "-" * 50)
    elif result.warnings:
        print(f"   ⚠️  {result.warnings[0]}")


def demo_javascript_style_validation():
    """Demonstrate JavaScript code style validation with Prettier."""
    print("\n" + "=" * 60)
    print("JAVASCRIPT STYLE VALIDATION (Prettier)")
    print("=" * 60)

    messy_js = """function hello(name){return`Hello ${name}!`}
const obj={a:1,b:2,c:3}"""

    validator = StyleValidator(language="javascript", formatter="prettier", auto_fix=True)

    result = validator.validate(messy_js)

    if result.is_valid:
        if result.metadata.get("output"):
            print("   ✅ Code formatted with Prettier:")
            print("   " + "-" * 50)
            for line in result.metadata["output"].split("\n"):
                print(f"   {line}")
            print("   " + "-" * 50)
        elif result.warnings:
            print(f"   ⚠️  {result.warnings[0]}")
        else:
            print("   ✅ Code is already properly formatted")
    else:
        print("   ❌ Style issues found")


def demo_multiple_languages():
    """Demonstrate style validation across multiple languages."""
    print("\n" + "=" * 60)
    print("MULTI-LANGUAGE STYLE VALIDATION")
    print("=" * 60)

    examples = {
        "python": {"formatter": "black", "code": "def add(a,b):return a+b"},
        "javascript": {"formatter": "prettier", "code": "function add(a,b){return a+b}"},
        "go": {"formatter": "gofmt", "code": "func add(a,b int)int{return a+b}"},
    }

    for language, config in examples.items():
        print(f"\n{language.upper()} ({config['formatter']}):")

        validator = StyleValidator(language=language, formatter=config["formatter"], auto_fix=True)

        result = validator.validate(config["code"])

        if result.is_valid:
            if result.metadata.get("output"):
                print(f"   Formatted: {result.metadata['output'].strip()}")
            elif result.warnings:
                print(f"   ⚠️  {result.warnings[0]}")
            else:
                print("   ✅ Already properly formatted")
        else:
            print(f"   ❌ {result.errors[0]}")


def demo_style_with_config():
    """Demonstrate using style validation with configuration files."""
    print("\n" + "=" * 60)
    print("STYLE VALIDATION WITH CONFIGURATION")
    print("=" * 60)

    # Example with line length configuration
    long_line_code = """def very_long_function_name_that_exceeds_typical_line_length_limits(parameter1, parameter2, parameter3, parameter4):
    return parameter1 + parameter2 + parameter3 + parameter4
"""

    print("\nChecking code with long lines:")
    validator = StyleValidator(language="python", formatter="black", show_diff=True)

    result = validator.validate(long_line_code)

    if not result.is_valid:
        print("   ❌ Style issues detected (line too long)")
        if result.metadata.get("has_style_issues"):
            print("   Black would reformat to wrap long lines")
    elif result.warnings:
        print(f"   ⚠️  {result.warnings[0]}")
    else:
        print("   ✅ Code meets style standards")


def main():
    """Run all style validation demos."""
    print("Style Validation Demo - Validated LLM")
    print("=====================================")
    print("\nThis demo shows how StyleValidator ensures generated code")
    print("follows proper formatting standards for various languages.")

    demos = [
        ("Python Style Validation", demo_python_style_validation),
        ("JavaScript Style Validation", demo_javascript_style_validation),
        ("Multi-Language Validation", demo_multiple_languages),
        ("Configuration-based Validation", demo_style_with_config),
    ]

    for i, (name, demo_func) in enumerate(demos, 1):
        try:
            print(f"\n[{i}/{len(demos)}] {name}")
            demo_func()
        except Exception as e:
            print(f"\n❌ Error in {name}: {str(e)}")

    print("\n" + "=" * 60)
    print("Style Validation Demo Complete!")
    print("=" * 60)
    print("\nNote: Some formatters may not be installed on your system.")
    print("Install them to see full functionality:")
    print("  - Python: pip install black isort autopep8")
    print("  - JavaScript: npm install -g prettier")
    print("  - Go: Go includes gofmt by default")
    print("  - Rust: rustup component add rustfmt")
    print("  - Java: Download google-java-format")


if __name__ == "__main__":
    main()
