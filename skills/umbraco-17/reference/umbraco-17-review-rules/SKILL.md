---
name: umbraco-17-review-rules
description: What to check when reviewing a diff in an Umbraco 17 project — the security surfaces specific to CMS rendering, the null-safety and alias traps in published content, the per-request cost patterns that make view-model construction the hot path, and the accessibility concerns in editor-authored and backoffice-extension output. Consult when reviewing an Umbraco diff for code quality, performance, or accessibility.
---

# Reviewing Umbraco 17 code

Supplements the generic reviewer checklists with what is specific to this stack. Everything here is
additive — the `reviewer-discipline` contract still governs scope, severity, and evidence.

**The facts behind these checks live in `umbraco-17-starter-facts`.** This file says *what to look
for*; that one says *why it is true and which versions it holds for*. Consult it rather than
re-deriving — and cite it when a finding rests on a platform behavior rather than on the diff alone,
since "this returns empty instead of throwing" is a claim a reader will want backing for.

## Code quality and security

**Anything serialized into client-visible markup is public.** Data attributes, inline scripts, and
rendered JSON are unauthenticated page content. A secret, token, or internal-only field there is a
**Blocker**, and the finding must say the credential is compromised and needs rotating — not merely
removed.

**Published content properties are frequently null.** Umbraco returns absent rather than throwing far
more often than typical .NET code assumes. Check for a null or empty guard before property access,
before enumerating a collection, and before dereferencing a picked item.

**Watch the alias traps.** Reserved and unprefixed generic aliases collide silently, a typo'd alias
renders empty rather than erroring, and the dropdown UI alias has a plausible wrong value that fails
to render. All three are in the starter facts.

**Authorization on custom endpoints.** Umbraco's own routing does not protect a custom controller or
minimal API you added. Check that every new endpoint has an explicit authorization decision, and treat
an unauthenticated write endpoint as a Blocker.

**Generated models are output, not source.** Flag hand edits — they are silently lost at the next
regeneration, possibly much later and by someone else.

**Schema artifacts are managed, not hand-edited.** Flag manual `.uda` edits, and flag `.uda` churn
staged without an intentional schema change behind it.

**Never hardcode identifiers or slugs.** Entity IDs differ per environment, and Umbraco appends a
numeric suffix to a colliding slug. Both are in the starter facts.

## Performance

**Per-request view-model construction is the hot path.** This is the single most productive place to
look in an Umbraco diff. Expensive or repeated content lookups, tree traversals, or media resolution
performed per request — and worse, performed inside a view — are **Major** at minimum. The fix is
moving the work into a service layer and caching where the result is stable.

**Content-tree traversal inside a loop.** Iterating children or block items and doing a per-item
lookup is the recurring N+1 shape here. Require pre-fetched collections.

**Media resolution inside a loop** without caching is **Major**.

**A caching gap is a legitimate finding, not speculation.** For a stable, expensive, frequently
rendered fragment — navigation, footer, sitewide settings, a listing — the *absence* of caching is
the finding. Umbraco offers a cached-partial mechanism; a project may instead memoize at the service
layer. Either is fine; neither being present for a sitewide fragment is not.

**Configuration read in a hot path.** Values pulled from configuration per request should be bound once
and injected, not re-read.

**Form submission handlers must be async, cancellable, and bounded.** A form handler is where a project
most often reaches an external system on a visitor's request, and it is the one outbound call whose
latency a visitor sits and waits through. A third-party endpoint that slows or stops takes the form with
it, and consumed synchronously it takes a request thread too. Require `async`, a `CancellationToken` on
the signature and passed to the call, **and a deadline** — a token alone bounds nothing if nothing ever
cancels it.

The general rule this is an instance of — that long-running outbound calls and streams must not be
consumed synchronously, must propagate cancellation, and must carry a timeout — belongs to whatever
review guidance covers the language and framework underneath, where one is installed; stating it here
as well would put a single defect into the merged report twice. Where none is installed, apply it
yourself: it holds for every outbound call and stream in the diff, not only the ones behind a form.

**Client-side cost must be justified.** A component that ships a framework runtime to render content
that is static or already server-rendered is a **Minor** to **Major** finding. Oversized data payloads
serialized into markup inflate every page's HTML.

## Accessibility

Most of what matters is in the generic checklist. What is Umbraco-specific:

**Editor-authored output is outside the template's control.** Rich-text output can lack image
dimensions and can carry heading levels an editor chose. When the defect originates in the editor
rather than the view, say so and attribute it correctly — flagging the template misdirects the fix.
The starter facts cover the image-dimension case specifically.

**Backoffice extensions are web components, and the same bar applies.** An extension built with the
backoffice's component library still needs accessible names, keyboard operability, and focus
management. Its being "admin-only" is not an exemption — editors and administrators include disabled
people.

**Block rendering repeats.** A semantic defect in one block view multiplies across every page using
that block, so severity should reflect reach. Conversely, a fix in a shared block view is unusually
high-leverage — worth saying so, since it changes how the developer prioritizes it.

**Slot:** `.agents/config/reviewer-rules/`
**If empty:** apply the checks above plus the generic checklists. Project-specific review rules — an
architectural seam that must not leak, a component contract, a documented exception — belong in that
slot; do not invent them, and note anything that looks like an unwritten convention as an observation
rather than a violation.
