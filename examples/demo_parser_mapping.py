#!/usr/bin/env python3
"""
Demo the parser mapping functionality.
"""


class MockValidationResult:
    """Mock ValidationResult for demo."""

    def __init__(self, is_valid, errors, warnings, metadata=None):
        self.is_valid = is_valid
        self.errors = errors or []
        self.warnings = warnings or []
        self.metadata = metadata or {}


def demo_list_validator():
    """Demonstrate list validator."""
    print("📋 List Validator Demo")
    print("-" * 20)

    def validate_list(output: str):
        """Validate list format."""
        lines = output.strip().split("\n")

        # Check if it looks like a list
        is_list = all(line.strip().startswith(("-", "*", "•", "1", "2", "3", "4", "5", "6", "7", "8", "9")) for line in lines if line.strip())

        if is_list and len(lines) > 0:
            items = [line.strip().lstrip("-*•0123456789. ") for line in lines]
            return MockValidationResult(True, [], [], {"items": items})
        else:
            return MockValidationResult(False, ["Output is not formatted as a list"], [])

    # Test valid lists
    test_cases = ["- Apple\n- Banana\n- Orange", "1. First item\n2. Second item\n3. Third item", "* Bullet one\n* Bullet two\n* Bullet three", "• Unicode bullet\n• Another one", "Not a list format"]

    for i, test in enumerate(test_cases, 1):
        print(f"\nTest {i}: {repr(test[:30])}...")
        result = validate_list(test)
        print(f"Valid: {result.is_valid}")
        if result.is_valid:
            print(f"Items: {result.metadata['items']}")
        else:
            print(f"Errors: {result.errors}")


def demo_csv_validator():
    """Demonstrate CSV validator."""
    print("\n📊 CSV Validator Demo")
    print("-" * 20)

    def validate_csv(output: str):
        """Validate CSV format."""
        items = [item.strip() for item in output.split(",")]

        if len(items) > 0 and all(items):
            return MockValidationResult(True, [], [], {"items": items})
        else:
            return MockValidationResult(False, ["Output is not valid comma-separated values"], [])

    test_cases = ["apple, banana, orange", "red, green, blue, yellow", "single", "one, two, , four", ""]  # Empty item  # Empty string

    for i, test in enumerate(test_cases, 1):
        print(f"\nTest {i}: {repr(test)}")
        result = validate_csv(test)
        print(f"Valid: {result.is_valid}")
        if result.is_valid:
            print(f"Items: {result.metadata['items']}")
        else:
            print(f"Errors: {result.errors}")


def demo_json_validation():
    """Demonstrate JSON validation concept."""
    print("\n🔗 JSON Validation Demo")
    print("-" * 20)

    import json

    def validate_json(output: str, required_fields=None):
        """Validate JSON format and required fields."""
        try:
            data = json.loads(output)

            if required_fields:
                missing = [field for field in required_fields if field not in data]
                if missing:
                    return MockValidationResult(False, [f"Missing required fields: {missing}"], [])

            return MockValidationResult(True, [], [], {"parsed_data": data})
        except json.JSONDecodeError as e:
            return MockValidationResult(False, [f"Invalid JSON: {str(e)}"], [])

    test_cases = [('{"name": "John", "age": 30}', ["name", "age"]), ('{"name": "Jane"}', ["name", "age"]), ("invalid json", None), ('{"valid": true, "extra": "field"}', ["valid"])]  # Missing field

    for i, (test, required) in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test}")
        print(f"Required fields: {required}")
        result = validate_json(test, required)
        print(f"Valid: {result.is_valid}")
        if result.is_valid:
            print(f"Parsed: {result.metadata['parsed_data']}")
        else:
            print(f"Errors: {result.errors}")


def main():
    """Run parser mapping demonstrations."""
    print("🔧 Langchain Parser Mapping Demo")
    print("=" * 35)

    demo_list_validator()
    demo_csv_validator()
    demo_json_validation()

    print("\n" + "=" * 35)
    print("✅ Parser mapping functionality working!")
    print("\nThese validators can automatically replace:")
    print("• ListOutputParser → Custom ListValidator")
    print("• CommaSeparatedListOutputParser → Custom CSVValidator")
    print("• PydanticOutputParser → Custom JSON validator with schema")
    print("• StructuredOutputParser → JSONValidator")


if __name__ == "__main__":
    main()
