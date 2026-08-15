# ADR 0006 — no unguarded preconditions

**Date:** 2026-08-04
**Gate:** 10/10 (check 10 is new).
**Origin:** the owner's observation that ADR 0005's fix was good but was *a patch to one instruction*,
and that resilience when something is not known up front should be a **principle guiding decisions**
rather than a repair applied case by case.

## The audit found a clean structural asymmetry

Auditing every instruction that depends on something existing:

| | Guarded for absence? |
|---|---|
| **Slot fallbacks** — code layout, tests, branch naming, commit format | **All of them** ✅ |
| **Non-slot instructions** — copy the closest block, find the exemplar, find the existing capability doc | **Three of four unguarded** ❌ |

And `design-system-authoring` had **zero** absence clauses, written the same day.

**The cause is not carelessness — it is that slots have a forcing function and instructions do not.**
Check 4 refuses a `**Slot:**` without an adjacent `**If empty:**`, so writing a slot *made* me consider
absence, every time, with no discipline involved. Nothing asked the same question of "copy the closest
existing component", so it went unasked.

The sharpest evidence: `/feature`'s Guard — "find the existing capability doc and update *that*" — was on
the unguarded list. That is the exact instruction ADR 0005 was about. I fixed the classifier in the
`workflow` skill and left the local instruction depending on the same precondition untouched, one
increment earlier.

## The ladder, including the owner's two additions

My existing fallback vocabulary was three rungs: infer, skip, ask. The owner's examples — reference
another codebase, or start sparse and let it fill in over time — are two more, and both are better than
skipping:

1. Infer from the project
2. **Borrow from a named external reference** — ask for it, never assume one, never silently import
   outside conventions as the project's
3. **Seed thin, marked to grow**
4. Proceed without, and say so
5. Ask

Never fabricate.

**Rung 3 turned out to be a pattern the toolkit had already used three times without naming it:** ADR
0005's thin area-level doc flagged for backfill; starter facts shipping as claims-to-verify that become
earned facts; `/plan`'s Tests fallback proposing a location as a new convention. Naming it makes it
reachable deliberately instead of by luck.

## Fixes

Four instructions guarded — `/feature`'s Guard, `/block` Step 5, `umbraco-17-planning`'s slice row, and
`design-system-authoring` Steps 1 and 3. `/block` and `design-system-authoring` got the full ladder:
ask for a reference codebase first, then establish the convention *explicitly and minimally* while
saying you are establishing rather than following it.

The framing I settled on for `/block`: **the first block in a project defines its conventions whether or
not anyone decided to.** That is why quietly picking a shape is worse than saying "I am establishing
this."

## Check 10, and two ways I got it wrong first

The audit's own lesson is that a principle without a forcing function gets applied when the author
happens to remember — so the exemplar pattern, which slipped twice and is greppable, now has a check.

Getting it right took two corrections, both worth recording:

**It passed trivially at first.** The first version asked whether a file contained an absence clause
*anywhere*. Every skill carrying a slot does, so it passed everything — **and its negative test produced
no output, which I nearly read as "nothing to report" rather than "the check does nothing."** Same class
of error as the pipeline that masked the gate's exit status: a check that cannot fail looks identical to
a check that passes.

**Then it flagged a frontmatter description.** A description is a trigger string, not an instruction, so
requiring a caveat inside one would trade triggering accuracy for nothing. Frontmatter is now excluded.

Once proximity-based, it immediately caught **two real cases in my own work from an hour earlier**: I had
added the greenfield guidance as a section sixty lines below the instructions it guards. Someone reading
Step 3 would never scroll to it. Both instruction sites now carry a local pointer.

**Honest limitation:** the absence pattern is broad enough to be satisfied incidentally — "has no "
matches prose that is not a guard. It is a heuristic forcing function, not a proof, and it will let a
weakly-worded guard through. That is an acceptable trade for a check that caught three real gaps on its
first run; a stricter pattern would produce false positives, which is the failure mode that gets checks
ignored.
