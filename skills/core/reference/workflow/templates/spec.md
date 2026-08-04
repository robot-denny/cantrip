# Spec for <slug>

> This spec captures initial requirements and design rationale. For **current system
> behavior**, see the doc named on the **Work type** line below — a new feature doc for a new
> capability, an existing feature doc for a change, or a `docs/` runbook for a fix.

branch: <branch-name>
design reference (if any): <link or component name>

**Work type**: <new-capability | change-to <existing-slug> | fix-infra>
**Feature doc**: <the capability doc this belongs to, named by AREA — or `none` for fix-infra>
<!--
  Feature doc is named by area, not by this increment. An increment called
  `placeholder-graphics-imageless-cards` may belong to a doc called `article-card`. See the
  `workflow` skill → "The naming tell". /plan and /feature target this name, not the slug.

  Decides which durable artifact this work earns. See the `workflow` skill → "Work types".
  - new-capability     → a new feature doc is created, named by capability, not by work
  - change-to <slug>   → no new file; observable behavior folds into that capability's doc
  - fix-infra          → no feature doc; durable record is a runbook under docs/
  The tell: transition-style acceptance criteria ("goes from… to…", "leaves no trace")
  are NOT new-capability.
-->

## Summary

...

## Functional Requirements

- ...

## Design Reference (only if one exists)

- Source: ...
- Component name: ...
- Key visual constraints: ...

## Possible Edge Cases

- ...

## Acceptance Criteria

- ...

## Scenarios (Draft)

Draft BDD scenarios derived from the acceptance criteria using Example Mapping. Each Rule maps
to an acceptance criterion; scenarios use concrete examples. These get verified and refined
after implementation — the feature doc holds the verified version.

### Rule: {acceptance criterion as a business rule}

```scenario
Scenario: {name with concrete example}
  Given {specific precondition}
  When {user action}
  Then {observable outcome}
```

## Open Questions

- ...

## Testing Guidelines

Meaningful tests for the cases below, without going too heavy:

- ...
