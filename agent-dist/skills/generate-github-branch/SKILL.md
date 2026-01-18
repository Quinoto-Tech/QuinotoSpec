---
name: Generate GitHub Branch
description: Creates a new feature branch.
---

# Generate GitHub Branch

This skill guides you through the process of creating a new git branch for a feature or fix.

## Instructions

1.  **Check Current Status**
    Ensure the working directory is clean or you are ready to switch branches.
    ```bash
    git status
    ```

2.  **Create and Switch to New Branch**
    Create a new branch with a descriptive name (kebab-case recommended).
    ```bash
    git checkout -b <branch-name>
    ```
