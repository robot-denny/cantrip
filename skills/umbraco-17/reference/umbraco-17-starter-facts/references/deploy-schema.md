---
name: deploy-schema
description: Umbraco Deploy .uda artifact mechanics, the ways local and environment schema drift apart, and which Cloud dashboard controls actually import
metadata:
  type: reference
---

# Deploy and schema facts

## Umbraco rewrites `.uda` files on local startup

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

## The bulk "update schema from data files" button does not import on Cloud

There are two similarly named controls in the Deploy dashboard and only one imports.

- The **bulk button** at the top of the dashboard refreshes the comparison view only. It reports
  "operation completed" without moving anything.
- The **per-row "Update item"** action does import file → database. It appears only for the *mismatch*
  state, and only when "hide up to date" is toggled on — otherwise the row is filtered out of view and
  the affordance is hidden.

**Why:** The bulk button's success message is the trap. It reads as though the import ran, so the next
step is to investigate why the import "did not take" rather than to run the actual import.

**How to apply:** Use the per-row action for mismatch rows, and the API for pending rows. Never
conclude anything from the bulk button's message.
**Type:** pattern
**Applies:** umbraco >=17 <18 on Umbraco Cloud
**Verified:** 17.4 (2026-05)

---

## Importing one pending artifact often clears the whole pending set

A single `POST /schema/item?udi=...` typically drops drift to zero even when many entries were
pending, because the one call unblocks Deploy's evaluation of the full set.

**How to apply:** Import the simplest dependency-free artifact first and re-check, before scripting a
loop over every pending entry.
**Type:** pattern
**Applies:** umbraco >=17 <18 on Umbraco Cloud
**Verified:** 17.4 (2026-05)

---

## A portal restart usually does not re-trigger schema import

The bootstrapper compares marker files under the Deploy directory, not `.uda` modification times.

**Why:** So a restart — the obvious first remedy — changes nothing, and the log line explaining why is
easy to miss: `Skipping Umbraco content and/or schema import at startup, because no files are provided
or none of the files exist.`

**How to apply:** Do not start remediation with a restart. If someone already did, check the startup
log for that line before concluding the restart failed for another reason.
**Type:** pattern
**Applies:** umbraco >=17 <18 on Umbraco Cloud
**Verified:** 17.4 (2026-05)

---

## An empty commit does not force a re-extraction either

When an empty commit follows one that already deployed, the pipeline logs `No changes in metadata
detected - no need to run an Umbraco Deploy extraction` and skips extraction.

**How to apply:** Also not a remedy. Its one use is diagnostic — the build log's schema-import step
names the artifact that actually will not deploy.
**Type:** pattern
**Applies:** umbraco >=17 <18 on Umbraco Cloud
**Verified:** 17.4 (2026-05)

---

## Cloud can auto-commit re-serialized `.uda` files back to the repository

When an artifact is imported into a Cloud database, Cloud may re-serialize it with normalized internal
identifiers and commit that itself.

**Why:** Your branch can be behind without you having done anything, so the next push conflicts for
reasons unrelated to your work.

**How to apply:** Fetch or pull before pushing after any Cloud-side import. Flag a workflow that
pushes schema without a preceding fetch.
**Type:** pattern
**Applies:** umbraco >=17 <18 on Umbraco Cloud
**Verified:** 17.4 (2026-07)

---

## Built-in entities that were never extracted create permanent drift noise

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

## Never author schema directly on a deployed environment

Schema authored in a deployed environment's backoffice becomes an environment-only entity with no
artifact in the repository.

**How to apply:** Author locally and let it flow through the repository. If orphans already exist,
either extract them to `.uda` and pull, or delete them so the file-backed version wins. Flag any
workflow that edits schema on a non-local environment.
**Type:** pattern
**Applies:** umbraco >=17 <18
**Verified:** 17.4 (2026-07)

---

## `.uda` compositions carry properties that the type's own groups do not list

A document type's `PropertyGroups` is not the whole picture — `CompositionContentTypes` references
must be resolved recursively.

**How to apply:** Resolve compositions when reading a type's real property set. Reading only the
type's own groups under-describes it, and anything derived from that reading — a generated doc, a
payload, a test's expected aliases — is quietly incomplete.
**Type:** pattern
**Applies:** umbraco >=17 <18
**Verified:** 17.4 (2026-07)

---

## Reading `.uda` group structure: `"Type": 1` marks a tab

Groups with `"Type": 1` are tabs. Groups without a `Type` use `tabAlias`/`groupAlias` as their
`Alias`.

**How to apply:** Needed when parsing artifacts directly rather than through the API.
**Type:** pattern
**Applies:** umbraco >=17 <18
**Verified:** 17.4 (2026-07)
