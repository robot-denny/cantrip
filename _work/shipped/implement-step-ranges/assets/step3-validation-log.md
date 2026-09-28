# Step 3 — validation log

Working tree: branch `robot-denny/implement-step-ranges`, HEAD `381fa03`.

The spell under test is `skills/core/spellbook/implement-step/SKILL.md`. The plan it is cast
against is the fixture `_work/implement-step-ranges/assets/fixtures/accordion-block-plan.md`, written
below as `<plan>`. The cast is `<plan> 3-4`.

Every expectation below asserts on what a worker receives: the composed prompt handed to step 3's
worker and the one handed to step 4's worker. That is the interface the behavior is observable
through, since a worker can only act on what its prompt holds. None asserts on the spell's wording.
The expected values come from the two scenarios under the rule "Earlier reports travel forward" in
`_features/plan-execution.md` and from the step's Manual validation in the plan, not from the edit.

## Expected, written before the edit

### The report step 3's worker returns

The fixture's step 3 creates one file. Its worker's report, as this log assumes it, is the block
below. The Notes line is the one the plan's Manual validation asks a temporarily edited fixture to
produce, so the value comes from the plan and not from the spell.

```
## Step 3 — DONE

**Files changed**:
- _scratch/accordion-block/step-3.txt (created)

**Validation results**:
- test -f _scratch/accordion-block/step-3.txt: pass

**Notes**:
fixture: convention chosen here
```

The transcripts below name three input files. `step3-report.md` is the block above saved as a
file. `step2-report.md` is the same block with every `3` replaced by `2`, standing in for step 2's
worker. `carried.md` is whatever sits between the `## Earlier in this run` heading and `## Your
step` in a composed prompt, with its fence lines stripped, so it can be compared with the report
that went in.

### Step 3's composed prompt

- Opens `You are executing **Step 3** of the plan at` followed by the fixture path.
- Has, in this order, the sections `## Plan context`, `## Key decisions already made (do not
  re-derive)`, `## Your step`, `## Behavioral envelope`, `## Reporting format`, and no others.
- Contains no line reading `## Earlier in this run`, and does not contain the string `fixture:
  convention chosen here` anywhere. Step 3 is the first step of the run, so there is nothing to
  carry.
- `## Your step` holds the fixture's `### Step 3 — Palette registration` block.

### Step 4's composed prompt

- Opens `You are executing **Step 4** of the plan at` followed by the fixture path.
- Has, in this order, the sections `## Plan context`, `## Key decisions already made (do not
  re-derive)`, `## Earlier in this run`, `## Your step`, `## Behavioral envelope`, `## Reporting
  format`, and no others. The new section sits after the key decisions and before the step.
- Between `## Earlier in this run` and `## Your step`, the report block above appears in full and
  unchanged: the heading `## Step 3 — DONE`, the Files changed list, the Validation results list,
  and the Notes line `fixture: convention chosen here`. Nothing is summarized or trimmed.
- The section holds that one block and nothing else, since step 3 is the only step finished so far
  in this run. In particular it holds no report for steps 1 or 2, which were never part of this
  cast.
- `## Your step` holds the fixture's `### Step 4 — Open and close behavior` block.

### Two derived cases, so the section's shape is pinned

- Cast `<plan> 2-4`, step 4's prompt: the section holds `## Step 2 — DONE` then `## Step 3 — DONE`,
  in that order, both in full.
- Cast `<plan> 4` after a separate cast of `<plan> 3` has finished: step 4's prompt has no `## Earlier
  in this run` section. A single-step cast is a run of one, and the earlier cast's report belongs
  to that cast, not this one.

### What the manual cast adds

The plan's Manual validation is the person's: cast `3-4` with the fixture's step 3 prompt
temporarily asking its worker to add the note `fixture: convention chosen here`, and confirm step
4's worker mentions that note in its own report. A worker can only mention what it received, so
the mention is the behavior observed end to end. Nothing here evidences that; it is still owed.

## RED: the spell at `381fa03`

The committed spell's worker prompt template lists these sections, in Step 4:

```
$ git show 381fa03:skills/core/spellbook/implement-step/SKILL.md | grep -n '^## ' | sed -n '/Plan context/,/Reporting format/p'
108:## Plan context
112:## Key decisions already made (do not re-derive)
116:## Your step
121:## Behavioral envelope
155:## Reporting format
```

Nothing between `## Key decisions already made` and `## Your step`, and nothing anywhere in Step 4
or Step 6 that says a finished step's report goes into the next prompt. Step 6's first outcome
bullet reads `return to Step 4 for step N+1` and carries nothing with it.

### Composed mechanically

`_work/implement-step-ranges/assets/step3-standin.py` lifts the worker prompt template out of
whichever `SKILL.md` it is given, fills the placeholders from the plan the way Step 2 and Step 4
say to, and prints the prompt. Pointed at the committed spell, with the step 3 report above in
hand for step 4:

```
$ git show 381fa03:skills/core/spellbook/implement-step/SKILL.md > spell-381fa03.md
$ P=_work/implement-step-ranges/assets/fixtures/accordion-block-plan.md
$ ST=_work/implement-step-ranges/assets/step3-standin.py
$ python3 $ST spell-381fa03.md $P 3-4 3 > red-step3.md
$ python3 $ST spell-381fa03.md $P 3-4 4 step3-report.md > red-step4.md

$ grep -n '^## ' red-step3.md
4:## Plan context
11:## Key decisions already made (do not re-derive)
21:## Your step
34:## Behavioral envelope
68:## Reporting format
73:## Step 3 — <DONE | BLOCKED>

$ grep -n '^## ' red-step4.md
4:## Plan context
11:## Key decisions already made (do not re-derive)
21:## Your step
35:## Behavioral envelope
69:## Reporting format
74:## Step 4 — <DONE | BLOCKED>

$ grep -c 'Earlier in this run' red-step4.md
0
$ grep -c 'fixture: convention chosen here' red-step4.md
0
```

| Prompt | The `381fa03` spell composes | Expected | Result |
|---|---|---|---|
| step 3 | Five sections, no `## Earlier in this run`, no trace of the note | The same | already GREEN |
| step 4 | The same five sections. The step 3 report was in hand and went nowhere: the prompt has no `## Earlier in this run` line and the note `fixture: convention chosen here` appears nowhere in it | A sixth section between the key decisions and the step, holding the block in full | RED: the convention chosen in step 3's notes is **invisible to step 4** |

So the plan's Test-first block is answered as written: with the committed spell, a convention
chosen in step 3's notes cannot reach step 4's worker, because nothing in the composed prompt
carries it.

The composition above is a stand-in: a dispatched worker cannot cast a spell, so the script fills
the spell's own template as the spell says to. The real cast is the person's and is listed as the
step's Manual validation.

## GREEN: the edited spell

**This section is a stand-in.** A dispatched worker cannot cast a spell. What follows is the edited
`SKILL.md`'s worker prompt template, filled by the same script against the fixture, with the parts
that can be checked mechanically checked that way. The real cast is still owed and is the step's
Manual validation.

### Automated gates

```
$ ./scripts/check-contract.sh
22 checks passed.
```

The diff is one file, `skills/core/spellbook/implement-step/SKILL.md`, 31 insertions and 2
deletions after the review fixes (the fence rule and the Notes bound). Four places change. Step 4 gains two paragraphs before the template saying what the
section carries, when it is left out, that only this run's reports travel, and that it has no cap
and why. The template gains the `## Earlier in this run` section between the key decisions and
`## Your step`. Step 6's first outcome bullet, the return to Step 4 for step N+1, now says the
finished block is added to what that step's prompt carries. The rule of thumb naming the right cut
adds this run's earlier reports to it. `git diff` has no lines touching Step 3's dirty-tree prompt,
the `**Slot:**` / `**If empty:**` pair, the spell-cast refusal in Step 2, the BLOCKED handling, or
the `Next:` line. The added lines hold no em-dash. `grep -rn "is the right cut\|return to Step 4
for step N+1" tests/ scripts/check-contract.sh` finds nothing, so no test or contract check names
either phrase that was reworded.

### Composed mechanically

The same script, pointed at the working-tree spell:

```
$ SK=skills/core/spellbook/implement-step/SKILL.md
$ python3 $ST $SK $P 3-4 3 > green-step3.md
$ python3 $ST $SK $P 3-4 4 step3-report.md > green-step4.md

$ grep -n '^## ' green-step3.md
4:## Plan context
11:## Key decisions already made (do not re-derive)
21:## Your step
34:## Behavioral envelope
68:## Reporting format
73:## Step 3 — <DONE | BLOCKED>

$ grep -n '^## ' green-step4.md
4:## Plan context
11:## Key decisions already made (do not re-derive)
21:## Earlier in this run
24:## Step 3 — DONE
36:## Your step
50:## Behavioral envelope
84:## Reporting format
89:## Step 4 — <DONE | BLOCKED>

$ grep -c 'Earlier in this run' green-step3.md green-step4.md
green-step3.md:0
green-step4.md:1
$ grep -c 'fixture: convention chosen here' green-step3.md green-step4.md
green-step3.md:0
green-step4.md:1

$ # the block between the section heading and "## Your step", fence stripped, against the report
$ diff step3-report.md carried.md && echo identical
identical
```

| Prompt | The edited spell composes | Matches Expected |
|---|---|---|
| step 3 | The five sections of the single-step form, no `## Earlier in this run`, no trace of the note. Step 3 is the first step of the run and the section is left out whole, heading included. | yes |
| step 4 | Six sections. `## Earlier in this run` sits at line 21, after the key decisions at line 11 and before `## Your step` at line 36. Between them is the step 3 report, inside a code fence, byte-identical to the block the log assumed, Notes line included. | yes |

Two things about the shape are worth naming. The report's own `## Step 3 — DONE` heading survives
verbatim, which is why line 24 appears in the heading list; the fence around it keeps that heading
from ending the section early in a markdown reading. And the step 3 prompt is 88 lines while the
step 4 prompt is 104, so the whole cost of carrying one report is the block plus its fence and
heading.

### The two derived cases

```
$ # cast 2-4, composing step 4 with step 2's and step 3's reports in hand
$ python3 $ST $SK $P 2-4 4 step2-report.md step3-report.md \
    | awk '/^## Earlier in this run/{f=1} /^## Your step/{f=0} f' | grep -n '^## Step\|^```'
3:```
4:## Step 2 — DONE
13:```
15:```
16:## Step 3 — DONE
26:```

$ # a single-step cast of 4, no reports from this run
$ python3 $ST $SK $P 4 4 | grep -c 'Earlier in this run'
0

$ # the script refuses a report on the first step of a run, so no earlier cast's block can slip in
$ python3 $ST $SK $P 3-4 3 step3-report.md; echo "exit $?"
the first step of a run has no earlier reports; none should be passed
exit 1
```

`2-4` carries both blocks in run order, each in its own fence. A single-step cast carries none.
The third case is the script's own guard rather than the spell's behavior: the spell says an
earlier cast's report belongs to that cast, and the script models that by never reading one.

### Step 3's composed prompt, in full

````
You are executing **Step 3** of the plan at `_work/implement-step-ranges/assets/fixtures/accordion-block-plan.md`. The main conversation dispatched you so it
can stay clean — work in this isolated context and report back.

## Plan context

An accordion block is a content block with a heading that a reader clicks to open or close a panel
of content underneath. This plan builds one in six steps. Each step is deliberately tiny: the worker
creates a single text file named after the step under `_scratch/accordion-block/`, and nothing else.
The unit of work here is one file per step.

## Key decisions already made (do not re-derive)

- **Every step writes exactly one file.** Step N creates `_scratch/accordion-block/step-N.txt`
  containing the step's title on one line. Nothing else is created or modified. The directory is
  git-ignored, so no step dirties the working tree.
- **No test harness.** The automated check for each step is `test -f` on the file it created.
  Steps 4 and 6 also carry a manual check, so a run across them exercises the case where a manual
  check sits inside a range.
- **The worker does not commit.** Changes stay in place for the developer to inspect.

## Your step

### Step 3 — Palette registration

> **Prompt**: Implement Step 3 of `_work/implement-step-ranges/assets/fixtures/accordion-block-plan.md`.
> Run `mkdir -p _scratch/accordion-block`, then create `_scratch/accordion-block/step-3.txt`
> containing the single line `Palette registration`. Create nothing else and modify nothing else.

**What to build**: `_scratch/accordion-block/step-3.txt`, one line: `Palette registration`.

**Validation**:
- [Automated]: `test -f _scratch/accordion-block/step-3.txt` — exits 0.

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
## Step 3 — <DONE | BLOCKED>

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

### Step 4's composed prompt, in full

````
You are executing **Step 4** of the plan at `_work/implement-step-ranges/assets/fixtures/accordion-block-plan.md`. The main conversation dispatched you so it
can stay clean — work in this isolated context and report back.

## Plan context

An accordion block is a content block with a heading that a reader clicks to open or close a panel
of content underneath. This plan builds one in six steps. Each step is deliberately tiny: the worker
creates a single text file named after the step under `_scratch/accordion-block/`, and nothing else.
The unit of work here is one file per step.

## Key decisions already made (do not re-derive)

- **Every step writes exactly one file.** Step N creates `_scratch/accordion-block/step-N.txt`
  containing the step's title on one line. Nothing else is created or modified. The directory is
  git-ignored, so no step dirties the working tree.
- **No test harness.** The automated check for each step is `test -f` on the file it created.
  Steps 4 and 6 also carry a manual check, so a run across them exercises the case where a manual
  check sits inside a range.
- **The worker does not commit.** Changes stay in place for the developer to inspect.

## Earlier in this run

```
## Step 3 — DONE

**Files changed**:
- _scratch/accordion-block/step-3.txt (created)

**Validation results**:
- test -f _scratch/accordion-block/step-3.txt: pass

**Notes**:
fixture: convention chosen here
```

## Your step

### Step 4 — Open and close behavior

> **Prompt**: Implement Step 4 of `_work/implement-step-ranges/assets/fixtures/accordion-block-plan.md`.
> Run `mkdir -p _scratch/accordion-block`, then create `_scratch/accordion-block/step-4.txt`
> containing the single line `Open and close behavior`. Create nothing else and modify nothing else.

**What to build**: `_scratch/accordion-block/step-4.txt`, one line: `Open and close behavior`.

**Validation**:
- [Automated]: `test -f _scratch/accordion-block/step-4.txt` — exits 0.
- [Manual]: open the file and confirm it names the step.

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
## Step 4 — <DONE | BLOCKED>

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

### A report that contains its own fenced block

Added after review. The first version of this step fenced each carried report with three
backticks. A report whose Notes paste a fenced snippet, which the worker envelope invites for
evidence, would close that wrap early and spill the rest of the report into the prompt ahead of
`## Your step`. The spell now says the fence is one backtick longer than the longest run inside the
block, and the stand-in does the same. `fenced-report.md` is the step 3 report with a three-backtick
block pasted under Notes.

```
$ python3 $ST $SK $P 3-4 4 fenced-report.md \
    | awk '/^## Earlier in this run/{f=1} /^## Your step/{f=0} f' | grep -n '^`\|^## \|^exit'
1:## Earlier in this run
3:````
4:## Step 3 — DONE
14:```
16:exit 0
17:```
18:````
```

The wrap opens and closes with four backticks, the pasted three-backtick block sits whole inside
it, and nothing from the report escapes before `## Your step`.

### Not evidenced here

- A real cast of `3-4` in a person's session with the fixture's step 3 prompt temporarily asking
  for the note `fixture: convention chosen here`, and step 4's worker mentioning that note in its
  own report. That is the step's Manual validation and is still owed. It is the only evidence that
  the orchestrating model actually fills the section the way the template says, rather than the
  template merely saying so.
- That the orchestrator carries the block exactly as the worker returned it. The script copies the
  file it is given; a model relaying a block could drop a line. The spell says "whole and
  unchanged", and the manual cast is where that is checked.
- The review-scope clause on the closing line and a spell-cast step inside a range. The plan's
  Steps 4 and 5 own those.
