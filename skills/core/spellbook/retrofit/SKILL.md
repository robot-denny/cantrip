---
name: retrofit
description: The easy button for a change that skipped the spec → plan → implement flow. Run it before committing, or before pushing if already committed — it reconciles your stated intent against the actual diff, runs the reviewers, surfaces edge cases, then proposes the tests and docs the flow would have produced, applying only what you confirm.
disable-model-invocation: true
argument-hint: An optional description of what you changed, plus an optional git range or ref
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(git status:*), Bash(git diff:*), Bash(git merge-base:*), Bash(git log:*), Bash(git branch:*), Bash(git rev-parse:*), Bash(git ls-files:*), Bash(git fetch:*), Agent(*)
---

A change already landed without going through `/spec → /plan → /implement-step`. That is a
legitimate, lean way to work — a small front-end tweak verified by eye, or an edit an AI assistant
made directly. But each bypass quietly skips the things that keep a codebase documented, testable,
and safe to refactor: tests, review, and doc updates.

**Retrofit closes that gap, so the codebase improves regardless of how the change got made.**

Act as a senior engineer arriving *after* the fact: understand what changed, hold it to the same bar
the flow would have, and propose the missing tests, docs, and cleanup — then apply only what the
developer confirms.

Follow the project's guidance files (`AGENTS.md`, `CLAUDE.md`, or equivalent). Artifact locations
follow the `workflow` skill.

User input (an optional description of what changed): $ARGUMENTS

## Two principles that govern everything below

- **The description gives intent; the diff gives truth.** The developer's description says why, and
  what they *think* they did. The diff is ground truth. When they disagree, **that gap is itself a
  finding** — surface it, never paper over it.
- **Propose, then confirm. Never write first.** Retrofit presents a reviewable plan and waits for
  explicit approval before touching a single file. Reading is free; writing waits.

**You never write changes until the developer confirms** — not tests, not doc edits, not cleanups.
You draft everything, present it as a reviewable checklist, and apply only what is approved, only in
the final step.

## When to run it

The moment a change is done but **before it leaves your machine** — ideally before committing, so
the tests, docs, and cleanup land in the same commit as the change, or before pushing if you already
committed.

Treat it as the reflex for any change that skipped the flow. It is the low-friction stand-in for
remembering to hand-run review, tests, and docs every single time — which is the whole point, so run
it even when the change feels too small to bother.

**The description is optional.** A bare `/retrofit` works. If no description is given, infer intent
from the commit messages on the range and from the diff itself, then **state which source you used**.
A single sentence sharpens the reconciliation, since that is how retrofit catches "you said X but
the diff does Y" — but never block waiting for one.

---

## Step 1 — Detect scope (compute the retrofit diff)

"Already landed" usually means the work is **already committed**, so a plain `git diff` would come
up empty and miss everything. Compute the full change set from all three sources.

**Resolve the base branch from the upstream tracking branch, not a local branch name.** A local
default branch is frequently stale — behind its remote — which inflates the diff with everything the
local copy is missing and mis-scopes the whole retrofit. Resolve it as
`git rev-parse --abbrev-ref @{u}`, `git fetch` that remote, then find the fork point with
`git merge-base HEAD @{u}`. Fall back to the local default branch only when there is no upstream.

Then gather:

- **Committed on the branch** — `git diff <merge-base>...HEAD`
- **Uncommitted** — `git diff HEAD` (staged and unstaged)
- **Untracked** — `git status --porcelain`, then **read every new source file in full.** A brand-new
  file appears nowhere in a diff, so without reading it directly you would review half the change.

If the developer passed an explicit range or ref (`HEAD~3..HEAD`, or a single commit), use that as
the scope instead of auto-detecting.

Concatenate these into one **retrofit diff** — the single source of truth for every later step. **If
it is empty, say so and stop.** There is nothing to retrofit.

**Separate source from generated output.** Build artifacts, lock files, and regenerated code are
*output*, not authored behavior. List them so nothing looks hidden, then analyze the **source**.

**Slot:** `.agents/config/paths.md` → `## Generated output`
**If empty:** treat as generated anything matching common build-output conventions — a dist or build
directory, lock files, files marked as generated in a header — and anything git reports as churn with
no corresponding intent in the description. When unsure, list it and ask rather than silently
analyzing or silently skipping it.

Report scope back in one or two lines before continuing: how many source files changed, spanning
which areas, and which paths you are treating as generated and skipping.

## Step 2 — Reconcile intent against the diff, and classify

Put intent and truth side by side.

**Classify what actually changed** — by layer and kind, using the project's own vocabulary where it
has one (see the `workflow` skill and any stack guidance).

**Then produce a reconciliation table.** These are the cheapest, highest-value findings retrofit
produces:

| Claimed in description | Present in diff? | Notes |
|---|---|---|
| "made the section label editable" | ✅ field added to the schema and bound in the template | matches |
| — | ⚠️ diff also regenerates 40 model files | not mentioned; expected side effect of a schema change — confirm intentional |
| "added a fallback when the label is empty" | ❌ not found | described but absent — lost, or still needed? |

Two discrepancy classes, both surfaced **prominently**:

- **Claims with no supporting change** — they said they did X; X isn't there. Did they forget to
  save, or is it on another branch?
- **Changes the description never mentioned** — an intentional side effect, a leftover debug line, or
  an accidental edit?

**Do not resolve these yourself.** State them plainly so the developer can.

**Then classify the work type** using the *Work types* table in the `workflow` skill — this is the
pivot deciding which documentation the change earns: `new-capability`, `change-to <existing-slug>`,
or `fix-infra`. The *tell*: if the change reads as a transition rather than standing behavior, it is
not a `new-capability`. Carry this classification through Step 5 — it drives everything about
documentation.

## Step 3 — Code review (reuse the reviewers)

Run the same three reviewers `/code-review` orchestrates — `accessibility-reviewer`,
`code-reviewer`, `perf-reviewer` — **in parallel**, but feed them the **retrofit diff from Step 1**
rather than letting them recompute their own staged-and-unstaged scope. The change may already be
committed, in which case a recomputed scope would come up empty.

Give each the retrofit diff, the full text of any new files, and brief repo context. They follow the
`reviewer-discipline` skill, so severity and evidence standards are already consistent.

Collect findings by severity. You will fold them into the proposal in Step 6, tagging each as
*retrofit can apply* or *needs human decision*.

*If every change is still uncommitted, running `/code-review` directly is equivalent — orchestrating
the reviewers here is what keeps retrofit correct regardless of commit state.*

## Step 4 — Surface edge cases

Reason from the **actual change** about cases it likely doesn't handle. This is thinking grounded in
the diff, not a checklist emitted blindly — but these are the recurring shapes, so use them as
prompts:

- **A new author-editable field** (the canonical case): what happens when it is left empty or never
  set? Is there a fallback to whatever was previously hardcoded? Is **existing content that predates
  the field** migrated, or does it render blank? Very long values? Escaping? And where the project has
  per-section or per-tenant overrides, does the right one win?
- **A template or view edit**: null model, empty collection, and whether the styling and structural
  context the surrounding system depends on is preserved.
- **A logic or service change**: null and boundary inputs, exceptions, caching implications.
- **An API change**: input validation, authorization, versioning.
- **Client-side code**: hydration failure, the shape of the data payload crossing into the client,
  and that **no secret crosses into client markup**.

List the concrete edge cases *this* change raises, each tied to where in the diff it applies.

## Step 5 — Test and documentation gap analysis (draft only)

### Tests

Find what already covers the changed code. Then decide, per the change:

- **Existing tests to modify** — behavior changed under a test asserting the old behavior.
- **New tests to add** — new behavior with no coverage. Draft them following the project's own test
  conventions.
- **Pragmatically, no automated test** — for a purely visual tweak already verified by eye, say so
  honestly. Propose at most a lightweight smoke test and let the developer decide, rather than
  manufacturing a brittle one.

**Draft the test code in the proposal. Do not write files yet.**

### Documentation

Branch on the work type from Step 2. This mirrors the `/feature` guard exactly, so retrofit does not
pollute the capability docs:

- **`new-capability`** → draft a new feature doc (Given/When/Then, business language, per the
  `workflow` skill's template and the `bdd-principles` skill).
- **`change-to <existing-slug>`** → draft an update to that capability's existing doc, folding in
  **only** user- or operator-observable behavior. Do not draft a new file. Keep architecture and
  migration criteria out — they are point-in-time.
- **`fix-infra`** → **no feature doc.** Draft a runbook under `docs/` instead.

Then check the **project's guidance file** itself: did the change introduce a convention, footgun, or
wiring that belongs there — a new endpoint group, a new directory that must satisfy a build
constraint, a new environment variable or secret, a new configuration option? If so, draft that
addition. Also check the README and `docs/` for anything now stale.

**Draft every doc edit for review. Apply nothing yet.**

## Step 6 — Present the proposal

Assemble one prioritized checklist in **two clearly labeled buckets**, because the whole point is
that the developer stays in control:

**A. Retrofit can apply on your confirmation** — mechanical, low-judgment work:

- Write the drafted tests
- Apply the drafted doc and guidance edits
- Small cleanups **tied to a cited review finding** — removing an unexplained debug line the
  reconciliation flagged, for instance

**B. Needs a human decision** — judgment calls retrofit will not make:

- Description-versus-diff discrepancies from Step 2
- Behavioral fixes from Step 3 findings, Blocker and Major especially
- Edge cases from Step 4 implying a code change or a content migration
- Work-type ambiguity, or whether a large change also warrants a backfilled spec for historical
  rationale

Order by impact. Give each item a one-line rationale and, where useful, the file and line it touches.
Keep review findings traceable to the reviewer that raised them.

End by asking explicitly:

> "Which of these should I apply? (e.g. 'all of A', 'A1 and A3', or 'none') I won't touch anything
> until you tell me."

**Do not apply anything before the developer answers.**

## Step 7 — Apply what was confirmed

Only after explicit approval, apply **exactly** the approved items — nothing more, no drive-by
refactors.

- Write the approved test files and doc edits.
- If tests were added for behavior that already exists, run them and report GREEN. If a test encodes
  a fix the developer also approved, follow RED → fix → GREEN.
- **A test written after the code still has to fail first.** Break the behavior or assert a wrong value,
  watch it go red, then restore. A test that has never failed proves only that it runs — and a test
  written against existing code is the easiest place to write one that cannot fail. See the
  `tdd-principles` skill, which also covers why a rule read out of code is not a tested rule.
- Run the automated gates the change touches and report each result.

  **Slot:** `.agents/config/stack.md` → `## Build`
  **If empty:** infer the build and test commands from the repo root and state which you used; if
  genuinely ambiguous, ask rather than guessing.

- Leave everything **uncommitted** for the developer to review. **Retrofit does not commit.**

If generated-output churn was flagged in Step 1 as incidental, remind the developer to discard it
rather than staging it.

Then end with a `Next:` line:

- If code changes are still needed from bucket B: `Next: address the open decisions above, then run
  /code-review, then /commit-message.`
- Otherwise: `Next: /code-review (fresh) to confirm the retrofitted state, then /commit-message.`

---

## Rules

- **Propose before you touch anything.** Reading is free; writing waits for confirmation.
- **Ground every finding in evidence** — file path plus line or snippet. No guessing about code you
  didn't read.
- **New files must be read in full** — they never appear in a diff.
- **Never treat generated output as behavior.**
- **Stay within the changed surface.** Surface concerns outside the diff as notes; don't fix them
  here.
- **Respect the work-type table**, so capability docs stay a catalog of capabilities and never a
  changelog of work.
