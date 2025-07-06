#!/usr/bin/env python3
"""
Software Engineering Tasks Demo

Demonstrates the new software engineering tasks for codebase analysis,
requirements generation, and user story creation.
"""

import json
from pathlib import Path

from validated_llm.tasks.software_engineering import AnalysisType, CodebaseAnalysisTask, RequirementsTask, RequirementType, UserStoryTask


def demo_codebase_analysis():
    """
    Demonstrate CodebaseAnalysisTask for analyzing project structure and quality.
    """
    print("=== Codebase Analysis Task Demo ===")

    # Create a comprehensive analysis task
    task = CodebaseAnalysisTask(
        analysis_types=[AnalysisType.ARCHITECTURE, AnalysisType.SECURITY, AnalysisType.QUALITY, AnalysisType.MAINTAINABILITY],
        project_language="python",
        project_type="web_application",
        include_dependencies=True,
        include_metrics=True,
        include_recommendations=True,
    )

    print(f"Task: {task.name}")
    print(f"Description: {task.description}")
    print(f"Analysis Types: {[t.value for t in task.analysis_types]}")

    # Sample codebase content for analysis
    sample_codebase = """
# app.py - Main Flask application
from flask import Flask, request, jsonify
import sqlite3
import hashlib

app = Flask(__name__)

# Global database connection (potential issue)
db_connection = sqlite3.connect('users.db')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    # SQL injection vulnerability
    query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
    cursor = db_connection.execute(query)
    user = cursor.fetchone()

    if user:
        return jsonify({"status": "success", "message": "Login successful"})
    else:
        return jsonify({"status": "error", "message": "Invalid credentials"})

@app.route('/users', methods=['GET'])
def get_users():
    # No authentication check
    cursor = db_connection.execute("SELECT * FROM users")
    users = cursor.fetchall()
    return jsonify(users)

@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']

    # Weak password hashing
    hashed_password = hashlib.md5(password.encode()).hexdigest()

    # More SQL injection potential
    query = f"INSERT INTO users (username, password) VALUES ('{username}', '{hashed_password}')"
    db_connection.execute(query)
    db_connection.commit()

    return jsonify({"status": "success", "message": "User registered"})

if __name__ == '__main__':
    app.run(debug=True)  # Debug mode in production

# models.py - Database models (missing)
# tests/ - No test directory
# requirements.txt - Dependencies not specified
"""

    print("\nSample Codebase to Analyze:")
    print("-" * 40)
    print(sample_codebase[:500] + "...")

    # Get the prompt that would be sent to the LLM
    prompt = task.prompt_template.format(codebase_content=sample_codebase)

    print(f"\nPrompt Length: {len(prompt)} characters")
    print("\nPrompt Preview:")
    print("-" * 40)
    print(prompt[:800] + "...")

    # Show the validation schema
    validator = task.create_validator()
    print(f"\nValidator: {validator.name}")
    print("Expected Output Structure:")
    print("- project_overview (name, language, type, complexity)")
    print("- analysis_results (architecture, security, quality scores)")
    print("- recommendations (priority, impact, effort)")
    print("- summary (overall_score, strengths, issues, next_steps)")


def demo_requirements_generation():
    """
    Demonstrate RequirementsTask for generating software requirements.
    """
    print("\n=== Requirements Generation Task Demo ===")

    # Create a comprehensive requirements task
    task = RequirementsTask(
        requirement_types=[RequirementType.FUNCTIONAL, RequirementType.NON_FUNCTIONAL, RequirementType.TECHNICAL],
        project_type="e_commerce_platform",
        stakeholders=["customers", "merchants", "administrators", "developers"],
        compliance_standards=["PCI-DSS", "GDPR"],
        include_acceptance_criteria=True,
        include_priorities=True,
        include_traceability=True,
    )

    print(f"Task: {task.name}")
    print(f"Description: {task.description}")
    print(f"Requirement Types: {[t.value for t in task.requirement_types]}")
    print(f"Stakeholders: {task.stakeholders}")
    print(f"Compliance: {task.compliance_standards}")

    # Sample project description
    project_description = """
    E-Commerce Platform Project:

    We need to build a modern e-commerce platform that allows:
    - Customers to browse products, add to cart, and checkout securely
    - Merchants to manage their inventory, orders, and customer data
    - Administrators to oversee the entire platform and manage users

    Key Features:
    - Product catalog with search and filtering
    - Shopping cart and checkout process
    - User authentication and authorization
    - Payment processing integration
    - Order management and tracking
    - Inventory management
    - Admin dashboard and analytics
    - Mobile-responsive design

    Technical Requirements:
    - Must handle 10,000+ concurrent users
    - 99.9% uptime requirement
    - PCI-DSS compliance for payment processing
    - GDPR compliance for data protection
    - Multi-language and multi-currency support
    - API-first architecture for mobile apps
    """

    print("\nProject Description:")
    print("-" * 40)
    print(project_description)

    # Get the prompt that would be sent to the LLM
    prompt = task.prompt_template.format(project_description=project_description)

    print(f"\nPrompt Length: {len(prompt)} characters")
    print("\nPrompt Preview:")
    print("-" * 40)
    print(prompt[:800] + "...")

    # Show the validation schema
    validator = task.create_validator()
    print(f"\nValidator: {validator.name}")
    print("Expected Output Structure:")
    print("- document_info (title, version, stakeholders)")
    print("- functional_requirements (ID, title, description, priority, acceptance_criteria)")
    print("- non_functional_requirements (category, metrics, target_values)")
    print("- technical_requirements (technology, justification, constraints)")
    print("- traceability_matrix (requirement mapping)")


def demo_user_story_generation():
    """
    Demonstrate UserStoryTask for generating user stories with acceptance criteria.
    """
    print("\n=== User Story Generation Task Demo ===")

    # Create a comprehensive user story task
    task = UserStoryTask(
        story_format="standard",
        include_acceptance_criteria=True,
        include_story_points=True,
        include_dependencies=True,
        include_business_value=True,
        persona_types=["customer", "merchant", "administrator"],
        epic_organization=True,
        min_stories=8,
        max_stories=15,
    )

    print(f"Task: {task.name}")
    print(f"Description: {task.description}")
    print(f"Story Format: {task.story_format}")
    print(f"Personas: {task.persona_types}")
    print(f"Epic Organization: {task.epic_organization}")
    print(f"Story Range: {task.min_stories}-{task.max_stories}")

    # Sample product requirements
    product_requirements = """
    E-Commerce Platform - User Stories Requirements:

    Product Vision:
    Create a user-friendly e-commerce platform that enables seamless online shopping
    experiences for customers while providing powerful tools for merchants to manage
    their businesses effectively.

    Key User Personas:
    1. Customer - End users who browse and purchase products
    2. Merchant - Sellers who list and manage their products
    3. Administrator - Platform managers who oversee operations

    Core Functionality Needed:

    Customer Experience:
    - Browse and search product catalog
    - View detailed product information and reviews
    - Add products to shopping cart
    - Secure checkout and payment processing
    - Order tracking and history
    - User account management
    - Wishlist and favorites

    Merchant Experience:
    - Product listing and inventory management
    - Order processing and fulfillment
    - Sales analytics and reporting
    - Customer communication tools
    - Store customization options

    Administration:
    - User and merchant management
    - Platform analytics and monitoring
    - Content moderation and quality control
    - System configuration and maintenance
    - Financial reporting and commission management

    Technical Considerations:
    - Mobile-first responsive design
    - Real-time inventory updates
    - Secure payment processing
    - Scalable architecture for growth
    - API integration capabilities
    """

    print("\nProduct Requirements:")
    print("-" * 40)
    print(product_requirements[:600] + "...")

    # Get the prompt that would be sent to the LLM
    prompt = task.prompt_template.format(product_requirements=product_requirements)

    print(f"\nPrompt Length: {len(prompt)} characters")
    print("\nPrompt Preview:")
    print("-" * 40)
    print(prompt[:800] + "...")

    # Show the validation schema
    validator = task.create_validator()
    print(f"\nValidator: {validator.name}")
    print("Expected Output Structure:")
    print("- backlog_info (product name, version, team info)")
    print("- personas (name, role, description, goals, pain_points)")
    print("- epics (ID, title, description, business_value, priority)")
    print("- user_stories (ID, title, story, persona, priority, story_points)")
    print("- acceptance_criteria (scenario, given-when-then format)")
    print("- dependencies and business_value for each story")


def demo_task_validation():
    """
    Demonstrate validation capabilities of the software engineering tasks.
    """
    print("\n=== Task Validation Demo ===")

    # Example of valid JSON output for CodebaseAnalysisTask
    valid_analysis_output = {
        "project_overview": {"name": "Flask Web App", "language": "python", "type": "web_application", "size": "small", "complexity": "medium", "description": "Simple Flask web application with user authentication"},
        "analysis_results": {
            "architecture": {
                "patterns": ["MVC", "Single Responsibility"],
                "issues": [
                    {
                        "severity": "high",
                        "category": "coupling",
                        "description": "Global database connection creates tight coupling",
                        "location": "app.py:8",
                        "recommendation": "Use dependency injection or connection pooling",
                    }
                ],
                "score": 6.5,
            },
            "security": {
                "vulnerabilities": [
                    {"type": "SQL Injection", "severity": "critical", "description": "Direct string concatenation in SQL queries", "file": "app.py", "line": 15, "mitigation": "Use parameterized queries or ORM"}
                ],
                "security_score": 3.0,
            },
            "quality": {
                "metrics": {"maintainability_index": 65.0, "cyclomatic_complexity": 8.2, "code_duplication": 12.0, "test_coverage": 0.0},
                "issues": [{"type": "complexity", "description": "High cyclomatic complexity in login function", "file": "app.py", "suggestion": "Break down into smaller functions"}],
                "quality_score": 5.5,
            },
        },
        "recommendations": [
            {
                "category": "Security",
                "priority": "high",
                "title": "Fix SQL Injection Vulnerabilities",
                "description": "Replace string concatenation with parameterized queries",
                "impact": "Prevents data breaches and unauthorized access",
                "effort": "medium",
                "timeline": "1-2 days",
            }
        ],
        "summary": {
            "overall_score": 5.0,
            "key_strengths": ["Simple architecture", "Clear separation of routes"],
            "critical_issues": ["SQL injection vulnerabilities", "No input validation"],
            "next_steps": ["Fix security issues", "Add input validation", "Implement proper error handling"],
        },
    }

    # Test validation
    analysis_task = CodebaseAnalysisTask()
    validator = analysis_task.create_validator()

    print("Testing CodebaseAnalysisTask validation...")
    result = validator.validate(json.dumps(valid_analysis_output, indent=2))

    print(f"Validation Result: {'✓ VALID' if result.is_valid else '✗ INVALID'}")
    if not result.is_valid:
        print(f"Errors: {result.errors}")
    if result.warnings:
        print(f"Warnings: {result.warnings}")

    # Show validator capabilities
    print(f"Validator Name: {validator.name}")
    print("Validation Features:")
    print("- JSON schema validation for structure")
    print("- Required field checking")
    print("- Data type validation")
    print("- Enum value validation")
    print("- Range validation for scores")


def main():
    """Run all software engineering task demonstrations."""
    print("Validated-LLM Software Engineering Tasks Demo")
    print("=" * 50)
    print()
    print("This demo showcases three new task types for software engineering workflows:")
    print("1. CodebaseAnalysisTask - Analyze code quality, security, and architecture")
    print("2. RequirementsTask - Generate comprehensive software requirements")
    print("3. UserStoryTask - Create user stories with acceptance criteria")
    print()

    try:
        demo_codebase_analysis()
        demo_requirements_generation()
        demo_user_story_generation()
        demo_task_validation()

        print("\n" + "=" * 50)
        print("Demo completed successfully!")
        print("\nNext Steps:")
        print("1. Use these tasks with ValidationLoop for actual LLM integration")
        print("2. Customize task parameters for your specific project needs")
        print("3. Extend the validators for additional domain-specific validation")
        print("4. Integrate with your development workflow and tools")

    except Exception as e:
        print(f"\nError during demo: {e}")
        print("Make sure all dependencies are installed and tasks are properly configured.")


if __name__ == "__main__":
    main()
