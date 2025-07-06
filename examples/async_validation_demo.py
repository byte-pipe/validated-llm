"""
Async Validation Demo

Demonstrates the performance benefits of async validation compared to synchronous validation.
Shows concurrent validation, batch processing, and performance comparisons.
"""

import asyncio
import json
import time
from typing import Any, Dict, List

from validated_llm.async_validation_loop import AsyncValidationLoop
from validated_llm.async_validator import AsyncBaseValidator, AsyncCompositeValidator, AsyncFunctionValidator, AsyncValidatorAdapter
from validated_llm.base_validator import ValidationResult
from validated_llm.validation_loop import ValidationLoop
from validated_llm.validators.async_json_schema import AsyncJSONSchemaValidator
from validated_llm.validators.async_range import AsyncRangeValidator
from validated_llm.validators.json_schema import JSONSchemaValidator
from validated_llm.validators.range import RangeValidator


class SlowValidator(AsyncBaseValidator):
    """Simulates a slow validation operation (e.g., API call, database query)."""

    def __init__(self, name: str, delay: float = 1.0, should_pass: bool = True):
        super().__init__(name=name, description=f"Slow validator with {delay}s delay")
        self.delay = delay
        self.should_pass = should_pass

    async def validate_async(self, output: str, context: Dict[str, Any] = None) -> ValidationResult:
        """Simulate slow validation with async sleep."""
        print(f"  {self.name}: Starting validation...")
        await asyncio.sleep(self.delay)
        print(f"  {self.name}: Validation complete!")

        if self.should_pass:
            return ValidationResult(is_valid=True, errors=[], metadata={"delay": self.delay})
        else:
            return ValidationResult(is_valid=False, errors=[f"{self.name} failed"], metadata={"delay": self.delay})


def demo_basic_async_validation():
    """Demonstrate basic async validation capabilities."""
    print("=== Basic Async Validation Demo ===")

    async def run_demo():
        # Create async validators
        print("\\n1. Creating async validators...")

        # JSON Schema validator
        schema = {"type": "object", "properties": {"name": {"type": "string"}, "age": {"type": "integer", "minimum": 0, "maximum": 150}, "email": {"type": "string", "format": "email"}}, "required": ["name", "age"]}
        json_validator = AsyncJSONSchemaValidator(schema)

        # Range validator
        range_validator = AsyncRangeValidator(min_value=18, max_value=65, value_type="integer")

        # Function validator
        async def check_name_length(output: str) -> bool:
            await asyncio.sleep(0.1)  # Simulate async operation
            data = json.loads(output)
            return len(data.get("name", "")) >= 2

        function_validator = AsyncFunctionValidator(check_name_length, name="NameLengthValidator")

        print("\\n2. Testing individual validators...")

        valid_json = '{"name": "John Doe", "age": 30, "email": "john@example.com"}'

        # Test JSON validator
        start = time.time()
        result = await json_validator.validate_async(valid_json)
        json_time = time.time() - start
        print(f"  JSON Schema validation: {'✓' if result.is_valid else '✗'} ({json_time:.3f}s)")

        # Test range validator (checking age)
        start = time.time()
        result = await range_validator.validate_async("30")
        range_time = time.time() - start
        print(f"  Range validation: {'✓' if result.is_valid else '✗'} ({range_time:.3f}s)")

        # Test function validator
        start = time.time()
        result = await function_validator.validate_async(valid_json)
        func_time = time.time() - start
        print(f"  Function validation: {'✓' if result.is_valid else '✗'} ({func_time:.3f}s)")

        return json_time + range_time + func_time

    return asyncio.run(run_demo())


def demo_concurrent_vs_sequential():
    """Compare concurrent vs sequential validation performance."""
    print("\\n=== Concurrent vs Sequential Validation Demo ===")

    async def run_comparison():
        # Create multiple slow validators
        validators = [
            SlowValidator("DatabaseValidator", delay=0.5),
            SlowValidator("APIValidator", delay=0.7),
            SlowValidator("FileValidator", delay=0.3),
            SlowValidator("NetworkValidator", delay=0.6),
        ]

        print("\\n1. Running validators sequentially...")
        start_time = time.time()

        sequential_composite = AsyncCompositeValidator(validators, operator="AND", concurrent=False)
        result = await sequential_composite.validate_async("test data")

        sequential_time = time.time() - start_time
        print(f"  Sequential execution: {sequential_time:.2f}s")
        print(f"  Result: {'✓ All passed' if result.is_valid else '✗ Some failed'}")

        print("\\n2. Running validators concurrently...")
        start_time = time.time()

        concurrent_composite = AsyncCompositeValidator(validators, operator="AND", concurrent=True)
        result = await concurrent_composite.validate_async("test data")

        concurrent_time = time.time() - start_time
        print(f"  Concurrent execution: {concurrent_time:.2f}s")
        print(f"  Result: {'✓ All passed' if result.is_valid else '✗ Some failed'}")

        speedup = sequential_time / concurrent_time
        print(f"\\n  Performance improvement: {speedup:.1f}x speedup!")

        return sequential_time, concurrent_time

    return asyncio.run(run_comparison())


def demo_batch_processing():
    """Demonstrate batch processing capabilities."""
    print("\\n=== Batch Processing Demo ===")

    async def run_batch_demo():
        # Create async validation loop
        async_loop = AsyncValidationLoop()

        # Register validators
        schema = {"type": "object", "properties": {"id": {"type": "integer"}, "name": {"type": "string"}, "score": {"type": "number", "minimum": 0, "maximum": 100}}, "required": ["id", "name", "score"]}

        async_loop.register_validator("json_validator", AsyncJSONSchemaValidator(schema))

        # Create batch requests
        batch_requests = []
        for i in range(5):
            batch_requests.append(
                {
                    "prompt_template": "Generate a JSON object with id {id}, name {name}, and score {score}",
                    "validator": "json_validator",
                    "input_data": {"id": i + 1, "name": f"Person_{i + 1}", "score": (i + 1) * 20},
                    "max_retries": 1,
                    "debug": False,
                }
            )

        print(f"\\n1. Processing {len(batch_requests)} validation requests...")
        print("   Note: This demo simulates the validation part only (no actual LLM calls)")

        # Simulate batch execution timing
        start_time = time.time()

        # For demo purposes, we'll simulate the validation results
        simulated_results = []
        for i, request in enumerate(batch_requests):
            # Create mock valid JSON output
            mock_output = json.dumps({"id": request["input_data"]["id"], "name": request["input_data"]["name"], "score": request["input_data"]["score"]})

            # Validate the mock output
            validator = async_loop.get_validator("json_validator")
            result = await validator.validate_async(mock_output)

            simulated_results.append({"success": result.is_valid, "output": mock_output, "attempts": 1, "validation_result": result, "execution_time": 0.1 + (i * 0.05)})  # Simulated time

        batch_time = time.time() - start_time

        print(f"\\n2. Batch processing results:")
        print(f"   Total time: {batch_time:.2f}s")
        print(f"   Average per request: {batch_time / len(batch_requests):.3f}s")

        success_count = sum(1 for r in simulated_results if r["success"])
        print(f"   Success rate: {success_count}/{len(simulated_results)} ({success_count/len(simulated_results)*100:.1f}%)")

        return batch_time

    return asyncio.run(run_batch_demo())


def demo_sync_vs_async_adapters():
    """Compare sync validators vs async adapters."""
    print("\\n=== Sync vs Async Adapter Demo ===")

    async def run_adapter_demo():
        # Create sync validators
        sync_json = JSONSchemaValidator({"type": "object", "properties": {"value": {"type": "integer"}}, "required": ["value"]})
        sync_range = RangeValidator(min_value=1, max_value=100, value_type="integer")

        # Create async adapters
        async_json = AsyncValidatorAdapter(sync_json)
        async_range = AsyncValidatorAdapter(sync_range)

        test_data = '{"value": 42}'

        print("\\n1. Testing sync validators (simulated)...")
        start = time.time()
        # Note: In real usage, sync validators would block the event loop
        sync_json_result = sync_json.validate(test_data)
        sync_range_result = sync_range.validate("42")
        sync_time = time.time() - start
        print(f"  Sync execution: {sync_time:.4f}s")
        print(f"  JSON result: {'✓' if sync_json_result.is_valid else '✗'}")
        print(f"  Range result: {'✓' if sync_range_result.is_valid else '✗'}")

        print("\\n2. Testing async adapters...")
        start = time.time()
        async_json_result = await async_json.validate_async(test_data)
        async_range_result = await async_range.validate_async("42")
        async_time = time.time() - start
        print(f"  Async execution: {async_time:.4f}s")
        print(f"  JSON result: {'✓' if async_json_result.is_valid else '✗'}")
        print(f"  Range result: {'✓' if async_range_result.is_valid else '✗'}")

        print("\\n3. Testing concurrent validation with adapters...")
        start = time.time()

        # Run both validations concurrently
        results = await asyncio.gather(async_json.validate_async(test_data), async_range.validate_async("42"))

        concurrent_time = time.time() - start
        print(f"  Concurrent execution: {concurrent_time:.4f}s")
        print(f"  Both results: {'✓' if all(r.is_valid for r in results) else '✗'}")

        return sync_time, async_time, concurrent_time

    return asyncio.run(run_adapter_demo())


def demo_real_world_scenario():
    """Demonstrate a real-world async validation scenario."""
    print("\\n=== Real-World Scenario Demo ===")

    async def run_scenario():
        print("\\nScenario: Validating user registration data with multiple checks")
        print("- JSON schema validation")
        print("- Age range validation")
        print("- Email format validation (simulated)")
        print("- Username availability check (simulated)")
        print("- Password strength check (simulated)")

        # Create validators that simulate real-world checks
        schema = {
            "type": "object",
            "properties": {
                "username": {"type": "string", "minLength": 3},
                "email": {"type": "string", "format": "email"},
                "age": {"type": "integer", "minimum": 13, "maximum": 120},
                "password": {"type": "string", "minLength": 8},
            },
            "required": ["username", "email", "age", "password"],
        }

        # Simulate external service calls with delays
        async def check_username_availability(output: str) -> bool:
            await asyncio.sleep(0.3)  # Database query simulation
            data = json.loads(output)
            username = data.get("username", "")
            # Simulate some usernames being taken
            taken_usernames = ["admin", "user", "test"]
            return username.lower() not in taken_usernames

        async def check_password_strength(output: str) -> bool:
            await asyncio.sleep(0.2)  # Security service call simulation
            data = json.loads(output)
            password = data.get("password", "")
            # Simple strength check
            has_digit = any(c.isdigit() for c in password)
            has_upper = any(c.isupper() for c in password)
            has_lower = any(c.islower() for c in password)
            return all([has_digit, has_upper, has_lower])

        async def validate_email_domain(output: str) -> bool:
            await asyncio.sleep(0.4)  # DNS/email service check simulation
            data = json.loads(output)
            email = data.get("email", "")
            # Simulate domain validation
            valid_domains = ["gmail.com", "yahoo.com", "outlook.com", "example.com"]
            domain = email.split("@")[1] if "@" in email else ""
            return domain in valid_domains

        # Create composite validator
        validators = [
            AsyncJSONSchemaValidator(schema),
            AsyncRangeValidator(min_value=13, max_value=120, value_type="integer"),
            AsyncFunctionValidator(check_username_availability, name="UsernameAvailability"),
            AsyncFunctionValidator(check_password_strength, name="PasswordStrength"),
            AsyncFunctionValidator(validate_email_domain, name="EmailDomainValidation"),
        ]

        composite = AsyncCompositeValidator(validators, operator="AND", concurrent=True)

        # Test data
        test_cases = [
            {"name": "Valid User", "data": {"username": "john_doe", "email": "john@gmail.com", "age": 25, "password": "SecurePass123"}},
            {"name": "Invalid User (taken username)", "data": {"username": "admin", "email": "admin@gmail.com", "age": 30, "password": "SecurePass123"}},
            {"name": "Invalid User (weak password)", "data": {"username": "jane_doe", "email": "jane@yahoo.com", "age": 28, "password": "password"}},
        ]

        print("\\nTesting registration validation scenarios...")

        total_time = 0
        for i, test_case in enumerate(test_cases, 1):
            print(f"\\n{i}. Testing: {test_case['name']}")

            json_data = json.dumps(test_case["data"])

            start = time.time()
            result = await composite.validate_async(json_data)
            elapsed = time.time() - start
            total_time += elapsed

            print(f"   Result: {'✓ Valid' if result.is_valid else '✗ Invalid'}")
            print(f"   Time: {elapsed:.2f}s")

            if not result.is_valid:
                print("   Errors:")
                for error in result.errors[:3]:  # Show first 3 errors
                    print(f"     - {error}")
                if len(result.errors) > 3:
                    print(f"     ... and {len(result.errors) - 3} more")

        print(f"\\nTotal validation time: {total_time:.2f}s")
        print(f"Average per validation: {total_time / len(test_cases):.2f}s")

        return total_time

    return asyncio.run(run_scenario())


def main():
    """Run all async validation demos."""
    print("Validated-LLM Async Validation Performance Demo")
    print("=" * 50)

    print("\\nThis demo showcases the performance benefits of async validation:")
    print("1. Concurrent validation of multiple validators")
    print("2. Batch processing capabilities")
    print("3. Non-blocking validation operations")
    print("4. Real-world scenario simulation")

    try:
        # Run demos
        basic_time = demo_basic_async_validation()
        seq_time, conc_time = demo_concurrent_vs_sequential()
        batch_time = demo_batch_processing()
        sync_time, async_time, concurrent_time = demo_sync_vs_async_adapters()
        scenario_time = demo_real_world_scenario()

        # Summary
        print("\\n" + "=" * 50)
        print("PERFORMANCE SUMMARY")
        print("=" * 50)
        print(f"Basic async validation: {basic_time:.3f}s")
        print(f"Sequential validation: {seq_time:.2f}s")
        print(f"Concurrent validation: {conc_time:.2f}s")
        print(f"Speedup ratio: {seq_time/conc_time:.1f}x")
        print(f"Batch processing: {batch_time:.2f}s")
        print(f"Real-world scenario: {scenario_time:.2f}s")

        print("\\nKey Benefits of Async Validation:")
        print("✓ Concurrent execution of multiple validators")
        print("✓ Non-blocking I/O operations")
        print("✓ Better resource utilization")
        print("✓ Improved throughput for batch operations")
        print("✓ Seamless integration with existing validators")

        print("\\nNext Steps:")
        print("1. Integrate AsyncValidationLoop into your applications")
        print("2. Convert I/O-bound validators to async implementations")
        print("3. Use batch processing for multiple validation requests")
        print("4. Monitor performance improvements in production")

    except Exception as e:
        print(f"\\nError during demo: {e}")
        print("Make sure all dependencies are installed and configured properly.")


if __name__ == "__main__":
    main()
