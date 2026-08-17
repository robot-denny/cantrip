---
name: artifact-mechanics
description: How Umbraco Deploy writes and reads `.uda` artifacts, and why local files and an environment's database drift apart
metadata:
  type: reference
---

# Umbraco Deploy artifact mechanics and drift

Facts about how artifacts are serialized and read, and about the four ways local files and an
environment's database come apart. For fixing drift that will not clear, read `deploy-remediation.md`
instead.

## Artifact mechanics

### Umbraco rewrites `.uda` files on local startup

Every local run can re-serialize `.uda` artifacts from the local database's signatures.

**Why:** Uncommitted `.uda` churn after a `run` is therefore usually *not* an intended schema change —
but it looks identical to one in a diff, so it gets staged and committed by reflex, and the repository
drifts from the shared environment without anyone making a decision.

**How to apply:** Treat unstaged `.uda` changes as suspect until confirmed intentional. Only commit
them when a type was deliberately changed in the backoffice, or when bulk-extracting built-in
defaults. Discarding is the default action, not the exception.
**Type:** pattern
**Applies:** umbraco >=17 <18
**Verified:** 17.4 (2026-07)

---

### `.uda` compositions carry properties that the type's own groups do not list

A document type's `PropertyGroups` is not the whole picture — `CompositionContentTypes` references
must be resolved recursively.

**How to apply:** Resolve compositions when reading a type's real property set. Reading only the
type's own groups under-describes it, and anything derived from that reading — a generated doc, a
payload, a test's expected aliases — is quietly incomplete.
**Type:** pattern
**Applies:** umbraco >=17 <18
**Verified:** 17.4 (2026-07)

---

### Reading `.uda` group structure: `"Type": 1` marks a tab

Groups with `"Type": 1` are tabs. Groups without a `Type` use `tabAlias`/`groupAlias` as their
`Alias`.

**How to apply:** Needed when parsing artifacts directly rather than through the API.
**Type:** pattern
**Applies:** umbraco >=17 <18
**Verified:** 17.4 (2026-07)

## Why local files and an environment's database drift apart

### Built-in entities that were never extracted create permanent drift noise

On initial provisioning, typically only user-authored entities get extracted to `.uda`. Built-in
defaults — stock data types, media types, the default language, member type, relation types — stay
database-only on every environment.

**Why:** The dashboard reports them as not-up-to-date forever, and that standing noise masks real
drift. Anyone learning to ignore the dashboard also learns to ignore genuine findings.

**How to apply:** Extract built-in defaults once and commit them, so the dashboard's signal means
something. Expect the same pattern from any package that adds built-in entities.
**Type:** pattern
**Applies:** umbraco >=17 <18
**Verified:** 17.4 (2026-04)

---

### Never author schema directly on a deployed environment

Schema authored in a deployed environment's backoffice becomes an environment-only entity with no
artifact in the repository.

**How to apply:** Author locally and let it flow through the repository. If orphans already exist,
either extract them to `.uda` and pull, or delete them so the file-backed version wins. Flag any
workflow that edits schema on a non-local environment.
**Type:** pattern
**Applies:** umbraco >=17 <18
**Verified:** 17.4 (2026-07)

---

### Cloud can auto-commit re-serialized `.uda` files back to the repository

When an artifact is imported into a Cloud database, Cloud may re-serialize it with normalized internal
identifiers and commit that itself.

**Why:** Your branch can be behind without you having done anything, so the next push conflicts for
reasons unrelated to your work.

**How to apply:** Fetch or pull before pushing after any Cloud-side import. Flag a workflow that
pushes schema without a preceding fetch.
**Type:** pattern
**Applies:** umbraco >=17 <18 on Umbraco Cloud
**Verified:** 17.4 (2026-07)
