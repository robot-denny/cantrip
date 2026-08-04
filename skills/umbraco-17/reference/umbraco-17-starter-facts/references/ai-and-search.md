---
name: ai-and-search
description: Umbraco.AI and Umbraco.Cms.Search configuration facts, secret handling, and the failure modes that report success while doing nothing
metadata:
  type: reference
---

# AI and Search facts

Every fact in this file describes a failure that **reports success**. That is what makes this stack's
configuration traps expensive: nothing errors, so the investigation starts from "the feature does not
work" with no thread to pull.

## `$`-referenced configuration keys must be allow-listed, and the refusal is swallowed

The AI core refuses to resolve a `$`-prefixed configuration reference unless its prefix appears in
`Umbraco:AI:AllowedConfigurationKeyPrefixes`. The defaults are only `Umbraco:AI:Secrets` and
`Umbraco:AI:Variables`.

**Why:** A reference to any other prefix throws internally — and **the searcher swallows it**, logging
only a generic vector-search failure. Embeddings and semantic search silently stop working while the
configuration looks correct and the connection appears configured.

**How to apply:** Extend `AllowedConfigurationKeyPrefixes` in committed configuration. **The .NET
configuration binder merges arrays by index, so re-list the two defaults before adding your own** —
omitting them replaces rather than extends, which breaks what previously worked. Flag a `$`-reference
whose prefix is not allow-listed.
**Type:** pattern
**Applies:** Umbraco.AI 17.x (landed in the pre-alignment 1.14.0)
**Verified:** 17.0 (2026-07)

---

## Without a default embedding profile, an index rebuild completes with zero documents

**Why:** The rebuild reports success. There is no warning that nothing was embedded.

**How to apply:** Set a default embedding profile before rebuilding. **Always verify the document
count is non-zero after any rebuild** — that check is the only thing distinguishing a working index
from an empty one.
**Type:** pattern
**Applies:** Umbraco.AI.Search 17.x
**Verified:** 17.0 (2026-07)

---

## The rebuild API returns 200 even when misconfigured

**How to apply:** Never treat a 200 from a rebuild as evidence the index has content. Assert the
resulting document count instead.
**Type:** pattern
**Applies:** Umbraco.AI.Search 17.x
**Verified:** 17.0 (2026-07)

---

## Secrets belong in configuration and are referenced from artifacts by placeholder

AI entity artifacts reference API keys as `$`-placeholders, never raw values. Each environment holds
its own key in that environment's settings.

**Why:** A raw key pasted into a backoffice connection form gets encrypted to the database and then
**breaks on data-protection key rotation** — so it works until it mysteriously does not, on a schedule
nobody remembers.

**How to apply:** Flag any raw key in a connection form, an artifact, or a committed file. A committed
key is a Blocker and must be treated as compromised and rotated, not merely removed.
**Type:** pattern
**Applies:** Umbraco.AI 17.x
**Verified:** 17.0 (2026-07)

---

## Cloud's app-settings UI rejects `:` in key names — use the double-underscore form

The portal's validator allows only alphanumerics and underscore, so `Anthropic:ApiKey` cannot be
entered. Use `Anthropic__ApiKey`.

**Why:** .NET flattens `__` back to `:` when building configuration, so placeholder references and
local settings keep the colon form unchanged. Only the portal entry differs.

**How to apply:** Use `__` in portal settings and `:` everywhere else. Flag a mismatch, which presents
as a key that resolves locally and not on the environment.
**Type:** pattern
**Applies:** Umbraco Cloud
**Verified:** 2026-07

---

## Existing AI entities do not auto-export when the Deploy packages are installed

The serializer writes on save. Installing the packages on an established instance exports nothing that
already exists.

**How to apply:** Open each entity and save it once, in dependency order — connections, contexts, and
guardrails first, then profiles, then prompts and settings, then agents. Verify artifacts appear, and
**grep the revision directory for raw secrets before committing** to confirm only placeholders are
present.
**Type:** pattern
**Applies:** Umbraco.AI.Deploy 17.x
**Verified:** 17.0 (2026-07)

---

## Profile settings did not serialize before Deploy 17.0.1

Earlier versions wrote `Settings: {}` to the artifact, so profile tuning could not deploy — and
deploying such an artifact **overwrote the target's settings with empty**.

**Why:** A silent downgrade of a working environment, caused by deploying what looked like a valid
artifact.

**How to apply:** The tell is a profile artifact with `Settings: {}` immediately after a save. On
17.0.1 or later, settings flow normally: edit, save, commit the artifact. Below it, do not deploy
profile artifacts.
**Type:** fixed-with-guard
**Applies:** Umbraco.AI.Deploy <17.0.1 affected; fixed in >=17.0.1
**Verified:** 17.0.1 (2026-07)

---

## The vector index does not deploy — it is per-environment and rebuilt by hand

Every AI entity deploys as schema. The index itself does not.

**How to apply:** After deploying to an environment, rebuild the index there and verify a non-zero
document count before promoting further. Skipping it leaves search returning empty results on an
environment that otherwise looks correctly deployed.
**Type:** pattern
**Applies:** Umbraco.AI.Search 17.x
**Verified:** 17.0 (2026-07)

---

## A keyword provider on a pre-release may throw on multi-word queries

A beta of the Examine-backed keyword provider throws a null-reference inside Examine for some
multi-word queries.

**How to apply:** Guard the keyword path so the page degrades to an empty state rather than a 500, and
remove the guard when a fixed release ships. This is the shape of fact most likely to have expired —
check the current provider version before assuming it still applies.
**Type:** fixed-with-guard
**Applies:** Umbraco.Cms.Search.Provider.Examine 1.0.0-beta.9
**Verified:** beta.9 (2026-07)

---

## Search framework registration is not idempotent across every call

Registration helpers differ in whether repeated invocation is safe.

**How to apply:** Register once in a single composer rather than defensively in several. Flag duplicate
registration of the same search component.
**Type:** pattern
**Applies:** Umbraco.Cms.Search 1.x
**Verified:** 1.0.0 (2026-07)
