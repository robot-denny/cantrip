# Feature: Plan Execution

A developer runs a saved plan one step at a time, or across a range of steps, and gets a short
report for each step. Each step runs in its own fresh context so the main conversation stays clean.
The developer chooses where to pause, and the plan's own report shows where the manual checks fall so
that choice is an informed one.

**Source**: `_work/implement-step-ranges/spec.md`
**Last verified**: 2026-09-28

---

## Increments

The per-feature mini-roadmap: shipped increments, planned increments, and parking-lot ideas.
Newest planned items first. When an item ships, flip the checkbox and point it at the archived
increment.

- [ ] Implement-step ranges (`_work/implement-step-ranges/spec.md`, built on
  `robot-denny/implement-step-ranges`, awaiting merge)
- [ ] Backfill the single-step behavior that predates this doc (`/feature` from-code mode, no spec)

---

## Behaviors

Scenarios are grouped by Rule — the business rule or acceptance criterion the scenarios prove.
Use concrete values (Specification by Example) and business language (Ubiquitous Language). See
the `bdd-principles` skill for guidance.

The plan in these scenarios is `accordion-block`, six numbered steps. Steps 4 and 6 end in a manual
check; the rest are verified by commands. A second plan, `legacy-hero`, has five numbered steps and
numbers its behavior-recording step.

### Rule: A closed range runs its steps in order and relays each report as it lands

```scenario
Scenario: Three steps run from one cast
  Given the plan "accordion-block" has six numbered steps
  When the developer casts /implement-step accordion-block 1-3
  Then steps 1, 2, and 3 run in that order, each in its own worker
  And the report for step 1 is relayed before step 2 starts
  And exactly one Next line appears, after the report for step 3
```

```scenario
Scenario: A range of one is the single-step cast
  Given the plan "accordion-block" has six numbered steps
  When the developer casts /implement-step accordion-block 4-4
  Then the output is identical to casting /implement-step accordion-block 4
```

### Rule: An open range runs to the plan's last numbered step

```scenario
Scenario: Running from step 3 to the end
  Given the plan "accordion-block" has six numbered steps
  And its behavior-recording step is unnumbered
  When the developer casts /implement-step accordion-block 3-
  Then steps 3, 4, 5, and 6 run in that order
  And the behavior-recording step is not dispatched
  And the Next line says to review, cast /code-review, then /commit-message, then archive the increment
```

### Rule: A single-step cast is unchanged

```scenario
Scenario: One step, as before
  Given the plan "accordion-block" has six numbered steps
  When the developer casts /implement-step accordion-block 2
  Then step 2 runs in its own worker
  And its report is relayed verbatim
  And the Next line points at /implement-step accordion-block 3
```

### Rule: A blocked step ends the run and says where to resume

```scenario
Scenario: The second step of a run blocks
  Given the plan "accordion-block" has six numbered steps
  When the developer casts /implement-step accordion-block 1-4
  And step 2's worker reports BLOCKED
  Then step 1's changes stay in place
  And no worker is started for steps 3 or 4
  And the relay shows step 1 DONE and step 2 BLOCKED
  And the Next line says to resolve the blocker and re-invoke /implement-step accordion-block 2-4
```

```scenario
Scenario: A worker returns no report block
  Given the plan "accordion-block" has six numbered steps
  When the developer casts /implement-step accordion-block 1-3
  And step 2's worker ends without a "Step 2" report block
  Then the run stops after step 2
  And the relay says step 2 is treated as BLOCKED because no report arrived
```

### Rule: A manual check inside a range does not pause the run

```scenario
Scenario: Running through the open-and-close check
  Given the plan "accordion-block" has six numbered steps
  And step 4 ends in a manual check that the accordion opens and closes
  When the developer casts /implement-step accordion-block 1-5
  Then the run continues from step 4 into step 5 without waiting
  And step 4's relayed report carries the evidence its worker captured for the manual check
```

### Rule: Later workers in a run see the reports of earlier steps

```scenario
Scenario: A convention chosen in step 1 reaches step 2
  Given the plan "accordion-block" has six numbered steps
  And the project's test-location slot is empty
  When the developer casts /implement-step accordion-block 1-2
  And step 1's report notes "no test location was configured; tests were placed under tests/blocks/"
  Then step 2's worker prompt contains a section "Earlier in this run" holding step 1's full report
  And step 2's tests are placed under tests/blocks/
```

```scenario
Scenario: The first step of a run carries no earlier reports
  Given the plan "accordion-block" has six numbered steps
  When the developer casts /implement-step accordion-block 3-4
  Then step 3's worker prompt has no "Earlier in this run" section
  And step 4's worker prompt has one, holding step 3's report
```

### Rule: The closing line names the review scope

```scenario
Scenario: No step committed
  Given the plan "accordion-block" leaves changes in place at every step
  When the developer casts /implement-step accordion-block 1-3
  Then the closing line says to cast /code-review with the uncommitted scope
  And it says that is because the run's changes are still uncommitted
```

```scenario
Scenario: One step in the run committed
  Given the plan "accordion-block" tells step 2 to commit
  When the developer casts /implement-step accordion-block 1-3
  And step 2's report carries the line "Committed: yes" under its Notes
  Then the closing line says to cast /code-review with the branch scope
  And it says that is because a step in the run committed, so the uncommitted diff would miss it
```

### Rule: The dirty-tree prompt fires once per run

```scenario
Scenario: A clean tree at the start
  Given the working tree is clean
  When the developer casts /implement-step accordion-block 1-3
  Then no dirty-tree prompt appears before step 1
  And no dirty-tree prompt appears before step 2 or step 3, although the tree is now dirty
```

```scenario
Scenario: A dirty tree at the start, declined
  Given the working tree has uncommitted changes
  When the developer casts /implement-step accordion-block 1-3
  And answers "no" to the dirty-tree prompt
  Then no step runs
```

### Rule: The plan report marks the steps that end in a manual check

```scenario
Scenario: Choosing a range from the plan report
  Given /plan has just saved "accordion-block" with six numbered steps
  When the closing report prints
  Then it lists steps 1 through 6 by number and title
  And steps 4 and 6 carry a manual-check mark
  And steps 1, 2, 3, and 5 do not
```

```scenario
Scenario: A plan with no manual checks
  Given /plan has just saved "legacy-hero", whose steps are all verified by commands
  When the closing report prints
  Then every step is listed and none carries a manual-check mark
```

### Rule: Every surface that said "one step per cast" describes the range

```scenario
Scenario: A reader learns the range form from the spell card
  Given a reader opens the /implement-step spell card
  When they read its Cast line
  Then it shows the single step, the closed range, and the open range
```

---

## Edge Cases

### Rule: A malformed or out-of-range bound aborts before any worker starts

```scenario
Scenario: A range past the end of the plan
  Given the plan "accordion-block" has six numbered steps
  When the developer casts /implement-step accordion-block 3-9
  Then no worker starts
  And the message lists the steps found, 1 through 6
```

```scenario
Scenario: A reversed range
  Given the plan "accordion-block" has six numbered steps
  When the developer casts /implement-step accordion-block 4-2
  Then no worker starts
  And the message shows the expected usage
```

```scenario
Scenario: A range that spans a gap in the plan's numbering
  Given a plan whose steps are numbered 1, 2, 4, 5, and 6
  When the developer casts /implement-step on it with 1-5
  Then no worker starts
  And the message lists the steps found, 1, 2, 4, 5, and 6
```

### Rule: A numbered spell-cast step ends the run before it

```scenario
Scenario: An older plan numbers its behavior-recording step
  Given the plan "legacy-hero" has five numbered steps
  And step 5 reads "run /feature update hero"
  When the developer casts /implement-step legacy-hero 3-
  Then steps 3 and 4 run
  And the run stops before step 5
  And the relay says step 5 is a spell-cast to be cast directly
  And the Next line says to cast it, then cast /code-review, then /commit-message
```

### Rule: A carried report cannot break the prompt it travels in

```scenario
Scenario: A carried report contains its own fenced block
  Given the plan "accordion-block" has six numbered steps
  And step 3's report pastes a three-backtick block of test output under its Notes
  When the developer casts /implement-step accordion-block 3-4
  Then step 4's worker prompt wraps step 3's report in a four-backtick fence
  And the whole report, pasted block included, sits inside that fence
```

---

## Test Coverage

This repository ships no test harness for spells. Every `Covered` row below was proved by a stand-in
script under `_work/implement-step-ranges/assets/` that applies the spell's stated rule to a fixture
plan, run and recorded in the named log at the named line. None was proved by a real cast in a
session, and those casts remain owed to a person. The one scenario with no script behind it was
read by a person on 2026-09-28 and found correct, and is recorded as `Not covered` because reading
is not a test.

| Scenario | Test File | Status |
|----------|-----------|--------|
| Three steps run from one cast | `_work/implement-step-ranges/assets/step1-validation-log.md:131` | Covered |
| A range of one is the single-step cast | `_work/implement-step-ranges/assets/step1-validation-log.md:133` | Covered |
| Running from step 3 to the end | `_work/implement-step-ranges/assets/step1-validation-log.md:132` | Covered |
| One step, as before | `_work/implement-step-ranges/assets/step1-validation-log.md:136` | Covered |
| The second step of a run blocks | `_work/implement-step-ranges/assets/step2-validation-log.md:134` | Covered |
| A worker returns no report block | `_work/implement-step-ranges/assets/step2-validation-log.md:144` | Covered |
| Running through the open-and-close check | `_work/implement-step-ranges/assets/step1-validation-log.md:132` | Covered |
| A convention chosen in step 1 reaches step 2 | `_work/implement-step-ranges/assets/step3-validation-log.md:180` | Covered |
| The first step of a run carries no earlier reports | `_work/implement-step-ranges/assets/step3-validation-log.md:200` | Covered |
| No step committed | `_work/implement-step-ranges/assets/step4-validation-log.md:226` | Covered |
| One step in the run committed | `_work/implement-step-ranges/assets/step4-validation-log.md:229` | Covered |
| A clean tree at the start | `_work/implement-step-ranges/assets/step4-validation-log.md:104` | Covered |
| A dirty tree at the start, declined | `_work/implement-step-ranges/assets/step4-validation-log.md:129` | Covered |
| Choosing a range from the plan report | `_work/implement-step-ranges/assets/step5-validation-log.md:144` | Covered |
| A plan with no manual checks | `_work/implement-step-ranges/assets/step5-validation-log.md:156` | Covered |
| A reader learns the range form from the spell card | — | Not covered |
| A range past the end of the plan | `_work/implement-step-ranges/assets/step1-validation-log.md:134` | Covered |
| A reversed range | `_work/implement-step-ranges/assets/step1-validation-log.md:135` | Covered |
| A range that spans a gap in the plan's numbering | `_work/implement-step-ranges/assets/step1-validation-log.md:153` | Covered |
| An older plan numbers its behavior-recording step | `_work/implement-step-ranges/assets/step4-validation-log.md:349` | Covered |
| A carried report contains its own fenced block | `_work/implement-step-ranges/assets/step3-validation-log.md:462` | Covered |

<!-- Status vocabulary. Each status is a claim about what is proved, not a stage in a process:
     read a row as its answer to "what does this entitle me to believe?"

     FOUR STATUSES RECORD AN OBSERVATION — what was seen, or that nothing was:

     - Covered: a test asserts this scenario, and its last run passed.
     - Test failing: a test asserts this scenario, and its last run did not pass. Named for what was
       observed rather than for its cause, because the cause may be behavior not built yet, a
       regression, or a doc that is simply wrong, and the row cannot tell those apart. Whatever
       reported the run is where the cause gets argued.
     - Not covered: the scenario is specified, and nothing asserts it.
     - Not covered (code-derived): the rule was inferred by reading the code — never specified and
       never tested, and so the weakest claim in this table.

     ONE STATUS RECORDS A DECISION, and it is the only one a person writes deliberately:

     - Ruled out — <reason>: the project has decided this scenario cannot be proved here, and
       the reason travels in the row so a later reader can judge whether it still holds.

     The split is the point. The four above say what happened; this one says somebody chose — the
     difference between a gap nobody has reached yet and a gap the project decided to live with. It is
     named unlike the other four on purpose: an earlier draft called it "Not coverable", which sat one
     syllable from "Not covered" and was misread as an ordinary gap every time somebody skimmed the
     table. A status that records a decision should not look like a status that records an absence. -->

---

## Revision Notes

- 2026-09-25: Draft scenarios from initial spec
- 2026-09-28: Verified against the finished spells and the six validation logs. Three scenarios
  added for behavior the increment settled at review: a gapped range aborts before any worker
  starts, a carried report is fenced so its own fenced block cannot break the prompt, and the
  commit signal a worker writes is the line `Committed: yes`. The spell-cast stop scenario gained
  its closing line. Coverage rows point at the stand-in runs; the real casts are still owed.
