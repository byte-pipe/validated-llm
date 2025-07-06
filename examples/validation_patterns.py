#!/usr/bin/env python3
"""
Common Validation Patterns Examples

This module demonstrates practical validation patterns and use cases
for the validated-llm framework.
"""

import json
import time
from pathlib import Path
from typing import Any, Dict, List

from validated_llm.tasks.code_generation import FunctionGenerationTask
from validated_llm.tasks.documentation import APIDocumentationTask
from validated_llm.tasks.json_generation import JSONGenerationTask
from validated_llm.validation_loop import ValidationLoop
from validated_llm.validators.composite import CompositeValidator
from validated_llm.validators.email import EmailValidator
from validated_llm.validators.json_schema import JSONSchemaValidator
from validated_llm.validators.markdown import MarkdownValidator
from validated_llm.validators.range import RangeValidator
from validated_llm.validators.syntax import SyntaxValidator
from validated_llm.validators.yaml import YAMLValidator


def pattern_1_user_registration_validation():
    """
    Pattern 1: User Registration Data Validation

    Validates user registration data with multiple validators:
    - Email format validation
    - JSON schema validation for structure
    - Range validation for age
    """
    print("=== Pattern 1: User Registration Validation ===")

    # Define user schema
    user_schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string", "minLength": 2, "maxLength": 50},
            "email": {"type": "string", "format": "email"},
            "age": {"type": "integer", "minimum": 13, "maximum": 120},
            "preferences": {"type": "array", "items": {"type": "string"}, "uniqueItems": True, "maxItems": 10},
        },
        "required": ["name", "email", "age"],
        "additionalProperties": False,
    }

    # Create composite validator
    user_validator = CompositeValidator(
        name="user_registration_validator",
        validators=[
            JSONSchemaValidator(name="structure", schema=user_schema),
            # Additional custom validations could go here
        ],
        combination_logic="AND",
    )

    # Test data
    test_cases = [
        # Valid user
        {"name": "Alice Johnson", "email": "alice@example.com", "age": 28, "preferences": ["coding", "reading", "cycling"]},
        # Invalid email
        {"name": "Bob Smith", "email": "invalid-email", "age": 35},
        # Missing required field
        {
            "name": "Charlie Brown",
            "email": "charlie@example.com"
            # Missing age
        },
    ]

    for i, user_data in enumerate(test_cases, 1):
        print(f"\nTest Case {i}: {user_data.get('name', 'Unknown')}")
        json_string = json.dumps(user_data)
        result = user_validator.validate(json_string)

        print(f"Valid: {result.is_valid}")
        if not result.is_valid:
            print(f"Errors: {result.errors}")


def pattern_2_api_response_validation():
    """
    Pattern 2: API Response Validation

    Validates API responses with nested objects and arrays.
    Common for microservices and API gateways.
    """
    print("\n=== Pattern 2: API Response Validation ===")

    # API response schema
    api_response_schema = {
        "type": "object",
        "properties": {
            "status": {"type": "string", "enum": ["success", "error", "pending"]},
            "data": {
                "type": "object",
                "properties": {
                    "users": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {"id": {"type": "integer"}, "name": {"type": "string"}, "email": {"type": "string", "format": "email"}, "active": {"type": "boolean"}},
                            "required": ["id", "name", "email"],
                        },
                    },
                    "pagination": {
                        "type": "object",
                        "properties": {"page": {"type": "integer", "minimum": 1}, "limit": {"type": "integer", "minimum": 1, "maximum": 100}, "total": {"type": "integer", "minimum": 0}},
                        "required": ["page", "limit", "total"],
                    },
                },
                "required": ["users", "pagination"],
            },
            "timestamp": {"type": "string", "format": "date-time"},
        },
        "required": ["status", "data", "timestamp"],
    }

    validator = JSONSchemaValidator(name="api_response", schema=api_response_schema, strict_mode=True)

    # Test API response
    api_response = {
        "status": "success",
        "data": {
            "users": [{"id": 1, "name": "Alice Johnson", "email": "alice@example.com", "active": True}, {"id": 2, "name": "Bob Smith", "email": "bob@example.com", "active": False}],
            "pagination": {"page": 1, "limit": 10, "total": 2},
        },
        "timestamp": "2024-01-15T10:30:00Z",
    }

    result = validator.validate(json.dumps(api_response, indent=2))
    print(f"API Response Valid: {result.is_valid}")
    if not result.is_valid:
        print(f"Errors: {result.errors}")


def pattern_3_progressive_validation():
    """
    Pattern 3: Progressive Validation

    Start with basic validation and progressively add more strict rules.
    Useful for iterative development and testing.
    """
    print("\n=== Pattern 3: Progressive Validation ===")

    # Sample email for testing
    test_email = "user@example.com"

    # Level 1: Basic format validation
    basic_validator = EmailValidator(name="basic_email", check_deliverability=False)

    # Level 2: Enhanced validation
    enhanced_validator = EmailValidator(name="enhanced_email", check_deliverability=True, require_mx_record=False)

    # Level 3: Strict validation
    strict_validator = EmailValidator(name="strict_email", check_deliverability=True, require_mx_record=True, allowed_domains=["example.com", "company.com"])

    validators = [("Basic", basic_validator), ("Enhanced", enhanced_validator), ("Strict", strict_validator)]

    for level_name, validator in validators:
        result = validator.validate(test_email)
        print(f"{level_name} Validation: {result.is_valid}")
        if not result.is_valid:
            print(f"  Errors: {result.errors}")


def pattern_4_content_quality_scoring():
    """
    Pattern 4: Content Quality Scoring

    Validates content quality using multiple criteria with scoring.
    Useful for content generation and review systems.
    """
    print("\n=== Pattern 4: Content Quality Scoring ===")

    # Create composite validator for article quality
    article_validator = CompositeValidator(
        name="article_quality",
        validators=[
            MarkdownValidator(name="format"),
            RangeValidator(name="length", min_value=300, max_value=1500, unit="words"),
            # Could add more validators for readability, grammar, etc.
        ],
        combination_logic="AND",
    )

    # Sample article content
    sample_article = """
    # Introduction to Machine Learning

    Machine learning is a subset of artificial intelligence that enables computers to learn and improve from experience without being explicitly programmed. This field has gained tremendous popularity in recent years due to its wide range of applications.

    ## Key Concepts

    ### Supervised Learning
    In supervised learning, algorithms learn from labeled training data to make predictions on new, unseen data. Common examples include classification and regression tasks.

    ### Unsupervised Learning
    Unsupervised learning works with unlabeled data to discover hidden patterns or structures within the dataset.

    ## Applications

    Machine learning is used in various domains:
    - Image recognition and computer vision
    - Natural language processing
    - Recommendation systems
    - Fraud detection
    - Autonomous vehicles

    ## Conclusion

    As machine learning continues to evolve, it will undoubtedly play an increasingly important role in shaping our technological future.
    """

    result = article_validator.validate(sample_article)
    print(f"Article Quality Valid: {result.is_valid}")
    print(f"Quality Score: {result.score}")
    if not result.is_valid:
        print(f"Issues: {result.errors}")
    if result.warnings:
        print(f"Warnings: {result.warnings}")


def pattern_5_code_generation_validation():
    """
    Pattern 5: Code Generation with Multi-Language Validation

    Generates and validates code in different programming languages.
    Useful for code generation tools and educational platforms.
    """
    print("\n=== Pattern 5: Code Generation Validation ===")

    # Python function validation
    python_code = """
def fibonacci(n):
    '''Generate fibonacci sequence up to n terms'''
    if n <= 0:
        return []
    elif n == 1:
        return [0]
    elif n == 2:
        return [0, 1]

    sequence = [0, 1]
    for i in range(2, n):
        sequence.append(sequence[i-1] + sequence[i-2])

    return sequence

# Test the function
print(fibonacci(10))
"""

    # JavaScript function
    javascript_code = """
function fibonacci(n) {
    if (n <= 0) return [];
    if (n === 1) return [0];
    if (n === 2) return [0, 1];

    const sequence = [0, 1];
    for (let i = 2; i < n; i++) {
        sequence.push(sequence[i-1] + sequence[i-2]);
    }

    return sequence;
}

console.log(fibonacci(10));
"""

    # Validate different languages
    code_samples = [("Python", python_code, "python"), ("JavaScript", javascript_code, "javascript")]

    for language, code, lang_id in code_samples:
        print(f"\n{language} Code Validation:")
        validator = SyntaxValidator(language=lang_id)
        result = validator.validate(code)

        print(f"  Syntax Valid: {result.is_valid}")
        if not result.is_valid:
            print(f"  Errors: {result.errors}")
        if result.metadata:
            print(f"  Metadata: {result.metadata}")


def pattern_6_configuration_validation():
    """
    Pattern 6: Configuration File Validation

    Validates YAML configuration files for applications.
    Common for DevOps, CI/CD, and application configuration.
    """
    print("\n=== Pattern 6: Configuration Validation ===")

    # Sample YAML configuration
    config_yaml = """
    app:
      name: "My Application"
      version: "1.0.0"
      debug: false

    database:
      host: "localhost"
      port: 5432
      name: "myapp_db"
      username: "dbuser"
      password: "secure_password"

    api:
      rate_limit: 1000
      timeout: 30
      allowed_origins:
        - "https://example.com"
        - "https://app.example.com"

    logging:
      level: "INFO"
      format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
      handlers:
        - type: "file"
          filename: "app.log"
        - type: "console"
    """

    # Validate YAML structure
    yaml_validator = YAMLValidator(name="config_validator", max_depth=5, check_duplicates=True)

    result = yaml_validator.validate(config_yaml)
    print(f"Configuration Valid: {result.is_valid}")
    if not result.is_valid:
        print(f"Errors: {result.errors}")
    if result.metadata:
        print(f"Structure Info: {result.metadata}")


def pattern_7_batch_validation_with_metrics():
    """
    Pattern 7: Batch Validation with Performance Metrics

    Validates multiple items efficiently while collecting performance metrics.
    Useful for data processing pipelines and quality assurance.
    """
    print("\n=== Pattern 7: Batch Validation with Metrics ===")

    # Sample email addresses to validate
    email_batch = ["valid@example.com", "another.valid@test.org", "invalid.email", "missing@", "@missing.com", "good.email@company.co.uk", "bad email@spaces.com", "unicode@tëst.com"]

    validator = EmailValidator(name="batch_email")

    # Track metrics
    results = []
    total_time = 0
    valid_count = 0

    print(f"Validating {len(email_batch)} email addresses...")

    for i, email in enumerate(email_batch, 1):
        start_time = time.time()
        result = validator.validate(email)
        validation_time = time.time() - start_time

        total_time += validation_time
        if result.is_valid:
            valid_count += 1

        results.append({"email": email, "valid": result.is_valid, "errors": result.errors, "time_ms": validation_time * 1000})

        print(f"  {i:2d}. {email:25s} -> {'✓' if result.is_valid else '✗'} " f"({validation_time*1000:.1f}ms)")

    # Summary metrics
    print(f"\nBatch Validation Summary:")
    print(f"  Total items: {len(email_batch)}")
    print(f"  Valid items: {valid_count}")
    print(f"  Success rate: {valid_count/len(email_batch)*100:.1f}%")
    print(f"  Total time: {total_time*1000:.1f}ms")
    print(f"  Average time per item: {total_time/len(email_batch)*1000:.1f}ms")


def pattern_8_conditional_validation():
    """
    Pattern 8: Conditional Validation Based on Content Type

    Applies different validation rules based on content characteristics.
    Useful for multi-format content systems and dynamic validation.
    """
    print("\n=== Pattern 8: Conditional Validation ===")

    # Sample content items with different types
    content_items = [
        {"type": "json", "content": '{"name": "Alice", "age": 30, "email": "alice@example.com"}'},
        {
            "type": "yaml",
            "content": """
name: Bob
age: 25
email: bob@example.com
preferences:
  - coding
  - reading
""",
        },
        {
            "type": "python",
            "content": """
def greet(name):
    return f"Hello, {name}!"

print(greet("World"))
""",
        },
    ]

    # Define validators for each type
    validators = {
        "json": JSONSchemaValidator(schema={"type": "object", "properties": {"name": {"type": "string"}, "age": {"type": "integer"}, "email": {"type": "string", "format": "email"}}, "required": ["name", "age", "email"]}),
        "yaml": YAMLValidator(),
        "python": SyntaxValidator(language="python"),
    }

    for item in content_items:
        content_type = item["type"]
        content = item["content"]

        print(f"\nValidating {content_type.upper()} content:")

        if content_type in validators:
            validator = validators[content_type]
            result = validator.validate(content)

            print(f"  Valid: {result.is_valid}")
            if not result.is_valid:
                print(f"  Errors: {result.errors}")
            if result.metadata:
                print(f"  Info: {result.metadata}")
        else:
            print(f"  No validator available for type: {content_type}")


def main():
    """Run all validation pattern examples"""
    print("Validated-LLM Framework - Common Validation Patterns")
    print("=" * 60)

    patterns = [
        pattern_1_user_registration_validation,
        pattern_2_api_response_validation,
        pattern_3_progressive_validation,
        pattern_4_content_quality_scoring,
        pattern_5_code_generation_validation,
        pattern_6_configuration_validation,
        pattern_7_batch_validation_with_metrics,
        pattern_8_conditional_validation,
    ]

    for pattern_func in patterns:
        try:
            pattern_func()
            print("\n" + "-" * 60)
        except Exception as e:
            print(f"Error in {pattern_func.__name__}: {e}")
            print("-" * 60)

    print("\nAll validation patterns completed!")


if __name__ == "__main__":
    main()
