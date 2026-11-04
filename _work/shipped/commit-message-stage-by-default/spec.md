# Spec for commit-message-stage-by-default

> This spec captures initial requirements and design rationale. For **current system
> behavior**, see the doc named on the **Work type** line below — a new feature doc for a new
> capability, an existing feature doc for a change, or a `docs/` runbook for a fix.

branch: robot-denny/commit-message-stage-by-default
design reference (if any): none

**Work type**: change-to commit-message
**Feature doc**: commit-message
<!--
  The /commit-message spell exists (skills/core/spellbook/commit-message/SKILL.md) but has no
  capability doc yet. Per the workflow skill, the classification does not depend on whether
  documentation exists: this changes an existing capability. /plan should create the doc at area
  level (`_features/commit-message.md`) covering what this increment establishes, and flag the
  rest of the spell's behavior for /feature's from-code backfill.
-->

## Summary

Today, casting `/commit-message` with edited files that are not staged stops and tells the
developer to stage them first. Adding "staging any files necessary" to the cast already gets the
behavior developers want: the agent looks at the unstaged changes, judges which belong with the
work, recommends what to include, and asks when it is unsure. This change makes that the default.

**Keep the change lean.** The agent's own judgment about which files are related is already
good, so the spell should not add rules, checklists, or heuristics for it. The change removes the
limitation and nothing more: the spell stops refusing when nothing is staged, it is allowed to
stage files, and it can see unstaged and new files alongside the staged ones.

The spell still never commits on its own. Staging happens only when the developer approves the
proposed message.

## Functional Requirements

- Unstaged and new files no longer stop the spell. It considers them along with anything already
  staged.
- Deciding which files belong in the commit is left to the agent's judgment. The spell does not
  prescribe how to decide.
- The proposal shows which files the agent would add to the commit, alongside the message.
- Staging happens only after the developer approves. A declined proposal leaves the working tree
  exactly as it was.
- A file is staged whole, never in part.
- A developer can say, in plain language, to commit only what is already staged.
- If there is nothing to commit at all, the spell says so and stops.

## Possible Edge Cases

- Nothing is staged and several unrelated sets of edits are present. Left to the agent's
  judgment; it may propose one set and suggest separate commits for the rest.
- A developer casts with the old phrase "staging any files necessary" out of habit. It should
  behave the same as the new default.

## Acceptance Criteria

- Unstaged edits no longer stop the spell.
- Files the agent judges related are proposed for the commit and staged on approval.
- Nothing is staged if the developer declines.
- A developer can limit the commit to what is already staged.

## Scenarios (Draft)

Draft BDD scenarios derived from the acceptance criteria using Example Mapping. Each Rule maps
to an acceptance criterion; scenarios use concrete examples. These get verified and refined
after implementation — the feature doc holds the verified version.

### Rule: Unstaged edits no longer stop the spell

```scenario
Scenario: Nothing staged, one edited file
  Given the developer has edited "README.md" and staged nothing
  When the developer casts /commit-message
  Then the spell does not stop with "nothing is staged"
  And it proposes committing "README.md" with a message
```

### Rule: Related files are proposed and staged on approval

```scenario
Scenario: A spell edit and its changelog entry
  Given the developer has staged "skills/core/spellbook/commit-message/SKILL.md"
  And has an unstaged edit to "CHANGELOG.md" describing that same spell change
  When the developer casts /commit-message
  Then the proposal includes "CHANGELOG.md"
  And when the developer approves, "CHANGELOG.md" is staged and committed with the spell edit
```

### Rule: Declining leaves the working tree untouched

```scenario
Scenario: Developer declines the proposal
  Given the developer has an unstaged edit to "CHANGELOG.md"
  And the spell has proposed committing it
  When the developer declines
  Then no commit is made
  And "CHANGELOG.md" is still unstaged
```

### Rule: A developer can limit the commit to what is already staged

```scenario
Scenario: Opting out in plain language
  Given the developer has staged "CHANGELOG.md"
  And has an unstaged edit to "README.md"
  When the developer casts /commit-message and says "just what's staged"
  Then the proposal covers "CHANGELOG.md" only
  And "README.md" stays unstaged
```

## Decisions

Settled during spec review:

- **Staging waits for approval.** The agent shows what it would stage alongside the message and
  stages only when the developer approves, so a declined message changes nothing.
- **Whole files only.** A file with both related and unrelated edits is staged whole or not at
  all.
- **Plain-language opt-out.** No fixed phrase; the agent interprets what the developer says.
- **Relatedness is the agent's call.** No relatedness rules, secret-file lists, or grouping
  heuristics. They would duplicate judgment the agent already exercises well.
- **No permission prompt for staging.** Staging runs without a prompt, as reading status and
  diffs does today. It only ever follows the developer's explicit approval of the proposal.

## Open Questions

- None.

## Testing Guidelines

Meaningful tests for the cases below, without going too heavy:

- Run the spell by hand in a scratch repository for each draft scenario and record the results in
  a validation log beside the increment.
- Confirm that the old "staging any files necessary" phrasing behaves the same as the default.
- Run `scripts/check-contract.sh` and confirm the edited spell still carries no project facts.
