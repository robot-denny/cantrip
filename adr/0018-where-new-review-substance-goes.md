# 0018. Where new review substance goes

**Status:** Accepted
**Date:** 2026-09-03

## Context

Two candidates for a fourth reviewer arrived within two days of each other, and both resolved
somewhere other than a reviewer.

The first was OWASP security rules. Its discovery settled on a core reference owned by
`code-reviewer`, because the substance "needs no new voice in the merged report and therefore no new
domain boundary." See `_work/owasp-security-review-rules/discovery.md`.

The second was prose quality. The toolkit's own documentation reads mechanical, and the fix that
stuck was `prose-discipline`, a reference the model picks up whenever it writes prose. What remained
was the enforcement question, and it produced a longer list of options than the OWASP case did,
because prose can be edited as well as reported on.

[ADR 0017](0017-when-a-gap-earns-a-runbook.md) set the bar for generalizing a rule: wait for a second
instance. This is the second instance, and it tests one thing the first did not. A reviewer reports
and changes nothing by contract. Every request that motivated `prose-discipline` was an instruction
to rewrite a document, not a request for a report. The need was never reviewer-shaped, and the
reviewer-shaped hole nearby is what made it look that way.

Two other forces bear on it. `/implement-step` runs `/code-review` between steps, so every reviewer
is dispatched dozens of times across one plan. Most of those steps touch no prose, and a prose
reviewer would be paid for on all of them to say nothing. The spell budget stands at nine of ten
([ADR 0010](0010-skills-not-commands.md)), so the tenth is the last one that does not require merging
two others first.

## Decision

**New review substance is a reference until something forces it elsewhere.** Two tests, applied in
order, decide whether it goes anywhere else.

| | The test | What it buys, and what it costs |
|---|---|---|
| 1 | **Does it need its own voice in the merged report?** | A reviewer is justified only when its findings cannot be attributed to an existing reviewer's domain. A new one adds a domain boundary to negotiate under `reviewer-discipline`, a dispatch paid on every `/implement-step`, and edits to every doc that states the reviewer count |
| 2 | **Does the work change files rather than report on them, and does the demand recur?** | A spell is justified only when both halves hold. Reviewers report; spells act. A demand that decays once the reference is in place is a migration, and a migration does not earn a permanent slot |

**Failing both tests is the common case and it is not a gap.** The substance ships as a reference and
enforcement waits for evidence.

**On prose specifically:** `prose-discipline` ships as a core reference. There is no prose reviewer
and no `/revise` spell. The voice half of the demand decays to near zero once the reference governs
what gets written. The durable half is accuracy drift and redundancy accretion in documents that
already exist, and so far that has been a housekeeping nuisance rather than a cost.

**The reversal condition, named so it can be recognised:** a stale document causing a real failure.
A wrong instruction followed, an onboarding blocked, a decision made from a doc that no longer
described the system. Rate is not the trigger. A pile of mildly untidy files is what a manual
pass is for.

## Alternatives considered

- **A fourth reviewer under `reviewer-discipline/agents/`** — *rejected.* Three reasons, any one of
  which would carry it. It is dispatched on every step of every plan to say nothing on most of them.
  The three-reviewer count is load-bearing across the README, the concepts doc, the spell cards, and
  the agent files, so adding one is a documentation migration. And it would deliver a report where
  the need was an edit.
- **A `/revise` spell, wide scope: voice, redundancy, and accuracy drift** — *rejected for now, and
  the strongest of the rejected options.* Accuracy drift is the one job here that never decays,
  because nothing at write time can repair a document that was true when written. It loses on
  evidence rather than on shape. It would take the last of ten slots to solve a problem that has not
  yet cost anything.
- **A `/tighten` spell, voice only** — *rejected.* Its demand curve reaches zero once the backlog is
  clear and the reference governs new writing. That is a migration tool, and a migration tool can be
  a prompt.
- **Contract checks on em-dash density and sentence length** — *rejected for now.* They gate the
  voice half, which is exactly the half a project's own brand voice is entitled to override. A gate
  that fires on house style gets switched off, and switching it off also silences the checks that
  were right.
- **Keeping `prose-discipline` repo-local rather than shipping it** — *rejected.* A feature doc has
  the same reader as a README. A consuming project needs the standard for the same reason this repo
  does.

## Consequences

- **The tenth spell slot stays open**, and the next candidate for it competes on evidence rather than
  on arriving first.
- **`prose-discipline` is unenforced by any gate**, deliberately. Its numeric targets are a standard
  the model applies at write time and a person applies when revising, and nothing fails a build over
  them.
- **The existing documentation backlog is cleared by hand**, once, with direct prompting rather than
  tooling. Roughly fifteen to twenty-five files.
- **Core still has no maintenance path for non-feature documentation.** `/guide --audit` covers
  editor guides inside a pack and `/testify audit` covers capability docs. Nothing sweeps a README, a
  roadmap, a runbook, or `docs/` for drift, and `docs/spell-cards.md` carries a hand-written staleness
  procedure because there was nowhere else to put it. This record does not close that gap. It records
  that the gap has not yet been worth the slot.
- **A new constraint on the layer contract:** `prose-discipline` yields to a project's declared voice
  in full. Its legibility rules apply regardless, its voice rules do not, and a configured prose
  linter outranks it rather than sitting beside it.
- **This record is the first document written under `prose-discipline`.** It is also the fairest test
  available of whether the standard survives contact with an ADR, which is the densest register the
  repo writes in.
