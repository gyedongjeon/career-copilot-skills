# Branching Strategy: GitHub Flow

This repository follows the **GitHub Flow** strategy to keep skill updates, documentation changes, and generated workflow improvements easy to review.

## Core Principles

1.  **The `main` branch is always usable.**
    *   Avoid committing directly to `main`.
    *   Skills, documentation, and examples in `main` should be reviewed and stable.

2.  **To work on something new, create a descriptive branch from `main`.**
    *   Use clear and concise names for branches.
    *   Examples: `feat/add-cover-letter-output`, `fix/job-search-links`, `docs/update-skill-readme`.

3.  **Commit and push to your branch regularly.**
    *   Pushing your work to the remote repository backs up your work and shares your progress with the team.

4.  **Open a Pull Request (PR) when you need feedback or are ready to merge.**
    *   PRs are for discussion, code review, and final checks.
    *   Provide a clear description of your changes in the PR.

5.  **Merge into `main` after review.**
    *   Merge only after checks pass and the change has been reviewed for correctness.

6.  **Clean up after merging to `main`.**
    *   Delete the feature branch once it has been merged.

## Branch Naming Convention

*   `feat/`: New features or enhancements.
*   `fix/`: Bug fixes.
*   `docs/`: Documentation changes (README, skill docs, workflow notes, etc.).
*   `refactor/`: Code changes that neither fix a bug nor add a feature.
*   `test/`: Adding or correcting tests.
*   `chore/`: Updates to build tasks, package manager configs, etc.
