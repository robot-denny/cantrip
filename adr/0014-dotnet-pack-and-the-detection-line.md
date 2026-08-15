# 0014. The `dotnet` pack, and the detection line it needed

**Status:** Accepted
**Date:** 2026-08-14

## Context

Two decisions, recorded together because the second exists only to serve the first.

The toolkit shipped no per-file guidance for the language most of the work it reviews is written
in. Core owns what makes something a defect at all — an error passed on with its origin lost, a log
call that folds its values into the message, an unvalidated input. The `umbraco-17` pack owns the
CMS. Between them sat C# and .NET: naming by code element, async and cancellation discipline,
structured logging, serialization, nullability, the modern syntax that is now the default. Nothing
named any of it, so a reviewer either invented the rule on the spot or let it pass, and an authoring
agent matched whatever the file it opened happened to do.

That raised the first question — where such content belongs, given that a pack already existed for
a technology built *on* .NET.

Writing it raised the second. Much of what per-file C# guidance would otherwise assert is not a
platform fact at all but a choice the project already made, and in a great many repositories has
already written down in `.editorconfig`. The contract had a way to *use* that answer once it sat in
a slot, and no way to *put* it there short of asking a human a question their repository could have
answered.

## Decision

### 1. `dotnet` is a pack in its own right, a peer of `umbraco-17`

Two model-invoked reference units, no spells: `dotnet-conventions` for authoring and
`dotnet-review-rules` for review.

C# and .NET apply to **every** .NET project, CMS or not, which is the whole of the argument. An
Umbraco project installs both packs and each answers what it owns; a .NET API, worker, or library
installs one and is not asked to carry a CMS.

Per [ADR 0003](0003-how-core-reaches-a-stack-pack.md) this costs core nothing. L0 asks for a *kind*
of guidance and lets skill discovery route it, so no L0 file names either pack. **This is the first
real test of that mechanism.** 0003 predicted a future pack would require no change to any L0 file;
adding this one required none, for exactly the stated reason.

Two units rather than one because they load at different moments — authoring while a file is being
written, review while a diff is being read — and a description engineered to fire on both is worse
at each than two engineered to fire on one. The trade is paid in context: two units means two
descriptions resident in every request rather than one, so the split buys firing precision with
permanent budget. At this size that is the right way round, but it is a real cost and it scales with
unit count, not with use.

### 2. A slot declaration may carry an optional `**Detect:**` line

It names how the project's own answer can be **read out of the repository**: which files to look at,
and what pattern in them constitutes an answer. It sits after the fallback, and it is optional.

The contract's rule 4 — prefer inference over interrogation — had nowhere to act. `**If empty:**`
governs behavior at *use* time, when a spell needs the fact and finds the slot blank. Nothing
governed *configuration* time, so `/setup` had no way to be told that a slot's answer was sitting in
a file three directories down.

**The recipe cannot live in core.** Setup's detection step is an L0 file, and check 8 forbids an L0
file from naming a technology — so core cannot say to read `csharp_style_var_*`, because that is a
technology name. The asymmetry is the mechanism rather than a limitation of it: **the pack owns the
recipe, core owns the instruction to honour one.** Core follows a line it could not have written,
the same way it fills a slot heading whose name it must not know.

## Alternatives considered

**Extend core's `code-reviewer` agent with C# rules.** Rejected twice over. Check 8 forbids
technology names in L0 and the reviewer agents ship as core, so it is not available. And it would
have covered only review — half the need — leaving authoring guidance with nowhere to go.

**Fold the content into the `umbraco-17` pack.** Rejected on three counts. It hides language
guidance from the majority case, since most .NET projects are not CMS projects. It puts
language-lifetime content behind a CMS-version release cadence — the `Async` suffix convention will
outlive several Umbraco majors. And it means a C#-only correction ships as a CMS pack release,
which is a change consumers must reason about for a reason unrelated to why they installed it.

**One combined unit instead of two.** Rejected on load timing, above.

**Leave it as an L2 project skill.** Rejected: every .NET project would then hand-maintain its own
copy of guidance that is true of the platform rather than of any project — which is both the
duplication the toolkit exists to remove and, per [ADR 0001](0001-layer-contract-and-slots.md), a
misfiling. L2 is for facts a project owns.

**Name the pack `csharp`.** Rejected: roughly half the content is platform rather than language —
`ILogger`, `CancellationToken`, `System.Text.Json`, csproj properties, the hosting model. A name
that excluded them would eventually need a second pack for the other half of one subject.

**Extend `**If empty:**` to carry detection rather than adding a line.** Rejected: they answer
different questions, at different times, for different readers. A fallback is read by a spell that
needs the fact *now* and cannot go looking; a recipe is read by the configuration spell, once,
before anyone needs the fact. Merging them would put an instruction in front of every reader who
cannot act on it.

**Put a general detection recipe in core.** Rejected by check 8, and rightly. Every recipe worth
following names files and configuration keys, and those are technology names by construction.

**Add a gate check that enforces the detection line.** Rejected: there is nothing to pair it with.
Check 4 refuses a `**Slot:**` with no `**If empty:**` because that combination is broken at use
time. A missing `**Detect:**` breaks nothing — it claims only that nothing is readable, which is the
honest state for a slot recording a decision no repository reveals. Recorded as a risk below rather
than solved with machinery.

## Consequences

- **Adding a pack changed no L0 file to accommodate it.** ADR 0003 paying out, on a pack it did not
  anticipate. The only L0 change in this increment is the detection line, which is a new capability
  rather than an accommodation, and would have been worth having for a pack that never shipped.
- **Two packs can now speak to the same diff, and that is new.** It bit immediately:
  `umbraco-17-review-rules` and `dotnet-review-rules` both stated the outbound-call rule at the same
  generality, so one defect in one file would have drawn two rows in the merged report. The CMS pack
  narrowed to its own instance — form submission handlers — and defers the general rule to whatever
  language guidance is installed. **This becomes a standing authoring cost**: a new pack rule needs
  checking against every other pack's, and the duplication is visible only in the merged report,
  which neither pack can see. Same shape as `reviewer-discipline`'s *Where two domains abut*, one
  layer out — that governs two reviewers repeating each other, this governs two packs.
- **`/setup` gained behavior that fires for projects which never adopt this pack.** Treating a
  formatter or editor configuration as authoritative for whatever it encodes is a change to a core
  spell; the pack's recipe narrows a general habit that now exists whether or not any pack is
  installed. That is the correct layering and it is also the widest blast radius in the increment.
- **Installing the pack costs a consuming project context on every request, used or not.** A unit's
  `description` is resident from the moment it is installed; only its body is load-triggered. The two
  descriptions are 593 and 492 characters — about 271 tokens, roughly 10% on top of the 26-unit
  always-on budget of ~2,900 tokens measured on this tree. Small, and worth stating plainly because
  the pack's whole pitch is that it is cheap to install and ignore: ignoring it is cheap, installing
  it is not free.
- **Check 9 folds a following `**Detect:**` line into the fallback text it compares.** Its capture
  runs from `**If empty:**` to the next blank line, so an adjacent detection line lands inside it —
  verified by running check 9's own extraction against the live declaration in `dotnet-conventions`.
  Harmless while a slot has one declarer. A *second* file declaring the same slot would have to
  reproduce the detection wording as well as the fallback wording, or check 9 reports one slot
  carrying two different fallbacks. If that ever bites, the fix is the rule the check exists to
  enforce: one point of authority, with the second file deferring rather than re-declaring.
- **Nothing enforces the detection line, by design.** Its use rests on authoring discipline, like
  ADR 0013's attribution rule. The failure mode is quiet and mild — setup asks a question the
  repository could have answered — which is why it did not earn machinery.
- **A pack with no spells is now a shape the toolkit has.** The README claimed a stack pack adds its
  own spells on top, which this pack makes false; the claim is corrected. It also means the
  deliberate eight-spell census is unthreatened by pack growth, since a reference-only pack costs
  nothing against it.
- **Nothing here reaches an existing project by update.** A pack is a separate manual install, so
  the README is the only channel by which anyone learns this exists. Documenting it is load-bearing
  rather than cosmetic, and the same will be true of every pack after it.
