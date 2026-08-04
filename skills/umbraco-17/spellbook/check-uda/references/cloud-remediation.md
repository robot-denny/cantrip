# Importing pending schema on Umbraco Cloud

Read this when `/check-uda` reports `mismatch` (signatures diverged) or `pending` (file exists, DB
missing) entries on a Cloud environment — typically after content transfers start failing as a result.

Three remediation paths, in order of preference. **Do not start with portal restarts or empty-commit
nudges** — see *What not to spend time on*, since both are commonly tried and usually do nothing.

## The distinction that costs people the most time

There are two different "Update" controls in the Deploy dashboard, and **only one of them imports.**

| Control | What it does |
|---|---|
| Bulk **"Update Umbraco Schema from data files"** button, top of dashboard | Does **not** import on Cloud. Refreshes the comparison view only, then reports "operation completed" without moving anything. |
| Per-row **"Update item"** action, in the right-click menu | **Does** import file → DB. But it appears only for the **mismatch** state, and only when "hide up to date" is toggled on — otherwise the row is filtered out of view and the affordance is hidden. That filtering is the trap. |

## Path 1 — Per-row "Update item" (try first, for mismatch)

Verified 2026-05-11; resolved in about 30 seconds.

1. Open the environment's backoffice → **Settings → Deploy**.
2. Toggle **"hide up to date"** on, so only non-matching rows remain visible.
3. Right-click the row and choose the action offered for its state. Which actions appear depends on
   which of the three checkmarks — file exists / exists in Umbraco / up to date — are missing:
   - **Mismatch** (file ✓, Umbraco ✓, up-to-date ✗) → **Update item**, imports file → DB. This is the
     fix.
   - **Pending** (file ✓, Umbraco ✗) → the dashboard may offer only **Create** (DB → file) or
     **Delete**, with no UI-driven import. If "Update item" isn't there, go to Path 2.
   - **Orphan** (file ✗, Umbraco ✓) → **Create**, exports DB → file.
4. Retry the content transfer.

## Path 2 — API call (for pending state, or many rows)

Use when the dashboard path is blocked — a pending row with no "Update item" action, or dozens of
entries where right-clicking each is impractical.

1. Get a token via the OAuth client-credentials flow (the `UMBRACO_LIVE_*` credentials).
2. Pick the simplest pending UDI — one with no dependencies, usually a data type or an AI context.
3. `POST ${UMBRACO_LIVE_URL}/umbraco/deploy/management/api/v1/schema/item?udi={url-encoded UDI}` with
   the bearer token and an empty body. Returns `200 OK / "Item updated."` and is idempotent.
4. Re-run `/check-uda`.

**Drift typically drops to zero in one shot even though only one UDI was imported** — the single call
unblocks Deploy's evaluation of the whole pending set. Worth knowing before you script a loop over
every entry.

Related Deploy management endpoints (the OpenAPI spec is sparse; these were inferred from naming, with
the full spec at `/umbraco/swagger/deploy-management/swagger.json`):

| Endpoint | Direction |
|---|---|
| `POST /schema/item?udi=...` | file → DB (import) |
| `DELETE /schema/item?udi=...` | remove the DB entity |
| `POST /schema/file?udi=...` | DB → file (extract) |
| `DELETE /schema/file?udi=...` | remove the `.uda` file |

## Path 3 — Portal restart plus empty-commit nudge (last resort)

Occasionally useful as a heavyweight bootstrap retry, but unreliable on Cloud:

1. Restart the environment from the Cloud portal.
2. If drift persists, push an empty commit and watch the Cloud activity log for the build's
   schema-import step. Errors there name the artifact that actually won't deploy — which is the real
   value of this path, not the restart itself.

## What not to spend time on

- **Portal restart alone.** The bootstrapper compares marker files (`deploy*` under the Deploy
  directory), not `.uda` modification times, so a vanilla restart usually doesn't re-trigger import.
  The tell is `INF Skipping Umbraco content and/or schema import at startup, because no files are
  provided or none of the files exist.` in the startup logs.
- **Empty-commit nudge alone.** When the empty commit follows a commit that already deployed, Cloud's
  pipeline emits `Checking for changes between {prev} and {current}` then `No changes in metadata
  detected - no need to run an Umbraco Deploy extraction`, and skips extraction entirely.
- **The bulk "Update Umbraco Schema from data files" button** — see the table above.

## Symptoms that point here

- `/check-uda` reports pending entries that don't clear after a portal restart or empty-commit nudge.
- Startup logs show the "Skipping Umbraco content and/or schema import at startup" line.
- A content transfer fails with `DeploySchemaMismatchException: Schema mismatch between environments`
  at the "Review manifest on target" step.
- An earlier variant: `RemoteApiException → InvalidOperationException: Could not retrieve artifact
  with UDI {umb://...}`.

## Afterwards

**Pull before your next push.** Cloud may have auto-committed normalized `.uda` files — re-serializing
artifacts with normalized internal IDs and committing them itself — so your local branch can be behind
without you having done anything.
