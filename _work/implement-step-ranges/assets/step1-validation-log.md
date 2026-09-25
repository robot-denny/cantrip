# Step 1 — validation log

Working tree: branch `robot-denny/implement-step-ranges`, HEAD `b812a22`.

The spell under test is `skills/core/spellbook/implement-step/SKILL.md`. The plan it is cast
against is the fixture `_work/implement-step-ranges/assets/fixtures/accordion-block-plan.md`,
six numbered steps plus an unnumbered final step. Each fixture step creates one file,
`_scratch/accordion-block/step-N.txt`, and nothing else.

Every expectation below asserts on what the developer sees: the report blocks relayed into the
conversation, the `Next:` line, and the files under `_scratch/accordion-block/`. None asserts on
the spell's wording. The expected values come from the scenarios in
`_features/plan-execution.md` and the spec's edge cases, not from the edit.

## Expected, written before the edit

`<plan>` below stands for `_work/implement-step-ranges/assets/fixtures/accordion-block-plan.md`.
`_scratch/accordion-block/` is empty before every cast.

### Cast `1-3`

- Three workers start, for steps 1, 2, and 3, in that order. Step 2's worker does not start until
  step 1's report has been relayed.
- The conversation shows three report blocks, in order: `## Step 1 — DONE`, `## Step 2 — DONE`,
  `## Step 3 — DONE`. Each names its own file under **Files changed** and reports
  `test -f _scratch/accordion-block/step-N.txt: pass`.
- Exactly one `Next:` line, after the third block. It says to review the diff, cast `/code-review`,
  then `/implement-step <plan> 4`.
- `ls _scratch/accordion-block/` prints `step-1.txt step-2.txt step-3.txt`. No `step-4.txt`.

### Cast `3-`

- Four workers start, for steps 3, 4, 5, and 6, in that order.
- Four report blocks in order: `## Step 3 — DONE` through `## Step 6 — DONE`.
- No worker starts for the unnumbered final step, and nothing in the relay mentions it as a step
  that ran.
- Exactly one `Next:` line, after the step 6 block. Because step 6 is the last numbered step, it
  says to review the diff, cast `/code-review`, then `/commit-message`, then archive the increment.
- `ls _scratch/accordion-block/` prints `step-3.txt step-4.txt step-5.txt step-6.txt`.

### Cast `4-4`

- Byte-for-byte the output of casting `<plan> 4`: one worker, one block `## Step 4 — DONE`, and one
  `Next:` line pointing at `/implement-step <plan> 5`. No wording that announces a run, a range, or
  a count of steps.
- `ls _scratch/accordion-block/` prints `step-4.txt`.

### Casts `3-9`, `4-2`, and `0-2`

- No worker starts.
- One message, and the same message for all three. It names the steps the plan has,
  `1, 2, 3, 4, 5, 6`, so the developer can pick a bound that exists.
- `ls _scratch/accordion-block/` prints nothing. In particular `3-9` does not run steps 3 through 6
  and complain afterwards: `step-3.txt` must not exist.

### Cast `-3`

- No worker starts.
- One message showing the expected usage. `-3` does not match the step grammar
  `^(\d+)(?:-(\d+)?)?$`, so it is malformed rather than out of range. The spec's edge cases list it
  with the usage line, and that is what is expected here. This is a deliberate narrowing of the
  plan's "message naming steps 1 through 6" for this one cast: the usage check runs before the
  plan is read, so the steps found are not known yet. Whether the message also names the steps is
  not asserted.
- `ls _scratch/accordion-block/` prints nothing.

## RED: the unedited spell

The spell at HEAD `b812a22` reads, in Step 1:

```
$ git show HEAD:skills/core/spellbook/implement-step/SKILL.md | sed -n '17,26p'
## Step 1 — Parse the arguments

Expect two whitespace-separated tokens:

1. **plan** — the increment's plan (a slug or a path)
2. **step_number** — an integer

If either is missing or malformed, abort with a one-line message showing the expected usage, and
stop. If the plan doesn't exist on disk, abort with a one-line message and stop. **Do not guess at
alternative paths.**
```

Walking each cast through that text:

| Cast | Unedited spell does | Expected | Result |
|---|---|---|---|
| `1-3` | `1-3` is not an integer, so Step 1 aborts with the usage line. No worker starts, no file is created. | Three blocks, three files, one `Next:` | RED |
| `3-` | Same abort. | Four blocks, four files, one `Next:` | RED |
| `4-4` | Same abort. | The single-step output for step 4 | RED |
| `3-9`, `4-2`, `0-2` | Same abort, with the usage line rather than the steps found. | No worker, a message naming steps 1 through 6 | RED (right stop, wrong message) |
| `-3` | Same abort with the usage line. | No worker, the usage line | already GREEN |

The walk-through above is a stand-in: a dispatched worker cannot cast a spell, so it reads the
spell and follows it. The real cast is the person's and is listed as the step's Manual validation.

## GREEN: the edited spell

**This section is a stand-in.** A dispatched worker cannot cast a spell. What follows is the edited
`SKILL.md` read and followed against the fixture, with the parts that can be checked mechanically
checked that way. The real cast is still owed and is the step's Manual validation.

### Automated gates

```
$ ./scripts/check-contract.sh
22 checks passed.

$ tests/run.sh
110/110 cases passed across 3 suites.
```

The diff is one file, `skills/core/spellbook/implement-step/SKILL.md`, 63 insertions and 27
deletions after the review fixes (a contiguity rule and the conventions slot read once per cast). `git diff` has no lines touching Step 3's dirty-tree prompt, the `**BLOCKED**:` bullet,
or the worker envelope between `## Behavioral envelope` and the end of the reporting format.

### The grammar and the bounds, applied mechanically

Step 1 and Step 2 of the edited spell state a regex and five bound rules. A short script,
`_work/implement-step-ranges/assets/step1-standin.py`, applies those rules, as written, to a plan
file and prints what each cast does before any worker starts. The script is not the spell; it is
the spell's parsing rules with nothing added, and it is kept beside this log so the transcript
below can be audited and re-run.

```
$ python3 _work/implement-step-ranges/assets/step1-standin.py \
    _work/implement-step-ranges/assets/fixtures/accordion-block-plan.md \
    1-3 3- 4-4 3-9 4-2 0-2 -3 4 6-6
steps found: [1, 2, 3, 4, 5, 6]; unnumbered final step present: True
 1-3: run [1, 2, 3] -> 3 worker(s), 3 report block(s), run, one Next: -> /implement-step <plan> 4
  3-: run [3, 4, 5, 6] -> 4 worker(s), 4 report block(s), run, one Next: -> /commit-message, archive
 4-4: run [4] -> 1 worker(s), 1 report block(s), single-step output, one Next: -> /implement-step <plan> 5
 3-9: OUT OF RANGE -> abort listing steps found [1, 2, 3, 4, 5, 6], no worker
 4-2: OUT OF RANGE -> abort listing steps found [1, 2, 3, 4, 5, 6], no worker
 0-2: OUT OF RANGE -> abort listing steps found [1, 2, 3, 4, 5, 6], no worker
  -3: MALFORMED -> usage line, no worker
   4: run [4] -> 1 worker(s), 1 report block(s), single-step output, one Next: -> /implement-step <plan> 5
 6-6: run [6] -> 1 worker(s), 1 report block(s), single-step output, one Next: -> /commit-message, archive
```

`4` and `4-4` print the same line, which is the byte-for-byte expectation. `3-` stops at 6 and the
`### Final —` heading is not counted as a step found. `3-9` aborts before step 3 runs.

The fifth rule, added after review, is that every number between `first` and `last` must be a step
found. Evidence uses a throwaway copy of the fixture with its `### Step 3` heading renamed so the
plan numbers 1, 2, 4, 5, 6:

```
$ sed 's/^### Step 3 — /### Step 3-removed — /' accordion-block-plan.md > gapped-plan.md
$ python3 _work/implement-step-ranges/assets/step1-standin.py gapped-plan.md 1-5 1-2 4-
steps found: [1, 2, 4, 5, 6]; unnumbered final step present: True
 1-5: OUT OF RANGE -> abort listing steps found [1, 2, 4, 5, 6], no worker
 1-2: run [1, 2] -> 2 worker(s), 2 report block(s), run, one Next: -> /implement-step <plan> 3
  4-: run [4, 5, 6] -> 3 worker(s), 3 report block(s), run, one Next: -> /commit-message, archive
```

`1-5` aborts before any worker starts even though both bounds exist, which is the case the rule
was added for. `1-2` and `4-` run, because no gap lies inside them. The gapped copy was deleted
after the run.

### The fixture's steps are runnable and leave no trace

Each fixture step's commands were run by hand for steps 1 through 3, then the directory removed.
This checks the fixture, not the spell.

```
step 1: test -f pass (Element type)
step 2: test -f pass (View)
step 3: test -f pass (Palette registration)
ls: step-1.txt step-2.txt step-3.txt
git status shows no _scratch entry
cleaned: ls: _scratch/accordion-block: No such file or directory
```

### The run loop, walked by reading

The script covers Steps 1 and 2. Steps 3 through 6 are followed by reading the edited text.

| Cast | Walk | Matches Expected |
|---|---|---|
| `1-3` | Step 3 runs `git status --short` once, since it sits outside the loop that Step 4 opens. Step 4 composes step 1's prompt from Context, Key Decisions, and the step 1 block. Step 5 dispatches one worker and waits. Step 6 surfaces `## Step 1 — DONE` before step 2's prompt is composed. The same for 2, then 3. After the step 3 block, one `Next:` line for N=3, pointing at `/implement-step <plan> 4`. Files: `step-1.txt` through `step-3.txt`. | yes |
| `3-` | As above for 3, 4, 5, 6. Step 4's manual check does not pause the loop; its worker attaches evidence per the envelope. After step 6, N=6 is the final numbered step, so the `Next:` line names `/commit-message` and archiving. The unnumbered final step was never a step found, so no prompt is composed for it. | yes |
| `4-4` | Step 1 sets `first` and `last` to 4 and says to run and report it exactly as `4`, with no wording that announces a run. One prompt, one worker, one block, one `Next:` to step 5. | yes |
| `3-9`, `4-2`, `0-2` | Step 2 aborts on the bound check with the steps-found message. Step 3 is never reached, so no dirty-tree prompt and no worker. | yes |
| `-3` | Step 1's regex rejects it; the usage line prints. Step 2 is never reached. | yes, per the narrowed expectation recorded above |

### Not evidenced here

- A real cast of `1-3`, `4-4`, and `3-9` in a person's session, watching three report blocks land
  in order and exactly one `Next:` line. That is the step's Manual validation and is still owed.
- What happens when a step in a run comes back BLOCKED, or returns no report block. The spell's
  Step 6 still carries only the single-step BLOCKED bullet; the plan's Step 2 owns that behavior.
- What happens when a spell-cast step, one whose content is "run `/feature update …`", sits inside
  the range. Step 2's refusal was written for a single cast and is unchanged here, so on `3-6` with
  a spell-cast at step 5 the literal reading hands back during extraction and steps 3 and 4 never
  run. The plan's Step 4 owns stopping before such a step and keeping what finished.
