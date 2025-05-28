# Tools

Development tools for the validated-llm project.

## Prompt-to-Task Converter

Converts text prompts into validated-llm task classes with appropriate validators.

### Usage

```bash
# Convert single prompt
python -m tools.prompt_to_task.cli convert my_prompt.txt

# Specify custom output location
python -m tools.prompt_to_task.cli convert my_prompt.txt --output path/to/my_task.py

# Interactive mode
python -m tools.prompt_to_task.cli convert my_prompt.txt --interactive

# Analyze only
python -m tools.prompt_to_task.cli convert my_prompt.txt --analyze-only
```

### Batch Conversion (NEW!)

Convert multiple prompt files at once with parallel processing and progress tracking:

```bash
# Convert all prompts in a directory
python -m tools.prompt_to_task.cli batch prompts/

# Convert with custom output directory
python -m tools.prompt_to_task.cli batch prompts/ --output-dir generated_tasks/

# Dry run to see what would be converted
python -m tools.prompt_to_task.cli batch prompts/ --dry-run

# Generate detailed report
python -m tools.prompt_to_task.cli batch prompts/ --report conversion_report.json

# Apply common validators to all files
python -m tools.prompt_to_task.cli batch data_prompts/ -v JSONValidator -v DateTimeValidator

# Use specific template for all conversions
python -m tools.prompt_to_task.cli batch api_prompts/ --template api_doc
```

### Features

- **Single File Conversion**: Convert individual prompts with interactive refinement
- **Batch Processing**: Convert entire directories of prompts efficiently
- **Format Detection**: Automatically detects JSON, CSV, lists, markdown, etc.
- **Smart Validators**: Suggests appropriate validators based on content
- **Parallel Processing**: Process multiple files concurrently for speed
- **Progress Tracking**: Beautiful progress bars with rich/tqdm
- **Detailed Reports**: JSON reports with conversion statistics
- **Template Support**: Apply consistent templates across conversions
- **Flexible Filtering**: Include/exclude patterns for file selection

### Batch Conversion Examples

```bash
# Convert all .txt and .prompt files recursively
python -m tools.prompt_to_task.cli batch . --include "*.txt" "*.prompt"

# Exclude test files and examples
python -m tools.prompt_to_task.cli batch prompts/ --exclude "*test*" "*example*"

# Parallel processing with 8 workers
python -m tools.prompt_to_task.cli batch large_collection/ --max-workers 8

# Sequential processing for debugging
python -m tools.prompt_to_task.cli batch prompts/ --sequential

# Overwrite existing files
python -m tools.prompt_to_task.cli batch prompts/ --overwrite
```

### Example Workflow

```bash
# 1. Convert a directory of prompts
python -m tools.prompt_to_task.cli batch legacy_prompts/ \
    --output-dir src/validated_llm/tasks/generated/ \
    --report migration_report.json

# 2. Check the report
cat migration_report.json | jq '.summary'

# 3. Use the generated tasks
from validated_llm.tasks.generated.email_task import EmailTask
from validated_llm.tasks.generated.report_task import ReportTask
```

### Progress Reporting

The batch converter supports multiple progress reporting backends:
- **auto** (default): Uses rich if available, falls back to tqdm or simple
- **rich**: Beautiful progress bars with summary tables
- **tqdm**: Classic progress bars
- **simple**: Plain text output
- **none**: No progress output

```bash
# Use rich progress bars
python -m tools.prompt_to_task.cli batch prompts/ --progress rich

# Simple text output
python -m tools.prompt_to_task.cli batch prompts/ --progress simple
```
