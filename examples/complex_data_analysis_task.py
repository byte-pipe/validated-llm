"""
Example: Complex Data Analysis Report Task

This example demonstrates a more sophisticated task that generates structured data analysis
reports with multiple sections, validation layers, and context-aware feedback.

This shows advanced patterns like:
- Multi-section output validation
- Statistical validation with actual computation
- Context-aware validation (using input data for validation logic)
- Custom validator configuration
- Complex prompt engineering with examples
"""

import json
import re
import statistics
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Type

# Add the src directory to Python path so we can import validated_llm
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from validated_llm.base_validator import BaseValidator, ValidationResult
from validated_llm.tasks.base_task import BaseTask


class DataAnalysisReportTask(BaseTask):
    """
    Complex task for generating comprehensive data analysis reports.

    This task takes raw data and generates a structured analysis report with:
    - Executive summary
    - Statistical analysis
    - Key insights
    - Recommendations
    - Data visualizations (text descriptions)
    """

    @property
    def name(self) -> str:
        return "Data Analysis Report Generation"

    @property
    def description(self) -> str:
        return "Generate comprehensive data analysis reports from raw datasets with statistical insights and recommendations"

    @property
    def prompt_template(self) -> str:
        return """
You are a senior data analyst tasked with creating a comprehensive analysis report.

DATASET INFORMATION:
Dataset Name: {dataset_name}
Dataset Description: {dataset_description}
Data Type: {data_type}
Sample Size: {sample_size}

RAW DATA:
{raw_data}

ANALYSIS REQUIREMENTS:
Generate a structured data analysis report with the following sections:

## EXECUTIVE SUMMARY
[2-3 sentences summarizing the key findings and business impact]

## STATISTICAL ANALYSIS
### Descriptive Statistics
- Mean: [calculated value]
- Median: [calculated value]
- Standard Deviation: [calculated value]
- Min/Max: [min] / [max]
- Outliers: [number of outliers detected]

### Distribution Analysis
[Description of data distribution pattern, skewness, normality]

## KEY INSIGHTS
1. [Most significant finding with supporting data]
2. [Second most important insight]
3. [Third key observation]
[Continue with additional insights as relevant]

## TRENDS AND PATTERNS
[Describe any temporal trends, correlations, or patterns discovered]

## RECOMMENDATIONS
### Immediate Actions
1. [Specific actionable recommendation]
2. [Second priority action]

### Long-term Strategy
1. [Strategic recommendation based on data]
2. [Additional strategic consideration]

## DATA VISUALIZATION SUGGESTIONS
1. Chart Type: [e.g., "Bar Chart"]
   Purpose: [what it would show]
   Key Variables: [x-axis, y-axis, grouping]

2. Chart Type: [e.g., "Time Series Plot"]
   Purpose: [what it would show]
   Key Variables: [variables to plot]

## LIMITATIONS AND ASSUMPTIONS
[Acknowledge any data limitations, assumptions made, or areas needing additional data]

OUTPUT REQUIREMENTS:
- Use exact section headers as shown above (with ##)
- Include actual calculated statistics where specified
- Provide specific, actionable insights
- Base all conclusions on the provided data
- Use professional, analytical language
- Include at least 3 key insights
- Include at least 2 immediate and 2 long-term recommendations
- Suggest at least 2 data visualizations

Your response:"""

    @property
    def validator_class(self) -> Type[BaseValidator]:
        return DataAnalysisReportValidator

    def get_prompt_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Prepare and enrich the prompt data."""
        # Convert raw_data to string if it's a list/dict
        raw_data = kwargs.get("raw_data", [])
        if isinstance(raw_data, (list, dict)):
            raw_data = json.dumps(raw_data, indent=2)

        # Calculate sample size if not provided
        sample_size = kwargs.get("sample_size")
        if sample_size is None and isinstance(kwargs.get("raw_data"), list):
            sample_size = len(kwargs["raw_data"])

        return {
            "dataset_name": kwargs.get("dataset_name", "Unknown Dataset"),
            "dataset_description": kwargs.get("dataset_description", "No description provided"),
            "data_type": kwargs.get("data_type", "Mixed"),
            "sample_size": sample_size or "Unknown",
            "raw_data": raw_data,
        }


class DataAnalysisReportValidator(BaseValidator):
    """
    Advanced validator for data analysis reports with multiple validation layers.

    This validator checks:
    - Required section structure
    - Statistical accuracy (when raw data available)
    - Content quality and depth
    - Professional language and tone
    - Actionability of recommendations
    """

    def __init__(self, required_sections: Optional[List[str]] = None, min_insights: int = 3, min_recommendations: int = 4, min_visualizations: int = 2, validate_statistics: bool = True, strict_formatting: bool = True):
        """
        Initialize the data analysis report validator.

        Args:
            required_sections: List of required section headers
            min_insights: Minimum number of key insights required
            min_recommendations: Minimum total recommendations (immediate + long-term)
            min_visualizations: Minimum number of visualization suggestions
            validate_statistics: Whether to validate statistical calculations
            strict_formatting: Whether to enforce strict section formatting
        """
        super().__init__(name="data_analysis_validator", description=f"Validates comprehensive data analysis reports ({min_insights}+ insights, {min_recommendations}+ recommendations)")

        self.required_sections = required_sections or ["EXECUTIVE SUMMARY", "STATISTICAL ANALYSIS", "KEY INSIGHTS", "TRENDS AND PATTERNS", "RECOMMENDATIONS", "DATA VISUALIZATION SUGGESTIONS", "LIMITATIONS AND ASSUMPTIONS"]

        self.min_insights = min_insights
        self.min_recommendations = min_recommendations
        self.min_visualizations = min_visualizations
        self.validate_statistics = validate_statistics
        self.strict_formatting = strict_formatting

    def validate(self, content: str, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """Validate the generated data analysis report."""
        errors = []
        warnings = []
        metadata = {}

        # Parse sections
        sections = self._parse_sections(content)
        metadata["sections_found"] = list(sections.keys())

        # 1. Structure validation
        structure_errors = self._validate_structure(sections)
        errors.extend(structure_errors)

        # 2. Content depth validation
        content_errors, content_warnings = self._validate_content_depth(sections)
        errors.extend(content_errors)
        warnings.extend(content_warnings)

        # 3. Statistical validation (if data available)
        if self.validate_statistics and context and "raw_data" in context:
            stats_errors, stats_warnings = self._validate_statistics(sections, context["raw_data"])
            errors.extend(stats_errors)
            warnings.extend(stats_warnings)

        # 4. Professional language validation
        language_warnings = self._validate_professional_language(content)
        warnings.extend(language_warnings)

        # 5. Actionability validation
        actionability_errors = self._validate_actionability(sections)
        errors.extend(actionability_errors)

        metadata.update(
            {
                "insights_count": self._count_insights(sections),
                "recommendations_count": self._count_recommendations(sections),
                "visualizations_count": self._count_visualizations(sections),
                "word_count": len(content.split()),
            }
        )

        return ValidationResult(is_valid=len(errors) == 0, errors=errors, warnings=warnings, metadata=metadata)

    def _parse_sections(self, content: str) -> Dict[str, str]:
        """Parse content into sections based on headers."""
        sections = {}

        # Split by ## headers
        parts = re.split(r"\n## ", content)

        for part in parts:
            if "##" in part or part.strip():
                # Clean up the header
                lines = part.strip().split("\n")
                if lines:
                    header = lines[0].replace("##", "").strip()
                    body = "\n".join(lines[1:]).strip()
                    sections[header] = body

        return sections

    def _validate_structure(self, sections: Dict[str, str]) -> List[str]:
        """Validate required section structure."""
        errors = []

        for required_section in self.required_sections:
            if required_section not in sections:
                errors.append(f"Missing required section: '{required_section}'")
            elif not sections[required_section].strip():
                errors.append(f"Section '{required_section}' is empty")

        return errors

    def _validate_content_depth(self, sections: Dict[str, str]) -> tuple[List[str], List[str]]:
        """Validate content depth and quality."""
        errors = []
        warnings = []

        # Executive Summary validation
        if "EXECUTIVE SUMMARY" in sections:
            summary = sections["EXECUTIVE SUMMARY"]
            sentences = re.split(r"[.!?]+", summary)
            sentence_count = len([s for s in sentences if s.strip()])

            if sentence_count < 2:
                errors.append("Executive summary must contain at least 2 sentences")
            elif sentence_count > 5:
                warnings.append("Executive summary might be too long (>5 sentences)")

        # Key Insights validation
        insights_count = self._count_insights(sections)
        if insights_count < self.min_insights:
            errors.append(f"Must include at least {self.min_insights} key insights (found: {insights_count})")

        # Recommendations validation
        recommendations_count = self._count_recommendations(sections)
        if recommendations_count < self.min_recommendations:
            errors.append(f"Must include at least {self.min_recommendations} total recommendations (found: {recommendations_count})")

        # Visualizations validation
        viz_count = self._count_visualizations(sections)
        if viz_count < self.min_visualizations:
            errors.append(f"Must suggest at least {self.min_visualizations} data visualizations (found: {viz_count})")

        return errors, warnings

    def _validate_statistics(self, sections: Dict[str, str], raw_data: Any) -> tuple[List[str], List[str]]:
        """Validate statistical calculations against actual data."""
        errors = []
        warnings = []

        if "STATISTICAL ANALYSIS" not in sections:
            return errors, warnings

        stats_section = sections["STATISTICAL ANALYSIS"]

        # Try to extract numeric data
        try:
            if isinstance(raw_data, str):
                raw_data = json.loads(raw_data)

            if isinstance(raw_data, list):
                # Extract numeric values
                numeric_data = []
                for item in raw_data:
                    if isinstance(item, (int, float)):
                        numeric_data.append(float(item))
                    elif isinstance(item, dict):
                        # Look for numeric values in dict
                        for value in item.values():
                            if isinstance(value, (int, float)):
                                numeric_data.append(float(value))

                if numeric_data:
                    # Calculate actual statistics
                    actual_mean = statistics.mean(numeric_data)
                    actual_median = statistics.median(numeric_data)
                    actual_std = statistics.stdev(numeric_data) if len(numeric_data) > 1 else 0
                    actual_min = min(numeric_data)
                    actual_max = max(numeric_data)

                    # Check reported statistics
                    self._check_statistic(stats_section, "Mean", actual_mean, errors, warnings)
                    self._check_statistic(stats_section, "Median", actual_median, errors, warnings)
                    self._check_statistic(stats_section, "Standard Deviation", actual_std, errors, warnings)
                    self._check_statistic(stats_section, "Min", actual_min, errors, warnings)
                    self._check_statistic(stats_section, "Max", actual_max, errors, warnings)

        except Exception as e:
            warnings.append(f"Could not validate statistics against raw data: {str(e)}")

        return errors, warnings

    def _check_statistic(self, text: str, stat_name: str, actual_value: float, errors: List[str], warnings: List[str]) -> None:
        """Check if a statistic is approximately correct in the text."""
        # Look for the statistic in the text
        pattern = rf"{stat_name}:\s*([0-9]+\.?[0-9]*)"
        match = re.search(pattern, text, re.IGNORECASE)

        if match:
            try:
                reported_value = float(match.group(1))
                # Allow 10% tolerance
                tolerance = abs(actual_value * 0.1) if actual_value != 0 else 0.1

                if abs(reported_value - actual_value) > tolerance:
                    errors.append(f"{stat_name} calculation incorrect: reported {reported_value}, should be approximately {actual_value:.2f}")
            except ValueError:
                warnings.append(f"Could not parse {stat_name} value from report")
        else:
            warnings.append(f"{stat_name} not found in statistical analysis section")

    def _validate_professional_language(self, content: str) -> List[str]:
        """Validate professional language and tone."""
        warnings = []

        # Check for informal language
        informal_words = ["awesome", "cool", "super", "totally", "basically", "kinda", "sorta"]
        content_lower = content.lower()

        found_informal = [word for word in informal_words if word in content_lower]
        if found_informal:
            warnings.append(f"Consider replacing informal language: {', '.join(found_informal)}")

        # Check for excessive exclamation marks
        if content.count("!") > 3:
            warnings.append("Excessive exclamation marks may appear unprofessional in analytical reports")

        # Check for first-person pronouns (should be minimal in professional reports)
        first_person = re.findall(r"\b(I|me|my|myself)\b", content, re.IGNORECASE)
        if len(first_person) > 2:
            warnings.append("Consider using more objective language (minimize first-person pronouns)")

        return warnings

    def _validate_actionability(self, sections: Dict[str, str]) -> List[str]:
        """Validate that recommendations are specific and actionable."""
        errors = []

        if "RECOMMENDATIONS" not in sections:
            return errors

        recommendations_text = sections["RECOMMENDATIONS"]

        # Check for vague language
        vague_phrases = ["should consider", "might want to", "could potentially", "it would be good to"]
        for phrase in vague_phrases:
            if phrase in recommendations_text.lower():
                errors.append(f"Recommendations contain vague language: '{phrase}' - be more specific and actionable")

        # Check for specific action verbs
        action_verbs = ["implement", "establish", "increase", "decrease", "develop", "create", "optimize", "reduce"]
        has_action_verbs = any(verb in recommendations_text.lower() for verb in action_verbs)

        if not has_action_verbs:
            errors.append("Recommendations should include specific action verbs (implement, establish, increase, etc.)")

        return errors

    def _count_insights(self, sections: Dict[str, str]) -> int:
        """Count the number of key insights."""
        if "KEY INSIGHTS" not in sections:
            return 0

        insights_text = sections["KEY INSIGHTS"]
        # Count numbered items
        numbered_items = re.findall(r"^\d+\.", insights_text, re.MULTILINE)
        return len(numbered_items)

    def _count_recommendations(self, sections: Dict[str, str]) -> int:
        """Count total recommendations (immediate + long-term)."""
        if "RECOMMENDATIONS" not in sections:
            return 0

        recommendations_text = sections["RECOMMENDATIONS"]
        # Count numbered items in both subsections
        numbered_items = re.findall(r"^\d+\.", recommendations_text, re.MULTILINE)
        return len(numbered_items)

    def _count_visualizations(self, sections: Dict[str, str]) -> int:
        """Count visualization suggestions."""
        if "DATA VISUALIZATION SUGGESTIONS" not in sections:
            return 0

        viz_text = sections["DATA VISUALIZATION SUGGESTIONS"]
        # Count numbered items
        numbered_items = re.findall(r"^\d+\.", viz_text, re.MULTILINE)
        return len(numbered_items)


def example_usage() -> None:
    """
    Example of how to use the complex DataAnalysisReportTask.

    This demonstrates:
    - Complex data preparation
    - Context-aware validation
    - Statistical validation
    - Multi-layered validation logic
    """
    from validated_llm.validation_loop import ValidationLoop

    # Create the complex task
    task = DataAnalysisReportTask()

    # Create validator with custom settings
    validator = task.create_validator(min_insights=3, min_recommendations=4, validate_statistics=True, strict_formatting=True)

    # Create validation loop
    loop = ValidationLoop(default_max_retries=3)

    # Prepare complex input data
    sales_data = [
        {"month": "Jan", "revenue": 45000, "units": 150},
        {"month": "Feb", "revenue": 52000, "units": 173},
        {"month": "Mar", "revenue": 48000, "units": 160},
        {"month": "Apr", "revenue": 61000, "units": 203},
        {"month": "May", "revenue": 58000, "units": 193},
        {"month": "Jun", "revenue": 64000, "units": 213},
    ]

    input_data = {
        "dataset_name": "Q1-Q2 2024 Sales Performance",
        "dataset_description": "Monthly sales revenue and unit sales data for first half of 2024",
        "data_type": "Time series sales data",
        "sample_size": len(sales_data),
        "raw_data": sales_data,
    }

    print("🔍 Generating comprehensive data analysis report...")
    print(f"📊 Dataset: {input_data['dataset_name']}")
    print(f"📈 Sample size: {input_data['sample_size']} months")
    print("=" * 60)

    try:
        result = loop.execute(prompt_template=task.prompt_template, validator=validator, input_data=input_data, context={"raw_data": sales_data}, debug=False)  # Pass raw data for statistical validation

        if result["success"]:
            print("📋 GENERATED ANALYSIS REPORT:")
            print("=" * 60)
            print(result["output"])
            print("=" * 60)
            print(f"✅ Success after {result['attempts']} attempt(s)")
            print(f"⏱️  Execution time: {result['execution_time']:.2f}s")

            # Show validation metadata
            if result["validation_result"] and result["validation_result"].metadata:
                metadata = result["validation_result"].metadata
                print(f"📊 Insights found: {metadata.get('insights_count', 'N/A')}")
                print(f"💡 Recommendations: {metadata.get('recommendations_count', 'N/A')}")
                print(f"📈 Visualizations: {metadata.get('visualizations_count', 'N/A')}")
                print(f"📝 Word count: {metadata.get('word_count', 'N/A')}")
        else:
            print("❌ Failed to generate valid analysis report:")
            if result["validation_result"]:
                print("\nValidation errors:")
                for error in result["validation_result"].errors:
                    print(f"  ❌ {error}")
                if result["validation_result"].warnings:
                    print("\nWarnings:")
                    for warning in result["validation_result"].warnings:
                        print(f"  ⚠️  {warning}")

    except Exception as e:
        print(f"❌ Error during analysis generation: {e}")


if __name__ == "__main__":
    example_usage()
