# Step 4 — validation log

Working tree: branch `robot-denny/implement-step-ranges`, HEAD `9496c35`.

The spell under test is `skills/core/spellbook/implement-step/SKILL.md`. Two fixture plans are
cast against it, both by path: the six-step accordion fixture at
`_work/implement-step-ranges/assets/fixtures/accordion-block-plan.md`, written below as `<plan>`,
and the five-step `legacy-hero-plan.md` beside it, written as `<legacy>`, which this step creates.

This step has three behaviors. Each one gets its own cycle below, in order: the expectation is
written, RED is recorded from the committed spell, the spell is edited, GREEN is recorded. The
second behavior's expectation was not written until the first behavior was GREEN, and so on.

Every expectation asserts on what the developer sees during and after a cast: whether a prompt
appeared and how many times, which workers started, what was relayed, and the one `Next:` line.
None asserts that a sentence exists in the spell. The expected values come from the scenarios in
`_features/plan-execution.md` under the rules "The dirty-tree prompt fires once per run", "The
closing line names the review scope", and "A numbered spell-cast step ends the run before it", and
from the step's Test-first block in the plan. None comes from the edit.

`_work/implement-step-ranges/assets/step4-standin.py` is the stand-in for this step. It extends the
step 2 script's outcome model. It is not the spell; it is the rules as written, kept beside this log
so the transcripts can be re-run.

---

## Behavior 1 — The dirty-tree prompt fires once per run

### Expected, written before the edit

Three casts of `<plan> 1-3`. The fixture's steps write only under `_scratch/`, which is git-ignored,
so the fixture itself never dirties the tree. The dirty tree comes from one uncommitted change the
person makes before casting, as the step's Manual validation says.

| Cast | Tree before the cast | Answer | Prompts seen | Workers started |
|---|---|---|---|---|
| `<plan> 1-3` | clean | none asked | 0 | 1, 2, 3 |
| `<plan> 1-3` | one uncommitted change | yes | 1, before step 1's worker starts, none before steps 2 or 3 | 1, 2, 3 |
| `<plan> 1-3` | one uncommitted change | no | 1 | none |

For the third row, the cast ends with one line saying nothing ran, no report block is relayed
because there is none, and no `Next:` line points at a later step. Declining means the run never
began; it is not a BLOCKED step and there is no worker's notes to read.

A fourth case pins the second row's shape from the other side. In a plan whose steps do dirty the
tree, which is every real plan, the tree is dirty before step 2 and before step 3 by the run's own
doing. The prompt count is still 1. The spec's clean-tree scenario says so in as many words: "no
dirty-tree prompt appears before step 2 or step 3, although the tree is now dirty".

### RED: the spell at `9496c35`

The committed spell's Step 3, in full:

```
$ git show 9496c35:skills/core/spellbook/implement-step/SKILL.md | sed -n '76,83p'
## Step 3 — Sanity-check the working tree

Run `git status --short`. If the tree is dirty, surface this before dispatching:

> Working tree is dirty. The worker will edit files on top of your uncommitted changes. Continue?
> (yes/no)

Wait for confirmation. If the tree is clean, skip the prompt and proceed.
```

Walking each row through that text, literally:

| Cast | The `9496c35` spell does | Expected | Result |
|---|---|---|---|
| clean tree | Step 3 finds a clean tree and skips the prompt. Step 4's loop sentence names Steps 4, 5, and 6 as the ones that repeat, so Step 3 is not revisited. No prompt. Workers 1, 2, 3 start. | The same | already GREEN, by structure |
| dirty tree, yes | Step 3 prompts once and waits. On "yes" Step 4 begins. Whether the prompt comes back before step 2 depends on how the reader takes "surface this before dispatching": dispatching happens three times in this cast, and the prompt names "the worker", singular, as if there were one. Structure says once; the sentence says before each dispatch. | 1 prompt, workers 1, 2, 3 | ambiguous: **the text does not say once**, and the prompt's own wording assumes a single worker |
| dirty tree, no | Step 3 says "Wait for confirmation" and nothing else. There is no branch for "no": the spell does not say whether the cast stops, whether the first worker starts anyway, or what the developer sees. | no worker starts, one line saying nothing ran | RED: **declining has no defined outcome** |

So the plan's RED is answered as written: the committed Step 3 describes the check without saying it
fires once, and it says nothing about declining. The walk-through is a stand-in. A dispatched worker
cannot cast a spell, so it reads the spell and follows it. The real cast is the person's and is the
step's Manual validation.

### GREEN: the edited spell

**This section is a stand-in.** A dispatched worker cannot cast a spell. What follows is the
edited Step 3, walked against the three rows, with the stand-in script encoding the same rule so
the walk can be re-run. The real casts are still owed and are the step's Manual validation.

```
$ ./scripts/check-contract.sh
22 checks passed.
```

The edited Step 3 opens by saying the check runs once per cast, before the first worker starts,
and never again during the run, and says why: between steps the tree is dirty by the run's own
doing. The prompt now says "This cast will edit files" rather than "The worker will edit files",
so it reads the same for a run of one and a run of three. The paragraph after the prompt has the
branch the committed spell lacked: on "yes", go to Step 4 and do not return; on "no", stop with no
worker started, nothing relayed, no `Next:` line, and one line saying nothing ran. `grep -rn "The
worker will edit files\|Wait for confirmation\|before dispatching" tests/ scripts/check-contract.sh
skills/ docs/ README.md` finds only an unrelated line in the code-review spell, so nothing outside
this file names the wording that changed. The Step 3 section holds no em-dash outside its heading.

```
$ P=_work/implement-step-ranges/assets/fixtures/accordion-block-plan.md
$ ST=_work/implement-step-ranges/assets/step4-standin.py

$ python3 $ST $P 1-3 --tree clean
cast 1-3: steps to run [1, 2, 3], first=1, last=3, run; tree clean at the start
  worker 1 starts (tree clean, no prompt) -> returns DONE
  worker 2 starts (tree dirty, no prompt) -> returns DONE
  worker 3 starts (tree dirty, no prompt) -> returns DONE
  relayed, in order:
    ## Step 1 — DONE
    ## Step 2 — DONE
    ## Step 3 — DONE
  prompts seen: 0; workers started: [1, 2, 3]; not started: []
  Next: review, /code-review, then /implement-step <plan> 4

$ python3 $ST $P 1-3 --tree dirty --answer yes
cast 1-3: steps to run [1, 2, 3], first=1, last=3, run; tree dirty at the start
  prompt before step 1: Working tree is dirty. This cast will edit files on top of your uncommitted changes. Continue? (yes/no) -> yes
  worker 1 starts (tree dirty, no prompt) -> returns DONE
  worker 2 starts (tree dirty, no prompt) -> returns DONE
  worker 3 starts (tree dirty, no prompt) -> returns DONE
  relayed, in order:
    ## Step 1 — DONE
    ## Step 2 — DONE
    ## Step 3 — DONE
  prompts seen: 1; workers started: [1, 2, 3]; not started: []
  Next: review, /code-review, then /implement-step <plan> 4

$ python3 $ST $P 1-3 --tree dirty --answer no
cast 1-3: steps to run [1, 2, 3], first=1, last=3, run; tree dirty at the start
  prompt before step 1: Working tree is dirty. This cast will edit files on top of your uncommitted changes. Continue? (yes/no) -> no
  Nothing ran.
  prompts seen: 1; workers started: []; relayed: nothing; Next: none
```

| Cast | The edited spell does | Matches Expected |
|---|---|---|
| clean tree | No prompt. Workers 1, 2, 3 start. The script marks the tree dirty from step 2 on, as a real plan's steps would leave it, and no prompt appears there. | yes |
| dirty tree, yes | One prompt, before step 1. None before steps 2 or 3. Workers 1, 2, 3 start. | yes |
| dirty tree, no | One prompt. No worker starts. Nothing relayed. One line, "Nothing ran." No `Next:` line. | yes |

The `Next:` lines in this transcript are the step 2 script's, carried over unchanged. Behavior 2
below changes them; this behavior asserts nothing about them.

---

## Behavior 2 — The closing line names the review scope

### Expected, written before the edit

The step's Test-first block names two casts of `<plan> 1-3`. The spec's two scenarios under "The
closing line names the review scope" give the expected values. Two more rows pin the shape at the
edges the plan's own rule touches: a run that reaches the plan's last numbered step, and a
single-step cast, which Step 4 of the spell calls a run of one.

| Cast | Reports in the run | Closing line names | And says, in one clause |
|---|---|---|---|
| `<plan> 1-3` | three DONE, none says it committed | `/code-review` with scope `uncommitted` | the run's changes are still uncommitted |
| `<plan> 1-3`, fixture step 2 temporarily told to commit | step 2's report says it committed | `/code-review` with scope `branch` | a step in the run committed, so the uncommitted diff would miss it |
| `<plan> 1-6` | six DONE, none committed | `/code-review` with scope `uncommitted`, then `/commit-message`, then archive the increment, as today | the run's changes are still uncommitted |
| `<plan> 4` | one DONE, not committed | `/code-review` with scope `uncommitted`, then `/implement-step <plan> 5` | the run's changes are still uncommitted |

In every row the line still opens with reviewing the diff and, where the run stopped short of the
plan's last step, still ends by pointing at the next single step by number. Only the scope and its
reason are new. The BLOCKED closing lines are not in this table: they point at where to resume,
not at review, and this behavior leaves them alone.

The signal for `branch` is the worker's report, not the tree. A step's report says it committed
only when the plan step told the worker to commit; the envelope otherwise forbids it and the report
would say nothing. One such report anywhere in the run is enough. The stand-in models this as a
fourth outcome, `COMMITTED`, meaning DONE with a report that says it committed. The plan's second
row asks for the fixture to be edited temporarily; the stand-in reads outcomes from its arguments,
so the fixture on disk is not touched, and the manual cast is where the edited fixture is used.

### RED: the spell at `9496c35`

The committed spell's closing lines, in Step 6:

```
$ git show 9496c35:skills/core/spellbook/implement-step/SKILL.md | sed -n '237,243p'
The `Next:` line appears **once per cast**, after the last step's report, never after every step.
Write it for the last step that ran, N:

- **DONE**: `Next: review changes (git diff), run /code-review when satisfied, then
  /implement-step {plan} {N+1}.`
  - If step N was the plan's final step: `Next: review changes (git diff), run /code-review, then
    /commit-message. After commit, archive the increment.`
```

Walking each row through that text, literally:

| Cast | The `9496c35` spell writes | Expected | Result |
|---|---|---|---|
| `<plan> 1-3`, none committed | `Next: review changes (git diff), run /code-review when satisfied, then /implement-step <plan> 4.` No scope. No reason. `/code-review` defaults to `uncommitted`, so the review would be right by accident, and the developer is not told why. | `/code-review uncommitted`, with the clause that the run's changes are still uncommitted | RED: **no scope and no reason** |
| `<plan> 1-3`, step 2 committed | The same line, word for word. Nothing in Step 6 reads the reports for a commit, so step 2's report saying it committed changes nothing. `/code-review` defaults to `uncommitted`, which diffs step 3's work alone and never sees steps 1 and 2. | `/code-review branch`, with the clause that a step committed so the uncommitted diff would miss it | RED: **the wrong scope, silently** |
| `<plan> 1-6`, none committed | `Next: review changes (git diff), run /code-review, then /commit-message. After commit, archive the increment.` No scope, no reason. | The same with `uncommitted` and its clause | RED |
| `<plan> 4` | `Next: review changes (git diff), run /code-review when satisfied, then /implement-step <plan> 5.` | The same with `uncommitted` and its clause | RED |

So the plan's RED is answered as written: today's closing line names no scope. The second row is
the one that matters. A developer following the line after a plan that commits per step would
cast a review that reports a diff of one step, or of nothing, and would have no clue in the line
that anything was missed. The walk-through is a stand-in; the real cast is the person's.

### GREEN: the edited spell

**This section is a stand-in.** A dispatched worker cannot cast a spell. What follows is the
edited Step 6, walked against the four rows, with the stand-in script printing the closing line
the way Step 6 now says to write it. The real casts, including the one with the fixture's step 2
temporarily told to commit, are still owed and are the step's Manual validation.

```
$ ./scripts/check-contract.sh
22 checks passed.
```

The edited Step 6 puts `{scope} ({reason})` after `/code-review` in both DONE lines, the one that
points at the next step and the one for the plan's final step. A paragraph after the list says how
the scope is decided: read every report relayed in this cast for a line saying the worker
committed; none means `uncommitted` with the reason "the run's changes are still uncommitted", any
means `branch` with the reason "a step in this run committed, so the uncommitted diff would miss
it". It says one such report is enough, that a single-step cast gets the same line, and it shows
the line for a run of three with no commits. The BLOCKED bullets are untouched. The Step 6 section
holds no em-dash that was not there at `9496c35`.

```
$ python3 $ST $P 1-3 | tail -1
  Next: review changes (git diff), run /code-review uncommitted (the run's changes are still uncommitted) when satisfied, then /implement-step <plan> 4.

$ python3 $ST $P 1-3 DONE COMMITTED DONE | grep -n 'Step 2\|Next'
7:    ## Step 2 — DONE  (Notes: Committed: yes)
10:  Next: review changes (git diff), run /code-review branch (a step in this run committed, so the uncommitted diff would miss it) when satisfied, then /implement-step <plan> 4.

$ python3 $ST $P 1-6 | tail -1
  Next: review changes (git diff), run /code-review uncommitted (the run's changes are still uncommitted), then /commit-message. After commit, archive the increment.

$ python3 $ST $P 4 | tail -1
  Next: review changes (git diff), run /code-review uncommitted (the run's changes are still uncommitted) when satisfied, then /implement-step <plan> 5.

$ # a BLOCKED run keeps its resume pointer, whatever an earlier step's report said
$ python3 $ST $P 1-4 COMMITTED BLOCKED | tail -1
  Next: read the worker's notes, resolve the blocker, then re-invoke /implement-step <plan> 2-4
```

| Cast | The edited spell writes | Matches Expected |
|---|---|---|
| `<plan> 1-3`, none committed | `/code-review uncommitted (the run's changes are still uncommitted)`, then step 4 | yes |
| `<plan> 1-3`, step 2 committed | `/code-review branch (a step in this run committed, so the uncommitted diff would miss it)`, then step 4 | yes |
| `<plan> 1-6` | `uncommitted` with its clause, then `/commit-message`, then archive | yes |
| `<plan> 4` | `uncommitted` with its clause, then step 5 | yes |

The last transcript is a guard, not a row: a run that blocks closes with the resume pointer from
step 2 of the plan, and the commit in step 1's report does not change that line.

---

## Behavior 3 — A numbered spell-cast step ends the run before it

### Expected, written before the edit

The fixture `<legacy>` has five numbered steps. Steps 1 to 4 each create one file under
`_scratch/legacy-hero/`. Step 5's prompt reads "Run `/feature update hero`" and builds nothing,
the way a plan written before the behavior-recording step was left unnumbered would read. The
spec's scenario "An older plan numbers its behavior-recording step" gives the first row. The other
rows pin the shape at the edges: the closed range that names the spell-cast step outright, the
single cast that already refuses it, and a range that stops short of it.

| Cast | Workers started | Relayed, in order | Closing |
|---|---|---|---|
| `<legacy> 3-` | 3, 4 | `## Step 3 — DONE`, `## Step 4 — DONE`, then "Step 5 is a spell-cast, not implementation work. Cast it directly: `/feature update hero`." | one `Next:` line that says to review, to cast `/feature update hero` directly, and to run `/code-review uncommitted` with its clause |
| `<legacy> 3-5` | 3, 4 | the same | the same |
| `<legacy> 5` | none | the spell-cast message alone | as today: the message is the whole answer |
| `<legacy> 1-4` | 1, 2, 3, 4 | four DONE blocks | the DONE line, pointing at step 5 |

The first two rows are the behavior. The run does not abort when Step 2 finds the spell-cast at
step 5: workers 3 and 4 start and finish, both blocks are relayed as they land, and only then does
the spell-cast message appear. Nothing from steps 3 and 4 is reverted. The third row is today's
single-cast refusal, unchanged. The fourth row never reaches step 5, so the run closes as any
DONE run does; the developer who then casts `<legacy> 5` meets the third row.

Where the check lives is a design choice the plan leaves open. Step 2 already reads every block
in one pass and already holds the single-cast refusal, so it is the one place that knows what a
spell-cast step is. The expectation is therefore: Step 2 marks the step and does not hand back
when it is not the first step to run; Step 4's loop stops before dispatching a marked step; Step 6
writes the message and the closing line. The single-cast case, where the marked step is the only
step, still hands back from Step 2 with no worker started, exactly as today. The stand-in reads the
plan the same way: a step block whose prompt line begins "Run `/" is a spell-cast.

### RED: the spell at `9496c35`

The committed spell's refusal, in Step 2, right after the batch extraction:

```
$ git show 9496c35:skills/core/spellbook/implement-step/SKILL.md | sed -n '67,74p'
**If the located step is a spell-cast rather than implementation work** — its content is "run
`/feature update …`" or similar — **do not dispatch a worker.** Dispatching one would have a code worker
execute a spell, which is the wrong mechanism. Say so and hand it back:

> Step N is a spell-cast, not implementation work. Cast it directly: `/<spell> <args>`.

A well-formed plan leaves the behavior-recording step unnumbered for exactly this reason, but older
plans number it.
```

Walking each row through that text, literally:

| Cast | The `9496c35` spell does | Expected | Result |
|---|---|---|---|
| `<legacy> 3-` | Step 2 resolves `3-` to `3-5` and extracts the blocks for 3, 4, and 5 in one pass. The refusal reads "the located step", singular, and says "hand it back". Step 5 is located, so the spell hands back during extraction. Step 4's loop is never reached. No worker starts. The developer sees the spell-cast message and nothing else. Files: none. | workers 3 and 4, two DONE blocks, then the message, then a `Next:` line | RED: **steps 3 and 4 never run**; the whole run aborts on a step it had not reached |
| `<legacy> 3-5` | The same. | The same | RED |
| `<legacy> 5` | Step 2 locates step 5, finds the spell-cast, hands back. No worker. | The same | already GREEN |
| `<legacy> 1-4` | Step 5 is never located, so the refusal never fires. Workers 1 to 4 run. The DONE line points at step 5. | The same | already GREEN |

So the plan's RED is answered as written: the refusal exists only for a single cast. Read against a
range, it turns a step the run has not reached into an abort of the whole run, which is the reading
the step 1 code review flagged. The walk-through is a stand-in; the real cast is the person's.

### GREEN: the edited spell

**This section is a stand-in.** A dispatched worker cannot cast a spell. What follows is the
edited spell walked against the rows, with the stand-in script reading the fixture the way Step 2
says to and applying the stop rule the way Step 4 and Step 6 now say to. The real cast of
`<legacy> 3-` is still owed and is the step's Manual validation.

```
$ ./scripts/check-contract.sh
22 checks passed.
```

Where the check lives: it stayed in Step 2. That is where every block is read in one pass and
where the single-cast refusal already sat, so there is one definition of a spell-cast step and one
place that recognizes it. Step 2 now marks the step and carries on, and hands back at once only
when the marked step is the first step to run, which covers every single cast of it. Step 4's loop
sentence moves to step N+1 only if the report says DONE and N+1 is not marked. Step 6's first
outcome bullet, the return to Step 4 for N+1, carries the same "not marked" condition, added on a
read of the diff so Step 6 is unambiguous on its own rather than only through Step 4's loop
sentence. Step 6 gains an outcome bullet, "DONE, and step N+1 is marked as a spell-cast", which ends the run, prints Step 2's
message for N+1, and writes a closing line of its own: review, cast the spell directly, then
`/code-review` with the scope rule from behavior 2, then commit and archive when S is the plan's
last numbered step. The cast goes before the review because the workflow's chain records behavior
before it reviews. The alternative, moving the refusal into the loop, would have put the
recognition of a spell-cast step in a second place; it was not taken. The added lines hold no
em-dash. `grep -rn "If the located step\|do not dispatch a worker\|Say so and hand it back\|move to
step N+1 only if" tests/ scripts/check-contract.sh skills/ docs/ README.md` finds nothing outside
this spell, so no test or contract check names the wording that changed.

```
$ L=_work/implement-step-ranges/assets/fixtures/legacy-hero-plan.md

$ python3 $ST $L 3-
cast 3-: steps to run [3, 4, 5], first=3, last=5, run; tree clean at the start
  worker 3 starts (tree clean, no prompt) -> returns DONE
  worker 4 starts (tree dirty, no prompt) -> returns DONE
  run ends before step 5: no worker is composed or dispatched for it
  relayed, in order:
    ## Step 3 — DONE
    ## Step 4 — DONE
    Step 5 is a spell-cast, not implementation work. Cast it directly: `/feature update hero`.
  prompts seen: 0; workers started: [3, 4]; not started: [5]
  Next: review changes (git diff), cast /feature update hero directly, run /code-review uncommitted (the run's changes are still uncommitted), then /commit-message. After commit, archive the increment.

$ python3 $ST $L 3-5 | tail -1
  Next: review changes (git diff), cast /feature update hero directly, run /code-review uncommitted (the run's changes are still uncommitted), then /commit-message. After commit, archive the increment.

$ python3 $ST $L 5
cast 5: steps to run [5], first=5, last=5, single-step cast; tree clean at the start
  Step 5 is a spell-cast, not implementation work. Cast it directly: `/feature update hero`.
  prompts seen: 0; workers started: []; relayed: the message alone; Next: none

$ python3 $ST $L 1-4 | tail -2
  prompts seen: 0; workers started: [1, 2, 3, 4]; not started: []
  Next: review changes (git diff), run /code-review uncommitted (the run's changes are still uncommitted) when satisfied, then /implement-step <plan> 5.

$ # the scope rule and the stop rule compose
$ python3 $ST $L 3- COMMITTED | tail -1
  Next: review changes (git diff), cast /feature update hero directly, run /code-review branch (a step in this run committed, so the uncommitted diff would miss it), then /commit-message. After commit, archive the increment.

$ # a block before the spell-cast step wins: the run never gets that far
$ python3 $ST $L 3- DONE BLOCKED | tail -1
  Next: read the worker's notes, resolve the blocker, then re-invoke /implement-step <plan> 4-5

$ # regression: the accordion fixture's unnumbered Final is not a step and never marks step 6
$ python3 $ST $P 5-
cast 5-: steps to run [5, 6], first=5, last=6, run; tree clean at the start
  worker 5 starts (tree clean, no prompt) -> returns DONE
  worker 6 starts (tree dirty, no prompt) -> returns DONE
  relayed, in order:
    ## Step 5 — DONE
    ## Step 6 — DONE
  prompts seen: 0; workers started: [5, 6]; not started: []
  Next: review changes (git diff), run /code-review uncommitted (the run's changes are still uncommitted), then /commit-message. After commit, archive the increment.
```

| Cast | The edited spell does | Matches Expected |
|---|---|---|
| `<legacy> 3-` | Workers 3 and 4 start and return DONE. The run ends before 5 with no worker for it. Relayed: two DONE blocks, then the message naming step 5 and `/feature update hero`. One `Next:` line: review, cast the spell directly, `/code-review uncommitted` with its clause, commit, archive. | yes |
| `<legacy> 3-5` | The same, since `3-` resolves to `3-5`. | yes |
| `<legacy> 5` | No worker. The message alone. | yes, unchanged from today |
| `<legacy> 1-4` | Four workers. The DONE line pointing at step 5. | yes |

The last transcript is worth a note. The first version of the stand-in ran step 6's block into
the accordion fixture's unnumbered `### Final` section, which holds a "Run `/feature update
accordion-block`" prompt, and so marked step 6 as a spell-cast and stopped `<plan> 5-` after step
5. The spell's Step 2 was never wrong about this: it ends a block at the next `### Step` heading
or the next top-level `---`, and the `---` sits between step 6 and the Final section. The script
now splits on `---` as well and the cast runs both steps. It is recorded because it is exactly the
mistake an orchestrator could make if it read a step block past its `---`, and the regression cast
is the check for it.

---

## Final gate

```
$ ./scripts/check-contract.sh
22 checks passed.
```

Run after each behavior and once more at the end. `git status --short` shows the spell modified and
three files added under `_work/implement-step-ranges/assets/`: this log, `step4-standin.py`, and
`fixtures/legacy-hero-plan.md`. Nothing under `_scratch/` was created; the stand-in dispatches no
worker and writes no file.

## Changed after review

Two sentences were added to the spell after the review of this step, and the stand-in and the
transcript above were updated to match.

- Step 2 now states the invariant its "first step to run" sentence rested on: a numbered
  spell-cast step is the behavior-recording step, so it is the last numbered step in any plan that
  has one. Both fixtures already obey this; the sentence makes it a rule rather than a coincidence.
- The commit signal is pinned. The envelope now requires a worker whose step told it to commit to
  write `Committed: yes` under Notes, and the scope rule looks for that line rather than for prose
  saying the worker committed. The stand-in's COMMITTED outcome relays that line.

## Not evidenced here

- A real cast of `<plan> 1-3` with one uncommitted change in the tree, showing the prompt once and
  not before steps 2 and 3, and a second cast answered "no" that runs nothing. Structure and text
  both now say once; only a cast shows the orchestrating model doing it.
- A real cast of `<legacy> 3-`, showing steps 3 and 4 running, the run stopping before 5, and the
  message. In particular, that the orchestrator reads step 5's block as far as its `---` and no
  further, which the stand-in's own slip above shows is the easy mistake.
- A real closing line read off a run, naming a scope and a reason. The stand-in prints the line
  Step 6 dictates; whether the model reads every relayed report for a commit, rather than the
  tree, is only visible in a cast where a step's report says it committed. The plan's second row,
  the fixture's step 2 temporarily told to commit, is the person's cast and touches the fixture
  only for its duration.
- The manual-check mark in `/plan`'s report and the documentation surfaces. The plan's Steps 5
  and 6 own those.
