# 0012. Pack companions are recommended, never required

**Status:** Accepted
**Date:** 2026-08-04

## Context

The `umbraco-17` pack routes backoffice extension work to an external plugin marketplace it does not
own — nine extension types in a routing table, each pointing at a skill from
`umbraco-cms-backoffice-skills`. That routing has been there since Phase 5 and works well; the canary
project exercised it live.

Three problems surfaced together:

1. **The dependency was never declared.** The README — the only file a consumer reads before installing —
   contained no mention of a marketplace or a plugin. Someone could install the pack, cast `/plan` on a
   dashboard, and get guidance quietly thinner than the pack was designed to give, with nothing to
   indicate why.
2. **A second marketplace was used in practice and cited nowhere.**
   `umbraco-cms-backoffice-testing-skills` was enabled in both the authoring environment and the canary
   project, and appeared in **zero** cantrip files. Given that `/plan` is TDD-first, the skill set
   covering extension test setup was the more consequential omission of the two.
3. **The absence path had never been observed.** Every environment that exercised the pack had the
   marketplace enabled, so the graceful degradation was designed and never run.

The pack did one thing right, which is what made this a gap rather than a bug: the routing table already
carried an absence clause telling the planner to note it in Key Decisions and plan from the codebase's
existing patterns. So absence was not silent *at cast time*. It was silent **at install time**, which is
the layer where the decision below applies.

This is [ADR 0006](0006-no-unguarded-preconditions.md)'s rule — no instruction may assume its
precondition exists — one layer out from where that ADR applies it. 0006 governs preconditions inside a
skill; this governs a precondition of the whole pack.

## Decision

**A stack pack may recommend external companions. It may never require them.**

Concretely:

- **The pack declares its companions machine-readably.** A `**Companion:** \`name\` — what it covers`
  line, in the same self-describing style as `**Slot:**` / `**If empty:**`. A pack declares its own;
  **core never names them**, which is what preserves L0's technology-agnosticism (ADR 0003).
- **`/setup` reads those declarations and reports enablement** — including *where from*, because an
  entry in a user's own settings works identically for that user while being absent for every teammate.
  Setup reports and recommends; it never enables a third-party plugin itself.
- **The README names every declared companion** as recommended, not required. Enforced by contract
  check 12, because the two halves of this — the declaration and the documentation — are edited in
  different files and nothing else keeps them in sync.
- **The absence clause says what is missing and how to fix it**, not merely that something was
  unavailable. A note that names the remedy is actionable; one that records an absence is a shrug.

### The ownership line this implies

Settling positioning also settles what we absorb versus point at:

**Cantrip's pack owns what makes work in a technology correct and durable. A companion owns what makes it
idiomatic to a specific library version.**

Platform behavior outlives package upgrades and belongs in the pack's starter facts. A library's API
surface, its mocking utilities, its fixture builders do not, and copying them here would go stale
invisibly — the worst failure mode for a fact file whose whole value is being trustworthy.

## Alternatives considered

**Make the marketplace a documented prerequisite.** Rejected on three grounds. It inverts ADR 0003's
principle one layer out: if the pack can be absent without breaking core, a marketplace can be absent
without breaking the pack. It taxes the majority for a minority path — the routing table fires only for
extension work, and a project doing content modelling and templates never touches it. And it makes our
install story depend on third-party distribution we do not control, which ADR 0004 already showed shifts
fast: two of its four recorded findings were wrong within four days.

**Absorb the companions' content into the pack.** Rejected by the ownership line above. It removes the
dependency by taking on a maintenance burden we cannot meet, and produces confidently stale guidance —
strictly worse than routing to something current.

**Leave it as-is, since the absence clause already handles it.** Rejected because the clause fires at
cast time, and the person who can act on it — whoever installs and configures the project — is not
present then. A finding surfaced only in a plan's Key Decisions reaches the reader after the plan was
already built the thinner way.

## Consequences

- **Any future pack inherits this.** An `optimizely` or `sitecore` pack declares companions the same way,
  documents them in the README, and check 12 enforces it without new code.
- **A new contract mechanism exists** — `**Companion:**` — and it is the second thing `/setup` discovers
  from a pack rather than being told. That is now a pattern rather than a one-off.
- **Core gains no technology knowledge**, which was the constraint that shaped the mechanism. Setup
  reports on companions it cannot name.
- **Enablement location becomes a reportable state.** Project-committed versus user-only is a real
  distinction with a silent failure attached, and `/setup` is the only place it surfaces.
- **The absence path is still unobserved.** Nothing here changes that: it remains untested until the pack
  is cast in a project without the marketplace enabled. Recorded as an open item rather than closed.

## Provenance

The positioning question was raised by the user after auditing the pack for undeclared dependencies; the
three findings above are theirs.

The sibling `tdd-principles` skill, added in the same change, is an adaptation of an externally published
skill — recorded in [ADR 0013](0013-attribution-for-adapted-external-work.md) along with what was
deliberately not carried over. Worth noting the shape: reaching for a named external reference is **rung 2
of [ADR 0006](0006-no-unguarded-preconditions.md)'s ladder**, and the ladder was written to govern how a
spell reasons about a project. It turns out to describe how the toolkit should be built as well.
