#!/usr/bin/env python3
"""
Test Generation Demo

This script demonstrates how to generate comprehensive unit tests
with automatic validation using the TestGenerationTask.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from validated_llm.tasks.test_generation import BDDTestGenerationTask, IntegrationTestGenerationTask, TestGenerationTask, UnitTestGenerationTask
from validated_llm.validation_loop import ValidationLoop


def demo_unit_test_generation():
    """Demonstrate unit test generation for a simple function."""
    print("\n" + "=" * 60)
    print("UNIT TEST GENERATION DEMO")
    print("=" * 60)

    # Create a unit test generation task
    task = UnitTestGenerationTask(language="python")

    # Generate tests for a factorial function
    print("\nGenerating unit tests for factorial function...")
    result = ValidationLoop(task=task, max_retries=3).execute(
        function_to_test="factorial",
        function_signature="def factorial(n: int) -> int",
        function_description="Calculate the factorial of a non-negative integer n",
        examples="""
        factorial(0) -> 1
        factorial(1) -> 1
        factorial(5) -> 120
        factorial(10) -> 3628800
        """,
        error_conditions="negative numbers, non-integer inputs, very large numbers",
        test_scenarios="normal cases, edge cases (0, 1), error cases (negative, non-int)",
    )

    if result.is_valid:
        print("\n✅ Generated comprehensive unit tests:")
        print("-" * 50)
        print(result.output)
        print("-" * 50)
        print(f"Validation metadata: {result.metadata}")
    else:
        print("\n❌ Test generation failed:")
        for error in result.errors:
            print(f"  - {error}")


def demo_class_test_generation():
    """Demonstrate test generation for a class."""
    print("\n" + "=" * 60)
    print("CLASS TEST GENERATION DEMO")
    print("=" * 60)

    task = TestGenerationTask(language="python", min_test_functions=4, include_setup_teardown=True)

    print("\nGenerating tests for a Stack class...")
    result = ValidationLoop(task=task, max_retries=3).execute(
        class_to_test="Stack",
        class_description="A LIFO (Last In First Out) data structure",
        class_methods="push(item), pop(), peek(), is_empty(), size()",
        test_scenarios="""
        - Test push operation adds items correctly
        - Test pop operation removes and returns last item
        - Test peek operation returns last item without removing
        - Test is_empty returns correct boolean
        - Test size returns correct count
        """,
        error_conditions="pop from empty stack, peek from empty stack",
        dependencies="No external dependencies required",
    )

    if result.is_valid:
        print("\n✅ Generated class tests:")
        print("-" * 50)
        print(result.output)
        print("-" * 50)
    else:
        print("\n❌ Test generation failed:")
        for error in result.errors:
            print(f"  - {error}")


def demo_javascript_test_generation():
    """Demonstrate JavaScript test generation."""
    print("\n" + "=" * 60)
    print("JAVASCRIPT TEST GENERATION DEMO")
    print("=" * 60)

    task = TestGenerationTask(language="javascript", test_framework="jest")

    print("\nGenerating Jest tests for async function...")
    result = ValidationLoop(task=task, max_retries=3).execute(
        function_to_test="fetchUserData",
        function_signature="async function fetchUserData(userId: string): Promise<User>",
        function_description="Fetch user data from API by user ID",
        examples="""
        await fetchUserData("123") -> {id: "123", name: "John", email: "john@example.com"}
        await fetchUserData("invalid") -> throws Error("User not found")
        """,
        test_scenarios="successful fetch, user not found, network error, invalid input",
        error_conditions="invalid user ID, network failure, server error",
        dependencies="Mock fetch API or HTTP client",
    )

    if result.is_valid:
        print("\n✅ Generated JavaScript tests:")
        print("-" * 50)
        print(result.output)
        print("-" * 50)
    else:
        print("\n❌ JavaScript test generation failed:")
        for error in result.errors:
            print(f"  - {error}")


def demo_bdd_test_generation():
    """Demonstrate BDD-style test generation."""
    print("\n" + "=" * 60)
    print("BDD TEST GENERATION DEMO")
    print("=" * 60)

    task = BDDTestGenerationTask(language="python")

    print("\nGenerating BDD-style tests for user authentication...")
    result = ValidationLoop(task=task, max_retries=3).execute(
        function_to_test="authenticate_user",
        function_signature="def authenticate_user(username: str, password: str) -> AuthResult",
        function_description="Authenticate user with username and password",
        test_scenarios="""
        Given a valid username and password
        When the user attempts to authenticate
        Then they should be granted access

        Given an invalid username
        When the user attempts to authenticate
        Then they should be denied access

        Given a valid username but invalid password
        When the user attempts to authenticate
        Then they should be denied access and attempt should be logged
        """,
        expected_behavior="Return AuthResult with success/failure and appropriate messages",
        error_conditions="empty credentials, SQL injection attempts, rate limiting",
    )

    if result.is_valid:
        print("\n✅ Generated BDD tests:")
        print("-" * 50)
        print(result.output)
        print("-" * 50)
    else:
        print("\n❌ BDD test generation failed:")
        for error in result.errors:
            print(f"  - {error}")


def demo_integration_test_generation():
    """Demonstrate integration test generation."""
    print("\n" + "=" * 60)
    print("INTEGRATION TEST GENERATION DEMO")
    print("=" * 60)

    task = IntegrationTestGenerationTask(language="python")

    print("\nGenerating integration tests for API endpoint...")
    result = ValidationLoop(task=task, max_retries=3).execute(
        function_to_test="user_registration_endpoint",
        function_description="REST API endpoint for user registration",
        test_scenarios="""
        - Test successful user registration with valid data
        - Test registration with duplicate email
        - Test registration with invalid email format
        - Test database integration and data persistence
        """,
        dependencies="Test database, HTTP client, email service mock",
        requirements="""
        - Set up test database before each test
        - Clean up test data after each test
        - Mock external email service
        - Test actual HTTP requests and responses
        """,
    )

    if result.is_valid:
        print("\n✅ Generated integration tests:")
        print("-" * 50)
        print(result.output)
        print("-" * 50)
    else:
        print("\n❌ Integration test generation failed:")
        for error in result.errors:
            print(f"  - {error}")


def main():
    """Run all test generation demos."""
    print("Test Generation Demo - Validated LLM")
    print("====================================")
    print("\nThis demo shows how to generate comprehensive unit tests")
    print("with automatic validation for quality and completeness.")

    demos = [
        ("Unit Test Generation", demo_unit_test_generation),
        ("Class Test Generation", demo_class_test_generation),
        ("JavaScript Test Generation", demo_javascript_test_generation),
        ("BDD Test Generation", demo_bdd_test_generation),
        ("Integration Test Generation", demo_integration_test_generation),
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
    print("Test Generation Demo Complete!")
    print("=" * 60)
    print("\nKey Features Demonstrated:")
    print("  - Automatic test quality validation")
    print("  - Multiple testing frameworks support")
    print("  - Edge case and error condition testing")
    print("  - BDD-style test generation")
    print("  - Integration test patterns")
    print("  - Comprehensive test coverage")


if __name__ == "__main__":
    main()
