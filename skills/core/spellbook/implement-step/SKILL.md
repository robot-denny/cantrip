---
name: implement-step
description: Execute a single step from a plan in a clean, isolated context so the main conversation stays uncluttered across a long plan. Dispatches the step with just the context it needs, enforces the plan's TDD and validation contract, and relays a structured report. Third stage of the spec → plan → implement chain.
disable-model-invocation: true
argument-hint: "<plan> <step-number>"
allowed-tools: Read, Glob, Bash(ls:*), Bash(git status:*), Agent(*)
---

You are dispatching a single plan step to a fresh context so the main conversation stays clean.
The worker does the work; you orchestrate.

Artifact locations follow the layout in the `workflow` skill — consult it rather than assuming
paths.

User input: $ARGUMENTS

## Step 1 — Parse the arguments

Expect two whitespace-separated tokens:

1. **plan** — the increment's plan (a slug or a path)
2. **step_number** — an integer

If either is missing or malformed, abort with a one-line message showing the expected usage, and
stop. If the plan doesn't exist on disk, abort with a one-line message and stop. **Do not guess at
alternative paths.**

## Step 2 — Read the plan and locate the step

Read the plan in full.

Locate the heading `### Step {step_number} — <title>`. Extract the block from that heading up to,
but not including, whichever comes first: the next `### Step ` heading, the next top-level `---`
that begins a new section, or end of file.

Also extract:

- The **Context** section
- The **Key Decisions** section
- The plan's **Spec** path and **Branch** name, if listed near the top

If the step number doesn't exist, abort with a message listing the step numbers you did find, and
stop.

**If the located step is a spell-cast rather than implementation work** — its content is "run
`/feature update …`" or similar — **do not dispatch a worker.** Dispatching one would have a code worker
execute a spell, which is the wrong mechanism. Say so and hand it back:

> Step N is a spell-cast, not implementation work. Cast it directly: `/<spell> <args>`.

A well-formed plan leaves the behavior-recording step unnumbered for exactly this reason, but older
plans number it.

## Step 3 — Sanity-check the working tree

Run `git status --short`. If the tree is dirty, surface this before dispatching:

> Working tree is dirty. The worker will edit files on top of your uncommitted changes. Continue?
> (yes/no)

Wait for confirmation. If the tree is clean, skip the prompt and proceed.

## Step 4 — Compose the worker prompt

Build a **self-contained** prompt. The worker has no access to this conversation — everything it
needs must be in the prompt.

````
You are executing **Step {N}** of the plan at `{plan}`. The main conversation dispatched you so it
can stay clean — work in this isolated context and report back.

## Plan context

{verbatim contents of the plan's Context section}

## Key decisions already made (do not re-derive)

{verbatim contents of the plan's Key Decisions section}

## Your step

{verbatim contents of the Step N block — heading, prompt, "What to build", "Test first" if
present, "Validation"}

## Behavioral envelope

- **Follow TDD if the step says "Test first"**: write the failing test, run it to confirm RED,
  then implement, then run again to confirm GREEN. Don't skip the RED check.
- **Run every command listed under "Validation"** at the end. Report each one's result.
- **For any validation you cannot mechanically verify, produce evidence — never attest.** A step whose
  check is "verify by eye" or "confirm it looks right" cannot be judged from here: you have no eyes, and
  "looks good" is an unverifiable claim that reads exactly like a real result. Instead **attach an
  artifact the orchestrator can judge** — capture a screenshot, save rendered output, print the actual
  values. If producing evidence needs a fixture that does not exist, create one, capture, then clean it
  up. Say plainly which validations are evidenced and which you could not evidence.
- **Do not commit — unless the step explicitly instructs it.** By default, leave changes in place: the
  user reviews, then runs `/code-review` and `/commit-message`. But some plans genuinely commit per step —
  a migration delivered as a sequence of pull requests, for instance. **If the step says to commit, the
  step wins**, and say in your report that you did. What must not happen is the step and this envelope
  quietly disagreeing, leaving it unclear whether a commit was expected.
- **Stay inside the step's scope.** Do not refactor surrounding code, do not drive-by fix
  unrelated issues, do not add anything the step does not require. If you find something
  concerning, mention it in your report and move on.
- **If the step removes anything, search the tests for it before declaring done.** Removal is not
  symmetric with addition: adding code cannot break a test that does not exist yet, but **removing a
  symbol, rule, class, or file breaks any test asserting its presence** — and such a test lives nowhere
  near the code it guards. Grep the test suite for what you removed and run whatever references it. A
  removal that passes the tests you thought to run is the classic way a green local run becomes a red
  CI run.
- **Read the project's guidance files** (`AGENTS.md`, `CLAUDE.md`, or equivalent) if you need
  conventions or formatting rules.
- **If you get stuck**, stop and report what you tried and what blocked you — don't thrash. A
  clean report on a blocked step is more useful than a half-implementation.

## Reporting format

When you finish, whether success or blocked, end your response with:

```
## Step {N} — <DONE | BLOCKED>

**Files changed**:
- path/to/file (created | modified | deleted)

**Validation results**:
- <command>: <pass | fail | n/a> — <one-line note if useful>

**Notes** (optional):
<anything the next step or the human reviewer should know — an open question, a deviation from the
plan's letter, a follow-up worth filing>
```
````

Before dispatching, check whether the project has standing rules the worker must respect — test
resilience conventions, formatting discipline, structural requirements — and fold them into the
envelope.

**Slot:** `.agents/config/conventions.md` → `## Implementation rules`
**If empty:** rely on the project's guidance files, which the envelope already points the worker
at. Do not invent rules.

## Step 5 — Dispatch

Dispatch the composed prompt to a fresh general-purpose worker context, and wait for its result —
you need it to relay.

Do **not** isolate to a worktree. The worker operates on the current checkout; if the user wanted
isolation they would have arranged it before invoking this.

*Portability note:* if worker dispatch is unavailable, the composed prompt is designed to be
pasted into a new session by hand. That degrades the convenience, not the contract — which is why
the prompt is self-contained.

## Step 6 — Relay the result

Surface the worker's report **verbatim** — the `## Step N — DONE | BLOCKED` block is the
load-bearing part. Then add a one-line `Next:` pointer:

- **DONE**: `Next: review changes (git diff), run /code-review when satisfied, then
  /implement-step {plan} {N+1}.`
  - If step N was the plan's final step: `Next: review changes (git diff), run /code-review, then
    /commit-message. After commit, archive the increment.`
- **BLOCKED**: `Next: read the worker's notes, resolve the blocker, then re-invoke
  /implement-step {plan} {N}.`

Do not print the worker's full transcript — only its final report block and your `Next:` line.

## Rules of thumb

- This executes **one** step. If the user wants steps chained automatically, that is a different
  tool — don't try to be clever.
- The worker's context is bounded by what you pass. Too little and it works blind; the whole plan
  and you bloat it with irrelevant steps. **Context + Key Decisions + Step N is the right cut.**
- The plan's **Validation** section is the truth about whether the step succeeded. Don't
  second-guess it.
