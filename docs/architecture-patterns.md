# Architecture Patterns in validated-llm

This document analyzes the software engineering patterns implemented in the validated-llm library, identifying how it maps to established architectural patterns.

## Core Architecture Overview

The `validated-llm` library acts as a validation and feedback layer on top of the core LLM functionality provided by the external `chatbot` library. The library implements a sophisticated "Self-Correcting AI Proxy" pattern that treats LLM calls as potentially failing operations requiring validation, retry logic, and feedback mechanisms.

```
Client → ValidationLoop (middleware) → ChatBot → LLM
Client ← ValidationLoop (validation) ← ChatBot ← LLM
```

## Primary Design Patterns

### 1. Middleware/Interceptor Pattern

**Implementation**: `ValidationLoop` class
**Purpose**: Sits between client and LLM service, intercepting requests/responses to add cross-cutting concerns

The `ValidationLoop` acts as middleware that:
- Intercepts prompts before sending to LLM
- Adds validation instructions to system prompts
- Validates responses after receiving from LLM
- Provides feedback for correction on validation failures

```python
# ValidationLoop orchestrates the middleware pipeline
def execute(self, prompt_template, validator, input_data, ...):
    # 1. Prepare prompt with validation instructions
    # 2. Send to ChatBot/LLM
    # 3. Validate response
    # 4. Provide feedback if invalid
    # 5. Retry if needed
```

### 2. Strategy Pattern

**Implementation**: `BaseValidator` hierarchy
**Purpose**: Interchangeable validation algorithms

Different validators (JSONValidator, XMLValidator, EmailValidator, etc.) are pluggable strategies that can be swapped without changing the core validation loop:

```python
@property
@abstractmethod
def validator_class(self) -> Type[BaseValidator]:
    """The validator class for this task."""
```

### 3. Template Method Pattern

**Implementation**: `BaseTask` abstract class
**Purpose**: Define workflow skeleton while allowing customization

The `BaseTask` defines the template structure where subclasses implement specific parts:

```python
class BaseTask(ABC):
    @property
    @abstractmethod
    def prompt_template(self) -> str:
        """The prompt template for this task."""

    @property
    @abstractmethod
    def validator_class(self) -> Type[BaseValidator]:
        """The validator class for this task."""
```

### 4. Proxy Pattern

**Implementation**: `ValidationLoop` acting as proxy to `ChatBot`
**Purpose**: Add validation behavior before/after LLM calls

The ValidationLoop proxies calls to the ChatBot while adding:
- Input preprocessing
- Output validation
- Error handling
- Retry logic

### 5. Circuit Breaker Pattern

**Implementation**: Retry mechanism with `max_retries`
**Purpose**: Prevent infinite loops and fail fast

```python
# Prevents infinite retry loops
max_retries: Optional[int] = None
```

The system stops attempting after a threshold, protecting against:
- Infinite validation failures
- Resource exhaustion
- Cascading failures

### 6. Composite Pattern

**Implementation**: Task system combining prompts + validators
**Purpose**: Compose complex validation workflows

Tasks combine multiple concerns into cohesive units:
- Prompt templates
- Validation logic
- Error handling
- Retry configuration

### 7. Observer/Feedback Loop Pattern

**Implementation**: ValidationResult feedback to LLM
**Purpose**: Self-correction through error feedback

When validation fails, the system:
1. Captures validation errors
2. Formats feedback messages
3. Sends feedback back to LLM
4. Requests corrected output

This creates a feedback loop where the AI system learns from its validation failures.

## Advanced Architectural Concepts

### Self-Correcting AI Proxy

This is the overarching pattern that combines multiple design patterns into a cohesive system for reliable AI computing:

**Components**:
- **Proxy Layer**: ValidationLoop intercepts LLM calls
- **Validation Engine**: Pluggable validators check outputs
- **Feedback System**: Error information sent back for correction
- **Circuit Breaker**: Prevents infinite retry loops
- **Strategy Selection**: Different validators for different output types

**Benefits**:
- Transforms unreliable LLM outputs into reliable, validated results
- Provides automatic error correction through feedback
- Enables complex validation workflows
- Maintains separation of concerns between LLM communication and validation

### Separation of Concerns

The architecture cleanly separates:

1. **LLM Communication** (`chatbot` library)
2. **Validation Logic** (`BaseValidator` implementations)
3. **Workflow Orchestration** (`ValidationLoop`)
4. **Task Definition** (`BaseTask` implementations)
5. **Configuration Management** (Config system)

### Plugin Architecture

The validator system implements a plugin architecture where:
- New validators can be added without modifying core code
- Validators are discovered dynamically
- Custom validation logic can be injected

## Comparison to Established Patterns

### Similar to Web Framework Middleware

This pattern is similar to middleware in web frameworks (Express.js, Django, ASP.NET):
- Request/response interception
- Cross-cutting concerns (validation, logging, error handling)
- Composable pipeline architecture

### Circuit Breaker (Microservices Pattern)

The retry mechanism implements the Circuit Breaker pattern from microservices architecture:
- Fail fast after threshold
- Protect downstream services
- Graceful degradation

### Aspect-Oriented Programming (AOP)

The validation concerns are applied as "aspects" around the core LLM functionality:
- Validation as a cross-cutting concern
- Separation from business logic
- Declarative configuration

## Conclusion

The `validated-llm` library implements a sophisticated combination of established software engineering patterns to address the unique challenges of working with unreliable AI systems. The "Self-Correcting AI Proxy" pattern could serve as a template for building reliable systems around other AI services that produce potentially invalid outputs.

This architectural approach demonstrates how classical software engineering patterns can be adapted and combined to solve modern AI reliability challenges.
