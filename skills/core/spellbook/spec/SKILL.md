---
name: spec
description: Turn a short idea into a saved feature spec — a titled, slugged spec document with acceptance criteria and draft BDD scenarios, plus a working branch and a work-type classification that decides which durable artifacts the work earns. First stage of the spec → plan → implement chain.
disable-model-invocation: true
argument-hint: Short feature description
allowed-tools: Read, Write, Glob, Bash(git status:*), Bash(git branch:*), Bash(git switch:*), Bash(git rev-parse:*)
---

> **Before drafting:** consult the `bdd-principles` skill for guidance on writing scenarios
> using Example Mapping, Specification by Example, and Ubiquitous Language.

You are spinning up a new feature spec for this project from a short idea provided below.
Always adhere to the rules and requirements in the project's guidance files (`AGENTS.md`,
`CLAUDE.md`, or equivalent).

Artifact locations throughout follow the layout in the `workflow` skill — consult it rather
than assuming paths.

User input: $ARGUMENTS

## High level behavior

Turn the user input above into:

- A human-friendly feature title in Title Case
- A safe git branch name not already taken
- A detailed markdown spec document in the increment's working directory

Then save the file(s) to disk and print a short summary of what you did.

## Step 1. Check the working tree

Check the current git branch, and **abort this entire process** if there are any uncommitted,
unstaged, or untracked files in the working directory. Tell the user to commit or stash their
changes before proceeding, and **do not go any further.**

**If the only untracked file is a `discovery.md` from a just-run `/explore`, name that specifically**
and recommend committing it: discovery precedes the branch this spell creates, so it belongs on the
base branch. A generic "commit or stash your changes" reads as a defect when the file was produced by
the spell the user was just told to run — which is exactly the sequence `/explore` ends by suggesting.

## Step 2. Parse the arguments

### First — is this continuing a discovery?

`/explore` writes a `discovery.md` into an increment's working directory and ends by pointing here with
that increment's slug. **Look for it before treating `$ARGUMENTS` as a fresh description.**

If `$ARGUMENTS` names an existing increment whose directory holds a `discovery.md`, read it, and take
these from it rather than re-deriving:

- **`feature_slug`** — the existing directory name. Deriving a fresh slug from the same words creates a
  **second** increment directory beside the first and orphans the discovery, while looking entirely
  normal.
- **`feature_title`** — the discovery's title.
- **The problem framing, the options considered, and the open questions** — the discovery has a section
  addressed to this spell. Carry those forward instead of asking again. Re-litigating discovery inside
  the spec is the specific waste this artifact exists to prevent.

**Say which discovery you picked up**, so a wrong match is visible immediately rather than after a spec
has been written against it.

If `$ARGUMENTS` names no such increment, continue below and treat it as a fresh description. That is the
common case — `/explore` is optional, and most increments start here.

### Then, from `$ARGUMENTS`, extract:

1. **`feature_title`** — a short, human-readable title in Title Case.
   Example: "Card Component for Dashboard Stats".

2. **`feature_slug`** — a git-safe slug:
   - Lowercase, kebab-case, only `a-z`, `0-9` and `-`
   - Replace spaces and punctuation with `-`
   - Collapse repeated `-` into one, trim `-` from both ends
   - Maximum length 40 characters

   Example: `card-component-dashboard`.

3. **`branch_name`** — derived from `feature_slug` per the project's convention.

   **Slot:** `.agents/config/conventions.md` → `## Branch naming`
   **If empty:** infer the prefix convention from existing branches (`git branch -a`) and use
   `<prefix>/feature/<feature_slug>`; if no convention is visible, use `feature/<feature_slug>`.

   This heading covers branch *conventions* broadly — naming, and **which remote branches are pushed
   to**. A repo with several remotes may have one that must never be pushed to; that belongs here, not
   in a slot of its own.

If you cannot infer a sensible `feature_title` and `feature_slug`, **ask the user to clarify
rather than guessing.**

## Step 3. Switch to a working branch

Before writing any content, switch to a new branch using `branch_name`. If that name is already
taken, append a version number — `<branch_name>-01`.

**Do not nest a working branch inside another working branch.** If the current branch is not the
project's default, you are probably already on a branch created for this work — or for a trial or
experiment that should stay put. Say what you see and ask, rather than branching from a branch:

> Currently on `<branch>`, which is not the default. Create `<branch_name>` from here, or stay on this
> branch?

If the project's conventions indicate that work happens on the current branch rather than a
per-increment branch, skip this step and say so in the final summary.

## Step 4. Draft the spec content

**Before writing, check the workspace you are about to write into.** If the layout resolves to a
directory that does not exist yet *and* a differently-named workspace directory already exists beside
it, stop and ask — creating a second workspace convention alongside an established one fragments the
project's history:

> This project already has `<existing>`. The layout would create `<new>`. Use the existing directory,
> or establish the new one?

Create a markdown spec document that planning can use directly, saved in the increment's
working directory under the `feature_slug`. Use the exact structure of the `templates/spec.md`
asset in the `workflow` skill. **Do not add technical implementation details such as code
examples.**

After writing the Acceptance Criteria section, use the **Example Mapping** technique to derive
draft scenarios:

- Treat each acceptance criterion as a **Rule** (blue card)
- Write concrete **Scenarios** (green cards) in Given/When/Then format that prove each rule
- Use **Specification by Example** — concrete values, not abstractions
- Use **Ubiquitous Language** — business terms ("content editor", "visitor", "page"), not
  technical terms ("document type", "controller", "API endpoint")
- Flag any uncertainty discovered while writing scenarios as an **Open Question** (red card)

Add these to the spec's "Scenarios (Draft)" section.

## Step 5. Classify the work type

Before deciding which downstream artifacts this work earns, classify it using the *Work types*
table in the `workflow` skill. Feature docs hold **evergreen capability behavior, one file per
capability named by area** — never a record of work done.

Write a `**Work type**:` line into the spec (in the Summary area, per the template) with
exactly one of these three literal values:

- **`new-capability`** — introduces a capability the project doesn't have yet (a new component,
  page type, or area of behavior). Earns a new feature doc, named by the capability.
- **`change-to <existing-slug>`** — modifies an existing capability (refactor, upgrade,
  migration, a new field on an existing thing). Folds into that capability's existing feature
  doc; **no new feature doc**. Name the existing slug — grep the feature docs by capability area
  to find it.
- **`fix-infra`** — a fix, infra, CI, or cleanup task with **no standing behavior change**.
  Earns no feature doc; its durable record is a runbook under `docs/` and/or a section in the
  project's guidance file.

**The tell:** if the spec's acceptance criteria read as *transitions* — "goes from red to…",
"leaves no trace after the change ships", "nothing the user sees changes", "compiles on the
stable stack" — rather than *standing behavior* ("a visitor can search from /search"), it is
**not** a `new-capability`. Pick `change-to` or `fix-infra`.

**Also record a `**Feature doc**:` line naming the capability doc this work belongs to** — the area,
not the increment. Per the `workflow` skill's naming tell, that name is routinely *different* from
`feature_slug`: an increment called `placeholder-graphics-imageless-cards` may well belong to a
capability doc called `article-card`.

- For `new-capability` where the area is undocumented, this is the area-level doc you are about to
  create.
- For `change-to`, it is the existing doc being amended.
- For `fix-infra`, write `none`.

Recording both lines is what lets `/plan` and `/feature` honor the classification without re-deciding
it — and the `Feature doc` line specifically is what stops the final step targeting a doc named after
the increment instead of the area.

## Step 6. Create the draft feature doc skeleton *(only for `new-capability`)*

**Skip this step entirely unless Step 5 classified the work as `new-capability`.** For
`change-to`, the behavior folds into the existing capability's doc during `/plan`; for
`fix-infra`, no feature doc is created at all. Creating one for either would pollute the
feature docs with a change or fix masquerading as a capability. In both cases the draft
scenarios still live in the spec from Step 4 — nothing is lost.

If (and only if) the work type is `new-capability`, create the draft feature doc **at the name recorded
on the `**Feature doc**:` line** — the capability or area, never the increment — using the structure of
the `templates/feature.md` asset in the `workflow` skill. Populate it with:

- The feature summary from the spec
- The draft scenarios from the spec's "Scenarios (Draft)" section
- A draft banner at the top: `> **Draft** — These scenarios have not yet been verified against
  an implementation. They will be refined during planning and verified after implementation.`
- A Source line pointing at the spec
- An empty test coverage table (no tests exist yet)
- A revision note: `{today's date}: Draft scenarios from initial spec`

This skeleton gives QA and planners the behavioral contract immediately, before implementation
begins.

## Step 7. Final output to the user

After the file(s) are saved, respond with a short summary. **Always report the work type;**
include the `Feature doc (draft)` line **only** when one was actually created.

For `new-capability`:

```
Branch: <branch_name>
Spec file: <path to the saved spec>
Work type: new-capability
Feature doc (draft): <path to the draft feature doc — named by area>
Title: <feature_title>
Next: /plan <feature_slug>
```

For `change-to <existing-slug>` or `fix-infra`:

```
Branch: <branch_name>
Spec file: <path to the saved spec>
Work type: change-to <existing-slug>   (or: fix-infra)
Feature doc: none — <for change-to: behavior folds into the existing capability's doc during /plan | for fix-infra: durable record is a runbook under docs/ and/or the project guidance file>
Title: <feature_title>
Next: /plan <feature_slug>
```

Do not repeat the full spec in the chat output unless the user explicitly asks to see it. The
goal is to save the files and report where they live and what branch to use.
