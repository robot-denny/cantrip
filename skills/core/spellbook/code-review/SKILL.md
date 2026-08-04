---
name: code-review
description: Review a change with the project's reviewers in parallel — accessibility, code quality, and performance — then merge their findings into one de-duplicated report with a proposed action plan, and apply nothing without explicit approval. Scopes to uncommitted work by default, or to the whole branch versus its base when the increment was built across several commits. Run before committing.
disable-model-invocation: true
allowed-tools: Read, Glob, Grep, Bash(git diff:*), Bash(git status:*), Agent(*)
---

Your job is to coordinate the project's reviewers in parallel over a change, then merge what they find
into a single actionable report.

## Find the reviewers before assuming their names

**Discover which reviewers are registered rather than assuming the canonical three.** A project may
have kept its own tailored reviewer under a different name — which is exactly what the install checker
*recommends* when it finds a name collision, so this is the expected case, not an edge one.

List the registered agents and map each to a role by its name and description:

| Role | Canonical name | Also matches |
|---|---|---|
| Accessibility | `accessibility-reviewer` | anything whose name or description is about accessibility, WCAG, or assistive technology |
| Code quality | `code-reviewer` | a differently-prefixed quality reviewer — `<stack>-code-reviewer`, `quality-reviewer` |
| Performance | `perf-reviewer` | `performance-reviewer`, or anything about performance and load |

**Prefer a project's tailored reviewer over the canonical one** where both exist. It carries project
rules and calibrated memory a generic reviewer cannot, and that is the whole reason the collision
guidance says to keep it.

**Slot:** `.agents/config/reviewer-rules/` → `## Reviewer names`
**If empty:** discover by the mapping above. If a role has no registered reviewer, run that pass inline
under the same contract rather than skipping it — and say which roles were dispatched and which ran
inline, so a thin review is never mistaken for a clean one.

## Goal

1. Gather the diff at the right **scope** — see below; the default misses work that was committed
   per step.
2. Run every discovered reviewer in parallel over the same diff.
3. Merge their feedback into one unified report, de-duplicating overlap.
4. Produce a proposed action plan as an ordered checklist.
5. Ask for explicit approval **before** changing any code.

## Process

**Collect the diff first, at the right scope.**

`$ARGUMENTS` may name a scope. Default to `uncommitted`; accept `branch` explicitly.

| Scope | Covers | Use when |
|---|---|---|
| `uncommitted` (default) | `git diff` plus `git diff --staged` | Reviewing work in progress before a commit |
| `branch` | Everything on this branch versus its base, **plus** uncommitted and untracked | The increment was built across several commits |

**Reach for `branch` whenever the work was built through `/implement-step` and each step was
committed** — an uncommitted-only diff then sees only the last step, or nothing at all, and reports a
clean review of a fraction of the change. That silent under-scoping is worse than an error.

For `branch`, resolve the base from the **upstream tracking branch**, not a local branch name — a stale
local default inflates the diff with everything the local copy is missing:

```bash
git rev-parse --abbrev-ref @{u}          # then fetch that remote
git merge-base HEAD @{u}                 # the fork point
git diff <merge-base>...HEAD             # committed on the branch
git diff HEAD                            # uncommitted
git status --porcelain                   # untracked — read new files in full
```

**New files appear in no diff**, so read them directly or you review half the change.

**If the resolved scope is empty, say so and stop — do not proceed.**

**Then invoke every discovered reviewer in parallel.** Give each:

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

If a role has no reviewer under any name, run that pass inline rather than dropping it. **Always report
which roles were covered and how**, because a review missing a whole dimension looks identical to one
that found nothing there.

If reviewers cannot be dispatched at all, run all three passes inline, sequentially, under
the same severity scale and merge rules. The report is what matters; parallel dispatch is an
efficiency, not the contract.
