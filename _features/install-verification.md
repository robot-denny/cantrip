# Feature: Install Verification

A consumer who has installed the toolkit can confirm in one pass what actually landed — which skills
resolve, whether their bundled assets are readable, whether review is running at full strength or
degraded, and which parts of their project the toolkit currently knows about. It distinguishes a
working install from a degraded one from a broken one, so problems surface before a spell is cast
rather than during one.

**Source**: `_work/shipped/install-verification/spec.md`
**Last verified**: 2026-08-17

---

## Increments

The per-feature mini-roadmap: shipped increments, planned increments, and parking-lot ideas.
Newest planned items first. When an item ships, flip the checkbox and point it at the archived
increment.

- [x] 2026-08-17 — Verification across several packs: a pack verifies alone, a reinstall hint names
  the pack that ships a unit, and a setting read by two packs is counted once
  (`_work/pack-boundaries-and-succession/spec.md`)
- [x] 2026-08-03 — Install verification check (`_work/shipped/install-verification/spec.md`)
- [ ] Parking lot: verify slot *content* rather than presence, if presence proves too weak in practice
- [ ] Parking lot: tell a unit that *moved* from one that was *deleted* — a consumer's records can pin
  a path a later release no longer ships, and today the only remedy is a reinstall nobody is told to run

---

## Behaviors

Scenarios are grouped by Rule — the business rule the scenarios prove. Use concrete values and
business language. See the `bdd-principles` skill for guidance.

### Rule: A complete install reports as wired, in any supported layout

```scenario
Scenario: A canonical-layout install passes
  Given a project where the toolkit was installed with the default command
  And the skills live in .agents/skills with symlinks from .claude/skills
  When the consumer runs the install check
  Then every expected skill is reported present
  And the check exits zero
```

```scenario
Scenario: A copied-layout install passes
  Given a project where the skills were copied directly into .claude/skills
  When the consumer runs the install check
  Then every expected skill is reported present
  And the check exits zero
```

```scenario
Scenario: A self-hosted source-symlinked install passes
  Given a project whose .claude/skills entries symlink directly to toolkit source
  When the consumer runs the install check
  Then every expected skill is reported present
  And the check exits zero
```

### Rule: A partial install names what is missing

```scenario
Scenario: A deliberate selective install passes but names what is absent
  Given a project where only some of the toolkit's skills were installed
  When the consumer runs the install check
  Then it reports how many of the toolkit's skills are installed
  And it names the count not installed as a legitimate selective install
  And the check exits zero
```

```scenario
Scenario: One missing skill is named
  Given a complete install with the plan skill removed
  When the consumer runs the install check
  Then the report names plan as missing
  And the check exits non-zero
```

```scenario
Scenario: The suggested fix names the pack that ships the missing unit
  Given a project whose records list the schema drift check but the unit never arrived
  When the consumer runs the install check
  Then the report names it missing
  And the suggested command names the Umbraco Cloud pack as its source
  And the command contains no placeholder the consumer would have to fill in
  And the check exits non-zero
```

### Rule: Assets are verified by reading, not by listing

```scenario
Scenario: A missing template is caught
  Given an install where the workflow skill's spec template has been deleted
  When the consumer runs the install check
  Then the report says the spec template is unreadable
  And the workflow skill is not reported as simply present
```

### Rule: Degraded is distinguished from broken

```scenario
Scenario: Unregistered reviewers are degraded, not broken
  Given a complete install where no reviewer agents are linked into .claude/agents
  When the consumer runs the install check
  Then review is reported as working but degraded to inline passes
  And the report names the command that registers them
  And the check exits zero
```

### Rule: Empty configuration is a working configuration

```scenario
Scenario: A fresh install with no slots filled reports as working
  Given a project with no .agents/config directory
  When the consumer runs the install check
  Then every slot is listed as empty
  And the report states that the toolkit works with all slots empty
  And the check exits zero
```

### Rule: The check reports only on the toolkit

```scenario
Scenario: No stack pack is not a finding
  Given a core-only install
  When the consumer runs the install check
  Then no finding mentions a missing pack
```

```scenario
Scenario: Unrelated skills are ignored
  Given a project with three of its own skills and one of its own agents installed
  When the consumer runs the install check
  Then the report covers only the toolkit's own skills and agents
```

### Rule: Each pack verifies on its own, without its siblings

```scenario
Scenario: A Deploy project verifies with no CMS pack installed
  Given a project with only the Umbraco Cloud pack installed
  When the consumer runs the install check
  Then both of that pack's units are reported present
  And no finding mentions the CMS pack
  And the check exits zero
```

```scenario
Scenario: A setting is surveyed because the pack that reads it is installed
  Given a project with only the Umbraco Cloud pack installed
  And the consumer has filled the block palette parity setting that pack reads
  When the consumer runs the install check
  Then the setting is reported filled
  And the report does not claim every setting is empty
```

### Rule: A setting read by two packs is counted once

```scenario
Scenario: Two packs reading one setting do not double-count it
  Given a project with the Umbraco Cloud pack and the CMS planning unit installed
  And both of them read the same Umbraco paths setting
  And the consumer has filled that setting
  When the consumer runs the install check
  Then the setting is counted as one filled setting
  And it is not counted twice
```

---

## Edge Cases

### Rule: A broken link looks fine to a listing and fails on every read

```scenario
Scenario: A dangling symlink is broken, not present
  Given a canonical-layout install whose .agents directory has been deleted
  When the consumer runs the install check
  Then each affected skill is reported broken
  And the check exits non-zero
```

```scenario
Scenario: Reviewer agents linked to the wrong place are broken, not configured
  Given reviewer agent files present in .claude/agents that cannot be read
  When the consumer runs the install check
  Then they are reported broken rather than registered
```

### Rule: A hand-vendored install is still assessable

```scenario
Scenario: No lockfile does not stop the check
  Given a project whose toolkit files were copied in by hand with no lockfile
  When the consumer runs the install check
  Then it assesses what is present rather than refusing to run
```

---

## Test Coverage

| Scenario | Test File | Status |
|----------|-----------|--------|
| A canonical-layout install passes | `tests/install-check/canonical-complete` | Covered |
| A copied-layout install passes | `tests/install-check/copied-complete` | Covered |
| A self-hosted source-symlinked install passes | `tests/install-check/source-symlinked-complete` | Covered |
| A deliberate selective install passes but names what is absent | `tests/install-check/selective-install` | Covered |
| One missing skill is named | `tests/install-check/missing-skill` | Covered |
| The suggested fix names the pack that ships the missing unit | `tests/install-check/cloud-unit-missing` | Covered |
| A missing template is caught | `tests/install-check/missing-template` | Covered |
| Unregistered reviewers are degraded, not broken | `tests/install-check/agents-unlinked` | Covered |
| A fresh install with no slots filled reports as working | `tests/install-check/no-config` | Covered |
| No stack pack is not a finding | `tests/install-check/foreign-units` | Covered |
| Unrelated skills are ignored | `tests/install-check/foreign-units` | Covered |
| A Deploy project verifies with no CMS pack installed | `tests/install-check/cloud-only` | Covered |
| A setting is surveyed because the pack that reads it is installed | `tests/install-check/cloud-only` | Covered |
| Two packs reading one setting do not double-count it | `tests/install-check/shared-slot-two-packs` | Covered |
| A dangling symlink is broken, not present | `tests/install-check/dangling-symlink` | Covered |
| Reviewer agents linked to the wrong place are broken | — | Not covered |
| No lockfile does not stop the check | `tests/install-check/no-lockfile` | Covered |

---

## Revision Notes

- 2026-08-03: Draft scenarios from initial spec
- 2026-08-03: Verified against the implementation. Draft banner removed. Coverage filled from
  `tests/install-check/`. Added the copied-layout scenario — implementation supports three layouts,
  where the draft named two. One edge case (reviewer agents linked but unreadable) is implemented and
  handled but has no fixture; left as Not covered rather than claiming coverage it lacks.
- 2026-08-03: `/code-review` found that a selective install reported nothing about absent skills,
  leaving FR1 only half met. Fixed, and the resulting behavior added here as a scenario with its own
  fixture — the finding is now covered rather than only mentioned.
- 2026-08-17: Folded in what changed when one pack became three. Four scenarios added under two new
  Rules plus one under an existing Rule; all four are covered by new fixtures. Two of them exist
  because `/code-review` found real defects rather than because they were specified: a setting read by
  units in two packs was surveyed for only one of them, so a Cloud-only project was never asked to
  fill a setting its own pack reads; and registering the second reader then counted the setting twice,
  turning a coverage gap into a wrong total. The move mechanics and the pack-boundary decisions stay in
  the shipped spec and [ADR 0015](../adr/0015-what-a-stack-pack-is-and-what-it-owes.md) — they are
  point-in-time, not standing behavior. Also parked the gap this increment created for consumers: the
  check cannot tell a unit that moved from one that was deleted.
