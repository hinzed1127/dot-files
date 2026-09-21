---
description: Review this branch's PR like a SR Eng, save to docs/pr-reviews/[branch-name]-review.md, open w/ Typora
---

The current git branch has been made a PR in Github. Please review this PR as if you were a senior engineer. Make sure to use `gh` to view the PR description, as well as any review comments that might be on the PR. If the PR description includes links to any Azure DevOps tickets, use `az` to pull down that ticket info for additional context on the work.

## Focus Areas
- Architecture and design decisions
- Potential bugs and edge cases
- Performance considerations
- Security implications
- Code maintainability and best practices
- Test coverage

## Review Format
- Start with a brief summary of the PR purpose and changes
- List strengths of the implementation
- Identify issues and improvement opportunities (ordered by priority)
- Provide specific code examples for suggested changes where applicable

Please be specific, constructive, and actionable in your feedback. 

## Output file name and location
- Output the review into a markdown file named "${branch-name}-review.md", where ${branch-name} is the git branch. If the branch name begins `dh-`, don't include that. For example, the reviewing a git branch named `dh-new-feature` would result in a review file named `new-feature-review.md`.
- Place the resulting file inside the `docs/pr-reviews/` directory.
- Check that `typora` is an executable command and then use it to open the file, i.e. `typora path/to/${branch-name}-review.md`. Let me know if that command isn't working.

