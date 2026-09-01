---
name: testify
description: Read a capability's Test Coverage table as a work queue — report which of its documented scenarios nothing proves, separate the ones that can be tested now from the ones blocked on missing test infrastructure, then write and run tests only for the rows a person approves and record in the doc what each run established. Use when asked what is untested, for the missing tests for a capability, or to close the gap between what a capability doc claims and what anything actually verifies.
disable-model-invocation: true
argument-hint: "<capability> — the name of a documented capability"
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

The user's argument: **$ARGUMENTS** — the name of a capability this project documents.

This spell asks one question and only one: **what does this project claim to do that nothing
proves?** Every other spell in the chain either decides what to build or builds it. This one reads
what has already been decided and reports where the evidence is missing.

The queue is not something this spell invents. A capability doc already ends with a **Test Coverage**
table mapping each of its scenarios to the test that proves it and to a status. That table is the
work queue, and reading it is the whole of the input.

Artifact locations follow the layout in the `workflow` skill — consult it rather than assuming paths.

## What this spell does not own

Three boundaries, and each of them is a place where a plausible next step belongs to somebody else.

- **It holds no knowledge of any test library.** How a test is written for this project's technology
  is a stack pack's answer, or the project's own tests'. Ask; never assume.
- **It never establishes the project's testing architecture.** Where proving a scenario needs a
  harness the project does not have, it says what is needed and stops. Deciding to adopt one is
  spec-sized work.
- **It never writes a scenario.** The doc's scenarios are `/feature`'s, and behavior that was never
  written as a scenario is invisible here. Where this spell notices such behavior in passing, it
  names it and points at `/feature` — it does not quietly add a row to make its own queue longer.

## Step 1 — Resolve the argument to a capability doc

The argument names a **capability** — an area of the system, the way capability docs are named.
Resolve it against the workspace layout described in the `workflow` skill.

Match loosely on the way people actually type a capability's name: casing, spacing, and hyphenation
are all noise. "article card", "Article Card", and `article-card` name one doc.

**When nothing resolves, the usual cause is that the argument named an increment rather than an
area.** The `workflow` skill records that the two are routinely different — an increment called
`placeholder-graphics-imageless-cards` amends a doc called `article-card`. So do not treat an
unresolved name as a missing capability to go and document, and do not quietly work on the nearest
doc as though it had been the one asked for. Instead:

- Say plainly that no capability of that name is documented.
- Offer the documented capabilities whose names are nearest to what was asked for, and let the
  person say which was meant.
- If the project documents no capabilities at all, say that instead, and name writing the first
  capability doc as the thing that has to happen before this spell has anything to read.

In every one of those cases, read no further and write nothing.

## Step 2 — Read the Test Coverage table

Read the whole doc, not only its table. The scenarios under the `Rule:` headings are what a test
would have to assert; the table only records what is currently proved. One without the other is not
enough to propose anything.

Then pair each table row with the scenario it names, and read its status. **The capability doc
template in the `workflow` skill is the authority on what each status claims** — read it there rather
than re-deriving it. What matters here is narrower: what each status means for this queue.

| The row says | What it is to this spell |
|---|---|
| `Covered` | Already proved. Not work. Leave the row alone. |
| `Test failing` | A test already asserts this scenario and did not pass last time it ran. Something exists; this is not a missing test. |
| `Not covered` | Specified, and nothing asserts it. **This is the queue.** |
| `Not covered (code-derived)` | Nobody specified this — it is a reading of the code. Unproved, but not unproved in the same way, and it is never mixed in with the rows above. |
| `Not coverable — <reason>` | The project has already decided. Skip it, never propose it, and carry its recorded reason forward so a reader can judge whether it still holds. |

**Four of those record an observation; the last records a decision.** The rows are listed in the
template's order, which puts three statuses beginning "Not cover-" together, and the third of them
means the opposite of the two above it — somebody weighed this scenario and chose, rather than nobody
having reached it yet. Read the whole of "Not coverable —" before treating a row as an ordinary gap.
Turning one into a proposal quietly converts a decision into a backlog item.

A scenario with no row at all is unproved and belongs in the queue. A row naming a scenario the doc
no longer contains is drift rather than work — note it and move on.

**When the doc has no Test Coverage table, or the table is empty, say so and stop.** That is not the
same as everything being unproved, and it is not the same as everything being proved: the doc simply
does not say, and this spell has no queue to work from. Do not manufacture one by treating every
scenario as untested — a project may perfectly well have tests the doc never recorded, and reporting
them as gaps would be a guess wearing the clothes of a finding. Building that table is `/feature`'s
job: it matches scenarios to tests across the project and writes the result. Name it and let the
person run it.

**When the doc has a table but no scenarios, there is nothing to prove.** Say that in a sentence
rather than reporting an empty queue as a result.

## Step 3 — Learn where tests live and how they are run

Two facts about the project are needed before anything can be proposed, and neither of them is this
spell's to know.

Where tests live in this project, and what they are named:

**Slot:** `.agents/config/stack.md` → `## Tests`
**If empty:** infer from existing test files. If the project has no tests yet, propose a location and
flag plainly that you are establishing a convention rather than following one — never settle it
silently.

Here that flag goes into the report, before anything is written — and the decision itself is not this
spell's to make. A project with no tests and no recorded place to put them needs somebody to choose a
testing convention deliberately, which is `/spec`'s work, not a side effect of asking for one
capability's missing tests.

How the project's tests are run:

**Slot:** `.agents/config/stack.md` → `## Build`
**If empty:** infer the build and test commands from the repo root and state which you used; if
genuinely ambiguous, ask rather than guessing.

If the way to run tests genuinely cannot be worked out, **say that it could not be determined and
invent nothing.** A command guessed at is worse than an absent one: it fails for a reason that has
nothing to do with the behavior under test, and the failure reads as the capability's.

Running a project's tests means running whatever command those two slots resolve to, which is why
this spell's tool grant is not narrowed to a named command — an installed toolkit cannot know the
command ahead of time, so it cannot name it in the grant. **That makes the boundary this spell's to
hold rather than the permission system's: use the shell only to run the test command the slots above
resolve to, and nothing else.** Not to inspect the project, not to move files, not to clean up after
a run. Every other thing this spell does has a tool of its own.

## Step 4 — Take library idiom from the project, never from this spell

Before proposing anything, find out how this project already writes a test.

If an installed stack pack or project skill offers guidance for the technology in play, consult it:
how tests are named and structured, which kind of test is the cheapest one that proves a given kind
of change, and what a test of each kind is allowed to reach for.

**Its absence is not an error.** Where no such guidance is installed, follow the conventions of the
tests the project already has — **read the ones Step 3 already located rather than searching again**,
since finding where tests live and reading how they are written are two questions about the same
files — and **name the tests you took those conventions from** in the report,
so the person reading it can tell a convention that was observed from one that was assumed. If the
project has no tests at all to read, there is no convention to follow yet — that is the case Step 3's
`## Tests` fallback describes, and it goes to `/spec` rather than being settled here.
