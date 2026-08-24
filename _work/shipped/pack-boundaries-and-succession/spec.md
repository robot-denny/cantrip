# Spec for pack-boundaries-and-succession

> This spec captures initial requirements and design rationale. For **current system
> behavior**, see the doc named on the **Work type** line below.

branch: pack-boundaries
design reference (if any): none

**Work type**: change-to install-verification
**Feature doc**: `_features/install-verification.md`

<!--
  Classified change-to rather than new-capability: no unit gains behavior. `check-uda` does what it
  already did; the audit performs the same assessment. What changes is which packs exist, what each
  contains, and therefore what a consumer installs and what the checker verifies — the install
  surface, which is install-verification's area.

  A SECOND feature doc also needs a touch: `_features/dotnet-guidance.md`, because the audit joins
  the `dotnet` pack. /plan's final step must cast `/feature update` twice. Recorded here so it is not
  discovered late.
-->

## Summary

Three packs' worth of content currently sits in one, organized by how it was authored rather than by
what it is about. This increment moves each unit to the pack its subject implies, establishes the
naming rule that lets a future pack replace a current one, and writes down the boundary test that
was previously applied by taste.

Discovery is at `_work/shipped/pack-boundaries-and-succession/discovery.md` and its framing is not repeated
here. Two of its findings govern this spec:

- **The pain is forward-looking, not observed.** Both real projects are Umbraco 17 *and* Cloud, so
  nothing is broken today. This work is justified by what it prevents, which sets the bar for scope:
  reorganize and document, do not rewrite guidance.
- **Version-boundness resists measurement.** Two proxies were tried and both misreported.
  `umbraco-edit` names no version while depending on an API that only exists from v14. **Units are
  classified by subject, by hand.**

## Functional Requirements

### The Cloud pack

- A new `umbraco-cloud` pack holds Umbraco Deploy and Cloud knowledge: `check-uda`, its
  `cloud-remediation.md` reference, and `deploy-schema.md` (currently inside
  `umbraco-17-starter-facts/references/`).
- The pack is **versionless**, annotating per feature where behavior differs by release — ADR 0015
  §3's "majors add" branch, as `dotnet` already takes.
- Its description covers Umbraco Deploy generally, not Cloud exclusively. Deploy is licensed
  standalone for on-premise, so `.uda` files can exist without Cloud; the trigger must not exclude
  those projects.

### The CMS pack

- `umbraco-17` **keeps its current name.** No rename. The rule is stated so that the existing name
  already complies: *a version-pinned pack carries its major in the pack name.* A future
  `umbraco-18` is then consistent without anything moving today.
- What remains is version-bound CMS content: `umbraco-17-planning`, `umbraco-17-review-rules`,
  `umbraco-17-starter-facts`, `umbraco-17-feature-backfill`, `block`, `umbraco-edit`.
- `umbraco-edit` gains a version-floor annotation. Its subject is version-bound in a way its prose
  never states.
- `block`'s cross-reference to `/check-uda` becomes cross-pack and gains the "where installed" hedge
  ADR 0015 requires.

### The audit

- `architecture-audit` leaves the Umbraco pack for `skills/dotnet/reference/codebase-audit/`.
- Umbraco-specific content returns to `umbraco-17`: `umbraco-version-agnostic.md`, and the
  Umbraco-specific portions of `headless-suitability.md`.
- **The agnostic half is seam-cut.** `lifecycle-stages.md`, `documentation-and-onboarding.md`,
  `resilience-and-ops.md`, and `scoring-rubric.md` are held to L0's no-technology-names rule from day
  one, so a later promotion to core is a move plus a roster edit rather than a rewrite. They are not
  promoted now — L0 may name no technology, and doing so would cost the concrete signals the audit
  depends on.

### Naming and succession

- **References carry the version in their name; spells do not.** References are model-invoked, so
  their names are internal plumbing and version-prefixing makes a project's pinned major visible.
  Spells are typed by humans, so `/block` must survive an upgrade unchanged.
- **One CMS major is installed at a time.** A migration means a new codebase on the new version
  referencing the old one, each with its own packs — not one codebase holding both.
- ADR 0015 gains the **variant axis** (host and product, not only version) and the **replacement
  operation**, both currently absent. Whether that is an amendment or a new ADR is left to `/plan`.

### Registration

- `ROSTER_PACK` and `PACK_SLOTS` in `scripts/check-install.sh` reflect the new layout; contract check
  13 gates the roster as it already does.
- `reinstall_hint()` returns a working command for units in the new pack.

## Possible Edge Cases

- A project installs `umbraco-cloud` without any CMS pack — a Deploy-only or on-premise case. The
  Cloud pack must stand alone.
- A project installs `umbraco-17` without `umbraco-cloud`. `block`'s hedged reference must degrade
  without losing guidance.
- A non-Umbraco .NET project installs `codebase-audit` and runs it. Nothing may assume a CMS.
- An existing install still pins `skills/umbraco-17/reference/architecture-audit/SKILL.md` in its
  lockfile — a path that no longer exists after the move.
- The audit runs against a repository whose stack it cannot identify.

## Acceptance Criteria

1. Every unit resolves from a pack whose subject matches the unit's subject.
2. No guidance is lost in any move — content that changes packs is relocated, not dropped, and
   content that is split is accounted for on both sides.
3. `umbraco-cloud` installs and functions with no CMS pack present.
4. `umbraco-17` installs and functions with no Cloud pack present, and `block`'s deferral degrades
   without silently losing guidance.
5. `codebase-audit` produces an assessment on a .NET repository with no Umbraco present.
6. The four seam-cut audit references contain no technology names.
7. The installer verifies the new layout: rosters match disk, slots resolve, reinstall hints work.
8. The contract gate passes, including the roster-drift check.
9. The naming rule and the one-major constraint are written where a future pack author will read
   them.

## Scenarios (Draft)

### Rule: Every unit resolves from a pack whose subject matches its subject

```scenario
Scenario: Deploy schema guidance is found in the Cloud pack
  Given a project that uses Umbraco Deploy
  When someone looks for guidance on .uda schema drift
  Then it is found in the Umbraco Cloud pack
  And it is not found in the Umbraco 17 pack
```

```scenario
Scenario: The codebase audit is found outside the CMS packs
  Given a .NET project with no content management system
  When someone looks for a structural assessment of the codebase
  Then it is found in the .NET guidance
  And installing it does not bring any Umbraco content with it
```

### Rule: A pack works without its siblings

```scenario
Scenario: A Deploy-only project installs the Cloud pack alone
  Given a project on Umbraco Deploy with no CMS pack installed
  When the schema check runs
  Then it reports on schema drift as normal
  And it does not report a missing dependency
```

```scenario
Scenario: A CMS-only project reaches a deferral it cannot follow
  Given a project with the Umbraco 17 pack and no Cloud pack
  When the block guidance reaches the point where it would defer to the schema check
  Then it says the schema check is available where installed
  And it states what the reader would otherwise have to check by hand
```

### Rule: The audit assesses a codebase without assuming a stack

```scenario
Scenario: An audit runs on a .NET project with no CMS
  Given a .NET solution with no Umbraco packages referenced
  When the codebase audit runs
  Then it produces an assessment with strengths and prioritized recommendations
  And no finding refers to a content management system
```

```scenario
Scenario: Two codebases organized differently are compared
  Given one codebase organized by feature and another organized by component kind
  When the two are compared
  Then the report describes the trade-off each organization makes
  And it does not declare one universally correct
```

### Rule: A move loses no guidance

```scenario
Scenario: Schema guidance split across two packs stays whole
  Given schema guidance that previously sat in a single pack
  When it is divided between the Cloud pack and the CMS pack
  Then every rule present before the split is present after it
  And no rule is present in both
```

### Rule: The installer verifies the new layout

```scenario
Scenario: A newly added Cloud unit is registered
  Given the Cloud pack ships a unit
  When the contract gate runs
  Then it passes only if that unit is listed in the pack roster
```

```scenario
Scenario: A consumer reinstalls a unit from the Cloud pack
  Given a project missing one Cloud pack unit
  When the install check reports the gap
  Then the suggested command names the Cloud pack
  And running it restores the unit
```

### Rule: A future pack can replace a current one

```scenario
Scenario: An upgrade swaps the CMS pack and keeps the Cloud pack
  Given a project on the Umbraco 17 pack together with the Cloud pack
  When the project moves to the next Umbraco major
  Then the CMS pack is replaced by the one for that major
  And the Cloud pack is unaffected
  And the block spell is still invoked by the same name
```

## Open Questions

Carried from discovery, minus the rename, which is resolved: **no rename.**

1. **Do `deploy-schema.md` and `cloud-remediation.md` merge?** Both cover Deploy artifact mechanics
   and Cloud dashboard behavior, and they will sit in one pack. Overlap is likely; whether they
   become one reference or stay two is a `/plan` decision. --I prefer fewer files when it will not degrade performance, so suggest merging them
2. **Amendment or new ADR?** The variant axis is a natural amendment to ADR 0015 §3. The replacement
   operation is arguably its own decision. Either is defensible.
3. **How much of `headless-suitability.md` is genuinely Umbraco?** Seven mentions, but "headless
   suitability" is a CMS-general concept. Needs reading, not counting — per the measurement caveat. --I am not very concerned about the headless suitability. We could even sacrifice this part of the eval and rubric altogether if it simplifies this spec.
4. **Does the existing demo-site install break?** Its lockfile pins
   `skills/umbraco-17/reference/architecture-audit/SKILL.md`, which will not exist. Whether this
   increment owes a migration note or the installer-hygiene increment absorbs it is open.
5. **Does the seam-cut rule get gated?** Contract check 8 enforces no-technology-names for L0 only.
   Applying it to four files that are not in L0 would need a new check or an explicit exemption list.
