"""
Example: Using the Built-in Story-to-Scenes Task

This example demonstrates how to use the pre-built StoryToScenesTask
to convert narrative stories into structured YAML scene files for video generation.

The StoryToScenesTask is one of the ready-to-use tasks included with validated-llm.
"""

import sys
from pathlib import Path

# Add the src directory to Python path so we can import validated_llm
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from validated_llm.tasks.story_to_scenes import StoryToScenesTask
from validated_llm.validation_loop import ValidationLoop


def example_short_story() -> str:
    """Return a sample story for scene conversion."""
    return """
The old lighthouse keeper, Samuel, had watched over the rocky coast for thirty years.
Every night, he climbed the winding stairs to light the beacon that guided ships safely home.

Tonight felt different. As storm clouds gathered on the horizon, Samuel noticed a small
fishing boat struggling against the rising waves. The boat's engine had failed, and it
was drifting dangerously close to the jagged rocks.

Without hesitation, Samuel cranked the lighthouse beam to its brightest setting and began
signaling the coast guard with the emergency pattern he'd memorized decades ago. The
bright flashes cut through the darkness like a knife.

Twenty minutes later, the coast guard vessel appeared, its searchlights sweeping the
turbulent waters. They threw a rescue line to the fishing boat just as the first massive
wave crashed against the lighthouse base.

As dawn broke, Samuel watched the rescued fisherman wave gratefully from the dock below.
Another life saved, another night's work done. He smiled, knowing that tomorrow he would
climb those stairs again, ready to be the guardian angel of the sea.
"""


def example_fairy_tale() -> str:
    """Return a sample fairy tale for scene conversion."""
    return """
In a magical forest where flowers sang and trees whispered secrets, lived a young fox
named Luna with fur that shimmered like moonlight. Unlike other foxes, Luna possessed
the rare gift of understanding the language of all forest creatures.

One morning, Luna discovered that the ancient Crystal Spring, source of all magic in
the forest, had begun to dim. The wise old owl explained that the spring's guardian
crystal had been stolen by the Shadow Witch who lived beyond the Thorny Mountains.

Determined to save her home, Luna set off on a perilous journey. She crossed babbling
brooks on lily pads offered by friendly frogs, climbed treacherous mountain paths with
help from sure-footed mountain goats, and finally reached the Shadow Witch's dark castle.

Inside the castle, Luna found the crystal imprisoned in a cage of twisted vines. Using
her gift, she spoke to the vines in their ancient plant language, convincing them that
they belonged in the sunlight, not in this dark place. The vines slowly unwound,
freeing the crystal.

With the crystal restored to its home, the forest bloomed brighter than ever before.
Luna was celebrated as a hero, but she knew the real magic came from kindness and
understanding between all living things.
"""


def run_story_conversion(story: str, story_title: str) -> None:
    """
    Convert a story to scenes using the built-in StoryToScenesTask.

    Args:
        story: The narrative story text
        story_title: Title for display purposes
    """
    print(f"🎬 Converting story to scenes: {story_title}")
    print("=" * 60)

    # Create the built-in task
    task = StoryToScenesTask()

    # Create validator (using default settings)
    validator = task.create_validator()

    # Create validation loop
    loop = ValidationLoop(default_max_retries=3)

    # Prepare input data
    input_data = {"story": story}

    try:
        result = loop.execute(prompt_template=task.prompt_template, validator=validator, input_data=input_data, debug=False)

        if result["success"]:
            print("🎥 GENERATED SCENES:")
            print("=" * 60)
            print(result["output"])
            print("=" * 60)
            print(f"✅ Success after {result['attempts']} attempt(s)")
            print(f"⏱️  Execution time: {result['execution_time']:.2f}s")

            # Show validation metadata if available
            if result["validation_result"] and result["validation_result"].metadata:
                result["validation_result"].metadata
                print(f"🎬 Scenes generated: {len(result['output'].split('- id:')) - 1}")

            # Show validation warnings if any
            if result["validation_result"] and result["validation_result"].warnings:
                print("\n⚠️  Validation warnings:")
                for warning in result["validation_result"].warnings:
                    print(f"  • {warning}")

        else:
            print("❌ Failed to generate valid scenes:")
            if result["validation_result"]:
                print("\nValidation errors:")
                for error in result["validation_result"].errors:
                    print(f"  ❌ {error}")

                if result["validation_result"].warnings:
                    print("\nWarnings:")
                    for warning in result["validation_result"].warnings:
                        print(f"  ⚠️  {warning}")

    except Exception as e:
        print(f"❌ Error during scene generation: {e}")

    print("\n" + "=" * 60 + "\n")


def demonstrate_validation_features() -> None:
    """
    Demonstrate the validation features with a deliberately problematic story.
    """
    print("🔍 Demonstrating validation with a minimal story...")
    print("=" * 60)

    minimal_story = "A person walked down a street. The end."

    task = StoryToScenesTask()
    validator = task.create_validator()
    loop = ValidationLoop(default_max_retries=2)  # Fewer retries for demo

    try:
        result = loop.execute(prompt_template=task.prompt_template, validator=validator, input_data={"story": minimal_story}, debug=False)

        print(f"Result: {'✅ Success' if result['success'] else '❌ Failed'}")
        print(f"Attempts: {result['attempts']}")

        if result["validation_result"]:
            if result["validation_result"].errors:
                print("Validation errors encountered:")
                for error in result["validation_result"].errors:
                    print(f"  ❌ {error}")

            if result["validation_result"].warnings:
                print("Validation warnings:")
                for warning in result["validation_result"].warnings:
                    print(f"  ⚠️  {warning}")

    except Exception as e:
        print(f"❌ Error: {e}")

    print("\n" + "=" * 60 + "\n")


def main() -> None:
    """
    Main function demonstrating the built-in StoryToScenesTask.
    """
    print("🎭 Story-to-Scenes Conversion Examples")
    print("Using the built-in StoryToScenesTask from validated-llm")
    print("=" * 60)
    print()

    # Example 1: Short realistic story
    lighthouse_story = example_short_story()
    run_story_conversion(lighthouse_story, "The Lighthouse Keeper")

    # Example 2: Fairy tale
    fairy_tale = example_fairy_tale()
    run_story_conversion(fairy_tale, "Luna and the Crystal Spring")

    # Example 3: Demonstrate validation (optional - might fail)
    print("🔧 Optional: Testing validation with minimal story")
    print("(This may fail to demonstrate validation in action)")
    demonstrate_validation_features()

    print("✨ Examples complete!")
    print("\nThe StoryToScenesTask validates:")
    print("• ✅ Valid YAML structure")
    print("• ✅ Required scene sections (image, audio, caption)")
    print("• ✅ Image prompts without style keywords")
    print("• ✅ Proper style field values")
    print("• ✅ Scene numbering and structure")
    print("• ✅ Content quality and length requirements")
    print("\nYou can use this task in your own code by importing:")
    print("from validated_llm.tasks.story_to_scenes import StoryToScenesTask")


if __name__ == "__main__":
    main()
