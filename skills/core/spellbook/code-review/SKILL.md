---
name: code-review
description: Review uncommitted changes with three reviewers in parallel — accessibility, code quality, and performance — then merge their findings into one de-duplicated report with a proposed action plan, and apply nothing without explicit approval. Run before committing.
disable-model-invocation: true
allowed-tools: Read, Glob, Grep, Bash(git diff:*), Bash(git status:*), Agent(*)
---

Your job is to coordinate three reviewers in parallel over the current changes, then merge what
they find into a single actionable report.

The reviewers:

- **accessibility-reviewer**
- **code-reviewer**
- **perf-reviewer**

## Goal

1. Gather the current diff, including **both** staged and unstaged changes.
2. Run all three reviewers in parallel over the same diff.
3. Merge their feedback into one unified report, de-duplicating overlap.
4. Produce a proposed action plan as an ordered checklist.
5. Ask for explicit approval **before** changing any code.

## Process

**Collect the diff first.** Use `git diff` for unstaged and `git diff --staged` for staged. **If
both are empty, say so and stop — do not proceed.**

**Then invoke all three reviewers in parallel.** Give each:

- The combined diff
- Brief repo context, so findings are grounded rather than generic

  **Slot:** `.agents/config/reviewer-rules/` → the shared context section
  **If empty:** derive a two-line orientation from the repo itself — its stack, its build entry
  point, and the shape of the change under review. Do not fabricate architectural claims.

Tell each reviewer to:

- **Be evidence-based** — file paths, line or snippet references, no guessing.
- **Review only what is in the diff.** Not the surrounding codebase.

## Merge the results

Into this shape:

1. **Summary** — 10 bullets maximum, total
2. **Accessibility findings** — include **all** findings from the reviewer, not just the top ones
3. **Code quality findings** — all of them
4. **Performance findings** — all of them
5. **Combined action plan** — an ordered checklist
6. **Questions and uncertainties** — anything needing human intent

All three reviewers use the same severity scale, so findings sort into one ranking:
**Blocker / Major / Minor / Nit.**

De-duplicate where multiple reviewers flag the same issue, but **never silently drop a unique
finding.** When two reviewers disagree on severity, take the higher one and note the disagreement —
it usually means the issue has two distinct costs.

## Rules

- **Do not edit any files yet.**
- **Do not make formatting-only changes** unless they fix a cited issue.

Finish by asking:

> Do you want me to implement the action plan now?

Wait for confirmation before making any changes.

After the action plan is applied, or explicitly skipped, end with:

`Next: /commit-message, then push`

## If a reviewer is unavailable

Newly added reviewers are loaded at session start, so a reviewer reported as not found usually
means the session predates its installation — say so and suggest restarting, rather than silently
producing a two-reviewer report.

If reviewers cannot be dispatched at all, run the three review passes inline, sequentially, under
the same severity scale and merge rules. The report is what matters; parallel dispatch is an
efficiency, not the contract.
