#!/usr/bin/env python3
"""
Example plugin: Credit Card Number Validator

This demonstrates how to create a custom validator plugin for validated-llm.
"""

import re
from typing import Any, Dict, Optional

from validated_llm.base_validator import BaseValidator, ValidationResult


class CreditCardValidator(BaseValidator):
    """
    Validates credit card numbers using the Luhn algorithm.

    Supports validation of major credit card formats including:
    - Visa (4xxx)
    - MasterCard (5xxx)
    - American Express (3xxx)
    - Discover (6xxx)
    """

    def __init__(self, allow_spaces: bool = True, require_type: Optional[str] = None):
        """
        Initialize the credit card validator.

        Args:
            allow_spaces: Whether to allow spaces in the card number
            require_type: Require specific card type ('visa', 'mastercard', 'amex', 'discover')
        """
        super().__init__(name="credit_card_validator", description=f"Validates credit card numbers using Luhn algorithm")
        self.allow_spaces = allow_spaces
        self.require_type = require_type

    def validate(self, output: str, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """
        Validate credit card number in the output.

        Args:
            output: The LLM output to validate
            context: Optional context information

        Returns:
            ValidationResult with validation status and feedback
        """
        result = ValidationResult(is_valid=True, errors=[])

        # Extract potential credit card numbers
        card_numbers = self._extract_card_numbers(output)

        if not card_numbers:
            result.add_error("No credit card numbers found in output")
            return result

        for card_number in card_numbers:
            # Clean the card number
            clean_number = self._clean_card_number(card_number)

            # Validate format
            if not self._is_valid_format(clean_number):
                result.add_error(f"Invalid credit card format: {card_number}")
                continue

            # Validate using Luhn algorithm
            if not self._luhn_check(clean_number):
                result.add_error(f"Credit card number fails Luhn check: {card_number}")
                continue

            # Check card type if required
            if self.require_type:
                card_type = self._detect_card_type(clean_number)
                if card_type != self.require_type:
                    result.add_error(f"Expected {self.require_type} card, got {card_type}: {card_number}")
                    continue

            # Add metadata about valid card
            card_type = self._detect_card_type(clean_number)
            if result.metadata is None:
                result.metadata = {}
            result.metadata[f"card_{card_number}"] = {"type": card_type, "masked": self._mask_card_number(clean_number)}

        return result

    def _extract_card_numbers(self, text: str) -> list[str]:
        """Extract potential credit card numbers from text."""
        # Pattern for credit card numbers (with optional spaces/dashes)
        pattern = r"\\b(?:\\d{4}[\\s-]?){3}\\d{4}\\b"
        return re.findall(pattern, text)

    def _clean_card_number(self, card_number: str) -> str:
        """Remove spaces and dashes from card number."""
        return re.sub(r"[\\s-]", "", card_number)

    def _is_valid_format(self, card_number: str) -> bool:
        """Check if card number has valid format."""
        # Must be 13-19 digits
        if not re.match(r"^\\d{13,19}$", card_number):
            return False
        return True

    def _luhn_check(self, card_number: str) -> bool:
        """Validate card number using Luhn algorithm."""

        def luhn_checksum(card_num: str) -> int:
            def digits_of(n: str) -> list[int]:
                return [int(d) for d in n]

            digits = digits_of(card_num)
            odd_digits = digits[-1::-2]
            even_digits = digits[-2::-2]
            checksum = sum(odd_digits)
            for d in even_digits:
                checksum += sum(digits_of(str(d * 2)))
            return checksum % 10

        return luhn_checksum(card_number) == 0

    def _detect_card_type(self, card_number: str) -> str:
        """Detect the type of credit card."""
        if card_number.startswith("4"):
            return "visa"
        elif card_number.startswith("5") or card_number.startswith("2"):
            return "mastercard"
        elif card_number.startswith("3"):
            return "amex"
        elif card_number.startswith("6"):
            return "discover"
        else:
            return "unknown"

    def _mask_card_number(self, card_number: str) -> str:
        """Mask card number for security."""
        if len(card_number) < 4:
            return "*" * len(card_number)
        return "*" * (len(card_number) - 4) + card_number[-4:]


# Plugin metadata - required for plugin discovery
PLUGIN_INFO = {
    "name": "credit_card_validator",
    "version": "1.0.0",
    "description": "Validates credit card numbers using the Luhn algorithm",
    "author": "validated-llm team",
    "validator_class": CreditCardValidator,
    "dependencies": [],
    "tags": ["finance", "validation", "credit-card", "luhn"],
}


if __name__ == "__main__":
    # Example usage
    validator = CreditCardValidator()

    # Test with valid Visa card (test number)
    test_output = "The card number is 4111 1111 1111 1111"
    result = validator.validate(test_output)

    print("Validation Result:")
    print(f"Valid: {result.is_valid}")
    print(f"Errors: {result.errors}")
    print(f"Metadata: {result.metadata}")
