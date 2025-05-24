# Tools

Development tools for the validated-llm project.

## Prompt-to-Task Converter

Converts text prompts into validated-llm task classes with appropriate validators.

### Usage

```bash
# Generate task (outputs to current directory)
python -m tools.prompt_to_task.cli my_prompt.txt

# Specify custom output location
python -m tools.prompt_to_task.cli my_prompt.txt --output path/to/my_task.py

# Interactive mode
python -m tools.prompt_to_task.cli my_prompt.txt --interactive

# Analyze only
python -m tools.prompt_to_task.cli my_prompt.txt --analyze-only
```

### Features

- Detects output format (JSON, CSV, text, lists)
- Suggests appropriate validators
- Generates complete task classes
- Interactive mode for refinement

### Example

```bash
# Convert a prompt (outputs to current directory)
python -m tools.prompt_to_task.cli email_prompt.txt

# For validated-llm projects, move to the appropriate location:
mv email_prompt_task.py src/validated_llm/tasks/prompt_to_task_generated/

# Then import and use:
from validated_llm.tasks.prompt_to_task_generated.email_prompt_task import EmailPromptTask
```
