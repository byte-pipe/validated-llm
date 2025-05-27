"""
Template library for prompt-to-task conversion.

This module provides a library of reusable templates for common prompt patterns,
making it easier to convert prompts to validated tasks by leveraging existing patterns.
"""

import difflib
import json
import os
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class PromptTemplate:
    """A reusable template for prompt-to-task conversion."""

    name: str
    category: str  # json, csv, email, api_docs, analysis_report, etc.
    description: str
    prompt_template: str
    validator_type: str  # Type of validator to use
    validator_config: Dict[str, Any] = field(default_factory=dict)
    json_schema: Optional[Dict[str, Any]] = None
    example_output: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    usage_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert template to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PromptTemplate":
        """Create template from dictionary."""
        return cls(**data)


class TemplateLibrary:
    """Manages a library of prompt templates."""

    def __init__(self, library_path: Optional[Path] = None):
        """
        Initialize the template library.

        Args:
            library_path: Path to store template library. Defaults to built-in templates.
        """
        self.library_path = library_path or Path(__file__).parent / "templates"
        self.library_path.mkdir(parents=True, exist_ok=True)
        self._templates: Dict[str, PromptTemplate] = {}
        self._load_templates()
        self._load_builtin_templates()

    def _load_templates(self) -> None:
        """Load templates from library path."""
        template_files = self.library_path.glob("*.json")
        for template_file in template_files:
            try:
                with open(template_file, "r") as f:
                    data = json.load(f)
                    template = PromptTemplate.from_dict(data)
                    self._templates[template.name] = template
            except Exception as e:
                print(f"Error loading template {template_file}: {e}")

    def _load_builtin_templates(self) -> None:
        """Load built-in templates."""
        builtin_templates = [
            # JSON Templates
            PromptTemplate(
                name="user_profile_json",
                category="json",
                description="Generate user profile information in JSON format",
                prompt_template="Generate a user profile for {name} who is {age} years old and works as {occupation}. Include contact information and interests.",
                validator_type="json",
                validator_config={
                    "required_fields": ["name", "age", "email", "occupation", "interests"],
                    "schema": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "age": {"type": "integer", "minimum": 0, "maximum": 150},
                            "email": {"type": "string", "format": "email"},
                            "occupation": {"type": "string"},
                            "interests": {"type": "array", "items": {"type": "string"}},
                        },
                        "required": ["name", "age", "email", "occupation", "interests"],
                    },
                },
                json_schema={
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "age": {"type": "integer", "minimum": 0, "maximum": 150},
                        "email": {"type": "string", "format": "email"},
                        "occupation": {"type": "string"},
                        "interests": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": ["name", "age", "email", "occupation", "interests"],
                },
                example_output='{"name": "John Doe", "age": 30, "email": "john@example.com", "occupation": "Software Engineer", "interests": ["coding", "hiking", "photography"]}',
                tags=["user", "profile", "personal", "json"],
            ),
            PromptTemplate(
                name="product_catalog_json",
                category="json",
                description="Generate product catalog entries in JSON format",
                prompt_template="Create a product catalog entry for {product_name} in the {category} category. Include pricing, description, and specifications.",
                validator_type="json",
                validator_config={
                    "required_fields": ["id", "name", "category", "price", "description"],
                    "schema": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "name": {"type": "string"},
                            "category": {"type": "string"},
                            "price": {"type": "number", "minimum": 0},
                            "currency": {"type": "string", "pattern": "^[A-Z]{3}$"},
                            "description": {"type": "string"},
                            "specifications": {"type": "object"},
                        },
                        "required": ["id", "name", "category", "price", "description"],
                    },
                },
                json_schema={
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "name": {"type": "string"},
                        "category": {"type": "string"},
                        "price": {"type": "number", "minimum": 0},
                        "currency": {"type": "string", "pattern": "^[A-Z]{3}$"},
                        "description": {"type": "string"},
                        "specifications": {"type": "object"},
                    },
                    "required": ["id", "name", "category", "price", "description"],
                },
                example_output='{"id": "PROD-001", "name": "Wireless Mouse", "category": "Electronics", "price": 29.99, "currency": "USD", "description": "Ergonomic wireless mouse with precision tracking", "specifications": {"dpi": 1600, "battery": "AA x2", "connectivity": "USB receiver"}}',
                tags=["product", "catalog", "ecommerce", "json"],
            ),
            # CSV Templates
            PromptTemplate(
                name="sales_report_csv",
                category="csv",
                description="Generate sales report data in CSV format",
                prompt_template="Generate a sales report for {period} showing daily sales data including date, product, quantity, and revenue.",
                validator_type="csv",
                validator_config={"required_columns": ["date", "product", "quantity", "revenue"], "min_rows": 5},
                example_output="date,product,quantity,revenue\n2024-01-01,Widget A,10,299.90\n2024-01-02,Widget B,5,149.95",
                tags=["sales", "report", "csv", "business"],
            ),
            # Email Templates
            PromptTemplate(
                name="business_email",
                category="email",
                description="Generate professional business emails",
                prompt_template="Write a professional email to {recipient} regarding {subject}. The tone should be {tone} and include {key_points}.",
                validator_type="email",
                validator_config={"require_subject": True, "min_body_length": 50, "require_greeting": True, "require_closing": True},
                example_output="Subject: Project Update\n\nDear Mr. Johnson,\n\nI hope this email finds you well...\n\nBest regards,\nJohn Doe",
                tags=["email", "business", "communication"],
            ),
            # API Documentation Templates
            PromptTemplate(
                name="rest_api_endpoint",
                category="api_docs",
                description="Generate REST API endpoint documentation",
                prompt_template="Document the {http_method} endpoint at {endpoint_path} that {endpoint_description}. Include request/response examples.",
                validator_type="markdown",
                validator_config={"required_sections": ["description", "request", "response", "example"], "require_code_blocks": True},
                example_output='## GET /api/users/{id}\n\nRetrieves user information by ID.\n\n### Request\n```http\nGET /api/users/123\n```\n\n### Response\n```json\n{\n  "id": 123,\n  "name": "John Doe"\n}\n```',
                tags=["api", "documentation", "rest", "markdown"],
            ),
            # Analysis Report Templates
            PromptTemplate(
                name="data_analysis_report",
                category="analysis_report",
                description="Generate data analysis reports with insights",
                prompt_template="Analyze the {dataset_name} dataset and provide insights on {analysis_focus}. Include summary statistics and recommendations.",
                validator_type="markdown",
                validator_config={"required_sections": ["summary", "methodology", "findings", "recommendations"], "require_statistics": True, "min_length": 500},
                tags=["analysis", "report", "data", "insights"],
            ),
            # SQL Query Templates
            PromptTemplate(
                name="sql_data_query",
                category="sql",
                description="Generate SQL queries for data retrieval",
                prompt_template="Write a SQL query to {query_objective} from the {table_name} table with conditions: {conditions}.",
                validator_type="sql",
                validator_config={"allowed_statements": ["SELECT"], "require_where_clause": True, "check_syntax": True},
                example_output="SELECT id, name, email FROM users WHERE age > 18 AND status = 'active';",
                tags=["sql", "query", "database"],
            ),
            # Story/Content Templates
            PromptTemplate(
                name="story_with_scenes",
                category="story",
                description="Generate stories with structured scenes",
                prompt_template="Write a {genre} story about {main_character} who {character_goal}. Include {num_scenes} scenes with clear progression.",
                validator_type="story_scenes",
                validator_config={"min_scenes": 3, "require_scene_titles": True, "require_scene_descriptions": True},
                tags=["story", "creative", "narrative", "scenes"],
            ),
        ]

        # Add built-in templates if they don't exist
        for template in builtin_templates:
            if template.name not in self._templates:
                self._templates[template.name] = template

    def add_template(self, template: PromptTemplate) -> None:
        """Add a new template to the library."""
        self._templates[template.name] = template
        self.save_template(template)

    def save_template(self, template: PromptTemplate) -> None:
        """Save template to disk."""
        template_path = self.library_path / f"{template.name}.json"
        with open(template_path, "w") as f:
            json.dump(template.to_dict(), f, indent=2)

    def get_template(self, name: str) -> Optional[PromptTemplate]:
        """Get a template by name."""
        return self._templates.get(name)

    def list_templates(self, category: Optional[str] = None, tags: Optional[List[str]] = None) -> List[PromptTemplate]:
        """
        List templates, optionally filtered by category or tags.

        Args:
            category: Filter by category
            tags: Filter by tags (matches any tag)

        Returns:
            List of matching templates
        """
        templates = list(self._templates.values())

        if category:
            templates = [t for t in templates if t.category == category]

        if tags:
            templates = [t for t in templates if any(tag in t.tags for tag in tags)]

        return sorted(templates, key=lambda t: (t.category, t.name))

    def find_similar_templates(self, prompt: str, top_k: int = 5) -> List[Tuple[PromptTemplate, float]]:
        """
        Find templates similar to the given prompt.

        Args:
            prompt: The prompt to match
            top_k: Number of top matches to return

        Returns:
            List of (template, similarity_score) tuples
        """
        similarities = []

        for template in self._templates.values():
            # Calculate similarity based on prompt template
            template_words = set(template.prompt_template.lower().split())
            prompt_words = set(prompt.lower().split())

            # Jaccard similarity
            intersection = template_words.intersection(prompt_words)
            union = template_words.union(prompt_words)
            jaccard_sim = len(intersection) / len(union) if union else 0

            # Also use difflib for sequence matching
            seq_matcher = difflib.SequenceMatcher(None, template.prompt_template.lower(), prompt.lower())
            seq_sim = seq_matcher.ratio()

            # Combined similarity
            similarity = (jaccard_sim + seq_sim) / 2

            similarities.append((template, similarity))

        # Sort by similarity and return top k
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]

    def get_categories(self) -> List[str]:
        """Get all unique categories."""
        return sorted(set(t.category for t in self._templates.values()))

    def get_all_tags(self) -> List[str]:
        """Get all unique tags."""
        all_tags = set()
        for template in self._templates.values():
            all_tags.update(template.tags)
        return sorted(all_tags)

    def update_usage_count(self, template_name: str) -> None:
        """Increment usage count for a template."""
        if template_name in self._templates:
            self._templates[template_name].usage_count += 1
            self.save_template(self._templates[template_name])

    def get_popular_templates(self, top_k: int = 10) -> List[PromptTemplate]:
        """Get most used templates."""
        templates = list(self._templates.values())
        templates.sort(key=lambda t: t.usage_count, reverse=True)
        return templates[:top_k]

    def export_template(self, name: str, output_path: Path) -> None:
        """Export a template to a file."""
        template = self.get_template(name)
        if template:
            with open(output_path, "w") as f:
                json.dump(template.to_dict(), f, indent=2)

    def import_template(self, input_path: Path) -> PromptTemplate:
        """Import a template from a file."""
        with open(input_path, "r") as f:
            data = json.load(f)
            template = PromptTemplate.from_dict(data)
            self.add_template(template)
            return template
