---
name: plan
description: Turn a spec into a phased, TDD-first implementation plan — independently-executable steps each runnable in a fresh context, with a paste-ready prompt per step, recorded key decisions, and a final step that records durable behavior according to the work type. Second stage of the spec → plan → implement chain.
disable-model-invocation: true
argument-hint: Path to a spec file, or a short feature description
allowed-tools: Read, Write, Glob, Grep, Bash(git branch:*), Bash(git status:*)
---

You are creating a detailed implementation plan for this project. Always follow the rules in the
project's guidance files (`AGENTS.md`, `CLAUDE.md`, or equivalent).

Artifact locations follow the layout in the `workflow` skill — consult it rather than assuming
paths.

User input: $ARGUMENTS

## High-level behavior

Turn the spec (or description) above into a saved plan file that:

- Breaks the work into independently-executable steps, each runnable in a fresh context window
- Follows TDD: tests are written **before** implementation in each step where testable behavior
  is introduced
- Includes a paste-ready prompt per step
- Records key design decisions so future implementers don't re-derive them

Plan along the project's own natural unit of work — the `workflow` skill's *Project framing*
section covers how to determine that. Do not impose a layer breakdown the architecture doesn't
use.

## Step 1 — Resolve the input

Resolve `$ARGUMENTS` in this order, stopping at the first that matches:

1. **A path** (contains `/` or ends in `.md`): read the file and use its contents as the spec. Extract
   `feature_title` and `feature_slug` from the path.
2. **A bare slug** — a single kebab-case token with no spaces. This is what `/spec` hands off, so it is
   the common case. **Resolve it against the workspace layout to find the existing spec** and read
   that; do not treat it as a description. If no spec resolves for the slug, say so and stop rather
   than silently inventing one — a slug that does not resolve usually means a typo or a spec that was
   never saved.
3. **A description** — free text with spaces. Treat it as the full spec, and derive `feature_slug`
   (lowercase, kebab-case, max 40 chars) and `feature_title` (Title Case) from it.

Also capture the **work type** — read the `**Work type**:` line from the spec
(`new-capability` / `change-to <existing-slug>` / `fix-infra`). If the spec has none, classify it
now using the *Work types* table in the `workflow` skill (the *tell*: transition-style acceptance
criteria are not `new-capability`). Carry the value into the plan header and let it drive the
final behavior-recording step (Step 4, rule 5).

Also read the spec's `**Feature doc**:` line and carry it through unchanged. **It names the capability
doc by area and is routinely different from `feature_slug`** — deriving the doc name from the slug
instead would point the final step at a doc named after the increment. If the spec has no such line,
determine it now using the `workflow` skill's naming tell.

## Step 2 — Understand the codebase context

Before planning, read enough of the codebase to answer:

- What existing patterns does this work extend or resemble? Check the relevant locations for the
  kind of thing being built.

  **Slot:** `.agents/config/paths.md` → `## Code layout`
  **If empty:** infer the layout by finding the closest existing analogue to what you are looking
  for and following its structure; if nothing analogous exists, say so in your output rather than
  inventing a convention.

- Are there existing types, components, or configurations that can be reused instead of created?
- What is the right test file location and naming convention here?

  **Slot:** `.agents/config/stack.md` → `## Tests`
  **If empty:** infer from existing test files; if the project has no tests yet, propose a
  location in Key Decisions and flag it as a new convention being established.

**Do not plan in a vacuum — ground every step in what already exists.**

### Stack-specific planning guidance

If an installed stack pack or project skill offers planning guidance for the technology in play,
consult it **before** writing the plan. The guidance worth looking for:

- **Live state inspection** — where a schema, model, or configuration can be queried live rather
  than inferred from files, so the plan names real identifiers instead of guesses. Record
  anything discovered this way in the plan's **Key Decisions** so implementers need not look it
  up again.
- **Sub-type routing** — whether the kind of thing being built has its own authoritative
  guidance that supersedes general patterns, and which one applies.
- **Typical step order** — the sequence that usually works for this stack.

If no such guidance is available, proceed with the generic sequencing rules below. Their absence
is not an error.

## Step 3 — Identify the layers

Classify the work into the layers that apply — not every piece of work has all of them. Use the
project's own layer vocabulary where one exists (see *Code layout* above and any stack guidance
from Step 2), rather than a generic MVC split.

For each layer the work touches, record: where it lives, and what constraint governs it. The
recurring ones worth checking:

- **Schema or data model** — anything downstream cannot compile or run against types that don't
  exist yet, so this leads.
- **Server-side rendering or logic** — the layer that turns data into output.
- **Client-side assets or components** — anything built, bundled, or hydrated separately.
- **Extension or plugin surfaces** — code loaded by a host platform rather than the app itself.
- **Tests** — per the *Tests* slot above.

## Step 4 — Sequence the steps

Order the layers into implementation steps following these rules:

1. **Schema first** — you cannot write tests or code against types that don't exist.
2. **Tests written before the implementation they cover** — each step that introduces testable
   behavior writes the test first (expect RED), then implements (expect GREEN). Keep
   test-writing and implementation in the **same step** when they are tightly coupled; split them
   when the implementation is large enough to warrant its own step. If the project has no test
   harness yet, treat a build plus a concrete manual check as the RED→GREEN signal and still
   author the target test file so it is ready when a harness lands.
3. **Manual verification checkpoints** — any step that changes visible behavior should end with a
   concrete check the developer can perform before moving on.
4. **Each step must be independently completable** — a clear start state (what was done before)
   and end state (what passes or exists after).
5. **Record the behavior as the final step — branch on work type:**
   - **`new-capability`** → `/feature update <the Feature doc name>` (or `/feature <spec path>` if no
     draft doc exists yet) to verify the capability's living doc against the actual implementation.
     **Use the recorded doc name, not the increment slug.**
   - **`change-to <existing-slug>`** → `/feature update <existing-slug>`. Fold in **only** the
     user- or operator-observable behavior changes. **Do not create a new feature doc.**
     Architecture and migration acceptance criteria — "the service is unit-testable", "the build
     is zero-warning", "the package leaves no trace" — are point-in-time. They stay in the
     shipped spec and must **not** be written into the capability doc as Rules.
   - **`fix-infra`** → **no feature doc.** The durable record is a runbook under `docs/` and/or a
     section in the project's guidance file. The final step writes that instead.

## Step 5 — Draft the plan content

Write the plan in the format below. Do not skip sections.

Where the format calls for a build, test, or run command, use the project's real commands.

**Slot:** `.agents/config/stack.md` → `## Build`
**If empty:** infer the build and test commands from the repo root and state which you used; if
genuinely ambiguous, ask rather than guessing.

Record any command you had to infer in the plan's Key Decisions, so the next increment doesn't
re-derive it.

````markdown
# Plan: {feature_title}

**Spec**: {path to the spec}
**Branch**: {current branch}
**Work type**: {new-capability | change-to <existing-slug> | fix-infra}  — copy verbatim from the
spec's `**Work type**:` line; this decides how the final step records behavior (see Step 4)
**Feature doc**: {the capability doc by area, or none} — copied from the spec; the final step targets
this, not the increment slug

## Context

[2–4 sentences: what this does and why, plus any background from the spec or codebase that
shapes the plan. What already exists that this builds on. Name the unit of work.]

---

## Key Decisions

- **[Decision topic]**: [Chosen approach and why — rule out alternatives briefly if useful]
- (repeat for each non-obvious design choice — include any identifiers or aliases discovered by
  live inspection in Step 2, plus any convention you had to assume because a slot was empty)

---

## Steps

Each step is designed to be completed independently in its own context window.
The step heading contains a ready-to-use prompt you can paste into a new session.

---

### Step N — [Short title]

> **Prompt**: Implement Step N of {plan path}. [One paragraph, fully self-contained: what
> file(s) to create or modify, what APIs or tools to use, what the end state is. Include the
> exact build or test command if relevant.]

**What to build**: [Enumerate files, scripts, or operations. Be specific: file paths, method
names, property aliases, endpoints, attribute names.]

**Test first** *(only for steps that introduce testable behavior)*:
- Write [the target test file], and/or define the concrete manual check
- The test should [describe what it asserts]
- Run [the test command] and confirm RED before implementing

**Validation**:
- [Automated]: [the build or test command] — and what a passing result looks like
- [Manual] *(if applicable)*: [where to look and what to confirm]

---

[Repeat for each implementation step]

---

### Final — Record the durable behavior *(a spell you cast, not an implement-step)*

**Do not number this as an implementation step.** It is cast directly — `/feature update <the Feature doc
name>` — after the implement-step loop finishes. Numbering it would invite `/implement-step <plan> N`,
which dispatches a code worker to run a spell: the wrong mechanism, and it blurs the chain's own
boundary between building and recording.

Pick the variant matching the plan header's **Work type**. Author it for that one variant only.

**If `new-capability`:**

> **Prompt**: Run `/feature update {the Feature doc name from the plan header}` to verify the living
> behavioral doc reflects the actual implementation. Review each scenario against the code and test results. Update any
> scenario where the implementation diverged from the draft. Fill in the test coverage table with
> real test paths and line numbers, or mark target tests pending if no harness exists yet. Remove
> the "Draft" banner. Commit the verified doc.
>
> **Validation**: Every scenario matches observable behavior; the coverage table has no
> unexpected "Not covered" gaps.

**If `change-to <existing-slug>`:**

> **Prompt**: Run `/feature update <existing-slug>`. Fold **only** the user- or
> operator-observable behavior changes from this work into the existing capability doc — do not
> create a new feature doc. Leave architecture and migration acceptance criteria in the shipped
> spec; they are point-in-time and must not appear as Rules. Add a revision note dated today
> describing what changed.
>
> **Validation**: The capability doc describes current behavior with no transition-style ("goes
> from… to…") Rules; no new feature doc was added.

**If `fix-infra`:**

> **Prompt**: Do **not** create or touch any feature doc. Capture the durable record as a runbook
> under `docs/`, and/or a section in the project's guidance file if it is operational guidance.
> Document what the change does and how to operate or reproduce it. Commit the runbook.
>
> **Validation**: A runbook exists; no feature doc was touched.

---

## File Summary

| Action | File |
|--------|------|
| Create | `path/to/file` |
| Modify | `path/to/file` |
| Create (delete after running) | `path/to/throwaway-script` |
| _(work type: `new-capability`)_ Create/Update | the new capability's feature doc |
| _(work type: `change-to <existing-slug>`)_ Update | the existing capability's doc (fold observable behavior only; **no new file**) |
| _(work type: `fix-infra`)_ Create/Update | a runbook under `docs/` (**no feature doc**) |
````

Include **only** the behavior-record row matching the plan's work type — the other two are
alternatives, not all three at once.

## Step 6 — Validate the plan before saving

Check that:

- Every step has a paste-ready prompt carrying enough context to act on without reading the rest
  of the plan
- TDD steps write the test, or define the manual check, *before* implementation
- No step depends on a result not established in a prior step
- Manual verification points exist wherever a visible-behavior check is natural
- The file summary lists every file to be created or modified
- Every command named in the plan is one that actually works in this project
- Any convention assumed because a slot was empty is recorded in Key Decisions

Then check the plan against the project's own known pitfalls.

**Slot:** `.agents/config/conventions.md` → `## Planning gotchas`
**If empty:** skip this check — do not invent constraints. If the codebase makes a
non-obvious structural requirement evident (a directory that must match a build glob, a registry
a new file must be added to), note it in Key Decisions and suggest recording it in the slot.

## Step 7 — Save and report

Save the plan into the increment's working directory alongside its spec.

Report in this format:

```
Plan: <path to the saved plan>
Steps: N
Branch: <current branch>
Next: /implement-step <feature_slug> 1  (run each step in a fresh context to keep the main one clean)
```

Do not print the full plan to chat — just the summary above. The plan lives in the file.
