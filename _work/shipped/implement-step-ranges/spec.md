# Spec for implement-step-ranges

> This spec captures initial requirements and design rationale. For **current system
> behavior**, see the doc named on the **Work type** line below — a new feature doc for a new
> capability, an existing feature doc for a change, or a `docs/` runbook for a fix.

branch: robot-denny/implement-step-ranges
design reference (if any): `_work/shipped/implement-step-ranges/discovery.md`, the discovery this spec continues

**Work type**: new-capability
**Feature doc**: plan-execution

## Summary

`/implement-step` runs one plan step per cast. A developer working through a plan of ten or more
steps casts it, reads the report, casts `/code-review`, approves its recommendations, and casts the
next step. On a small feature most of that loop is the person being present to say "go on". The
checkpoints that earn their keep catch taste, an over-complicated route the developer would not have
taken, and the team's remedy for that is a rule in the project's conventions rather than a human
watching every step.

This increment lets the developer choose where to pause, independent of how the plan was cut. A cast
may name a range of steps. The spell runs them in order, one fresh worker per step, relays each
report as it lands, and stops at the end of the range or at the first step that comes back BLOCKED.
Review stays a cast the person makes at the pause. The plan's closing report marks which steps end in
a manual check, so the developer can choose a range without opening the plan file.

The result at the end of a plan is unchanged. What falls is the number of times a person has to say
"proceed".

The area has no capability doc yet, so this increment creates `_features/plan-execution.md` at area
level. It will be thin: it records the range behavior this increment establishes and flags the
single-step behavior for `/feature`'s from-code mode to backfill.

## Functional Requirements

**Three argument forms, one behavior.**

- `/implement-step <plan> 4` runs step 4. Its behavior and output do not change.
- `/implement-step <plan> 1-3` runs steps 1, 2, and 3 in that order.
- `/implement-step <plan> 3-` runs from step 3 to the last numbered step of the plan.

A range of one, `4-4`, behaves exactly like `4`. A range whose bounds are reversed, or whose start or
end names a step the plan does not have, aborts before any worker runs, with the same one-line message
the single-step form already gives, listing the step numbers found. The open form is how a developer
says "to the end"; a closed range does not clamp.

**One fresh worker per step, in order.** Each step in the run gets its own worker with the same
self-contained prompt the single-step form composes today: the plan's Context, its Key Decisions, and
the step's own block. Nothing about the worker envelope changes.

**Earlier reports travel forward.** From the second step of a run onward, the worker's prompt carries
a section headed *Earlier in this run* holding the full report block of every step already finished
in this run. That gives a later worker what the human would have read between casts: a deviation from
the plan, a convention chosen because a slot was empty, an open question. The section holds only
reports from this run, not from earlier casts against the same plan.

**BLOCKED stops the run.** When a step's worker reports BLOCKED, or returns no report block at all,
the run stops there. Steps already finished stay finished. The relay says which step blocked and the
closing line points at re-invoking from that step. A missing report block is treated as BLOCKED and
named as such, since a run cannot tell an unfinished step from a finished one without it.

**A manual check does not stop the run.** A step whose validation includes a manual check runs like
any other. The worker attaches evidence rather than attesting, as the envelope already requires, and
the relay carries that evidence to the pause. Choosing where manual checks fall inside a range is the
developer's decision, made from the plan report.

**Reports relay verbatim, one closing line per run.** Each step's report block is surfaced as it
lands, unchanged, exactly as the single-step form does. The `Next:` line appears once, after the last
step of the run, not after every step.

**The closing line names the review scope.** After a run the closing line says to review the diff and
cast `/code-review`, and names the scope: `uncommitted` when no step in the run committed, `branch`
when any step's report says it did. It says in one clause why that scope, so a developer who has never
seen an empty review knows what would have gone wrong. After a run that reached the plan's last
numbered step, the line continues as today: `/commit-message`, then archive the increment.

**The dirty-tree prompt fires once.** The working-tree check runs before the first step of the run.
Between steps the tree is dirty by design, so the check is not repeated. Declining the prompt means no
step runs.

**An older plan's numbered spell-cast step ends the run early.** Plans written before the
behavior-recording step was left unnumbered may number it. A single cast already refuses such a step
and hands it back. A run that reaches one stops before it, relays everything finished, and hands it
back with the same message. It does not abort the whole run.

**The plan report marks the seams.** `/plan`'s closing report lists every numbered step by number and
title, and marks each step whose validation carries a manual check. The mark is derived from the
step's own Validation block, so a plan author adds nothing. The rest of the report, the path, the step
count, the branch, and the `Next:` line, is unchanged.

**Every surface that says "one step" is updated.** The `workflow` skill, the README's spellbook row,
`docs/layout.md`, and the spell cards for `/implement-step` and `/plan` all describe one step per
cast. Each is updated to describe the range as an ordinary documented form. The quick start and any
teaching material continue to lead with the single-step cast, as an editorial choice, not because the
range is hidden.

**Not in this increment.**

- No automatic review between steps or at the pause. ADR 0003 says spells chain by suggestion and
  never invoke each other, and the developer casts `/code-review` at the pause.
- No "stop at the next manual check" form. The plan report tells the developer where the seams are,
  and two stopping rules behind one argument is the cleverness the spell's rules of thumb warn against.
- No checkpoints in the plan format, and no suggested first range in the plan's `Next:` line.
- No warning about plan length. The fourteen-step plan seen in the field is a sizing problem upstream
  of this spell and is filed on the roadmap separately.

## Possible Edge Cases

- A range of one, `4-4`, must produce the single-step output, not a run wrapper around one step.
- `3-9` on a six-step plan aborts before step 3 runs. It does not run 3 through 6 and then complain.
- `0-2`, `2-1`, and `-3` are malformed and abort with the usage line.
- The first step of a run blocks. The relay is one BLOCKED report and a closing line, and no other
  worker was started.
- A plan that commits per step. After the run the uncommitted diff is empty, so the closing line names
  `branch` and says why.
- A step in the middle of the run commits and the rest do not. Any commit in the run selects `branch`.
- A worker returns prose with no report block. The run stops, and the relay says the step is treated
  as BLOCKED because no report arrived.
- A run of ten steps. Ten verbatim report blocks land in the main conversation. Accepted: the blocks
  are compact and a merged summary would hide which step a failed validation belonged to.
- The open form on a plan whose behavior-recording step is unnumbered runs to the last numbered step
  and never reaches the spell-cast step.
- A range that spans a manual check. The run does not pause; the evidence is in that step's report,
  and the developer knew the check was there from the plan report.

## Acceptance Criteria

- A developer can cast `/implement-step <plan> N-M` and the steps N through M run in order, each in
  its own worker, with each report relayed verbatim as it finishes.
- A developer can cast `/implement-step <plan> N-` and the run continues to the plan's last numbered
  step.
- A single-step cast behaves and reports exactly as before.
- A BLOCKED step, or a step with no report block, ends the run there. Finished steps stay finished,
  and the closing line says where to resume.
- A manual check inside a range does not pause the run, and its evidence appears in that step's
  relayed report.
- From the second step of a run, the worker's prompt carries every earlier report from the same run.
- The closing line after a run names the review scope, `uncommitted` or `branch`, with a one-clause
  reason, and appears once per run.
- The dirty-tree prompt fires once per run, before the first step.
- A malformed or out-of-range bound aborts before any worker starts, naming the steps found.
- A numbered spell-cast step inside a range ends the run before it, with everything earlier finished.
- `/plan`'s closing report lists every numbered step and marks those ending in a manual check.
- The workflow skill, README row, layout doc, and both spell cards describe the range form.

## Scenarios (Draft)

Draft BDD scenarios derived from the acceptance criteria using Example Mapping. Each Rule maps
to an acceptance criterion; scenarios use concrete examples. These get verified and refined
after implementation — the feature doc holds the verified version.

The plan in these scenarios is `accordion-block`, six numbered steps:

| Step | Title | Ends in a manual check |
|---|---|---|
| 1 | Element type | no |
| 2 | View | no |
| 3 | Palette registration | no |
| 4 | Open and close behavior | yes |
| 5 | Nested content | no |
| 6 | Styling | yes |

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
  And step 2's report says it committed
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

### Rule: A numbered spell-cast step ends the run before it

```scenario
Scenario: An older plan numbers its behavior-recording step
  Given the plan "legacy-hero" has five numbered steps
  And step 5 reads "run /feature update hero"
  When the developer casts /implement-step legacy-hero 3-
  Then steps 3 and 4 run
  And the run stops before step 5
  And the relay says step 5 is a spell-cast to be cast directly
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
  Given /plan has just saved a plan whose steps are all verified by commands
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

## Open Questions

- **Whether the *Earlier in this run* section needs a cap.** A plan rarely passes fifteen steps and a
  report block is a few dozen lines, so the section is bounded by the plan. Not capped here. If a
  consumer reports a worker prompt too long to be useful, the cap is the first thing to add.
- **Whether a run should ever pause for a manual check.** Discovery decided no, and the plan report
  is the remedy. If developers keep spanning manual checks by accident and wishing they had not, the
  rejected "stop at the next seam" form is the candidate to revisit, as a separate argument rather
  than a second meaning for the open form.
- **Where the range appears in teaching material.** The spell card and README document it. The quick
  start leads with the single step. Whether onboarding material ever mentions ranges is an editorial
  call left to whoever next edits it.
- **The fourteen-step plan.** Out of scope, and worth a roadmap entry of its own: a plan long enough
  to be tedious is usually a spec holding several increments, and nothing today says so at plan time.
- **Backfilling the area doc.** `_features/plan-execution.md` starts with only the range scenarios.
  The single-step behavior that existed before this increment is undocumented and is a candidate for
  `/feature`'s from-code mode.

## Testing Guidelines

Meaningful tests for the cases below, without going too heavy:

- **The layer contract holds.** `scripts/check-contract.sh` passes over the edited spells and docs: no
  project facts, no hardcoded paths, no naming of the source repos.
- **A dry run against a fixture plan.** This repo has no harness for spells, so the RED and GREEN
  signal is a validation log beside the increment: a six-step fixture plan with two manual checks,
  cast with `1-3`, `3-`, `4-4`, `3-9`, and `4-2`, with the relay output and the closing line captured
  for each. The BLOCKED case is exercised by a fixture step written to block.
- **The prompt carries earlier reports.** For a two-step run, capture the second worker's composed
  prompt and confirm the *Earlier in this run* section holds the first step's report verbatim, and
  that the first worker's prompt has no such section.
- **The plan report marks the right steps.** Cast `/plan` on a spec whose steps mix command and manual
  validation and confirm the marks match the Validation blocks.
- **Every one-step sentence is gone.** Grep the workflow skill, README, layout doc, and spell cards for
  "one step" and confirm each surviving mention describes the single-step form as one of three.
