"""
Prompt analyzer that detects output patterns and structure.

This module analyzes prompt text to identify:
- Template variables ({variable})
- Expected output formats (JSON, CSV, lists, etc.)
- Validation requirements
- Structure patterns
"""

import json
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from .template_library import PromptTemplate, TemplateLibrary


@dataclass
class AnalysisResult:
    """Result of prompt analysis."""

    # Template variables found in prompt
    template_variables: List[str]

    # Detected output format
    output_format: str  # 'json', 'csv', 'list', 'text', 'unknown'

    # For JSON: detected schema structure
    json_schema: Optional[Dict[str, Any]] = None

    # For CSV: detected column names
    csv_columns: Optional[List[str]] = None

    # For lists: detected list item pattern
    list_pattern: Optional[str] = None

    # Validation hints found in prompt
    validation_hints: Optional[List[str]] = None

    # Confidence score (0.0 to 1.0)
    confidence: float = 0.0

    # Raw patterns found
    patterns: Optional[Dict[str, Any]] = None

    # Matched templates from library
    matched_templates: Optional[List[Tuple[PromptTemplate, float]]] = None

    def __post_init__(self) -> None:
        if self.validation_hints is None:
            self.validation_hints = []
        if self.patterns is None:
            self.patterns = {}
        if self.matched_templates is None:
            self.matched_templates = []


class PromptAnalyzer:
    """
    Analyzes prompts to detect output patterns and structure.

    This analyzer uses pattern matching and heuristics to identify:
    - What kind of output the prompt expects
    - What validation would be appropriate
    - What template variables are used
    """

    def __init__(self, template_library: Optional[TemplateLibrary] = None) -> None:
        """Initialize the prompt analyzer.

        Args:
            template_library: Optional template library to use for matching
        """
        self.template_library = template_library or TemplateLibrary()
        self.json_indicators = [
            r'\{[^{}]*"[^"]*"[^{}]*\}',  # JSON object pattern
            r"\[[^[\]]*\{[^}]*\}[^[\]]*\]",  # JSON array pattern
            "json",
            "JSON",
            '"key":',
            '"name":',
            '"id":',
            "return.*json",
            "output.*json",
            "format.*json",
            "structure.*json",
        ]

        self.csv_indicators = [r"csv", r"CSV", r"comma.separated", r"comma-separated", r"columns?:", r"headers?:", r"Name,.*,.*", r"[A-Za-z]+,[A-Za-z]+,[A-Za-z]+", "spreadsheet", "table format"]

        self.list_indicators = [r"^\d+\.", r"^\*", r"^-", "list of", "items:", "bullet points", "enumerate", "one per line"]  # Numbered/bulleted lists

        self.validation_keywords = [
            "required",
            "must",
            "should",
            "validate",
            "ensure",
            "check",
            "verify",
            "format",
            "minimum",
            "maximum",
            "between",
            "length",
            "type",
            "integer",
            "string",
            "number",
            "email",
            "url",
            "phone",
            "date",
        ]

    def analyze(self, prompt_text: str) -> AnalysisResult:
        """
        Analyze a prompt to detect patterns and structure.

        Args:
            prompt_text: The prompt text to analyze

        Returns:
            AnalysisResult with detected patterns and suggestions
        """
        # Extract template variables
        template_vars = self._extract_template_variables(prompt_text)

        # Detect output format
        output_format, format_confidence = self._detect_output_format(prompt_text)

        # Extract format-specific details
        json_schema = None
        csv_columns = None
        list_pattern = None

        if output_format == "json":
            json_schema = self._extract_json_schema(prompt_text)
        elif output_format == "csv":
            csv_columns = self._extract_csv_columns(prompt_text)
        elif output_format == "list":
            list_pattern = self._extract_list_pattern(prompt_text)

        # Extract validation hints
        validation_hints = self._extract_validation_hints(prompt_text)

        # Find similar templates
        matched_templates = self.template_library.find_similar_templates(prompt_text, top_k=3)

        # Enhance JSON schema detection with template library
        if output_format == "json" and matched_templates:
            json_schema = self._enhance_json_schema_with_templates(json_schema, matched_templates)

        # Calculate overall confidence
        confidence = self._calculate_confidence(prompt_text, output_format, format_confidence, json_schema, csv_columns, list_pattern)

        return AnalysisResult(
            template_variables=template_vars,
            output_format=output_format,
            json_schema=json_schema,
            csv_columns=csv_columns,
            list_pattern=list_pattern,
            validation_hints=validation_hints,
            confidence=confidence,
            patterns={"format_confidence": format_confidence, "has_examples": self._has_examples(prompt_text), "has_constraints": len(validation_hints) > 0},
            matched_templates=matched_templates,
        )

    def _extract_template_variables(self, prompt_text: str) -> List[str]:
        """Extract template variables like {variable} from prompt."""
        # More strict pattern to avoid matching JSON content
        # Only match single words or underscore-separated words
        pattern = r"\{([a-zA-Z_][a-zA-Z0-9_]*)\}"
        matches = re.findall(pattern, prompt_text)

        # Clean up variable names and remove duplicates
        variables = []
        for match in matches:
            var_name = match.strip()
            if var_name and var_name not in variables:
                # Skip if it looks like JSON property (contains quotes or colons)
                if '"' not in var_name and ":" not in var_name and "," not in var_name:
                    variables.append(var_name)

        return variables

    def _detect_output_format(self, prompt_text: str) -> tuple[str, float]:
        """
        Detect the expected output format.

        Returns:
            Tuple of (format_name, confidence_score)
        """
        text_lower = prompt_text.lower()

        # Count indicators for each format
        json_score = self._count_indicators(text_lower, self.json_indicators)
        csv_score = self._count_indicators(text_lower, self.csv_indicators)
        list_score = self._count_indicators(text_lower, self.list_indicators)

        # Determine format based on highest score
        max_score = max(json_score, csv_score, list_score)

        if max_score == 0:
            return "text", 0.3  # Default to text with low confidence

        if json_score == max_score:
            return "json", min(0.9, 0.3 + json_score * 0.1)
        elif csv_score == max_score:
            return "csv", min(0.9, 0.3 + csv_score * 0.1)
        elif list_score == max_score:
            return "list", min(0.9, 0.3 + list_score * 0.1)
        else:
            return "text", 0.3

    def _count_indicators(self, text: str, indicators: List[str]) -> int:
        """Count how many indicators are found in text."""
        count = 0
        for indicator in indicators:
            if re.search(indicator, text, re.IGNORECASE):
                count += 1
        return count

    def _extract_json_schema(self, prompt_text: str) -> Optional[Dict[str, Any]]:
        """
        Extract JSON schema from prompt examples or descriptions.

        This is a simplified extraction that looks for JSON examples
        and tries to infer schema structure.
        """
        # Look for JSON-like structures in the prompt
        json_patterns = [
            r'\{[^{}]*"[^"]*":[^{}]*\}',  # Simple JSON objects
            r"\{[^{}]*\}",  # Any curly braces content
        ]

        schema: dict[str, Any] = {"type": "object", "properties": {}}
        found_properties = set()

        # Extract property names from JSON examples
        for pattern in json_patterns:
            matches = re.findall(pattern, prompt_text)
            for match in matches:
                # Try to parse as JSON to extract keys
                try:
                    parsed = json.loads(match)
                    if isinstance(parsed, dict):
                        for key in parsed.keys():
                            found_properties.add(key)
                except:
                    # If parsing fails, look for quoted strings that might be keys
                    key_pattern = r'"([^"]+)":'
                    keys = re.findall(key_pattern, match)
                    found_properties.update(keys)

        # Look for key descriptions in text
        key_patterns = [
            r'"([^"]+)":\s*([^,}\]]+)',  # "key": description
            r"([a-zA-Z_][a-zA-Z0-9_]*)\s*\([^)]*\)",  # key(type)
            r"([a-zA-Z_][a-zA-Z0-9_]*)\s*:\s*([^\n,]+)",  # key: description
        ]

        for pattern in key_patterns:
            matches = re.findall(pattern, prompt_text)
            for match in matches:
                if len(match) >= 2:
                    key, description = match[0], match[1]
                    found_properties.add(key)

        # Build basic schema
        if found_properties:
            for prop in found_properties:
                schema["properties"][prop] = {"type": "string"}  # Default to string
            schema["required"] = list(found_properties)
            return schema

        return None

    def _extract_csv_columns(self, prompt_text: str) -> Optional[List[str]]:
        """Extract CSV column names from prompt."""
        columns = []

        # Look for explicit column definitions
        column_patterns = [
            r"columns?:\s*([^\n]+)",
            r"headers?:\s*([^\n]+)",
            r"([A-Za-z][A-Za-z0-9_]*),\s*([A-Za-z][A-Za-z0-9_]*),\s*([A-Za-z][A-Za-z0-9_]*)",
        ]

        for pattern in column_patterns:
            matches = re.findall(pattern, prompt_text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    columns.extend([col.strip() for col in match if col.strip()])
                else:
                    # Split by comma and clean
                    cols = [col.strip() for col in match.split(",")]
                    columns.extend([col for col in cols if col])

        return columns if columns else None

    def _extract_list_pattern(self, prompt_text: str) -> Optional[str]:
        """Extract list item pattern from prompt."""
        # Look for list examples
        list_patterns = [
            r"^\d+\.\s*(.+)$",  # 1. item
            r"^\*\s*(.+)$",  # * item
            r"^-\s*(.+)$",  # - item
        ]

        lines = prompt_text.split("\n")
        patterns_found = []

        for line in lines:
            line = line.strip()
            for pattern in list_patterns:
                match = re.match(pattern, line)
                if match:
                    patterns_found.append(match.group(1))

        if patterns_found:
            # Return the most common pattern or first one
            return patterns_found[0]

        return None

    def _extract_validation_hints(self, prompt_text: str) -> List[str]:
        """Extract validation requirements from prompt text."""
        hints = []
        text_lower = prompt_text.lower()

        # Look for validation keywords and their context
        for keyword in self.validation_keywords:
            if keyword in text_lower:
                # Find sentences containing the keyword
                sentences = re.split(r"[.!?]+", prompt_text)
                for sentence in sentences:
                    if keyword.lower() in sentence.lower():
                        hints.append(sentence.strip())

        return hints

    def _has_examples(self, prompt_text: str) -> bool:
        """Check if prompt contains examples of expected output."""
        example_indicators = ["example:", "for example", "like:", "such as", "```", "sample:", "output:", "format:"]

        text_lower = prompt_text.lower()
        return any(indicator in text_lower for indicator in example_indicators)

    def _calculate_confidence(self, prompt_text: str, output_format: str, format_confidence: float, json_schema: Optional[Dict], csv_columns: Optional[List], list_pattern: Optional[str]) -> float:
        """Calculate overall confidence in the analysis."""
        base_confidence = format_confidence

        # Boost confidence based on additional details found
        if output_format == "json" and json_schema:
            base_confidence += 0.2
        elif output_format == "csv" and csv_columns:
            base_confidence += 0.2
        elif output_format == "list" and list_pattern:
            base_confidence += 0.2

        # Boost confidence if examples are present
        if self._has_examples(prompt_text):
            base_confidence += 0.1

        # Ensure confidence stays within bounds
        return min(1.0, max(0.0, base_confidence))

    def _enhance_json_schema_with_templates(self, detected_schema: Optional[Dict[str, Any]], matched_templates: List[Tuple[PromptTemplate, float]]) -> Optional[Dict[str, Any]]:
        """Enhance detected JSON schema using matched templates."""
        if not matched_templates:
            return detected_schema

        # Find the best matching JSON template
        best_json_template = None
        best_score = 0.0

        for template, score in matched_templates:
            if template.json_schema and template.category == "json" and score > best_score:
                best_json_template = template
                best_score = score

        if best_json_template and best_score > 0.5:  # Use template if similarity is high enough
            template_schema = best_json_template.json_schema
            if template_schema is None:
                return detected_schema

            if detected_schema:
                # Merge detected schema with template schema
                merged_schema = template_schema.copy()
                if "properties" in detected_schema:
                    merged_schema.setdefault("properties", {}).update(detected_schema["properties"])
                if "required" in detected_schema:
                    merged_schema["required"] = list(set(merged_schema.get("required", []) + detected_schema["required"]))
                return merged_schema
            else:
                # Use template schema directly
                return template_schema

        return detected_schema
