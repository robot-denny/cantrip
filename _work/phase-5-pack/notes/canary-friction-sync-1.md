# Canary friction sync #1 — what the first real cast found

**Date:** 2026-08-03. Source: the demo-site consumer, after install + `/spec` + `/plan` on one real
increment. **Every finding was actionable and every one is now fixed.**

## The headline was a design flaw no reading would have found

**Work-type classification was coverage-dependent.** The same work classified differently based only on
whether the surrounding capability already had a doc — because `change-to <existing-slug>` has no slug
to name when no doc exists, so the classifier fell through to `new-capability`. **The deciding factor
was doc debt, not the nature of the change.**

Concretely: enhancing an undocumented article card would have created
`_features/article-card-placeholders.md` — a doc named after a *piece of work*, which is exactly what
the Guard exists to prevent. The Guard was being defeated by the path that reaches it.

This never appeared in either source repo because both documented their capabilities early. It appears
immediately on a brownfield repo — and brownfield adoption is an explicit goal, which is why
`/feature` has a from-code mode at all. **A classifier that misbehaves precisely on under-documented
repos undercuts the feature built for under-documented repos.**

All three proposed fixes adopted, and the consumer's framing was better than my contract's:

1. **A naming tell** — if the doc name reads as a *behavior* rather than an *area a stakeholder would
   name*, it is a Rule inside the area's doc. This rhymes with the existing transition-versus-standing
   tell, which is a good sign the distinction is real. It also catches what the transition tell misses:
   a behavior-named doc can be full of perfectly good standing-behavior Rules and still be the wrong
   file.
2. **Area-level naming when the area is undocumented** — the change that actually dissolves the
   coverage-dependence, by making `new-capability` converge on the artifact `change-to` would have
   produced. One outcome with two entry points instead of a fork.
3. **Splitting a doc is editorial, not per-increment** — the classifier biases toward amend.

Recorded as ADR 0005.

**The consequence I had to chase:** area-level naming decouples the doc's identity from the increment
slug, so the plan's templated `/feature update <feature_slug>` would target the wrong name. Adopting
the fix without also threading an explicit `Feature doc:` field through spec → plan → feature would have
introduced a new bug while fixing an old one. Both done together.

## A real defect in `/plan` that I introduced

`/spec` hands off `/plan <feature_slug>`, but Step 1 branched only on "path versus description" — so a
bare slug fell to *description* and **re-derived a new slug from the slug string**, producing a plan
divorced from its spec.

I introduced this at 2.1 when I changed the handoff to a slug and did not update the receiving end. A
two-file change where I only made one. Step 1 now resolves a bare slug against the workspace layout,
and **stops rather than inventing** when nothing resolves.

## Their open question, answered: no, and now yes

They asked whether `check-install.sh` detects the four-way install scatter. They had cleaned before
running it, so they could not tell.

**Answer: it did not.** Reproduced on a fresh install — 4 of 4 locations written, checker reported a
clean install with no mention. Now it detects and reports both redundant locations with the safe cleanup
command, considering only toolkit-roster names so a project's own `skills/` contents are never
implicated. Fixtured at 14 cases.

Worth noting their cleanup instinct was right and the obvious one was dangerous: `rm -rf skills/` would
have destroyed tracked project content; `git clean -fd` was correct.

## The two smaller spell fixes

**Workspace divergence** — `/spec` created `_work/` beside an existing `_specs/` without comment. It now
stops and asks when the layout would create a workspace directory next to an established one, because
fragmenting a project's history across two conventions is worse than either convention.

**Branch nesting** — `/spec` correctly inferred a branch prefix from history, then nested the new branch
inside the trial branch. It now notices when the current branch is not the default and asks rather than
branching from a branch.

## Positives worth banking

**ADR 0003 pack routing works, and self-scoped correctly.** `/plan` consulted `umbraco-17-planning`,
which **declined to impose a schema step on a view-and-CSS change.** That mechanism had never once run
with a pack present — it rested entirely on reasoning until this cast. It routed *and* knew when not to
apply.

**The filled-slot path works.** Every previous test was all-slots-empty. `/plan` consumed real build and
test commands, `## Unit of work`, `## Code layout`, and `## Planning gotchas`.

**Graceful degradation confirmed independently** — `/spec` cast with 0 of 14 slots filled produced
sensible output throughout, which is ADR 0001's acceptance test passing in someone else's repo.

## The pattern across three syncs

Three distinct defect classes have now been found only by running against reality: a generalization that
was structurally clean and produced garbage; an install checker that passed eleven self-built fixtures
and gave dangerous advice to its first real user; and a classifier that is correct on well-documented
repos and wrong on the ones the toolkit exists to help.

**None was catchable by the gate, and none by a careful read.** The gate tests whether a file is shaped
right. Reality tests whether it is right.
