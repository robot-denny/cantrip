---
name: commit-message
description: Analyze staged changes and propose a commit message that explains why something changed rather than restating what changed, following the project's own commit conventions. Shows a summary, proposes the message, and waits for approval — never auto-commits.
disable-model-invocation: true
allowed-tools: Bash(git status:*), Bash(git diff:*), Bash(git log:*), Bash(git commit:*)
---

## Context

- Current git status: !`git status`
- Currently staged diff: !`git diff --staged`

Analyze the staged changes above and create a commit message. **Use present tense, and explain
*why* something changed — not merely what changed.** The diff already shows what changed; the
message earns its place by capturing the reasoning that isn't recoverable from the code.

If nothing is staged, say so and stop.

## Format

Follow the project's existing commit convention.

**Slot:** `.agents/config/conventions.md` → `## Commit format`
**If empty:** infer the convention from `git log --oneline -30` — whether the project uses
conventional-commit type prefixes, emoji, ticket references, a subject-line length limit, or plain
prose. Match what the history actually does. If the history is inconsistent or empty, use a plain
imperative subject line under ~72 characters, followed by a body explaining why.

Whatever the convention, the body should:

- Explain the reasoning, constraint, or problem that motivated the change
- Note anything a future reader would otherwise have to re-derive
- Stay in present tense

## Attribution trailers

If the project's convention includes attribution or co-authorship trailers, place them at the very
end, separated from the body by a blank line.

**Slot:** `.agents/config/conventions.md` → `## Commit trailers`
**If empty:** check `git log` for trailers the project already uses and match them. If there are
none, add none — do not introduce a trailer convention the project hasn't adopted.

## Output

1. Show a summary of what is currently staged
2. Propose the commit message
3. Ask for confirmation before committing

**Do not auto-commit.** Wait for approval, and only commit if the user says so.

`Next: push, or /retrofit if this change skipped the workflow`
