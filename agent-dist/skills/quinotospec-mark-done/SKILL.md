---
name: Mark Done
description: Automates marking tasks as done, including recursive renaming of files and folders when all sub-tasks are completed.
---

# Mark Done Skill

Use this skill when the user indicates that a specific technical task (TSK-XXX) is completed. This skill will update the task tracker files to reflect the completion status and automatically rename artifacts if they are fully completed.

## Usage

When you finish a coding task, run the python script with the Task ID.

## Behavior

1.  **Mark Task**: Finds the `TSK-XXX` in the task files and prefixes it with `__` (e.g., `__TSK-XXX`).
2.  **File Completion**: If all tasks in a file are marked done, the file references are updated and the file is renamed to `__filename.md`.
3.  **User Story Completion**: If a task file is completed, the corresponding User Story ID (`US-XXX`) in `user-histories.md` is marked with `__` and rename de proposal folder to `__proposal_name`.
