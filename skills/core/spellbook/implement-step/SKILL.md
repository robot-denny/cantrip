---
name: implement-step
description: Execute one plan step, or a range of steps in order, each in a clean, isolated context so the main conversation stays uncluttered across a long plan. Takes a single step (4), a closed range (1-3), or an open range to the last numbered step (3-). Dispatches each step with just the context it needs, one fresh worker per step, enforces the plan's TDD and validation contract, and relays a structured report per step. Third stage of the spec → plan → implement chain.
disable-model-invocation: true
argument-hint: "<plan> <N | N-M | N->"
allowed-tools: Read, Glob, Bash(ls:*), Bash(git status:*), Agent(*)
---

You are dispatching one plan step, or a range of steps in order, to fresh contexts so the main
conversation stays clean. Each step gets its own worker. The worker does the work; you orchestrate.

Artifact locations follow the layout in the `workflow` skill — consult it rather than assuming
paths.

User input: $ARGUMENTS

## Step 1 — Parse the arguments

Expect two whitespace-separated tokens:

1. **plan** — the increment's plan (a slug or a path)
2. **steps** — which steps to run, in one of three forms:
   - `4` runs step 4
   - `1-3` runs steps 1, 2, and 3, in that order
   - `3-` runs from step 3 to the plan's last numbered step

The second token must match `^(\d+)(?:-(\d+)?)?$`. If either token is missing, or the second does
not match, abort with a one-line message showing the expected usage, and stop. If the plan doesn't
exist on disk, abort with a one-line message and stop. **Do not guess at alternative paths.**

Call the first number **first** and the second number **last**. A single number sets both to the
same value. An open range such as `3-` has no `last` yet; Step 2 resolves it against the plan. The
closed range `N-N` is the single-step form `N` spelled differently: run it and report it exactly as
a single step, with no wording that announces a run.

## Step 2 — Read the plan and locate the steps

Read the plan in full.

Collect every heading of the form `### Step N — <title>`. Those N are the **steps found**. An
unnumbered final step, `### Final — …`, is not one of them and never runs from here.

Resolve the bounds against the steps found, before anything else happens:

- An open range resolves `last` to the highest step found. `3-` on a six-step plan is `3-6`.
- `first` must be at least 1 and must be a step found. `last` must be a step found. `first` must
  not be greater than `last`.
- Every number from `first` to `last` must be a step found. A plan numbered 1, 2, 4, 5 has a gap,
  and `1-5` on it would fail at step 3 with two workers already run; it aborts here instead.

If any of those fails, abort with a message listing the step numbers you did find, and stop. No
worker has started. A closed range never clamps: `3-9` on a six-step plan is an error, not `3-6`,
because the developer named a step that is not there and should be told so before anything runs.
Reversed (`4-2`) and zero (`0-2`) bounds abort with the same message.

The steps to run are `first` through `last`, ascending. For each, locate its heading
`### Step {N} — <title>` and extract the block from that heading up to, but not including,
whichever comes first: the next `### Step ` heading, the next top-level `---` that begins a new
section, or end of file.

Also extract, once for the whole cast:

- The **Context** section
- The **Key Decisions** section
- The plan's **Spec** path and **Branch** name, if listed near the top

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

Steps 4, 5, and 6 run once per step in the run, in ascending order: compose step N's prompt,
dispatch it, wait, relay its report, then move to step N+1. Compose a step's prompt only when it is
about to be dispatched, never all of them up front. A single-step cast is a run of one.

Once for the whole cast, before the first prompt is composed, check whether the project has standing
rules the worker must respect — test resilience conventions, formatting discipline, structural
requirements — and fold them into every step's envelope. The rules do not change between steps, so
read them once.

**Slot:** `.agents/config/conventions.md` → `## Implementation rules`
**If empty:** rely on the project's guidance files, which the envelope already points the worker
at. Do not invent rules.

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
- **Follow the `tdd-principles` skill for what the test asserts.** Assert observable behavior through
  the interface a user of the code would use — never that something merely *exists*, and never an
  expected value computed the same way the implementation computes it. Correct RED→GREEN ordering does
  not make an assertion correct, and this step is where that gets decided.
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

## Step 5 — Dispatch

Dispatch the composed prompt to a fresh general-purpose worker context, and wait for its result —
you need it to relay.

One worker at a time. In a run, the next step's worker starts only after this one has returned and
its report has been relayed. Steps in a plan build on each other, so running them side by side
would have a later worker editing files an earlier one has not finished with.

Do **not** isolate to a worktree. The worker operates on the current checkout; if the user wanted
isolation they would have arranged it before invoking this.

*Portability note:* if worker dispatch is unavailable, the composed prompt is designed to be
pasted into a new session by hand. That degrades the convenience, not the contract — which is why
the prompt is self-contained.

## Step 6 — Relay the result

Surface the worker's report **verbatim** — the `## Step N — DONE | BLOCKED` block is the
load-bearing part. In a run, surface each step's block as its worker returns, before the next step
is dispatched, so the developer watches the run land one step at a time.

The `Next:` line appears **once per cast**, after the last step's report, never after every step.
Write it for the last step that ran, N:

- **DONE**: `Next: review changes (git diff), run /code-review when satisfied, then
  /implement-step {plan} {N+1}.`
  - If step N was the plan's final step: `Next: review changes (git diff), run /code-review, then
    /commit-message. After commit, archive the increment.`
- **BLOCKED**: `Next: read the worker's notes, resolve the blocker, then re-invoke
  /implement-step {plan} {N}.`

Do not print the worker's full transcript — only its final report block and your `Next:` line.

## Rules of thumb

- This executes **the steps it was given**, one at a time, in order, and then stops. A range is the
  developer choosing where the next pause falls. It is not a request to keep going past the range,
  to skip a step, or to run steps side by side. Don't try to be clever.
- The worker's context is bounded by what you pass. Too little and it works blind; the whole plan
  and you bloat it with irrelevant steps. **Context + Key Decisions + Step N is the right cut.**
- The plan's **Validation** section is the truth about whether the step succeeded. Don't
  second-guess it.
