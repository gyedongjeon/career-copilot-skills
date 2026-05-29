# Agent Instructions

This file provides repository-specific context and operational rules for AI assistants working on this project.

## Core Directives
- **Source of Truth**: Always refer to the following documents for workflow rules:
    - [docs/branching-strategy.md](docs/branching-strategy.md)
    - [docs/commit-convention.md](docs/commit-convention.md)
    - [docs/pr-convention.md](docs/pr-convention.md)
- **Branching**: Follow GitHub Flow. Use `feat/`, `fix/`, `docs/`, etc. Never commit to `main`.
- **Commits**: Use Conventional Commits as defined in [docs/commit-convention.md](docs/commit-convention.md).
- **Pull Requests**: Follow the template and standards defined in [docs/pr-convention.md](docs/pr-convention.md).
- **Language**: Follow each skill's language policy. User-facing summaries should use the user's request language when a skill says so. Skill definitions, repository documentation, and code comments should remain in clear English unless there is a specific reason otherwise.

## Project Mission
- **Project**: `career-copilot-skills`
- **Objective**: Maintain a collection of reusable AI agent skills for career support workflows, including European job search, company research, job fit analysis, cover letter writing, and resume tailoring.
- **Primary Users**: Job seekers who keep their resume in Markdown and want personalized, file-based outputs for applications and interview preparation.
- **Core Outputs**: Markdown reports and application documents saved under the matching `*-results/` directories while preserving previous generated files.

## Operational Preferences
- Be concise and technical.
- Preserve original inputs such as resumes and skill definitions unless the user explicitly asks to update them.
- Follow each skill's `SKILL.md` workflow and output path exactly.
- Do not invent job postings, company facts, skills, achievements, or application details.
- Prefer clear, practical application documents over overly polished or generic language.
