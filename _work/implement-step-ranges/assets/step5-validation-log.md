# Step 5 — validation log

Working tree: branch `robot-denny/implement-step-ranges`, HEAD `47887de`.

The spell under test is `skills/core/spellbook/plan/SKILL.md`, and the part under test is its
Step 7, the closing report a developer reads after a plan is saved. Two fixture plans stand in
for a plan `/plan` has just written: the six-step accordion fixture at
`_work/implement-step-ranges/assets/fixtures/accordion-block-plan.md`, written below as `<plan>`,
whose steps 4 and 6 each carry a `- [Manual]` line under **Validation**, and the five-step
`legacy-hero-plan.md` beside it, written as `<legacy>`, none of whose steps carries one. The
legacy fixture's step 5 is a numbered spell-cast with `**Validation**: none`, so it also checks
that a step with no Validation list at all is listed and unmarked.

Every expectation asserts on the report the developer sees: which lines appear under `Steps:`,
in what order, and which carry the mark. None asserts that a sentence exists in the spell. The
expected values come from the two scenarios under "The plan report marks the steps that end in a
manual check" in `_features/plan-execution.md`, and from the step's prompt in the plan, which
fixes the line shape as `  N  <title>`. None comes from the edit.

`_work/implement-step-ranges/assets/step5-standin.py` is the stand-in for this step. It reads a
plan file and prints the report, deriving the step list and the marks from the plan alone. It is
not the spell; it is the report rule as written, kept beside this log so the transcripts can be
re-run. The `Branch:` and `Next:` lines it prints are reproduced so the report reads whole and are
not what this step tests.

---

## Expected, written before the edit

### `<plan>`: six steps, two marked

Everything between `Steps:` and `Branch:` is new. The four other lines are today's, unchanged.

```
Plan: _work/implement-step-ranges/assets/fixtures/accordion-block-plan.md
Steps: 6
  1  Element type
  2  View
  3  Palette registration
  4  Open and close behavior (manual check)
  5  Nested content
  6  Styling (manual check)
Branch: <current branch>
Next: /implement-step <feature_slug> 1  (run each step in a fresh context to keep the main one clean)
```

Six lines, one per numbered step, in plan order. Each is two spaces, the step number, two spaces,
and the title from the step's `### Step N — <title>` heading. Steps 4 and 6 end in `(manual
check)`; steps 1, 2, 3, and 5 do not. The fixture's unnumbered `### Final` section is not a step
and has no line. `Steps: 6` counts the numbered steps, as it does today.

### `<legacy>`: five steps, none marked

```
Plan: _work/implement-step-ranges/assets/fixtures/legacy-hero-plan.md
Steps: 5
  1  Element type
  2  View
  3  Call to action
  4  Styling
  5  Record the durable behavior
Branch: <current branch>
Next: /implement-step <feature_slug> 1  (run each step in a fresh context to keep the main one clean)
```

Five lines, no mark on any of them. Step 5 has `**Validation**: none` rather than a list, and is
listed like the rest. The mark comes only from a `- [Manual]` line, so a plan whose author wrote
nothing under Validation gets a plain line, never an error and never a guessed mark.

### What the mark must not come from

The mark is derived. The plan template in Step 5 already puts a step's manual check on a line
beginning `- [Manual]`, so a plan author writes nothing extra to earn the mark and cannot forget
to. A step whose Validation block mentions the word "manual" in an `[Automated]` line, or whose
prose says "check by eye" without the `[Manual]` line, is not marked. Neither fixture exercises
that case; it is stated here so the edit does not widen the rule.

---

## RED: the spell at `47887de`

The committed Step 7, in full:

````
$ git show 47887de:skills/core/spellbook/plan/SKILL.md | sed -n '297,310p'
## Step 7 — Save and report

Save the plan into the increment's working directory alongside its spec.

Report in this format:

```
Plan: <path to the saved plan>
Steps: N
Branch: <current branch>
Next: /implement-step <feature_slug> 1  (run each step in a fresh context to keep the main one clean)
```

Do not print the full plan to chat — just the summary above. The plan lives in the file.
````

The report has no step list. It names a count and nothing between the count and the branch, so a
developer choosing a range has to open the plan file to learn where the manual checks fall. The
stand-in's `--committed` mode prints that format, and both fixtures come out four lines long:

```
$ python3 step5-standin.py <plan> --committed
Plan: _work/implement-step-ranges/assets/fixtures/accordion-block-plan.md
Steps: 6
Branch: robot-denny/implement-step-ranges
Next: /implement-step accordion-block 1  (run each step in a fresh context to keep the main one clean)

$ python3 step5-standin.py <legacy> --committed
Plan: _work/implement-step-ranges/assets/fixtures/legacy-hero-plan.md
Steps: 5
Branch: robot-denny/implement-step-ranges
Next: /implement-step legacy-hero 1  (run each step in a fresh context to keep the main one clean)
```

| Fixture | Expected under `Steps:` | The `47887de` spell prints | Result |
|---|---|---|---|
| `<plan>` | six lines, steps 4 and 6 marked | nothing | RED |
| `<legacy>` | five lines, none marked | nothing | RED, for the list; the absence of marks is trivially met by an absent list |

The second row is why the accordion fixture is the one that carries the step. A report with no
list satisfies "no marks" for free, and only the marked fixture can fail for the right reason.

---

## GREEN: the edited spell

**This section is a stand-in.** A dispatched worker cannot cast a spell. What follows is the
edited Step 7 read against each fixture as `/plan` would read the plan it had just saved, and the
stand-in's output for the same rule. The real cast is the person's and is the step's Manual
validation.

The edited Step 7 now says, after the format block: list every numbered step on its own line, in
plan order, as two spaces, the number, two spaces, and the heading's title; the unnumbered final
step is not listed; append `(manual check)` to a step whose **Validation** block carries a line
beginning `- [Manual]`; the mark is derived from the plan, so the author adds nothing; a step with
no such line gets a plain line, including one whose Validation reads `none`.

```
$ python3 step5-standin.py <plan>
Plan: _work/implement-step-ranges/assets/fixtures/accordion-block-plan.md
Steps: 6
  1  Element type
  2  View
  3  Palette registration
  4  Open and close behavior (manual check)
  5  Nested content
  6  Styling (manual check)
Branch: robot-denny/implement-step-ranges
Next: /implement-step accordion-block 1  (run each step in a fresh context to keep the main one clean)

$ python3 step5-standin.py <legacy>
Plan: _work/implement-step-ranges/assets/fixtures/legacy-hero-plan.md
Steps: 5
  1  Element type
  2  View
  3  Call to action
  4  Styling
  5  Record the durable behavior
Branch: robot-denny/implement-step-ranges
Next: /implement-step legacy-hero 1  (run each step in a fresh context to keep the main one clean)
```

| Fixture | The edited spell does | Matches Expected |
|---|---|---|
| `<plan>` | Six `### Step N —` headings, so six lines. Steps 4 and 6 each have `- [Manual]: open the file and confirm it names the step.` under **Validation**, so those two lines end in `(manual check)`. Steps 1, 2, 3, and 5 have only an `[Automated]` line and are plain. The `### Final` heading is not a `### Step`, so it has no line and does not count. | yes, line for line |
| `<legacy>` | Five headings, five lines. No step has a `- [Manual]` line. Step 5's Validation reads `none`; the spell says such a step gets a plain line, and it does. | yes, line for line |

A third run against `accordion-block-blocking-plan.md`, the step 2 BLOCKED variant of the accordion
fixture, prints the same six lines with the same two marks. Its only difference from `<plan>` is in
step 2's prompt, which the report does not read, so this is a check that the mark comes from the
Validation block and from nowhere else in a step.

The mark's placement matters for the person's cast. The spell reads a step's **Validation** block,
and the plan template in Step 5 puts the manual check there on a `- [Manual]` line. A plan `/plan`
writes from that template therefore carries the signal without the author's involvement, which is
what "derived" means in the spec. What a cast alone can show is that the orchestrating model lists
from the plan it saved rather than from the steps it remembers drafting, and that it does not mark
a step whose Validation merely mentions checking by eye without the `[Manual]` line.

---

## Final gate

```
$ ./scripts/check-contract.sh
22 checks passed.
```

`git status --short` shows the spell modified and two files added under
`_work/implement-step-ranges/assets/`: this log and `step5-standin.py`. `git diff --stat` shows
`skills/core/spellbook/plan/SKILL.md` with fifteen insertions and no deletions: the four lines of
today's report are still present in the format block, so no contract check or test that reads them
had anything to lose. `grep -rn "Steps:" scripts/check-contract.sh tests/` finds nothing; no check
reads this report. Every `**Slot:**` / `**If empty:**` pair in the spell is untouched. Nothing under
`_scratch/` was created.

## Not evidenced here

- A real cast of `/plan` on a throwaway two-step description, one step verified by a command and one
  by eye, showing the closing report list both steps and mark only the second. This is the step's
  Manual validation and is still owed. The scratch increment it creates is deleted afterwards.
- That the orchestrating model derives the list from the saved file rather than from its own draft.
  The two agree when the save is faithful, and only a cast where they differ would tell them apart.
- A plan of ten or more steps, where the two-space column before the number no longer aligns the
  titles. The format is the plan's `  N  <title>` and this log does not widen it.
- The documentation surfaces and the spell card for `/plan`. Plan Step 6 owns those.
