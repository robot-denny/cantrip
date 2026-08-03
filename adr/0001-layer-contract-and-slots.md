# 0001. Layer contract and the slot mechanism

**Status:** Accepted
**Date:** 2026-08-03

## Context

Cantrip extracts a working toolkit out of two host projects that have been tailored in place
for months. The coupling to those projects does not sit in separable files — it cuts *through*
them. A single command file is simultaneously a generic planning engine, a stack-specific
skill-routing table, and a set of hardcoded project paths.

So extraction is splitting files along seams, and a seam needs a contract on both sides: what
a shipped file may contain, and where the removed facts go instead. Every file extracted after
this decision conforms to it, which makes it the most expensive thing to get wrong and the
cheapest thing to get right first.

The evidence for what the contract must cover came from surveying what is actually embedded in
the files bound for L0:

- Absolute `nvm` paths pinned to **two different Node versions** across the two repos —
  unshippable by construction, and the clearest proof that environment assumptions must move.
- Build and test commands naming specific project directories.
- Local URLs on two different ports.
- Workspace paths (`_specs/`, `_plans/`, `_features/`, `_audits/`) and a code-layout map
  keyed by project-specific assembly names.
- Project-specific framing of the work itself ("a feature is almost always a vertical slice").
- Reviewer orientation blurbs describing one project's architecture.
- A tooling mode that changes behavior (models generated vs committed).

## Decision

**Three layers, with a one-line invariant:** an L0 or L1 file contains no fact about any
specific project. L1 may hold facts about a *technology*; only L2 holds facts about a
*project*.

**Four slot files** — `paths.md`, `stack.md`, `conventions.md`, and `reviewer-rules/` under
`.agents/config/` — because the surveyed facts cluster into exactly four kinds: where things
live, how to run things, how this project works, and what each reviewer enforces.

**Slots are referenced in plain markdown, with no templating and no build step.** Every
reference is a `**Slot:**` line naming file and heading, immediately followed by an
`**If empty:**` line giving the fallback. Fallbacks may infer from the repo, skip and say so,
or ask the user — never fabricate.

**Graceful degradation with all slots empty is a hard requirement**, not a nicety. It is the
acceptance test for a fresh install and what makes the toolkit usable on day one, before any
setup interview has run.

**Editing a vendored L0/L1 file is a divergence, not a workflow.** If tailoring a project
requires editing core, that is a missing slot and gets reported as one.

The normative spec is [docs/contract.md](../docs/contract.md).

## Alternatives considered

**Token substitution (`{{slot:stack.build_command}}`) with a processor.** Rejected: it buys
compile-time validation at the cost of a build step, and it makes the shipped files
unreadable on their own. Markdown-first and LLM-portable is a stated design principle;
a file that needs preprocessing to be understood violates it. The `**Slot:**`/`**If empty:**`
convention gets most of the validation benefit — a grep can check the pairing — with none of
the machinery.

**One combined `project.md` slot file.** Rejected: reviewers should load only their own rules,
and a single file forces every consumer to read everything. The four-way split also gives the
setup skill a natural work breakdown, since each file has a different detection strategy.

**Relative markdown links from the skill directory to config.** Rejected: relative depth
depends on where the skill was vendored, so the links break under exactly the condition the
toolkit is built for — being installed into layouts we do not control. Canonical absolute-
from-repo-root paths in prose survive that.

**Allowing local edits as the tailoring mechanism** (copy-once, edit freely). Rejected: this
is the current pain. It is also actively unsafe here, because the underlying `skills update`
was verified to silently clobber local modifications with no warning, no merge, and no hash
check against local state.

## Consequences

- Every extracted file now has a mechanical acceptance test, automatable as
  `scripts/check-contract.sh` (increment 0.6) — which means every later checkpoint has teeth
  rather than relying on a careful read.
- The "all slots empty" requirement gives Phase 3's standalone-install goal a concrete
  definition of done.
- Discovering a needed slot mid-extraction is now a normal event with a defined response
  (extend the contract, note it in the ADR log) rather than an excuse to leak a project fact.
- The setup skill (increment 6.1) inherits its specification: fill these four files, detecting
  before asking.
- Cost: every slot reference is three lines instead of one inline fact, so L0 files get
  somewhat longer and more verbose than the originals they came from. Accepted — legibility
  for the human reviewing a de-projected file matters more than terseness, and Checkpoint B
  exists to confirm that trade is landing well on a real file.
