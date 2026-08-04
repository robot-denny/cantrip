---
name: setup
description: Configure the toolkit for this project — detect what can be read from the repository, mine what is already written down in its guidance files, and ask only for what neither supplies. Writes the L2 config slots and the workspace scaffold, preserves any tailored agents the project already has, and reports what it could not determine. Run once after installing, and again after adding a stack pack.
disable-model-invocation: true
argument-hint: "(no arguments — run it in the project root)"
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(git status:*), Bash(git branch:*), Bash(git log:*), Bash(git remote:*), Bash(git check-ignore:*), Bash(ls:*)
---

Configure the toolkit for this project by filling its L2 slots and placing its workspace scaffold.

**Detection over interrogation.** Most of what the toolkit needs is already discoverable — either in the
repository's structure or in prose someone has already written. Asking for what you could have read is
the failure mode this spell exists to avoid: an interview long enough to be abandoned leaves a project
worse configured than a short one.

So work in three tiers, and only reach the next when the previous cannot answer.

## Scope — what this configures, and what it does not

**Fill only the slots the installed skills actually read.** The slot files are the toolkit's
configuration, not a second home for the project's documentation.

A fact that no installed skill consumes belongs in the project's guidance file (`AGENTS.md`,
`CLAUDE.md`) or a runbook under `docs/` — even a genuinely important one. How secrets are managed, how
promotion between environments works, who restarts what: real, load-bearing, and **not** slot material,
because nothing reads it from there and a slot nobody reads is documentation misfiled as configuration.

When you meet such a fact during the interview, say where it belongs rather than inventing a heading.

## Step 0 — Establish what is installed

Read `skills-lock.json` if present, and list the installed skills. Two things follow from it:

- **Which slots to fill.** A core-only install does not need pack headings.
- **Which pack facts to record anyway.** If the project clearly has facts belonging to a pack that is
  *not yet installed*, **write them under their correct pack heading regardless.** An unread heading
  costs nothing, and it is already correct when the pack lands. Do not misfile a pack fact under a core
  heading to give it a home — that is harder to find later than an unread section.

Run `scripts/check-install.sh` if it is available and report anything broken before configuring; there
is no point configuring a broken install.

## Step 1 — Detect what the repository already answers

These are readable without asking. **Fill them, then show the user what you filled for confirmation** —
confirming a draft is far faster than answering a question, and it surfaces a wrong inference
immediately.

| Slot | Read it from |
|---|---|
| `conventions.md` → `## Branch naming` | `git branch -a` for the prefix convention; `git remote -v` for whether any remote must never be pushed to |
| `conventions.md` → `## Commit format` | `git log --oneline -30` — prefixes, emoji, ticket references, subject length |
| `conventions.md` → `## Commit trailers` | `git log` for trailers already in use |
| `stack.md` → `## Build` | Solution and project files, `package.json` scripts, `Makefile` — **and any pre-push or CI hook**, which is where the authoritative command usually lives |
| `stack.md` → `## Tests` | Test project and spec locations, test runner config |
| `paths.md` → `## Code layout` | The directory structure, and where the closest analogue of each kind of thing lives |
| `paths.md` → `## Generated output` | `.gitignore`, plus build and report directories |
| `paths.md` → `## Workspace` | Whether the default layout already exists, or a different convention is in use — see Step 4 |

**Prefer the CI or hook command over the one in a README.** A README drifts; a hook is executed.

## Step 2 — Mine what is already written down

**This is where the leverage is.** The remaining slots are the high-value ones, and they are **not
detectable from structure** — they are hard-won constraints that a fresh clone does not reveal. But they
are frequently already written, in prose, somewhere in the repo.

Before asking anything, read:

- The project's guidance file — `CLAUDE.md`, `AGENTS.md`, or equivalent
- Runbooks under `docs/`
- Any reviewer or agent memory the project keeps
- Architecture notes, decision records, a README's conventions section

Harvest these:

| Slot | What you are looking for |
|---|---|
| `conventions.md` → `## Planning gotchas` | Constraints a plan must satisfy — a directory that must match a build glob, a verification only one command surfaces, a version rule a validator enforces. **Almost never detectable; almost always written down somewhere.** |
| `conventions.md` → `## Implementation rules` | Standing rules — warnings-as-errors, style to match, a contract new components must honor, a hook that must pass |
| `conventions.md` → `## Unit of work` | How the project describes a slice of work, and which layers one spans |
| `conventions.md` → `## Memory` | Where agent memory lives, and whether it is committed |
| `reviewer-rules/` → the shared context section | A two-line repo orientation for reviewers: stack, entry point, architectural shape |
| `reviewer-rules/accessibility.md`, `code.md`, `performance.md` | Per-reviewer project rules — an architectural seam that must not leak, a component contract, a documented exception. **Offer these but do not force them**; a project that keeps its own tailored reviewers may not need them at all, since those already carry their rules |
| `reviewer-rules/` → `## Reviewer names` | Only needed if the project's reviewers are named such that role-matching could be ambiguous. `/code-review` discovers by role, so leave this empty unless discovery actually picks wrong |

**Propose what you harvested, with its source.** "From `CLAUDE.md` § *CI hygiene*: …" lets the user
correct a misreading immediately, and tells them the fact is now in two places — which is worth saying,
since the slot is the copy the toolkit reads.

### Pack slots — read them from the pack, do not hardcode them

A stack pack declares its own slots, and **core must not know their names.** Naming them here would put
technology facts in a core file and would need editing for every future pack.

So **read the installed pack's skills and collect their slot declarations.** Every skill states the slots
it reads in the same `**Slot:**` / `**If empty:**` form used throughout, which makes the pack's
configuration surface self-describing. Fill what you find by the same three tiers.

Per Step 0, if the project clearly has facts belonging to a pack that is **not yet installed**, record
them under the heading that pack will read — even though you cannot know it from here, the user or the
project's guidance file usually can. If neither can, leave the fact for a later run rather than misfiling
it under a core heading.

An unfilled pack heading is never a finding: the install checker only surveys a pack's slots once the
pack that reads them is present.

## Step 3 — Ask only for the residue

Whatever tiers 1 and 2 could not answer, ask — **one question at a time**, and only for slots an
installed skill actually reads.

Say plainly that **every slot may be left empty**, and that the toolkit works with all of them empty.
This is true, it is the contract's acceptance test, and knowing it changes how someone answers: they
stop inventing conventions to fill a blank and say "we don't have one yet," which is the more useful
answer.

For anything left empty, record *why* — "no convention established yet" is materially different from
"not asked", and the next person to run this should be able to tell them apart.

## Step 4 — Place the workspace scaffold

Create what the `workflow` skill's layout expects and the project lacks: the increment workspace, the
capability-doc directory, a roadmap, and a git-ignored scratch directory.

**If the project already has a differently-named workspace convention** — its own specs or plans
directories — **do not silently create a second one beside it.** Say what you found and offer the choice:

> This project already uses `<existing>`. The toolkit's default is `<default>`. Adopt the default for new
> work and leave the existing history in place, or point the `## Workspace` slot at your existing
> directories?

Both are legitimate. Record the decision in the slot with a note about the split, so the next reader
understands why two conventions coexist rather than treating it as drift.

## Step 5 — Preserve what the project already has

**Detect the project's own agents before touching anything.** If it has a reviewer under a name the
toolkit also uses, or a differently-named one filling the same role, that agent almost certainly carries
project rules and calibrated memory the toolkit's generic version does not.

**Never overwrite it, and never link over it.** Report the situation, recommend keeping theirs, and note
that `/code-review` discovers reviewers by role rather than by exact name — so a tailored reviewer under
its own name is found and used.

If a reviewer's memory directory is keyed to a name that is changing, **say that renaming the directory
is required or the memory is silently orphaned** while review appears to work normally.

The same caution applies to any project-authored skill sharing a name with a toolkit one: report, do not
replace.

## Step 6 — Report

```
Toolkit setup
  Installed:      N core skill(s){, plus <pack>}
  Slots filled:   N of M   (detected: N · harvested: N · asked: N)
  Left empty:     N        <- each with a reason
  Scaffold:       <created | already present | using the project's existing layout>
  Preserved:      <the project's own agents and skills, untouched>

Facts noted but not slot material:
  <fact> -> belongs in <the guidance file | docs/>

Next: /explore for a new problem, or /spec to start an increment.
```

Then suggest running `scripts/check-install.sh` to confirm the result.

## What not to do

- **Do not ask for what the repository answers.** Every avoidable question spends the user's patience on
  something you could have read.
- **Do not invent a convention to fill a slot.** An empty slot degrades gracefully by design; a fabricated
  one gets followed. This is the contract's hardest rule and setup is where it is most tempting to break,
  because a blank looks like a failure.
- **Do not fill slots no installed skill reads**, and do not invent headings for facts that do not fit.
- **Do not overwrite anything the project already has** — agents, skills, workspace directories, or
  guidance files.
- **Do not treat a greenfield project as under-configured.** A new project genuinely has no conventions
  yet, and recording "not established yet" is the correct, useful answer. The first few increments
  establish them; run this again then.
