# Canary sync #3 — from-code validated, and it was gated against its best use

**Date:** 2026-08-04. Source: the demo-site consumer casting `/feature` on a pre-existing, partly
documented capability. **This closes §10's "brownfield adoption story — no candidate yet."**

## The finding: my spell forbade what they did

Their cast combined **update mode on an existing doc** with **the from-code technique** to backfill the
parts of the capability that had never been documented — only the newest increment had a Rule.

That is precisely what branch 3 excludes. It reads: *only if nothing above resolves and there is
**no** existing feature doc.* So the technique was gated behind "nothing else exists," while its most
valuable application is **"a doc exists and covers less than the code does"** — which is the ordinary
condition of every real codebase.

The mechanism was right and the gate was wrong. From-code is now documented as **a mode and also a
technique**: the cold-start mode unchanged, plus an explicit instruction in update mode to compare the
doc against the *code* rather than only against the artifacts, and apply F1–F4 to whatever the code does
that the doc does not describe.

Why this matters beyond one cast: without it, **a doc stays permanently partial.** Each increment
documents its own change, nothing ever documents what was already there, and the doc looks maintained
while covering a fraction of the capability. That is the failure mode brownfield adoption has to beat,
and it is invisible — a partial doc reads exactly like a complete one.

## The by-product I under-specified

Reading schema, model, and view together found an **orphaned CSS rule** (no view emits it since an
earlier increment) and a **view comment contradicting the code** (claiming something isn't rendered when
it is).

My `Open Issues` hook existed and fired, but named only "a property nothing reads, a mismatched
identifier." Broadened to include dead styling, comments contradicting code, unreachable branches, and
defaults that can never apply — with the reason stated:

**This pass is unusually good at finding these because it is the one pass that compares what each layer
claims against what the others do.** A doc written by hand from the same code would miss them, because a
person describes what they believe the code does. This describes what each layer actually says, and the
disagreements fall out. The stale comment is the most dangerous of the four, since a reader trusts it.

## The third coverage state

They separated **test-verified** rules from **code-derived-untested** ones. My table had two states,
`Covered` and `Not covered`, which cannot express that — so a partially-backfilled doc would present
verified and inferred behavior with equal confidence.

Added `Not covered (code-derived)`: inferred from reading the code, never specified and never tested —
**the weakest claim in the document.** Keeping it distinct is what makes a backfilled doc honest, and a
reader can now tell verified from inferred at a glance. From-code mode's rows now start in this state
rather than plain `Not covered`.

## What this closes

The direction doc's §10 listed **"Brownfield adoption story — the toolkit assumes docs accrete from day
one; adopting on an existing site needs a way to backfill `_features/` from existing code. No candidate
yet."**

There is now a candidate, exercised on a real repo: `/feature` in update mode applying the from-code
technique. It backfilled a full capability from schema, model, and view — and surfaced two code defects
as a by-product.

**Every surface of the chain is now validated on a real project.** The remaining unexercised paths are
the ones that need a *different kind* of project rather than another cast: a greenfield build with no
exemplars (the ADR 0006 rung-2 and rung-3 branches), and a second consumer to test whether the setup
skill's detection generalizes past one repo.
