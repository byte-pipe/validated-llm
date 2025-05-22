"""
Demo: Using the Built-in Story-to-Scenes Task

This example shows how to use the pre-built StoryToScenesTask without actually
running the LLM (to avoid long execution times in examples).

This demonstrates the task structure and shows how users can integrate it.
"""

import sys
from pathlib import Path

# Add the src directory to Python path so we can import validated_llm
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from validated_llm.tasks.story_to_scenes import StoryToScenesTask


def demo_task_structure() -> None:
    """Demonstrate the StoryToScenesTask structure and capabilities."""

    print("🎭 Story-to-Scenes Task Demo")
    print("=" * 60)

    # Create the built-in task
    task = StoryToScenesTask()

    print(f"📋 Task Name: {task.name}")
    print(f"📝 Description: {task.description}")
    print()

    # Show sample story
    sample_story = """
    A young explorer discovered a hidden temple deep in the jungle. Inside, ancient
    murals told the story of a lost civilization. As she studied the walls, a secret
    door opened, revealing a chamber filled with glowing crystals. She carefully
    documented her findings before returning to share this amazing discovery.
    """

    print("📖 Sample Story:")
    print(sample_story.strip())
    print()

    # Show what the prompt would look like
    formatted_prompt = task.format_prompt(story=sample_story.strip())

    print("🎯 Generated Prompt (first 500 chars):")
    print("-" * 40)
    print(formatted_prompt[:500] + "...")
    print("-" * 40)
    print()

    # Show validator configuration
    validator = task.create_validator()
    print(f"🔍 Validator: {validator.name}")
    print(f"📏 Description: {validator.description}")
    print()

    # Show validation instructions
    instructions = validator.get_validation_instructions()
    print("📋 Validation Instructions (first 300 chars):")
    print("-" * 40)
    print(instructions[:300] + "...")
    print("-" * 40)
    print()

    print("✨ Ready to use! Here's how to run it:")
    print()
    print("```python")
    print("from validated_llm.tasks.story_to_scenes import StoryToScenesTask")
    print("from validated_llm.validation_loop import ValidationLoop")
    print()
    print("task = StoryToScenesTask()")
    print("validator = task.create_validator()")
    print("loop = ValidationLoop(default_max_retries=3)")
    print()
    print("result = loop.execute(")
    print("    prompt_template=task.prompt_template,")
    print("    validator=validator,")
    print("    input_data={'story': your_story_text}")
    print(")")
    print("```")
    print()


def demo_expected_output_format() -> None:
    """Show what the expected YAML output format looks like."""

    print("🎬 Expected Output Format")
    print("=" * 60)

    expected_yaml = """- id: 1
  image:
    prompt: "A young explorer with a backpack standing at the entrance of an ancient temple hidden in dense jungle foliage"
    style: "cinematic"
  audio:
    narration: "Deep in the jungle, a young explorer discovers a hidden temple covered in vines and mystery."
  caption:
    text: "Hidden Temple"
    style: "elegant"

- id: 2
  image:
    prompt: "Ancient stone walls covered with colorful murals depicting a lost civilization, illuminated by torch light"
    style: "photorealistic"
  audio:
    narration: "Inside the temple, ancient murals reveal the secrets of a civilization lost to time."
  caption:
    text: "Ancient Murals"
    style: "elegant"

- id: 3
  image:
    prompt: "A secret chamber glowing with ethereal blue and purple crystal formations, creating magical ambient lighting"
    style: "artistic"
  audio:
    narration: "A hidden door opens to reveal a chamber filled with glowing crystals, their light dancing on the walls."
  caption:
    text: "Crystal Chamber"
    style: "elegant"
"""

    print("📄 Sample YAML Output:")
    print("-" * 40)
    print(expected_yaml.strip())
    print("-" * 40)
    print()

    print("🔍 The validator checks for:")
    print("• ✅ Valid YAML syntax")
    print("• ✅ Required sections: image, audio, caption")
    print("• ✅ Image prompts (10+ chars, no style keywords)")
    print("• ✅ Image style (photorealistic, cinematic, or artistic)")
    print("• ✅ Audio narration (5+ chars)")
    print("• ✅ Caption text (non-empty)")
    print("• ✅ Optional: voice, pace, caption style/position")
    print("• ✅ Scene numbering and structure")
    print("• ✅ Best practices (3-10 scenes, consistent styles)")


def main() -> None:
    """Main demo function."""

    demo_task_structure()
    print()
    demo_expected_output_format()

    print()
    print("🚀 To actually run the story conversion:")
    print("poetry run python examples/story_to_scenes_example.py")
    print()
    print("⚠️  Note: Story conversion can take 30-60 seconds as it generates")
    print("detailed YAML scenes with complex validation requirements.")


if __name__ == "__main__":
    main()
