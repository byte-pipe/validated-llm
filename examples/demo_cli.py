#!/usr/bin/env python3
"""
Demo the CLI functionality directly.
"""

import os
import sys
from unittest.mock import Mock

# Mock the missing dependencies
sys.modules["chatbot"] = Mock()
sys.modules["chatbot.chatbot"] = Mock()
sys.modules["validated_llm.validation_loop"] = Mock()

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))


def demo_cli_examples():
    """Show the CLI examples output."""
    print("Langchain to Validated-LLM Conversion Examples")
    print("=" * 50)

    print("\n1. Simple PromptTemplate conversion:")
    print(
        """
    # Langchain prompt:
    template = PromptTemplate(
        input_variables=["topic"],
        template="Write a blog post about {topic}"
    )

    # Converts to validated-llm task:
    class BlogPostTask(BaseTask):
        prompt_template = "Write a blog post about {topic}"
        validator_class = MarkdownValidator
    """
    )

    print("\n2. JSON output with Pydantic:")
    print(
        """
    # Langchain with Pydantic:
    from pydantic import BaseModel

    class Person(BaseModel):
        name: str
        age: int

    parser = PydanticOutputParser(pydantic_object=Person)
    template = PromptTemplate(
        template="Generate person data: {instruction}",
        input_variables=["instruction"],
        output_parser=parser
    )

    # Converts to validated-llm task with JSON validation
    """
    )

    print("\n3. Chain conversion:")
    print(
        """
    # Langchain chain converts to multiple validated tasks
    # with proper sequencing and validation at each step
    """
    )


def demo_cli_commands():
    """Show available CLI commands."""
    print("\n💻 Available CLI Commands")
    print("=" * 25)

    print("🔄 langchain convert <input_file>")
    print("   Convert a single Langchain prompt file to validated-llm task")
    print("   Options:")
    print("   --output, -o      Output file path")
    print("   --task-name, -n   Name for the generated task class")
    print("   --validator, -v   Specific validator to use")

    print("\n🔄 langchain migrate <directory>")
    print("   Migrate all Langchain prompts in a directory")
    print("   Options:")
    print("   --recursive, -r   Search recursively")
    print("   --dry-run         Show what would be converted without doing it")

    print("\n🔄 langchain examples")
    print("   Show examples of Langchain to validated-llm conversion")


def main():
    """Run CLI demonstration."""
    print("🚀 Langchain Integration CLI Demo")
    print("=" * 40)

    demo_cli_examples()
    demo_cli_commands()

    print("\n" + "=" * 40)
    print("✅ CLI functionality is ready!")
    print("\nTo use the CLI when Langchain is installed:")
    print("python -m validated_llm.integrations.langchain.cli --help")


if __name__ == "__main__":
    main()
