#!/usr/bin/env python3
"""
Code Generation Demo

This script demonstrates the code generation capabilities of validated-llm,
showing how to generate functions, classes, and complete programs with
automatic syntax validation.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from validated_llm.tasks.code_generation import ClassGenerationTask, FunctionGenerationTask, ProgramGenerationTask
from validated_llm.validation_loop import ValidationLoop


def demo_function_generation():
    """Demonstrate function generation with syntax validation."""
    print("\n" + "=" * 60)
    print("FUNCTION GENERATION DEMO")
    print("=" * 60)

    # Create a function generation task
    task = FunctionGenerationTask(language="python")

    # Generate a binary search function
    print("\nGenerating a binary search function...")
    result = ValidationLoop(task=task, max_retries=3).execute(
        function_name="binary_search",
        function_description="Perform binary search on a sorted list to find target element",
        parameters="arr: list[int], target: int",
        return_type="int",
        specifications="""
        - Return the index of target if found, -1 otherwise
        - Use iterative approach, not recursive
        - Handle edge cases (empty list, single element)
        - Include appropriate comments
        """,
        algorithm="Binary search with left and right pointers",
        examples="""
        binary_search([1, 3, 5, 7, 9], 5) -> 2
        binary_search([1, 3, 5, 7, 9], 6) -> -1
        binary_search([], 5) -> -1
        """,
        include_docstring=True,
        include_type_hints=True,
    )

    if result.is_valid:
        print("\n✅ Generated function (syntax validated):")
        print(result.output)
        print(f"\nMetadata: {result.metadata}")
    else:
        print("\n❌ Generation failed:")
        for error in result.errors:
            print(f"  - {error}")


def demo_class_generation():
    """Demonstrate class generation with syntax validation."""
    print("\n" + "=" * 60)
    print("CLASS GENERATION DEMO")
    print("=" * 60)

    # Create a class generation task
    task = ClassGenerationTask(language="python")

    # Generate a stack data structure class
    print("\nGenerating a Stack class...")
    result = ValidationLoop(task=task, max_retries=3).execute(
        class_name="Stack",
        class_description="A LIFO (Last In First Out) data structure with standard operations",
        methods="push(item), pop(), peek(), is_empty(), size()",
        properties="_items (internal list), _max_size (optional capacity)",
        specifications="""
        - Implement using a Python list internally
        - Support optional max_size parameter in constructor
        - Raise appropriate exceptions (EmptyStackError, FullStackError)
        - Include __str__ and __repr__ methods
        - Add type hints for all methods
        """,
        include_docstring=True,
    )

    if result.is_valid:
        print("\n✅ Generated class (syntax validated):")
        print(result.output)
    else:
        print("\n❌ Generation failed:")
        for error in result.errors:
            print(f"  - {error}")


def demo_program_generation():
    """Demonstrate complete program generation."""
    print("\n" + "=" * 60)
    print("PROGRAM GENERATION DEMO")
    print("=" * 60)

    # Create a program generation task
    task = ProgramGenerationTask(language="python")

    # Generate a word frequency counter program
    print("\nGenerating a word frequency counter program...")
    result = ValidationLoop(task=task, max_retries=3).execute(
        program_purpose="Count word frequencies in text files",
        io_description="Read from file path provided as command-line argument, output frequency table to stdout",
        main_functionality="""
        1. Parse command-line arguments (file path, optional --top N for top N words)
        2. Read and process the text file
        3. Count word frequencies (case-insensitive, ignore punctuation)
        4. Display results as a formatted table
        5. Handle errors gracefully (file not found, permission errors)
        """,
        specifications="""
        - Use argparse for command-line parsing
        - Use collections.Counter for frequency counting
        - Format output as aligned columns
        - Include shebang line and main guard
        - Add --help documentation
        """,
        include_docstring=True,
    )

    if result.is_valid:
        print("\n✅ Generated program (syntax validated):")
        print(result.output)
    else:
        print("\n❌ Generation failed:")
        for error in result.errors:
            print(f"  - {error}")


def demo_javascript_generation():
    """Demonstrate JavaScript code generation."""
    print("\n" + "=" * 60)
    print("JAVASCRIPT GENERATION DEMO")
    print("=" * 60)

    # Create a function generation task for JavaScript
    task = FunctionGenerationTask(language="javascript")

    # Generate a debounce function
    print("\nGenerating a debounce function in JavaScript...")
    result = ValidationLoop(task=task, max_retries=3).execute(
        function_name="debounce",
        function_description="Create a debounced version of a function that delays execution",
        parameters="func, delay",
        return_type="function",
        specifications="""
        - Return a new function that delays calling func
        - Cancel previous timeout if called again within delay
        - Preserve 'this' context and arguments
        - Use modern ES6+ syntax with arrow functions
        """,
        examples="""
        const debouncedSearch = debounce(searchAPI, 300);
        // Rapid calls will only execute searchAPI once after 300ms
        """,
        include_docstring=True,
    )

    if result.is_valid:
        print("\n✅ Generated JavaScript function (syntax validated):")
        print(result.output)
    else:
        print("\n❌ Generation failed:")
        for error in result.errors:
            print(f"  - {error}")


def demo_multi_language():
    """Demonstrate code generation in multiple languages."""
    print("\n" + "=" * 60)
    print("MULTI-LANGUAGE GENERATION DEMO")
    print("=" * 60)

    # Same algorithm in different languages
    languages = ["python", "javascript", "go"]

    for language in languages:
        print(f"\n{'=' * 40}")
        print(f"Generating factorial function in {language.upper()}")
        print(f"{'=' * 40}")

        task = FunctionGenerationTask(language=language)

        result = ValidationLoop(task=task, max_retries=2).execute(
            function_name="factorial", function_description="Calculate factorial of n using recursion", parameters="n (integer)", return_type="integer", specifications="Handle base case of n <= 1", include_docstring=True
        )

        if result.is_valid:
            print(f"\n✅ {language.upper()} version:")
            print(result.output)
        else:
            print(f"\n❌ {language.upper()} generation failed")


def main():
    """Run all code generation demos."""
    print("Code Generation Demo - Validated LLM")
    print("=====================================")

    demos = [
        ("Function Generation", demo_function_generation),
        ("Class Generation", demo_class_generation),
        ("Program Generation", demo_program_generation),
        ("JavaScript Generation", demo_javascript_generation),
        ("Multi-Language Generation", demo_multi_language),
    ]

    for i, (name, demo_func) in enumerate(demos, 1):
        try:
            print(f"\n[{i}/{len(demos)}] Running {name}...")
            demo_func()
        except Exception as e:
            print(f"\n❌ Error in {name}: {str(e)}")
            import traceback

            traceback.print_exc()

    print("\n" + "=" * 60)
    print("Code Generation Demo Complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
