"""
Example: Custom Email Generation Task

This example shows how to create a custom task with your own prompt template
and validator. This task generates professional emails and validates them
for proper structure and tone.
"""

import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Type

# Add the src directory to Python path so we can import validated_llm
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from validated_llm.base_validator import BaseValidator, ValidationResult
from validated_llm.tasks.base_task import BaseTask


class EmailGenerationTask(BaseTask):
    """Custom task for generating professional emails."""

    @property
    def name(self) -> str:
        return "Professional Email Generation"

    @property
    def description(self) -> str:
        return "Generate professional emails with proper structure and tone"

    @property
    def prompt_template(self) -> str:
        return """
Generate a professional email based on the following requirements:

TO: {recipient}
SUBJECT: {subject}
PURPOSE: {purpose}
TONE: {tone}

EMAIL REQUIREMENTS:
- Include proper greeting (Dear/Hello + name)
- Clear, concise body paragraphs
- Professional closing (Best regards, Sincerely, etc.)
- Your signature line
- Use {tone} tone throughout
- Length: 50-200 words

OUTPUT FORMAT:
Subject: [subject line]
To: [recipient]

[Email body starting with greeting]

[Professional closing]
[Your name]

Your response:"""

    @property
    def validator_class(self) -> Type[BaseValidator]:
        return EmailValidator


class EmailValidator(BaseValidator):
    """Validates generated emails for professional structure and content."""

    def __init__(self, min_words: int = 50, max_words: int = 200, required_tone: Optional[str] = None):
        """
        Initialize the email validator.

        Args:
            min_words: Minimum word count for email body
            max_words: Maximum word count for email body
            required_tone: Expected tone (formal, friendly, urgent, etc.)
        """
        super().__init__(name="email_validator", description=f"Validates professional emails ({min_words}-{max_words} words)")
        self.min_words = min_words
        self.max_words = max_words
        self.required_tone = required_tone

    def validate(self, content: str, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """Validate the generated email."""
        errors = []
        warnings = []

        lines = content.strip().split("\n")

        # Check for required email components
        if not self._has_subject_line(lines):
            errors.append("Missing 'Subject:' line")

        if not self._has_recipient_line(lines):
            errors.append("Missing 'To:' line")

        if not self._has_greeting(content):
            errors.append("Missing proper greeting (Dear/Hello + name)")

        if not self._has_professional_closing(content):
            errors.append("Missing professional closing (Best regards, Sincerely, etc.)")

        # Validate word count
        word_count = len(content.split())
        if word_count < self.min_words:
            errors.append(f"Email too short: {word_count} words (minimum: {self.min_words})")
        elif word_count > self.max_words:
            warnings.append(f"Email might be too long: {word_count} words (recommended max: {self.max_words})")

        # Check for tone appropriateness (basic checks)
        if self.required_tone:
            tone_issues = self._check_tone(content, self.required_tone)
            warnings.extend(tone_issues)

        # Check for common email issues
        if content.count("!") > 3:
            warnings.append("Excessive exclamation marks may appear unprofessional")

        if any(word.isupper() and len(word) > 3 for word in content.split()):
            warnings.append("Avoid using ALL CAPS words in professional emails")

        return ValidationResult(is_valid=len(errors) == 0, errors=errors, warnings=warnings, metadata={"word_count": word_count})

    def _has_subject_line(self, lines: List[str]) -> bool:
        """Check if email has a subject line."""
        return any(line.strip().lower().startswith("subject:") for line in lines)

    def _has_recipient_line(self, lines: List[str]) -> bool:
        """Check if email has a recipient line."""
        return any(line.strip().lower().startswith("to:") for line in lines)

    def _has_greeting(self, content: str) -> bool:
        """Check for proper greeting."""
        greetings = ["dear", "hello", "hi", "good morning", "good afternoon"]
        content_lower = content.lower()
        return any(greeting in content_lower for greeting in greetings)

    def _has_professional_closing(self, content: str) -> bool:
        """Check for professional closing."""
        closings = ["best regards", "sincerely", "kind regards", "thank you", "best", "regards", "yours truly", "respectfully"]
        content_lower = content.lower()
        return any(closing in content_lower for closing in closings)

    def _check_tone(self, content: str, required_tone: str) -> List[str]:
        """Basic tone checking - this could be enhanced with ML models."""
        warnings = []
        content_lower = content.lower()

        if required_tone.lower() == "formal":
            informal_words = ["hey", "yeah", "gonna", "wanna", "awesome", "cool"]
            found_informal = [word for word in informal_words if word in content_lower]
            if found_informal:
                warnings.append(f"Informal words detected for formal tone: {', '.join(found_informal)}")

        elif required_tone.lower() == "friendly":
            if content.count(".") > content.count("!") * 3:
                warnings.append("Consider adding more enthusiasm for friendly tone")

        elif required_tone.lower() == "urgent":
            if "urgent" not in content_lower and "asap" not in content_lower:
                warnings.append("Consider adding urgency indicators for urgent tone")

        return warnings


# Example usage function
def example_usage() -> None:
    """
    Example of how to use the custom EmailGenerationTask.

    This would typically be called from user code like:

    from validated_llm.validation_loop import ValidationLoop
    from examples.custom_email_task import EmailGenerationTask

    task = EmailGenerationTask()
    validator = task.create_validator(required_tone="formal")
    loop = ValidationLoop(default_max_retries=3)

    result = loop.execute(
        prompt_template=task.prompt_template,
        validator=validator,
        input_data={
            "recipient": "john.doe@company.com",
            "subject": "Project Update Meeting",
            "purpose": "Schedule a meeting to discuss project status",
            "tone": "professional"
        }
    )
    """
    from validated_llm.validation_loop import ValidationLoop

    # Create the custom task
    task = EmailGenerationTask()

    # Create validator with custom settings
    validator = task.create_validator(required_tone="formal")

    # Create validation loop
    loop = ValidationLoop(default_max_retries=3)

    # Prepare input data
    input_data = {"recipient": "sarah.johnson@company.com", "subject": "Quarterly Report Review", "purpose": "Request feedback on Q3 financial report", "tone": "formal"}

    # Execute with custom parameters
    try:
        result = loop.execute(prompt_template=task.prompt_template, validator=validator, input_data=input_data)

        if result["success"]:
            print("Generated email:")
            print("=" * 50)
            print(result["output"])
            print("=" * 50)
            print(f"✅ Success after {result['attempts']} attempt(s)")
            print(f"⏱️  Execution time: {result['execution_time']:.2f}s")
        else:
            print("❌ Failed to generate valid email:")
            if result["validation_result"]:
                print("Validation errors:")
                for error in result["validation_result"].errors:
                    print(f"  - {error}")

    except Exception as e:
        print(f"Error during email generation: {e}")


if __name__ == "__main__":
    example_usage()
