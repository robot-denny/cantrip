# Phase 1 rationale — the seam proof

**Date:** 2026-08-03
**Increment:** 1.1 — extract `/spec`
**Gate:** `scripts/check-contract.sh` — 7/7 passing
**Result: the contract holds.** Two refinements needed, neither structural.

## Why `/spec` was the right exemplar

It exercises every contract mechanism in one file — spine reference, work-type classification,
template read, BDD reference, and a genuine project fact — without `/plan`'s stack-routing
complexity. If the contract were going to fail, it would fail here.

Re-measured before extracting, per the standing rule that the source repos are live: 116 / 107
/ 35 diff lines, unchanged since the plan. Client project as base, demo project read as diff
hunks only.

## Outcome

116 source lines → 166 extracted (+43%), which lands where ADR 0001 predicted: slot references
cost three lines where an inline fact cost one.

Every load-bearing element survives — all seven slug rules, Example Mapping's five bullets, the
three literal work-type values, *the tell*, the Step 6 skip guard, both Step 7 output shapes,
and the `Next:` chain. Zero project facts remain.

Folded in from the demo project's version:

- "grep the feature docs by capability area" — a concrete method where the base only said
  "name the existing slug"
- "compiles on the stable stack" as a fourth *tell* example
- "the draft scenarios still live in the spec — nothing is lost", which preempts the natural
  worry when Step 6 is skipped
- "recording this line is what lets `/plan` and `/feature` honor the classification without
  re-deciding it" — the base stated the rule without the reason

Kept from the base: its two explicit Step 7 output blocks. The demo project had compressed them
into one block with an inline `←` annotation, which is more compact but ambiguous to follow.

## Refinement 1: one slot, one point of authority

**The finding that matters.** The first draft re-declared the workspace-paths slot inside
`/spec`. That is wrong, and it would have been wrong eight more times.

The `workflow` skill already owns the workspace layout — it carries the `paths.md` slot
reference and the default layout as its fallback. So `/spec` defers: "artifact locations follow
the layout in the `workflow` skill." The result is that this spell carries exactly **one** slot
reference, for branch naming, which is a fact no other toolkit file owns.

The failure mode avoided is drift. Eight spells each carrying a copy of the same slot reference
is eight places to update and eight chances for the fallbacks to disagree — which is precisely
how the two source repos ended up with the same command in two different states. Duplicating
the slot mechanism would have rebuilt the disease the toolkit exists to cure.

Now in `docs/contract.md` as a normative rule, with the corollary that **toolkit-internal paths
are not slots** — a spell reading `.agents/skills/workflow/templates/spec.md` is naming
something the toolkit controls, not a project fact.

## Refinement 2: canonical paths instead of `@`-references

The source used `@_specs/_template.md`, Claude Code's auto-loading file reference. That cannot
survive extraction: the path is project-relative, and the `@` form is Claude-specific.

Replaced with the canonical install path, `.agents/skills/workflow/templates/spec.md`, read
explicitly. Slightly weaker than an auto-load — the agent must choose to read it — but portable,
and it survives being vendored into layouts the toolkit does not control.

## Judgment calls worth revisiting

- **Step 1 aborts on a dirty working tree.** Opinionated, and inherited from both sources. Kept
  because a spec that starts by switching branches over uncommitted work is worse. Flagged in
  case any consuming project finds it too strict.
- **Step 3 creates a branch.** Not every project works branch-per-increment, so this degrades:
  if conventions indicate work happens on the current branch, the step is skipped and the
  summary says so.
- **The `-01` collision suffix** is a mild opinion carried from the source. Harmless default.

## Carried forward

- Only one slot needed for the whole spell. If that ratio holds across the spellbook, the
  four-file slot schema from ADR 0001 is likely oversized rather than undersized — worth
  re-checking at the Checkpoint C census rather than adding slots speculatively.
- Still structural-only validation. Whether `/spec` *behaves* well cannot be known until it is
  cast in a live session (Phase 3 install, Phase 4 self-hosting).
