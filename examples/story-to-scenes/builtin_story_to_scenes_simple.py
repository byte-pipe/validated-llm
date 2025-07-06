"""
Quick test of the built-in StoryToScenesTask with a simple story.
"""

import sys
from pathlib import Path

# Add the src directory to Python path so we can import validated_llm
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from validated_llm.tasks.story_to_scenes import StoryToScenesTask
from validated_llm.validation_loop import ValidationLoop


def main() -> None:
    """Test with a simple story."""

    simple_story = """
A brave knight discovered a dragon sleeping in a cave filled with treasure.
The knight carefully approached and found the dragon was actually protecting
a lost village child. Together, they returned the child safely home.
"""

    print("🎬 Testing StoryToScenesTask with simple story...")

    # Create the built-in task
    task = StoryToScenesTask()
    validator = task.create_validator()
    loop = ValidationLoop(default_max_retries=2)

    try:
        result = loop.execute(prompt_template=task.prompt_template, validator=validator, input_data={"story": simple_story})

        if result["success"]:
            print("✅ Success!")
            print("Generated YAML:")
            print("-" * 40)
            print(result["output"][:500] + "..." if len(result["output"]) > 500 else result["output"])
            print("-" * 40)
            print(f"Attempts: {result['attempts']}")
        else:
            print("❌ Failed")
            if result["validation_result"]:
                for error in result["validation_result"].errors[:3]:  # Show first 3 errors
                    print(f"Error: {error}")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
