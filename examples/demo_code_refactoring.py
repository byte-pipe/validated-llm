#!/usr/bin/env python3
"""
Demo script for CodeRefactoringTask - improving code quality while preserving functionality.

This demo shows how to:
1. Refactor complex functions to be cleaner and more maintainable
2. Modernize legacy code patterns
3. Optimize code for performance
4. Apply clean code principles
"""

import sys
from typing import Optional

from validated_llm.tasks.code_refactoring import CleanCodeRefactoringTask, CodeRefactoringTask, ModernizationRefactoringTask, PerformanceRefactoringTask
from validated_llm.validation_loop import ValidationLoop


def demo_basic_refactoring():
    """Demo basic code refactoring."""
    print("\n" + "=" * 60)
    print("Demo 1: Basic Code Refactoring - Complex Function")
    print("=" * 60)

    # Complex, poorly structured code
    original_code = """
def process_orders(orders):
    total = 0
    items = []
    for order in orders:
        if order['status'] == 'active':
            for item in order['items']:
                if item['quantity'] > 0:
                    if item['price'] > 0:
                        subtotal = item['quantity'] * item['price']
                        if order['discount'] > 0:
                            subtotal = subtotal * (1 - order['discount'] / 100)
                        total = total + subtotal
                        items.append({'name': item['name'], 'subtotal': subtotal})
    result = {'total': total, 'items': items}
    return result
"""

    print("\nOriginal code:")
    print(original_code)

    # Create refactoring task
    task = CodeRefactoringTask(language="python", check_complexity=True, check_naming=True, max_complexity=5)

    # Execute refactoring
    loop = ValidationLoop(task=task, max_retries=3)

    try:
        result = loop.execute(
            original_code=original_code,
            refactoring_goals=["Reduce nesting and complexity", "Extract helper functions", "Improve variable names", "Add type hints", "Handle edge cases"],
            focus_readability=True,
            extract_functions=True,
        )

        if result.output:
            print("\n✅ Refactored code:")
            print(result.output)
            print(f"\nValidation: {result.validation_result}")
            if result.validation_result and result.validation_result.metadata:
                print(f"Improvements: {result.validation_result.metadata.get('improvements', [])}")
    except Exception as e:
        print(f"\n❌ Error: {e}")


def demo_clean_code_refactoring():
    """Demo clean code principles refactoring."""
    print("\n" + "=" * 60)
    print("Demo 2: Clean Code Refactoring - Data Processing")
    print("=" * 60)

    # Code violating clean code principles
    original_code = """
def calc(d):
    r = []
    for i in d:
        if i > 0:
            if i % 2 == 0:
                r.append(i * 2)
            else:
                r.append(i * 3)
    s = 0
    for i in r:
        s = s + i
    return s / len(r) if len(r) > 0 else 0
"""

    print("\nOriginal code (poor naming, complex logic):")
    print(original_code)

    # Use CleanCodeRefactoringTask
    task = CleanCodeRefactoringTask(language="python")
    loop = ValidationLoop(task=task, max_retries=3)

    try:
        result = loop.execute(
            original_code=original_code, refactoring_goals=["Use meaningful variable and function names", "Apply single responsibility principle", "Make the code self-documenting", "Reduce cognitive complexity"]
        )

        if result.output:
            print("\n✅ Clean code refactored version:")
            print(result.output)
    except Exception as e:
        print(f"\n❌ Error: {e}")


def demo_performance_refactoring():
    """Demo performance-focused refactoring."""
    print("\n" + "=" * 60)
    print("Demo 3: Performance Refactoring - List Processing")
    print("=" * 60)

    # Inefficient code
    original_code = """
def find_duplicates(numbers):
    duplicates = []
    for i in range(len(numbers)):
        for j in range(i + 1, len(numbers)):
            if numbers[i] == numbers[j]:
                if numbers[i] not in duplicates:
                    duplicates.append(numbers[i])
    return sorted(duplicates)
"""

    print("\nOriginal code (O(n²) complexity):")
    print(original_code)

    # Use PerformanceRefactoringTask
    task = PerformanceRefactoringTask(language="python")
    loop = ValidationLoop(task=task, max_retries=3)

    try:
        result = loop.execute(
            original_code=original_code, refactoring_goals=["Improve time complexity", "Use efficient data structures", "Eliminate nested loops where possible"], performance="O(n) or O(n log n) time complexity"
        )

        if result.output:
            print("\n✅ Performance-optimized version:")
            print(result.output)
    except Exception as e:
        print(f"\n❌ Error: {e}")


def demo_modernization_refactoring():
    """Demo code modernization refactoring."""
    print("\n" + "=" * 60)
    print("Demo 4: Modernization Refactoring - Legacy Python")
    print("=" * 60)

    # Legacy Python code
    original_code = """
def merge_dicts(dict1, dict2):
    result = {}
    for key in dict1.keys():
        result[key] = dict1[key]
    for key in dict2.keys():
        result[key] = dict2[key]
    return result

def format_string(name, age, city):
    return "Name: %s, Age: %d, City: %s" % (name, age, city)

def read_file(filename):
    f = open(filename, 'r')
    content = f.read()
    f.close()
    return content
"""

    print("\nOriginal legacy code:")
    print(original_code)

    # Use ModernizationRefactoringTask
    task = ModernizationRefactoringTask(language="python")
    loop = ValidationLoop(task=task, max_retries=3)

    try:
        result = loop.execute(original_code=original_code, refactoring_goals=["Use modern Python features", "Add type hints", "Use context managers", "Use f-strings for formatting", "Use dictionary unpacking"])

        if result.output:
            print("\n✅ Modernized version:")
            print(result.output)
    except Exception as e:
        print(f"\n❌ Error: {e}")


def demo_javascript_refactoring():
    """Demo JavaScript code refactoring."""
    print("\n" + "=" * 60)
    print("Demo 5: JavaScript Refactoring - ES6+ Modernization")
    print("=" * 60)

    # Old JavaScript code
    original_code = """
function processUsers(users) {
    var result = [];
    for (var i = 0; i < users.length; i++) {
        var user = users[i];
        if (user.active) {
            var obj = {
                id: user.id,
                name: user.firstName + ' ' + user.lastName,
                email: user.email
            };
            result.push(obj);
        }
    }
    return result;
}

function sum(arr) {
    var total = 0;
    for (var i = 0; i < arr.length; i++) {
        total += arr[i];
    }
    return total;
}
"""

    print("\nOriginal JavaScript (ES5 style):")
    print(original_code)

    # Refactor to modern JavaScript
    task = ModernizationRefactoringTask(language="javascript")
    loop = ValidationLoop(task=task, max_retries=3)

    try:
        result = loop.execute(
            original_code=original_code, refactoring_goals=["Use ES6+ features", "Replace var with const/let", "Use arrow functions", "Use array methods (map, filter, reduce)", "Use template literals", "Use destructuring"]
        )

        if result.output:
            print("\n✅ Modern JavaScript version:")
            print(result.output)
    except Exception as e:
        print(f"\n❌ Error: {e}")


def demo_error_handling_refactoring():
    """Demo refactoring with focus on error handling."""
    print("\n" + "=" * 60)
    print("Demo 6: Error Handling Refactoring")
    print("=" * 60)

    # Code with poor error handling
    original_code = """
def process_data(data):
    result = json.loads(data)
    user_id = result['user']['id']
    items = result['items']
    total = 0
    for item in items:
        total += item['price'] * item['quantity']
    return {'user_id': user_id, 'total': total}
"""

    print("\nOriginal code (no error handling):")
    print(original_code)

    task = CodeRefactoringTask(language="python", refactoring_style="clean_code")
    loop = ValidationLoop(task=task, max_retries=3)

    try:
        result = loop.execute(
            original_code=original_code,
            refactoring_goals=["Add comprehensive error handling", "Handle missing keys gracefully", "Add input validation", "Return meaningful error messages", "Add logging for debugging"],
            specifications="The function should handle invalid JSON, missing keys, and invalid data types",
        )

        if result.output:
            print("\n✅ Refactored with error handling:")
            print(result.output)
    except Exception as e:
        print(f"\n❌ Error: {e}")


def main():
    """Run all demos."""
    print("Code Refactoring Task Demo")
    print("This demo shows various code refactoring scenarios")

    # Check if user wants to run a specific demo
    if len(sys.argv) > 1:
        demo_num = sys.argv[1]
        demos = {
            "1": demo_basic_refactoring,
            "2": demo_clean_code_refactoring,
            "3": demo_performance_refactoring,
            "4": demo_modernization_refactoring,
            "5": demo_javascript_refactoring,
            "6": demo_error_handling_refactoring,
        }

        if demo_num in demos:
            demos[demo_num]()
        else:
            print(f"Unknown demo number: {demo_num}")
            print("Available demos: 1-6")
    else:
        # Run all demos
        demo_basic_refactoring()
        demo_clean_code_refactoring()
        demo_performance_refactoring()
        demo_modernization_refactoring()
        demo_javascript_refactoring()
        demo_error_handling_refactoring()

        print("\n" + "=" * 60)
        print("All demos completed!")
        print("Run with a demo number (1-6) to see specific examples")


if __name__ == "__main__":
    main()
