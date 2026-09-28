# Step 2 — validation log

Working tree: branch `robot-denny/implement-step-ranges`, HEAD `d63df31`.

The spell under test is `skills/core/spellbook/implement-step/SKILL.md`. Two fixtures are cast
against it. `<plan>` stands for the six-step fixture,
`_work/implement-step-ranges/assets/fixtures/accordion-block-plan.md`, and `<blocking>` for its
variant `_work/implement-step-ranges/assets/fixtures/accordion-block-blocking-plan.md`, whose step 2
creates nothing and reports `## Step 2 — BLOCKED` with the note `fixture: deliberate block`. Every
other fixture step creates one file, `_scratch/accordion-block/step-N.txt`.

Every expectation below asserts on what the developer sees: the report blocks relayed into the
conversation, the `Next:` line, and the files under `_scratch/accordion-block/`. None asserts on
the spell's wording. The expected values are lifted from the two scenarios under the rule "A blocked
step ends the run and says where to resume" in `_features/plan-execution.md`, and from the spec's
edge cases, not from the edit.

## Expected, written before the edit

`_scratch/accordion-block/` is empty before every cast.

### Cast `<blocking> 1-4`

- Two workers start, for steps 1 and 2, in that order. No worker starts for step 3 or step 4.
- The conversation shows two report blocks, in order: `## Step 1 — DONE`, then
  `## Step 2 — BLOCKED` whose Notes read `fixture: deliberate block`.
- Nothing after the step 2 block reads as a third step starting or finishing.
- Exactly one `Next:` line, after the step 2 block. It says to read the worker's notes, resolve the
  blocker, and re-invoke `/implement-step <blocking> 2-4`. The `4` is the range's original end,
  not the plan's last step and not the blocked step alone.
- `ls _scratch/accordion-block/` prints `step-1.txt` and nothing else. In particular `step-3.txt`
  does not exist, and `step-1.txt` was not removed or reverted by the stop.

### Cast `<plan> 1-3`, where step 2's worker ends without a report block

No fixture forces this; it is the case where a worker runs out of context or answers in prose and
its final message carries no `## Step 2 —` heading. The expectation is the second scenario under
the rule, plus the spec's edge case for it.

- Two workers start, for steps 1 and 2. No worker starts for step 3.
- The conversation shows `## Step 1 — DONE`, then whatever step 2's worker did return, then a
  sentence in the orchestrator's own words saying step 2 is treated as BLOCKED because no report
  arrived. That sentence names the reason; "BLOCKED" alone would read as the worker's verdict when
  it is the run's.
- Exactly one `Next:` line, after that sentence. It says to resolve the blocker and re-invoke
  `/implement-step <plan> 2-3`.
- `ls _scratch/accordion-block/` prints `step-1.txt` and, depending on how far the worker got,
  possibly `step-2.txt`. `step-3.txt` does not exist.

### Two derived cases, so the resume pointer's shape is pinned

- `<blocking> 2-4`: one worker, one block `## Step 2 — BLOCKED`, no worker for 3 or 4, and a
  `Next:` line pointing at `/implement-step <blocking> 2-4` again. This is the spec's "first step
  of a run blocks" edge case.
- `<blocking> 2` and `<blocking> 2-2`: the single-step output, unchanged from before the increment:
  one block, and a `Next:` line pointing at `/implement-step <blocking> 2`, with no range and no
  wording that announces a run.

## RED: the spell at `d63df31`

The committed spell's run loop and relay read:

```
$ git show d63df31:skills/core/spellbook/implement-step/SKILL.md | sed -n '87,89p'
Steps 4, 5, and 6 run once per step in the run, in ascending order: compose step N's prompt,
dispatch it, wait, relay its report, then move to step N+1. Compose a step's prompt only when it is
about to be dispatched, never all of them up front. A single-step cast is a run of one.

$ git show d63df31:skills/core/spellbook/implement-step/SKILL.md | sed -n '195,203p'
The `Next:` line appears **once per cast**, after the last step's report, never after every step.
Write it for the last step that ran, N:

- **DONE**: `Next: review changes (git diff), run /code-review when satisfied, then
  /implement-step {plan} {N+1}.`
  - If step N was the plan's final step: `Next: review changes (git diff), run /code-review, then
    /commit-message. After commit, archive the increment.`
- **BLOCKED**: `Next: read the worker's notes, resolve the blocker, then re-invoke
  /implement-step {plan} {N}.`
```

Walking each cast through that text, literally:

| Cast | The `d63df31` spell does | Expected | Result |
|---|---|---|---|
| `<blocking> 1-4` | Step 6 relays `## Step 1 — DONE`, then Step 4 says "move to step N+1". Step 2's worker returns BLOCKED; Step 6 relays it and Step 4 again says move to N+1. Nothing anywhere says a BLOCKED report ends a run, so steps 3 and 4 are composed, dispatched, and relayed as DONE. The `Next:` line is written for the last step that ran, 4, which was DONE, so it points at `/implement-step <blocking> 5`. Files: `step-1.txt`, `step-3.txt`, `step-4.txt`. | Two blocks, one `Next:` naming `2-4`, no `step-3.txt` | RED: the run **continues past the block** and the resume pointer never appears |
| `<plan> 1-3`, no block from step 2 | Step 6 says to surface the report verbatim and calls the block the load-bearing part, but has no branch for its absence. Neither the DONE nor the BLOCKED bullet applies to step 2, and Step 4 moves on to step 3. Step 3 returns DONE, so the `Next:` line points at `/implement-step <plan> 4` and the missing report is never mentioned. | Stop after step 2, a sentence naming the missing report, `Next:` naming `2-3` | RED: the run **continues** and has **nothing to say** about the missing block |
| `<blocking> 2-4` | As the first row: step 2 blocks, steps 3 and 4 run anyway, `Next:` points at `5`. | One block, `Next:` naming `2-4` | RED |
| `<blocking> 2`, `<blocking> 2-2` | One worker, one BLOCKED block, `Next:` pointing at `/implement-step <blocking> 2`. | The same | already GREEN |

So the plan's "record which" is answered: the committed spell continues past a BLOCKED report
rather than having nothing to say, because the loop sentence in Step 4 is unconditional. For a
missing report block it does both: it continues, and it has no sentence for the case.

The walk-through above is a stand-in: a dispatched worker cannot cast a spell, so it reads the
spell and follows it. The real cast is the person's and is listed as the step's Manual validation.

## GREEN: the edited spell

**This section is a stand-in.** A dispatched worker cannot cast a spell. What follows is the edited
`SKILL.md` read and followed against the two fixtures, with the parts that can be checked
mechanically checked that way. The real cast is still owed and is the step's Manual validation.

### Automated gates

```
$ ./scripts/check-contract.sh
22 checks passed.
```

The diff is one file, `skills/core/spellbook/implement-step/SKILL.md`, 25 insertions and 4
deletions after the review fix that excepts the no-report case from "only the report block". Two places change. Step 4's loop sentence gains the clause "only if that report says
DONE" and a pointer at Step 6, so it no longer contradicts the stop rule. Step 6 gains four outcome
bullets between the relay paragraph and the `Next:` paragraph, and the `**BLOCKED**:` bullet splits
into a single-step form, unchanged in wording, and a run form carrying `{N}-{last}`. `git diff` has
no lines touching Step 3's dirty-tree prompt, the `**Slot:**` / `**If empty:**` pair, the
spell-cast refusal in Step 2, or the worker envelope. `grep -rn "re-invoke\|BLOCKED" tests/
scripts/check-contract.sh` finds nothing, so no test or contract check names the wording that
moved.

### The stop rule, applied mechanically

Step 4 and Step 6 of the edited spell state a loop and a stop rule. A short script,
`_work/implement-step-ranges/assets/step2-standin.py`, applies them as written to a plan file, a
cast, and the outcome each worker returns, and prints what is relayed, which workers started, and
the one `Next:` line. It is not the spell; it is the stop rule with nothing added, kept beside this
log so the transcript can be audited and re-run. `<plan>` in its output stands for whichever fixture
it was given.

```
$ B=_work/implement-step-ranges/assets/fixtures/accordion-block-blocking-plan.md
$ P=_work/implement-step-ranges/assets/fixtures/accordion-block-plan.md
$ S=_work/implement-step-ranges/assets/step2-standin.py

$ python3 $S $B 1-4 DONE BLOCKED
cast 1-4: steps to run [1, 2, 3, 4], first=1, last=4, run
  worker 1 starts -> returns DONE
  worker 2 starts -> returns BLOCKED
  relayed, in order:
    ## Step 1 — DONE
    ## Step 2 — BLOCKED
  workers started: [1, 2]; not started: [3, 4]
  Next: read the worker's notes, resolve the blocker, then re-invoke /implement-step <plan> 2-4

$ python3 $S $P 1-3 DONE NOREPORT
cast 1-3: steps to run [1, 2, 3], first=1, last=3, run
  worker 1 starts -> returns DONE
  worker 2 starts -> returns NOREPORT
  relayed, in order:
    ## Step 1 — DONE
    (worker 2's final message, no report block)
    Step 2 is treated as BLOCKED because no report arrived.
  workers started: [1, 2]; not started: [3]
  Next: read the worker's notes, resolve the blocker, then re-invoke /implement-step <plan> 2-3

$ python3 $S $B 2-4 BLOCKED
cast 2-4: steps to run [2, 3, 4], first=2, last=4, run
  worker 2 starts -> returns BLOCKED
  relayed, in order:
    ## Step 2 — BLOCKED
  workers started: [2]; not started: [3, 4]
  Next: read the worker's notes, resolve the blocker, then re-invoke /implement-step <plan> 2-4

$ python3 $S $B 2 BLOCKED
cast 2: steps to run [2], first=2, last=2, single-step cast
  worker 2 starts -> returns BLOCKED
  relayed, in order:
    ## Step 2 — BLOCKED
  workers started: [2]; not started: []
  Next: read the worker's notes, resolve the blocker, then re-invoke /implement-step <plan> 2

$ python3 $S $B 2-2 BLOCKED
  (identical to the cast of 2 above, line for line)

$ python3 $S $P 3- DONE DONE BLOCKED
cast 3-: steps to run [3, 4, 5, 6], first=3, last=6, run
  worker 3 starts -> returns DONE
  worker 4 starts -> returns DONE
  worker 5 starts -> returns BLOCKED
  relayed, in order:
    ## Step 3 — DONE
    ## Step 4 — DONE
    ## Step 5 — BLOCKED
  workers started: [3, 4, 5]; not started: [6]
  Next: read the worker's notes, resolve the blocker, then re-invoke /implement-step <plan> 5-6

$ python3 $S $P 1-4 DONE DONE DONE BLOCKED
  ... worker 4 starts -> returns BLOCKED; workers started: [1, 2, 3, 4]; not started: []
  Next: read the worker's notes, resolve the blocker, then re-invoke /implement-step <plan> 4

$ python3 $S $P 1-3
  (control: three DONE blocks, one Next: -> /implement-step <plan> 4, as in the step 1 log)
```

Each line matches the Expected section: two workers and two blocks on `<blocking> 1-4`, no worker
for 3 or 4, and a pointer at `2-4`; the no-report case stops after step 2 with a sentence naming the
missing report and points at `2-3`; the first-step-blocks case points at `2-4` again; the
single-step casts print the single-step pointer with no run wording. The two extra rows pin the
open-range case, where `last` was resolved by Step 2 to 6, and the case where the blocked step is
`last`, where the pointer collapses to the single step.

### The fixture's steps leave the expected files

Fixture step 1 and the blocking step 2 were run by hand, then the directory removed. This checks
the fixture and the file-state expectation, not the spell.

```
fixture step 1 by hand:
  test -f step-1.txt: pass
fixture step 2 (blocking) by hand: creates nothing, reports BLOCKED
  ls after the stop:
step-1.txt
  step-3.txt absent: pass
  git status entries for _scratch: 0
cleaned: ls: _scratch/accordion-block: No such file or directory
```

The blocking fixture differs from the six-step fixture only in its title, its header note, its
Key Decisions (one bullet reworded and one added), the step 2 block, the plan path inside every
prompt, and the step 2 row of the file summary. `diff` between the two shows nothing else.

### The run, walked by reading

The script covers the loop and the stop rule. The relay wording and the untouched steps are
followed by reading the edited text.

| Cast | Walk | Matches Expected |
|---|---|---|
| `<blocking> 1-4` | Step 3 checks the tree once. Step 4 composes step 1's prompt, Step 5 dispatches, Step 6 relays `## Step 1 — DONE`; N is 1, below `last` 4, so the first outcome bullet returns to Step 4 for step 2. Step 2's worker returns BLOCKED. Step 6 relays the block, whose Notes read `fixture: deliberate block`, then the BLOCKED bullet ends the run: step 3 is neither composed nor dispatched, step 1's file is left as is. The run-form `Next:` bullet writes `/implement-step <blocking> 2-4`, with `last` the 4 that Step 2 resolved. | yes |
| `<plan> 1-3`, no block from step 2 | As above through step 1. Step 2's worker returns prose with no `## Step 2 —` heading. Step 6's fourth bullet relays that message as it came, adds the orchestrator's sentence that step 2 is treated as BLOCKED because no report arrived, and ends the run. The `Next:` line is written as for BLOCKED in a run: `/implement-step <plan> 2-3`. Step 3 never starts. | yes |
| `<blocking> 2-4` | Step 2's worker is the first and blocks. One block, the run ends, `Next:` names `2-4`. | yes |
| `<blocking> 2`, `<blocking> 2-2` | Step 1 sets `first` and `last` to 2 and says to run and report it as a single step. The single-step `**BLOCKED**` bullet is the committed wording, so the output is unchanged from before the increment. | yes |

### Not evidenced here

- A real cast of `<blocking> 1-4` in a person's session, watching `## Step 1 — DONE` land, then
  `## Step 2 — BLOCKED`, then one `Next:` line naming `2-4`, with `step-3.txt` absent. That is the
  step's Manual validation and is still owed.
- A real worker that returns no report block. No fixture forces one, since a worker told to omit
  its report is not the same as one that ran out of room. The stand-in models the outcome; the
  relay sentence's exact wording is the orchestrator's and is not pinned beyond naming the reason.
- The `## Earlier in this run` section, the review-scope clause on the closing line, and a
  spell-cast step inside a range. The plan's Steps 3, 4, and 5 own those.
