# Pull Request Convention

To ensure high-quality code reviews and a clear project history, all Pull Requests (PRs) should follow this convention.

## PR Title Format
Follow the same convention as our commit messages:
`<type>[optional scope]: <description>`

Examples:
- `feat: add cover letter submission template`
- `fix: correct resume tailoring output path`
- `docs: update PR convention document`

## PR Description Template
A good PR description helps reviewers understand **what** changed and **why**.

```markdown
## Summary
Briefly describe the changes introduced by this PR.

## Key Changes
- List major skill, documentation, or workflow changes.
- Mention any new dependencies or output files added.

## Related Issues
- Closes #123 (if applicable)

## Screenshots / Media (Optional)
Add screenshots, generated document previews, or sample output when useful.

## Checklist
- [ ] My code follows the project's style guidelines.
- [ ] I have performed a self-review of my code.
- [ ] I have reviewed generated documents or examples for accuracy.
- [ ] My changes generate no new warnings.
```

## PR Process
1. **Atomic PRs**: Keep PRs focused on a single task or feature.
2. **Draft PRs**: Use Draft PRs for work-in-progress if you need early feedback.
3. **Reviewers**: Tag relevant team members for review.
4. **Approval**: Get approval when working in a team; for solo work, self-review carefully before merging.
