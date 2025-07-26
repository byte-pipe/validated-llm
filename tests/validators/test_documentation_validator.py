"""Tests for DocumentationValidator."""

import pytest

from validated_llm.validators.documentation import DocumentationType, DocumentationValidator


class TestDocumentationValidator:
    """Test cases for DocumentationValidator."""

    def test_valid_readme(self):
        """Test validation of a valid README."""
        readme_content = """
# My Project

This is a great project that does amazing things.

## Installation

```bash
pip install my-project
```

## Usage

```python
import my_project
result = my_project.do_something()
```

## Examples

Here are some examples of how to use the project.

## License

MIT License
"""

        validator = DocumentationValidator(doc_type=DocumentationType.README, min_sections=3, require_code_examples=True)

        result = validator.validate(readme_content)

        assert result.is_valid
        assert len(result.errors) == 0
        assert result.metadata["section_count"] >= 3
        assert result.metadata["code_blocks_found"] >= 1

    def test_empty_documentation(self):
        """Test validation of empty documentation."""
        validator = DocumentationValidator()
        result = validator.validate("")

        assert not result.is_valid
        assert "Documentation content is empty" in result.errors[0]

    def test_missing_required_sections(self):
        """Test validation when required sections are missing."""
        content = """
# My Project

This is a project description.

## Random Section

Some content here.
"""

        validator = DocumentationValidator(doc_type=DocumentationType.README, required_sections=["Installation", "Usage"])

        result = validator.validate(content)

        assert not result.is_valid
        assert any("Missing required sections" in error for error in result.errors)
        assert "Installation" in str(result.errors)
        assert "Usage" in str(result.errors)

    def test_insufficient_sections(self):
        """Test validation when there are too few sections."""
        content = """
# My Project

This is a project description.

## Only Section

Not enough sections.
"""

        validator = DocumentationValidator(min_sections=5)
        result = validator.validate(content)

        assert not result.is_valid
        assert any("Insufficient sections" in error for error in result.errors)

    def test_api_documentation_validation(self):
        """Test API-specific validation."""
        api_content = """
# API Documentation

## Overview

This is our REST API.

## Authentication

Use Bearer tokens.

## Endpoints

### GET /users

Returns a list of users.

Response: 200 OK

```json
{
  "users": []
}
```

## Examples

```bash
curl -X GET https://api.example.com/users
```
"""

        validator = DocumentationValidator(doc_type=DocumentationType.API, require_api_documentation=True)

        result = validator.validate(api_content)

        assert result.is_valid
        assert result.metadata["http_methods_found"]
        assert "GET" in result.metadata["http_methods_found"]
        assert result.metadata["status_codes_found"]
        assert "200" in result.metadata["status_codes_found"]
        assert result.metadata["has_authentication_docs"]

    def test_code_examples_required(self):
        """Test validation when code examples are required but missing."""
        content = """
# My Project

This is a project without code examples.

## Installation

Install it somehow.

## Usage

Use it somehow.
"""

        validator = DocumentationValidator(require_code_examples=True)
        result = validator.validate(content)

        assert not result.is_valid
        assert any("Code examples are required" in error for error in result.errors)

    def test_link_validation(self):
        """Test markdown link validation."""
        content_with_links = """
# My Project

Check out [our website](https://example.com) and [broken link]() and [bad url](http://bad url).

## Installation

See [installation guide](#installation-guide).
"""

        validator = DocumentationValidator(check_links=True)
        result = validator.validate(content_with_links)

        assert not result.is_valid
        assert result.metadata["links_found"] == 3
        assert len(result.metadata["broken_links"]) > 0

    def test_section_content_length(self):
        """Test validation of section content length."""
        content = """
# My Project

Long description that meets the minimum word count requirements for this section to be considered valid content.

## Short Section

Too short.

## Another Short

Also short.
"""

        validator = DocumentationValidator(min_words_per_section=10)
        result = validator.validate(content)

        # Should have warnings about short sections
        assert len(result.warnings) > 0
        assert any("insufficient content" in warning for warning in result.warnings)
        assert result.metadata["short_sections"]

    def test_changelog_validation(self):
        """Test changelog-specific validation."""
        changelog_content = """
# Changelog

## [1.2.0] - 2024-01-15

### Added
- New feature X
- New feature Y

### Fixed
- Bug fix A
- Bug fix B

## [1.1.0] - 2024-01-01

### Changed
- Updated feature Z
"""

        validator = DocumentationValidator(doc_type=DocumentationType.CHANGELOG, required_sections=[])  # Don't require specific sections for this test
        result = validator.validate(changelog_content)

        assert result.is_valid
        assert result.metadata["versions_found"] >= 2
        assert result.metadata["dates_found"] >= 2
        assert "Added" in result.metadata["change_types_found"]
        assert "Fixed" in result.metadata["change_types_found"]

    def test_tutorial_validation(self):
        """Test tutorial-specific validation."""
        tutorial_content = """
# Tutorial: Getting Started

## Prerequisites

You need Python 3.8+ installed.

## Step 1: Installation

Install the package:

```bash
pip install example-package
```

## Step 2: Basic Usage

Create a simple script:

```python
import example_package
example_package.hello()
```

## Troubleshooting

If you encounter issues, try reinstalling.
"""

        validator = DocumentationValidator(doc_type=DocumentationType.TUTORIAL, required_sections=[])  # Don't require specific sections for this test
        result = validator.validate(tutorial_content)

        assert result.is_valid
        assert result.metadata["has_prerequisites"]
        assert result.metadata["has_troubleshooting"]
        assert result.metadata["code_blocks_found"] >= 2

    def test_forbidden_sections(self):
        """Test validation of forbidden sections."""
        content = """
# My Project

Description here.

## TODO

This section should not be in final docs.

## Installation

Install instructions.
"""

        validator = DocumentationValidator(forbidden_sections=["TODO", "FIXME"])

        result = validator.validate(content)

        assert len(result.warnings) > 0
        assert any("discouraged sections" in warning for warning in result.warnings)
        assert "TODO" in result.metadata["forbidden_sections_found"]

    def test_spelling_validation(self):
        """Test basic spelling validation."""
        content_with_errors = """
# My Project

This project has some spelling erors and recieve functionality.

## Installation

Follow the follwing steps.
"""

        validator = DocumentationValidator(check_spelling=True)
        result = validator.validate(content_with_errors)

        # Should have warnings about spelling
        assert len(result.warnings) > 0
        assert result.metadata["spelling_issues_found"] > 0

    def test_table_of_contents_recommendation(self):
        """Test recommendation for table of contents."""
        long_content = """
# My Project

Description

## Section 1
Content

## Section 2
Content

## Section 3
Content

## Section 4
Content

## Section 5
Content

## Section 6
Content
"""

        validator = DocumentationValidator()
        result = validator.validate(long_content)

        # Should recommend TOC for long documents
        assert any("table of contents" in warning.lower() for warning in result.warnings)
        assert not result.metadata["has_table_of_contents"]

    def test_code_block_language_specification(self):
        """Test validation of code block language specification."""
        content = """
# My Project

Example with language:

```python
print("Hello World")
```

Example without language:

```
some code here
```
"""

        validator = DocumentationValidator(require_code_examples=True, min_sections=1, required_sections=[])  # Lower requirement  # Don't require specific sections
        result = validator.validate(content)

        assert result.is_valid  # Still valid, just warnings
        assert any("missing language specification" in warning for warning in result.warnings)

    def test_get_description(self):
        """Test validator description."""
        validator = DocumentationValidator(doc_type=DocumentationType.API, required_sections=["Overview", "Endpoints"])

        description = validator.get_description()
        assert "api" in description
        assert "2" in description  # number of required sections


if __name__ == "__main__":
    pytest.main([__file__])
