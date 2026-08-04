# 0005. Work-type classification must not depend on documentation coverage

**Status:** Accepted
**Date:** 2026-08-03
**Reported by:** the canary consumer, from the first real cast of `/spec` on a brownfield repo

## Context

The work-type classifier had a flaw that no amount of reading it would have found, because it only
manifests on a repository with documentation debt — and both source projects had documented their
capabilities from early on.

**The same piece of work classified differently depending only on whether the surrounding capability
already had a doc.** Enhancing a documented area resolved to `change-to`, appending a Rule to the
existing doc. Enhancing an *undocumented* area resolved to `new-capability`, spawning a new doc — not
because the nature of the change differed, but because `change-to <existing-slug>` has no slug to name
when no doc exists, so the classifier fell through.

The deciding factor was **doc debt, not the nature of the change.** That is precisely backwards: the
classification is supposed to describe the work.

Concretely, on the canary: adding placeholder graphics to an article card. The article card is a real
capability, undocumented. `change-to` had nothing to point at, so the work became a `new-capability`
that would have created `_features/article-card-placeholders.md` — a doc named after a *piece of work*,
which is the exact outcome the Guard exists to prevent.

This matters more than a classification nicety, because **brownfield adoption is an explicit goal.**
`/feature`'s from-code mode exists so a project with no specs can backfill behavioral docs. A
classifier that misbehaves precisely on under-documented repos undercuts that.

## Decision

Three changes, all adopted from the consumer's proposal, which framed the problem better than the
original contract did.

**1. Add a naming tell for amend-versus-create.**

> If the doc name you would create reads as a **behavior** (`article-card-placeholders`) rather than an
> **area a stakeholder would name** (`article-card`), it belongs as a Rule inside the area's doc, not
> as a new file.

This parallels the existing *transition versus standing behavior* tell exactly — same kind of test,
applied to the document's name rather than to its Rules. That the two tells rhyme is a good sign the
underlying distinction is real.

**2. When `new-capability` is chosen but the nearest area is undocumented, name the doc at AREA level.**

This is the change that actually dissolves the coverage-dependence. Naming at area level makes the
`new-capability` path **converge on the same artifact `change-to` would have produced.** The two
branches stop diverging on doc debt; the debt instead shows up honestly as an under-populated area doc,
flagged for `/feature`'s from-code mode to backfill.

The classification stops being a fork with two different outcomes and becomes one outcome with two
entry points.

**3. Deciding when to split one capability doc into several is editorial, not per-increment.**

It is a readability judgment made deliberately, when a doc has grown unwieldy — not an output of
classifying a single increment. **The classifier biases toward amend.**

## Consequences

- **The capability doc's identity is now decoupled from the increment slug.** Area-level naming means
  the doc (`article-card`) routinely differs from the increment (`placeholder-graphics-imageless-cards`).
  The plan template's final step read `/feature update <feature_slug>`, which would target the wrong
  name — so `/spec` now records an explicit **`feature-doc:`** field that `/plan` and `/feature` carry
  through. Without that, adopting this ADR would have introduced a new bug while fixing an old one.
- Under-documented areas produce thin docs rather than misnamed ones. A thin doc is visible debt with a
  known remedy; a misnamed doc is invisible debt that pollutes the capability catalog permanently.
- `fix-infra` is unaffected — it never earned a doc, so coverage never entered into it.

## What this says about the checks

Nothing in the gate could have caught this, and nothing in a careful read would have either. It is not
a contract violation, not a missing slot, not a leaked project fact — it is a *classifier that behaves
correctly on well-documented repositories and incorrectly on the ones the toolkit is meant to help
adopt.*

It took a real cast, on a real brownfield repo, by someone who had not written the spell. That is the
third distinct class of defect this project has found only by running against reality — after a
generalization that was structurally clean and produced garbage, and an install checker that passed
eleven self-built fixtures while giving dangerous advice to its first real user.
