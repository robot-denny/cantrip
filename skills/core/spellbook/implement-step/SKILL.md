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
worker has started. A closed range never clamps: `3-9` on a six-step plan is an error, not `3-6`.
The developer named a step that is not there and should be told so before anything runs.
Reversed (`4-2`) and zero (`0-2`) bounds abort with the same message.

The steps to run are `first` through `last`, ascending. For each, locate its heading
`### Step {N} — <title>`. Extract the block from that heading up to, but not including, whichever
comes first: the next `### Step ` heading, the next top-level `---` that begins a new section, or
end of file.

Also extract, once for the whole cast:

- The **Context** section
- The **Key Decisions** section
- The plan's **Spec** path and **Branch** name, if listed near the top

**If a located step is a spell-cast rather than implementation work**, one whose content is "run
`/feature update …`" or similar, **never dispatch a worker for it.** Dispatching one would have a
code worker execute a spell, which is the wrong mechanism. Mark the step as a spell-cast and carry
on; Step 4 stops the run before it. A numbered spell-cast step is a plan's behavior-recording step,
so it is the last numbered step in every plan that has one, and nothing follows it. That is why a
marked step that is the first step to run is always a single cast of it, with nothing to run before
it. Hand it back now, with no worker started:

> Step N is a spell-cast, not implementation work. Cast it directly: `/<spell> <args>`.

A well-formed plan leaves the behavior-recording step unnumbered for exactly this reason, but older
plans number it. A range that reaches such a step is not an error. Every step before it runs as
usual, the run ends there, and Step 6 hands the step back with the same message.

## Step 3 — Sanity-check the working tree

This check runs once per cast, before the first worker starts, and never again during the run.
Between steps the tree is dirty by the run's own doing. Each finished step leaves its changes in
place for the developer to review, and the next worker builds on them. Asking again would be
asking about the run's own work.

Run `git status --short`. If the tree is dirty, surface this before the first worker starts:

> Working tree is dirty. This cast will edit files on top of your uncommitted changes. Continue?
> (yes/no)

Wait for the answer. On "yes", go to Step 4 and do not return here for the rest of the cast. On
"no", stop: no worker starts, nothing is relayed, and there is no `Next:` line. Say in one line
that nothing ran. If the tree is clean, skip the prompt and proceed.

## Step 4 — Compose the worker prompt

Steps 4, 5, and 6 run once per step in the run, in ascending order: compose step N's prompt,
dispatch it, wait, relay its report, then move to step N+1 only if that report says DONE and step
N+1 is not marked as a spell-cast. Step 6 says what ends a run early. Compose a step's prompt only
when it is about to be dispatched, never all of them up front. A single-step cast is a run of one.

Once for the whole cast, before the first prompt is composed, check whether the project has standing
rules the worker must respect: test resilience conventions, formatting discipline, structural
requirements. Fold them into every step's envelope. The rules do not change between steps, so read
them once.

**Slot:** `.agents/config/conventions.md` → `## Implementation rules`
**If empty:** rely on the project's guidance files, which the envelope already points the worker
at. Do not invent rules.

Build a **self-contained** prompt. The worker has no access to this conversation — everything it
needs must be in the prompt.

From the second step of a run onward, the prompt gains a section headed `## Earlier in this run`.
It carries the report block of every step that finished earlier in this run. Each block goes in
whole and unchanged, inside its own code fence, in the order the steps ran. Make that fence one
backtick longer than the longest run of backticks inside the block, and never shorter than three,
so a fenced snippet a worker pasted as evidence cannot close the wrap early and spill the rest of
the report into the prompt. This template's own outer fence uses four backticks for the same
reason. Carrying the block forward this way gives the worker what the developer would have read
between two single-step casts. It may be a deviation from the
plan, a convention chosen because a slot was empty, or an open question left in the notes. On the
first step of a run, and on every single-step cast, leave the section out entirely, heading
included. Carry only this run's reports. A report from an earlier cast against the same plan
belongs to that cast, and the developer has already read it.

The section has no cap. A plan is bounded and a report block is a few dozen lines, so the section
cannot grow past what the plan allows. If a worker prompt ever proves too long to be useful, a cap
on this section is the first thing to add.

````
You are executing **Step {N}** of the plan at `{plan}`. The main conversation dispatched you so it
can stay clean — work in this isolated context and report back.

## Plan context

{verbatim contents of the plan's Context section}

## Key decisions already made (do not re-derive)

{verbatim contents of the plan's Key Decisions section}

## Earlier in this run

{the full report block of every step finished earlier in this run, in run order, each inside its
own code fence one backtick longer than any backtick run inside it; leave this whole section out on
the first step of a run}

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
  step wins**, and write the line `Committed: yes` under **Notes** so the orchestrator can see it
  without reading prose. What must not happen is the step and this envelope quietly disagreeing,
  leaving it unclear whether a commit was expected.
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

Keep Notes to a handful of lines. Anything longer, such as full command output or a diff, goes in
a file under the increment's working directory, and Notes names it by path. In a run, every report
is carried into each later step's prompt, so a long one is paid once per remaining step.
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

Then read the block's outcome. It decides whether the run goes on:

- **DONE**, N is below `last`, and step N+1 is not marked as a spell-cast: return to Step 4 for
  step N+1, adding this block to the reports that step's prompt carries under `## Earlier in this
  run`.
- **DONE**, and N is `last`: the run is complete. Write the `Next:` line.
- **DONE**, and step N+1 is marked as a spell-cast: the run ends here, however far the range
  reaches past N+1. Do not compose or dispatch it. Print the spell-cast message from Step 2 for
  step N+1, then write the `Next:` line as for a stop before a spell-cast.
- **BLOCKED**: the run ends here. Do not compose or dispatch step N+1, however far the range
  reaches past it. Every step that finished earlier in this run stays exactly as its worker left it;
  revert nothing. Write the `Next:` line.
- **No `## Step N —` block at all**: treat the step as BLOCKED. Relay the worker's final message as
  it came, then add one sentence of your own saying that step N is treated as BLOCKED because no
  report arrived. A run cannot tell an unfinished step from a finished one without the block, and
  starting step N+1 on top of an unknown state is worse than stopping. Then write the `Next:` line
  as for BLOCKED.

The `Next:` line appears **once per cast**, after the last step's report, never after every step.
Write it for the last step that ran, N:

- **DONE**: `Next: review changes (git diff), run /code-review {scope} ({reason}) when satisfied,
  then /implement-step {plan} {N+1}.`
  - If step N was the plan's final step: `Next: review changes (git diff), run /code-review {scope}
    ({reason}), then /commit-message. After commit, archive the increment.`
- **DONE**, stopped before a spell-cast step S: step S is what comes next, so the line points at
  casting it rather than at `/implement-step {plan} {S}`. The cast comes before the review because
  the chain records behavior before it reviews. `Next: review changes (git diff), cast /<spell>
  <args> directly, run /code-review {scope} ({reason}), then /commit-message. After commit, archive
  the increment.` That ending is for S being the plan's last numbered step, which it is in every
  plan that numbers its behavior-recording step. If steps follow S, end with `then /implement-step
  {plan} {S+1}.` instead.
- **BLOCKED**, single-step cast: `Next: read the worker's notes, resolve the blocker, then
  re-invoke /implement-step {plan} {N}.`
- **BLOCKED**, in a run: `Next: read the worker's notes, resolve the blocker, then re-invoke
  /implement-step {plan} {N}-{last}.` Here `last` is the range's original end as Step 2 resolved
  it. So `1-4` blocked at step 2 points at `2-4`, and `3-` on a six-step plan blocked at step 5
  points at `5-6`. When N is `last` itself, write `{N}` alone: the resume is a single step, and
  Step 1 already treats `N-N` as that step spelled differently.

`{scope}` is the argument `/code-review` takes, and the run's reports decide it. Read every report
relayed in this cast for the line `Committed: yes` under its Notes, which the envelope requires of
a worker whose step told it to commit. If none has it, the scope is
`uncommitted` and the reason is `the run's changes are still uncommitted`. If any has it, the
scope is `branch` and the reason is `a step in this run committed, so the uncommitted diff would
miss it`. One such report anywhere in the run is enough. The reason travels in the line, in
parentheses, so a developer who has never seen an empty review knows what would have gone wrong.
A single-step cast is a run of one and gets the same line, decided by its one report. A run of
three with no commits closes with:

> Next: review changes (git diff), run /code-review uncommitted (the run's changes are still
> uncommitted) when satisfied, then /implement-step {plan} 4.

Do not print the worker's full transcript — only its final report block and your `Next:` line.
The one exception is the no-report case above, where the final message is relayed because there is
no block to relay instead.

## Rules of thumb

- This executes **the steps it was given**, one at a time, in order, and then stops. A range is the
  developer choosing where the next pause falls. It is not a request to keep going past the range,
  to skip a step, or to run steps side by side. Don't try to be clever.
- The worker's context is bounded by what you pass. Too little and it works blind; the whole plan
  and you bloat it with irrelevant steps. **Context + Key Decisions + this run's earlier reports +
  Step N is the right cut.**
- The plan's **Validation** section is the truth about whether the step succeeded. Don't
  second-guess it.
