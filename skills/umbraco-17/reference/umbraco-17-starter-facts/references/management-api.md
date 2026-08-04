---
name: management-api
description: Umbraco 17 Management API shapes, auth behavior, and known quirks in the Playwright test-helper package
metadata:
  type: reference
---

# Management API and test-helper facts

## Access tokens expire in 299 seconds

The client-credentials token from
`/umbraco/management/api/v1/security/back-office/token` is valid for 299 seconds.

**Why:** Just under five minutes, which is long enough that a short script never notices and a
multi-step setup routine fails partway through — usually on whichever call happens to cross the
boundary, so the failure looks intermittent and unrelated to auth.

**How to apply:** Re-authenticate before each logical group of operations rather than acquiring one
token for a whole sequence. Flag any setup routine that fetches a token once and then makes many
sequential calls.
**Type:** pattern
**Applies:** umbraco >=17 <18
**Verified:** 17.3 (2026-07)

---

## Document-type properties come back as a flat array, not nested in groups

The API returns properties directly on the type as `properties`. There is no `groups` nesting in the
response, whatever the backoffice UI's tabs suggest.

**How to apply:** Use `elementType.properties ?? []`. Flag `groups?.flatMap(g => g.properties)` — it
yields undefined and then an empty list, so the code appears to work while asserting nothing.
**Type:** pattern
**Applies:** umbraco >=17 <18
**Verified:** 17.3 (2026-07)

---

## `getByName()` returns `false`, not `null`, when nothing matches

The test-helper package's lookup returns `false` for a miss.

**Why:** `expect(x).toBeNull()` therefore **fails** on a missing entity, and worse,
`expect(x).toBeFalsy()` **passes** — so a test that was supposed to prove an entity exists passes
against an entity that does not.

**How to apply:** Assert with `.toBeTruthy()` for presence and `.toBeFalsy()` for absence. Flag any
`.toBeNull()` / `.not.toBeNull()` on a `getByName()` result.
**Type:** pattern
**Applies:** `@umbraco/playwright-testhelpers` 17.x
**Verified:** 17.1.0-beta.7 (2026-07)

---

## `getByName()` has a `recurseChildren` short-circuit bug

The helper can fail to find an entity that exists, when it sits deeper than the recursion reaches.

**How to apply:** Always provide a fallback — fetch a known parent's children directly and match
there. Document the workaround with a *why* comment so it can be removed when fixed upstream.
**Type:** fixed-with-guard
**Applies:** `@umbraco/playwright-testhelpers` 17.x
**Verified:** 17.1.0-beta.7 (2026-07)

---

## `STORAGE_STAGE_PATH` is an intentional upstream typo

The exported name in the test-helper package is misspelled — "STAGE" rather than "STATE".

**Why:** It looks exactly like a local mistake, so a reviewer or a well-meaning refactor "corrects"
it and the import breaks.

**How to apply:** Do not flag it as wrong, and do not rename it. If the comment explaining it is
missing, that is the thing worth flagging.
**Type:** false-positive-suppression
**Applies:** `@umbraco/playwright-testhelpers` 17.x
**Verified:** 17.1.0-beta.7 (2026-07)

---

## The backoffice is a Lit SPA, so UI-driven login helpers do not work

A login helper that looks for `[name="username"]` will not find it in the DOM.

**How to apply:** Authenticate via the OAuth client-credentials flow instead, and write the token
into the storage-state format the backoffice expects. Flag any test attempting UI login.
**Type:** pattern
**Applies:** umbraco >=17 <18
**Verified:** 17.3 (2026-07)

---

## Never hardcode entity IDs — they differ per environment

Document, document-type, folder, template, and data-type identifiers are environment-specific.

**How to apply:** Look them up dynamically — walk tree roots, or search by name. Flag any UUID
literal used as a node reference in a script or test.
**Type:** pattern
**Applies:** umbraco >=17 <18
**Verified:** 17.3 (2026-07)

---

## Never hardcode URL slugs — Umbraco appends a numeric suffix on collision

When a name duplicates an existing sibling, the generated slug gains `-2`, `-3`, and so on.

**How to apply:** After publishing, read the actual URL from the API response or the document's
`urls` property. Flag any test asserting a slug path it constructed itself.
**Type:** pattern
**Applies:** umbraco >=17 <18
**Verified:** 17.3 (2026-07)

---

## Bootstrapping `editorAlias` from a document's values misses never-saved properties

Building an update payload by reading `editorAlias` values off an existing document only covers
properties that have been saved at least once. A property never touched in the backoffice is absent
from `values`, so setting it on another document throws "no editorAlias known".

**Why:** The absence is invisible until you target a document that lacks the property, which is
typically a different document from the one you bootstrapped against.

**How to apply:** Require either a declared fallback map covering every property the code writes, or
an explicit skip guard when a property is absent. Flag payload builders that rely solely on
bootstrapping.
**Type:** pattern
**Applies:** umbraco >=17 <18
**Verified:** 17.3 (2026-07)

---

## The Delivery API is the sanctioned way to resolve a URL without hardcoding a slug

Where a test or script needs a page's real URL, querying the Delivery API is the approved approach
rather than constructing a path.

**How to apply:** Accept this as a valid resolution pattern. Flag it only when it is *missing* and a
constructed slug is used instead.
**Type:** false-positive-suppression
**Applies:** umbraco >=17 <18
**Verified:** 17.3 (2026-07)

---

## Restoring several documents in a teardown needs each restore guarded independently

If a teardown restores more than one document, a throw from the first prevents the rest from running,
leaving later documents dirty for the next run.

**How to apply:** Collect errors per restore and raise an aggregate at the end. A single restore needs
no guard — it either succeeds or throws, which is correct. Flag multi-restore teardowns without
independent guarding.
**Type:** pattern
**Applies:** umbraco >=17 <18
**Verified:** 17.3 (2026-07)

---

## Sanitizing a document before restore must be scoped to the aliases the test touched

A sanitize step that nulls every value clobbers real editor content on a shared environment.

**How to apply:** Scope sanitization to the minimum set of aliases the test writes. Flag a sanitize
routine operating on the whole document.
**Type:** pattern
**Applies:** umbraco >=17 <18
**Verified:** 17.3 (2026-07)
