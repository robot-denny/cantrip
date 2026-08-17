---
name: umbraco-17-audit-patterns
description: Assessment criteria for judging whether an existing Umbraco codebase follows the platform's own conventions — composition and service registration, schema-as-code discipline, content access and block patterns, and how ready the site is to serve a decoupled frontend. Consult when auditing or inheriting an Umbraco codebase, comparing two Umbraco solutions, or deciding whether a site's structure is idiomatic rather than merely working. This is judgement criteria, not a defect list — for reviewing a specific diff, use the Umbraco review rules instead.
---

# Umbraco 17 audit patterns

Criteria for assessing an existing Umbraco codebase at the structural level: what an idiomatic
solution looks like, what the warning signs are, and how the judgement shifts with the codebase's
lifecycle stage.

A repo-level architecture audit, where one is installed, is the natural consumer — it covers the
.NET foundation and the structure around it, and leaves framework-idiomatic use to guidance like
this. Nothing here depends on that audit being present; the criteria stand on their own.

**This unit judges a codebase. It does not review a diff.** Line-level defects in changed code are
the review rules' subject, and a finding belongs to one or the other, never both.

## The reference files

| Reference | What it covers |
|---|---|
| `references/version-agnostic-patterns.md` | Patterns that hold across Umbraco majors — composition, service registration, content access, and schema discipline, with the version-sensitive parts called out rather than assumed |
| `references/headless-suitability.md` | Whether a site is positioned to serve a decoupled frontend: its current orientation, and a readiness assessment |

## Version scope

The patterns hold across majors, which is why this unit describes them rather than pinning them to
one release. Anything genuinely version-sensitive — which packages exist in a given major, what a
later major deprecates — is named as version-sensitive where it appears, and should be confirmed
against the major the project actually runs. Establish that version first; the reference files say
how.
