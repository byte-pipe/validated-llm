#!/usr/bin/env python3
"""
Example plugin: Social Security Number Validator

This demonstrates a more complex validator plugin that checks for
PII (Personally Identifiable Information) and can optionally redact it.
"""

import re
from typing import Any, Dict, List, Optional

from validated_llm.base_validator import BaseValidator, ValidationResult


class SocialSecurityValidator(BaseValidator):
    """
    Validates and optionally redacts Social Security Numbers (SSNs).

    This validator can:
    - Detect SSN patterns in text
    - Validate SSN format
    - Check against known invalid SSN patterns
    - Optionally flag for redaction
    """

    def __init__(self, allow_ssn: bool = False, redact_found: bool = True, strict_format: bool = True):
        """
        Initialize the SSN validator.

        Args:
            allow_ssn: Whether SSNs are allowed in the output
            redact_found: Whether to provide redacted version
            strict_format: Whether to require strict XXX-XX-XXXX format
        """
        super().__init__(name="social_security_validator", description="Validates and detects Social Security Numbers for PII protection")
        self.allow_ssn = allow_ssn
        self.redact_found = redact_found
        self.strict_format = strict_format

        # Known invalid SSN patterns
        self.invalid_patterns = {"000", "666", "900", "999", "00", "0000"}  # Invalid area numbers  # Invalid group numbers  # Invalid serial numbers

    def validate(self, output: str, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """
        Validate output for SSN content.

        Args:
            output: The LLM output to validate
            context: Optional context information

        Returns:
            ValidationResult with validation status and feedback
        """
        result = ValidationResult(is_valid=True, errors=[])

        # Find potential SSNs
        ssns = self._find_ssns(output)

        if ssns:
            if not self.allow_ssn:
                result.add_error(f"Social Security Numbers detected but not allowed. " f"Found {len(ssns)} potential SSN(s).")

            # Validate each SSN
            valid_ssns = []
            invalid_ssns = []

            for ssn in ssns:
                if self._is_valid_ssn(ssn):
                    valid_ssns.append(ssn)
                else:
                    invalid_ssns.append(ssn)

            # Add warnings for invalid SSNs
            for invalid_ssn in invalid_ssns:
                result.add_warning(f"Invalid SSN format detected: {invalid_ssn}")

            # Add metadata
            if result.metadata is None:
                result.metadata = {}

            result.metadata["ssn_detection"] = {
                "total_found": len(ssns),
                "valid_ssns": len(valid_ssns),
                "invalid_ssns": len(invalid_ssns),
                "all_ssns_redacted": [self._redact_ssn(ssn) for ssn in ssns] if self.redact_found else [],
            }

            # Provide redacted version if requested
            if self.redact_found and ssns:
                redacted_output = self._redact_output(output, ssns)
                result.metadata["redacted_output"] = redacted_output

        return result

    def _find_ssns(self, text: str) -> List[str]:
        """Find potential SSNs in text."""
        patterns = [
            r"\\b\\d{3}-\\d{2}-\\d{4}\\b",  # XXX-XX-XXXX
            r"\\b\\d{3}\\s\\d{2}\\s\\d{4}\\b",  # XXX XX XXXX
        ]

        if not self.strict_format:
            patterns.append(r"\\b\\d{9}\\b")  # XXXXXXXXX

        ssns = []
        for pattern in patterns:
            matches = re.findall(pattern, text)
            ssns.extend(matches)

        return list(set(ssns))  # Remove duplicates

    def _is_valid_ssn(self, ssn: str) -> bool:
        """Check if SSN has valid format and isn't a known invalid pattern."""
        # Clean the SSN
        clean_ssn = re.sub(r"[^\\d]", "", ssn)

        # Must be 9 digits
        if len(clean_ssn) != 9:
            return False

        # Check format: AAA-GG-SSSS
        area = clean_ssn[:3]
        group = clean_ssn[3:5]
        serial = clean_ssn[5:]

        # Check invalid patterns
        if area in self.invalid_patterns:
            return False
        if group == "00":
            return False
        if serial == "0000":
            return False

        # Check area number ranges
        area_num = int(area)
        if area_num == 0 or area_num == 666 or area_num >= 900:
            return False

        return True

    def _redact_ssn(self, ssn: str) -> str:
        """Redact an SSN, keeping only last 4 digits."""
        clean_ssn = re.sub(r"[^\\d]", "", ssn)
        if len(clean_ssn) >= 4:
            return f"***-**-{clean_ssn[-4:]}"
        else:
            return "***-**-****"

    def _redact_output(self, text: str, ssns: List[str]) -> str:
        """Create a redacted version of the output."""
        redacted = text
        for ssn in ssns:
            redacted_ssn = self._redact_ssn(ssn)
            redacted = redacted.replace(ssn, redacted_ssn)
        return redacted


# Plugin metadata
PLUGIN_INFO = {
    "name": "social_security_validator",
    "version": "1.0.0",
    "description": "Validates and detects Social Security Numbers for PII protection",
    "author": "validated-llm team",
    "validator_class": SocialSecurityValidator,
    "dependencies": [],
    "tags": ["pii", "privacy", "social-security", "redaction", "compliance"],
}


if __name__ == "__main__":
    # Example usage
    validator = SocialSecurityValidator(allow_ssn=False, redact_found=True)

    # Test with SSN in output
    test_output = "John's SSN is 123-45-6789 and he was born in 1990."
    result = validator.validate(test_output)

    print("Validation Result:")
    print(f"Valid: {result.is_valid}")
    print(f"Errors: {result.errors}")
    print(f"Warnings: {result.warnings}")
    print(f"Metadata: {result.metadata}")

    if result.metadata and "redacted_output" in result.metadata:
        print(f"\\nRedacted Output: {result.metadata['redacted_output']}")
