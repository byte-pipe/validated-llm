# Validated-LLM Best Practices Guide

This guide provides proven patterns and recommendations for using the validated-llm framework effectively in production environments.

## Table of Contents

1. [Validator Selection Strategy](#validator-selection-strategy)
2. [Task Design Patterns](#task-design-patterns)
3. [Error Handling Strategy](#error-handling-strategy)
4. [Performance Best Practices](#performance-best-practices)
5. [Security Considerations](#security-considerations)
6. [Testing Strategy](#testing-strategy)
7. [Production Deployment](#production-deployment)
8. [Monitoring and Observability](#monitoring-and-observability)

## Validator Selection Strategy

### 1. Choose the Right Validator for Your Use Case

#### Content Type Based Selection

| Content Type     | Primary Validator                        | Secondary Validator               | Use Case                     |
| ---------------- | ---------------------------------------- | --------------------------------- | ---------------------------- |
| Structured Data  | `JSONSchemaValidator`                    | `XMLValidator`                    | API responses, configuration |
| User Input       | `EmailValidator`, `PhoneNumberValidator` | `RegexValidator`                  | Forms, contact info          |
| Generated Code   | `SyntaxValidator`                        | `StyleValidator`, `TestValidator` | Code generation              |
| Natural Language | `MarkdownValidator`                      | `RangeValidator`                  | Documentation, articles      |
| Configuration    | `YAMLValidator`, `ConfigValidator`       | `JSONSchemaValidator`             | App settings                 |
| Database         | `SQLValidator`                           | `RegexValidator`                  | Query generation             |

#### Validation Strictness Levels

```python
# Level 1: Basic Format Validation
email_basic = EmailValidator(
    check_deliverability=False,
    allow_smtputf8=True
)

# Level 2: Enhanced Validation
email_enhanced = EmailValidator(
    check_deliverability=True,
    require_mx_record=True,
    allowed_domains=["company.com", "partner.org"]
)

# Level 3: Strict Production Validation
email_strict = EmailValidator(
    check_deliverability=True,
    require_mx_record=True,
    allowed_domains=["company.com"],
    block_disposable=True,
    require_tld=True
)
```

### 2. Validator Composition Patterns

#### Sequential Validation (All Must Pass)

```python
from validated_llm.validators.composite import CompositeValidator

# All validators must pass
strict_article = CompositeValidator(
    name="article_validator",
    validators=[
        MarkdownValidator(name="format"),
        RangeValidator(name="length", min_value=800, max_value=1200, unit="words"),
        RegexValidator(name="headings", pattern=r"^#{1,3}s+", flags="m")
    ],
    combination_logic="AND"
)
```

#### Alternative Validation (Any Can Pass)

```python
# Accept multiple formats
flexible_data = CompositeValidator(
    name="data_validator",
    validators=[
        JSONSchemaValidator(name="json", schema=json_schema),
        XMLValidator(name="xml", xsd_path="schema.xsd"),
        YAMLValidator(name="yaml")
    ],
    combination_logic="OR"
)
```

#### Weighted Validation (Quality Scoring)

```python
# Custom scoring logic
class QualityScoredValidator(BaseValidator):
    def init(self):
        super().init("quality_scorer", "Quality-based validation")
        self.validators = [
            (SyntaxValidator(), 0.4),      # 40% weight
            (StyleValidator(), 0.3),       # 30% weight
            (TestValidator(), 0.3)         # 30% weight
        ]

    def validate(self, output: str, context=None) -> ValidationResult:
        total_score = 0.0
        errors = []

        for validator, weight in self.validators:
            result = validator.validate(output, context)
            if result.score is not None:
                total_score += result.score * weight
            if not result.is_valid:
                errors.extend(result.errors)

        return ValidationResult(
            is_valid=total_score >= 0.7,  # 70% threshold
            score=total_score,
            errors=errors,
            metadata={"quality_score": total_score}
        )
```

### 3. Progressive Validation Strategy

Start with loose validation and tighten based on requirements:

```python
class ProgressiveEmailValidator:
    def init(self, stage: str = "development"):
        self.stage = stage

    def get_validator(self):
        if self.stage == "development":
            return EmailValidator(check_deliverability=False)
        elif self.stage == "staging":
            return EmailValidator(
                check_deliverability=True,
                require_mx_record=False
            )
        else:  # production
            return EmailValidator(
                check_deliverability=True,
                require_mx_record=True,
                block_disposable=True
            )

# Usage
validator = ProgressiveEmailValidator(stage=os.getenv("STAGE", "development"))
email_validator = validator.get_validator()
```

## Task Design Patterns

### 1. Single Responsibility Principle

Design tasks that do one thing well:

```python
# ❌ Bad: Mixed responsibilities
class UserEmailAndProfileTask(BaseTask):
    # Generates both email content AND user profile data
    pass

# ✅ Good: Focused responsibility
class UserProfileTask(BaseTask):
    # Only generates user profile data
    pass

class WelcomeEmailTask(BaseTask):
    # Only generates welcome email content
    pass
```

### 2. Configurable Validation Levels

```python
class ConfigurableDocumentationTask(BaseTask):
    def init(self, validation_level: str = "standard", **kwargs):
        self.validation_level = validation_level

        if validation_level == "basic":
            validator = MarkdownValidator()
        elif validation_level == "standard":
            validator = CompositeValidator(
                validators=[
                    MarkdownValidator(),
                    RangeValidator(min_value=200, max_value=2000, unit="words")
                ],
                combination_logic="AND"
            )
        elif validation_level == "strict":
            validator = CompositeValidator(
                validators=[
                    MarkdownValidator(),
                    RangeValidator(min_value=500, max_value=1500, unit="words"),
                    DocumentationValidator(
                        required_sections=["overview", "usage", "examples"]
                    )
                ],
                combination_logic="AND"
            )

        super().init(
            name=f"documentation_task_{validation_level}",
            validator=validator,
            **kwargs
        )
```

### 3. Context-Aware Validation

```python
class ContextAwareTask(BaseTask):
    def prepare_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        # Adjust validation based on context
        audience = data.get("audience", "general")

        if audience == "technical":
            # More strict validation for technical content
            data["validation_config"] = {
                "require_code_examples": True,
                "min_technical_depth": 0.8
            }
        elif audience == "beginner":
            # More lenient, focus on clarity
            data["validation_config"] = {
                "require_definitions": True,
                "max_complexity_score": 0.6
            }

        return data
```

## Error Handling Strategy

### 1. Graceful Degradation

```python
class RobustValidationLoop:
    def init(self, primary_task, fallback_task=None):
        self.primary_task = primary_task
        self.fallback_task = fallback_task

    def execute(self, data):
        try:
            # Try primary task with strict validation
            result = ValidationLoop(self.primary_task, max_retries=3).execute(data)
            if result.success:
                return result
        except Exception as e:
            logger.warning(f"Primary task failed: {e}")

        if self.fallback_task:
            # Fall back to simpler validation
            logger.info("Falling back to simpler validation")
            return ValidationLoop(self.fallback_task, max_retries=1).execute(data)

        raise ValidationError("All validation strategies failed")
```

### 2. Error Classification and Handling

```python
class ErrorHandler:
    @staticmethod
    def classify_error(validation_result: ValidationResult) -> str:
        errors = validation_result.errors

        if any("JSON" in error for error in errors):
            return "format_error"
        elif any("required" in error.lower() for error in errors):
            return "missing_field"
        elif any("length" in error.lower() for error in errors):
            return "length_error"
        else:
            return "unknown_error"

    @staticmethod
    def get_retry_strategy(error_type: str) -> dict:
        strategies = {
            "format_error": {"max_retries": 2, "delay": 0.5},
            "missing_field": {"max_retries": 3, "delay": 1.0},
            "length_error": {"max_retries": 1, "delay": 0.1},
            "unknown_error": {"max_retries": 1, "delay": 0.5}
        }
        return strategies.get(error_type, {"max_retries": 1, "delay": 0.5})
```

### 3. Custom Error Messages for LLM Feedback

```python
class LLMFriendlyErrorFormatter:
    @staticmethod
    def format_errors(validation_result: ValidationResult) -> str:
        if validation_result.is_valid:
            return "Perfect! Your output meets all requirements."

        formatted_errors = []
        for error in validation_result.errors:
            if "JSON" in error:
                formatted_errors.append(
                    "❌ JSON Format: " + error +
                    "n💡 Tip: Check for proper quotes, commas, and brackets."
                )
            elif "required" in error.lower():
                formatted_errors.append(
                    "❌ Missing Field: " + error +
                    "n💡 Tip: Make sure all required fields are included."
                )
            else:
                formatted_errors.append("❌ " + error)

        return "nn".join(formatted_errors)
```

## Performance Best Practices

### 1. Validator Caching and Reuse

```python
from functools import lru_cache
import threading

class ValidatorPool:
    def init(self):
        self._pools = {}
        self._lock = threading.Lock()

    def get_validator(self, validator_type: str, **config):
        config_key = str(sorted(config.items()))
        pool_key = f"{validator_type}:{config_key}"

        with self._lock:
            if pool_key not in self._pools:
                if validator_type == "email":
                    self._pools[pool_key] = EmailValidator(**config)
                elif validator_type == "json_schema":
                    self._pools[pool_key] = JSONSchemaValidator(**config)
                # ... etc

            return self._pools[pool_key]

# Global validator pool
validator_pool = ValidatorPool()

# Usage
email_validator = validator_pool.get_validator(
    "email",
    check_deliverability=True,
    require_mx_record=True
)
```

### 2. Async Validation for High Throughput

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

class AsyncValidator:
    def init(self, validator, max_workers=4):
        self.validator = validator
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

    async def validate_async(self, output: str) -> ValidationResult:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor,
            self.validator.validate,
            output
        )

    async def validate_batch(self, outputs: List[str]) -> List[ValidationResult]:
        tasks = [self.validate_async(output) for output in outputs]
        return await asyncio.gather(*tasks)

# Usage
async def process_batch():
    validator = AsyncValidator(EmailValidator())
    emails = ["user1@example.com", "user2@example.com", ...]
    results = await validator.validate_batch(emails)
    return results
```

### 3. Validation Result Caching

```python
import hashlib
from functools import wraps

def cache_validation(expiry_seconds=300):
    """Cache validation results to avoid recomputation"""
    cache = {}

    def decorator(validate_func):
        @wraps(validate_func)
        def wrapper(self, output: str, context=None):
            # Create cache key
            content_hash = hashlib.md5(output.encode()).hexdigest()
            cache_key = f"{self.class.name}:{content_hash}"

            # Check cache
            if cache_key in cache:
                cached_result, timestamp = cache[cache_key]
                if time.time() - timestamp < expiry_seconds:
                    return cached_result

            # Compute and cache
            result = validate_func(self, output, context)
            cache[cache_key] = (result, time.time())

            return result
        return wrapper
    return decorator

# Usage in custom validator
class CachedEmailValidator(EmailValidator):
    @cache_validation(expiry_seconds=600)  # 10 minute cache
    def validate(self, output: str, context=None):
        return super().validate(output, context)
```

## Security Considerations

### 1. Input Sanitization

```python
class SecureValidator(BaseValidator):
    def init(self, name: str, description: str):
        super().init(name, description)
        self.max_input_size = 1024 * 1024  # 1MB limit

    def validate(self, output: str, context=None) -> ValidationResult:
        # Size check
        if len(output) > self.max_input_size:
            return ValidationResult(
                is_valid=False,
                errors=[f"Input too large: {len(output)} bytes (max: {self.max_input_size})"]
            )

        # Basic sanitization
        if self._contains_potential_injection(output):
            return ValidationResult(
                is_valid=False,
                errors=["Input contains potentially malicious content"]
            )

        return self._do_validation(output, context)

    def _contains_potential_injection(self, text: str) -> bool:
        dangerous_patterns = [
            r'<scriptb[^<]*(?:(?!</script>)<[^<]*)*</script>',
            r'javascript:',
            r'vbscript:',
            r'onloads*=',
            r'onerrors*=',
        ]

        for pattern in dangerous_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
```

### 2. Secure Configuration Management

```python
# .validated-llm.yml
validation:
  max_retries: 3
  timeout: 30
  security:
    max_input_size: 1048576  # 1MB
    allow_html: false
    sanitize_input: true

validators:
  sql:
    allowed_operations: ["SELECT", "INSERT", "UPDATE"]
    blocked_keywords: ["DROP", "DELETE", "TRUNCATE", "ALTER"]

  regex:
    max_pattern_length: 1000
    timeout: 5
```

### 3. Audit Logging

```python
import logging
from datetime import datetime

class AuditLogger:
    def init(self):
        self.logger = logging.getLogger("validation_audit")
        handler = logging.FileHandler("validation_audit.log")
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def log_validation(self, validator_name: str, input_hash: str,
                      is_valid: bool, errors: List[str] = None):
        self.logger.info(
            f"Validation - Validator: {validator_name}, "
            f"Input Hash: {input_hash}, Valid: {is_valid}, "
            f"Errors: {len(errors or [])}"
        )

    def log_security_event(self, event_type: str, details: dict):
        self.logger.warning(
            f"Security Event - Type: {event_type}, Details: {details}"
        )

# Global audit logger
audit = AuditLogger()
```

## Testing Strategy

### 1. Validator Unit Testing

```python
import pytest
from validated_llm.validators.email import EmailValidator

class TestEmailValidator:
    @pytest.fixture
    def validator(self):
        return EmailValidator()

    @pytest.mark.parametrize("email,expected", [
        ("valid@example.com", True),
        ("invalid.email", False),
        ("test@", False),
        ("@example.com", False),
    ])
    def test_email_validation(self, validator, email, expected):
        result = validator.validate(email)
        assert result.is_valid == expected

    def test_validation_errors(self, validator):
        result = validator.validate("invalid.email")
        assert not result.is_valid
        assert len(result.errors) > 0
        assert "email" in result.errors[0].lower()

    def test_edge_cases(self, validator):
        # Empty string
        result = validator.validate("")
        assert not result.is_valid

        # Very long email
        long_email = "a" * 300 + "@example.com"
        result = validator.validate(long_email)
        # Behavior depends on validator configuration
```

### 2. Integration Testing

```python
class TestValidationLoop:
    def test_successful_validation(self):
        task = PersonJSONTask()
        loop = ValidationLoop(task, max_retries=3)

        data = {"name": "Alice", "age": 30}
        result = loop.execute(data)

        assert result.success
        assert result.validated_output
        assert result.attempts[0].validation_result.is_valid

    def test_retry_behavior(self):
        # Use a task that's likely to fail initially
        task = ComplexJSONTask()
        loop = ValidationLoop(task, max_retries=3)

        data = {"complex_requirement": "generate nested data"}
        result = loop.execute(data)

        # Should have made multiple attempts
        assert len(result.attempts) > 1

        if result.success:
            assert result.validated_output
        else:
            # Examine failure patterns
            for attempt in result.attempts:
                assert attempt.validation_result is not None
```

### 3. Performance Testing

```python
import time
import statistics

class TestPerformance:
    def test_validator_performance(self):
        validator = EmailValidator()
        emails = ["test@example.com"] * 1000

        times = []
        for email in emails:
            start = time.time()
            validator.validate(email)
            times.append(time.time() - start)

        avg_time = statistics.mean(times)
        assert avg_time < 0.001  # Less than 1ms per validation

        p95_time = statistics.quantiles(times, n=20)[18]  # 95th percentile
        assert p95_time < 0.005  # 95th percentile under 5ms

    def test_memory_usage(self):
        import psutil
        import os

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss

        # Create many validators
        validators = [EmailValidator() for _ in range(1000)]

        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory

        # Should not use excessive memory
        assert memory_increase < 100 * 1024 * 1024  # Less than 100MB
```

## Production Deployment

### 1. Environment Configuration

```python
# config/production.yml
validation:
  max_retries: 2  # Fewer retries in production
  timeout: 15     # Shorter timeout

  security:
    max_input_size: 1048576
    audit_logging: true

  performance:
    cache_results: true
    cache_ttl: 300
    max_concurrent_validations: 10

llm:
  model: "gemma3:27b"
  temperature: 0.1  # More deterministic in production
  max_tokens: 2048

monitoring:
  enable_metrics: true
  log_level: "INFO"
  alert_on_failure_rate: 0.1  # Alert if >10% failures
```

### 2. Health Checks

```python
from typing import Dict, Any

class HealthChecker:
    def init(self, validators: List[BaseValidator]):
        self.validators = validators

    def check_health(self) -> Dict[str, Any]:
        health_status = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "validators": {}
        }

        for validator in self.validators:
            try:
                # Quick validation test
                test_result = validator.validate("test")
                health_status["validators"][validator.name] = {
                    "status": "healthy",
                    "response_time": getattr(test_result, "response_time", None)
                }
            except Exception as e:
                health_status["status"] = "degraded"
                health_status["validators"][validator.name] = {
                    "status": "unhealthy",
                    "error": str(e)
                }

        return health_status

# Usage in Flask/FastAPI
@app.route('/health')
def health_check():
    checker = HealthChecker([EmailValidator(), JSONSchemaValidator()])
    return jsonify(checker.check_health())
```

### 3. Circuit Breaker Pattern

```python
import time
from enum import Enum

class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class CircuitBreaker:
    def init(self, failure_threshold=5, timeout=60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED

    def call(self, func, *args, **kwargs):
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time > self.timeout:
                self.state = CircuitState.HALF_OPEN
            else:
                raise Exception("Circuit breaker is OPEN")

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e

    def _on_success(self):
        self.failure_count = 0
        self.state = CircuitState.CLOSED

    def _on_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN

# Usage
class ResilientValidator:
    def init(self, validator):
        self.validator = validator
        self.circuit_breaker = CircuitBreaker()

    def validate(self, output: str, context=None):
        return self.circuit_breaker.call(
            self.validator.validate,
            output,
            context
        )
```

## Monitoring and Observability

### 1. Metrics Collection

```python
import time
from collections import defaultdict, Counter

class ValidationMetrics:
    def init(self):
        self.validation_counts = Counter()
        self.validation_times = defaultdict(list)
        self.error_counts = Counter()
        self.success_rates = defaultdict(list)

    def record_validation(self, validator_name: str, duration: float,
                         success: bool, error_type: str = None):
        self.validation_counts[validator_name] += 1
        self.validation_times[validator_name].append(duration)

        if success:
            self.success_rates[validator_name].append(1)
        else:
            self.success_rates[validator_name].append(0)
            if error_type:
                self.error_counts[f"{validator_name}:{error_type}"] += 1

    def get_stats(self) -> Dict[str, Any]:
        stats = {}

        for validator_name in self.validation_counts:
            times = self.validation_times[validator_name]
            successes = self.success_rates[validator_name]

            stats[validator_name] = {
                "total_validations": self.validation_counts[validator_name],
                "avg_duration": sum(times) / len(times),
                "success_rate": sum(successes) / len(successes),
                "p95_duration": sorted(times)[int(len(times) * 0.95)]
            }

        return stats

# Global metrics collector
metrics = ValidationMetrics()
```

### 2. Structured Logging

```python
import logging
import json

class StructuredLogger:
    def init(self, name: str):
        self.logger = logging.getLogger(name)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def log_validation(self, event: str, validator_name: str,
                      duration: float, success: bool, **kwargs):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "event": event,
            "validator": validator_name,
            "duration_ms": duration * 1000,
            "success": success,
            **kwargs
        }

        self.logger.info(json.dumps(log_data))

# Usage
logger = StructuredLogger("validated_llm")

# In validator
start_time = time.time()
result = validator.validate(output)
duration = time.time() - start_time

logger.log_validation(
    event="validation_completed",
    validator_name=validator.name,
    duration=duration,
    success=result.is_valid,
    error_count=len(result.errors),
    input_length=len(output)
)
```

### 3. Alerting

```python
class AlertManager:
    def init(self, webhook_url: str = None):
        self.webhook_url = webhook_url
        self.thresholds = {
            "error_rate": 0.1,      # 10% error rate
            "avg_duration": 5.0,    # 5 second average
            "p95_duration": 10.0    # 10 second 95th percentile
        }

    def check_and_alert(self, stats: Dict[str, Any]):
        for validator_name, validator_stats in stats.items():
            alerts = []

            if validator_stats["success_rate"] < (1 - self.thresholds["error_rate"]):
                alerts.append(f"High error rate: {validator_stats['success_rate']:.2%}")

            if validator_stats["avg_duration"] > self.thresholds["avg_duration"]:
                alerts.append(f"High average duration: {validator_stats['avg_duration']:.2f}s")

            if validator_stats["p95_duration"] > self.thresholds["p95_duration"]:
                alerts.append(f"High P95 duration: {validator_stats['p95_duration']:.2f}s")

            if alerts:
                self._send_alert(validator_name, alerts)

    def _send_alert(self, validator_name: str, alerts: List[str]):
        message = f"🚨 Validator Alert: {validator_name}n" + "n".join(alerts)

        if self.webhook_url:
            # Send to Slack/Teams/etc
            import requests
            requests.post(self.webhook_url, json={"text": message})
        else:
            # Log alert
            logging.error(f"ALERT: {message}")
```

---

This best practices guide provides a foundation for using validated-llm effectively in production environments. Always adapt these patterns to your specific use case and requirements.
