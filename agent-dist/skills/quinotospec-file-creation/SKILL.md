---
name: File Creation
description: Standards and guidelines for creating files, specifically temporary scripts.
trigger: ["script", "temp", "create file", "new file"]
scope: [".quinoto-spec/scripts/**"]
tools: ["write_to_file", "list_dir"]
---

# File Creation & Scripts

## Temporary Scripts
When creating scripts for one-off tasks, data migrations, temporary interactions (e.g., with PDFs, or APIs), or testing snippets:

1.  **Location**: ALWAYS place them in the `./quinoto-spec/scripts/` directory at the project root (`app/scripts/`).
2.  **Naming Convention**: Prefix the filename with `temp_`.
    -   Example: `./quinoto-spec/scripts/temp_read_pdf.py`

## Usage
- Do not create script files in the project root.
- Ensure the `./quinoto-spec/scripts/` directory exists before writing.
