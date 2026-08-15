# 0015. What a stack pack is, and what it owes

**Status:** Accepted
**Date:** 2026-08-15

## Context

Two packs now exist and they do not look alike. `umbraco-17` ships three spells and five
references; `dotnet` ships two references and nothing else. Neither shape is wrong, and nothing
in the repository says so — a third author reading both would reasonably conclude one of them is
incomplete.

ADR 0003 settled *how* core reaches a pack without naming one. It never said **why a pack is
worth having**, which turns out to be the question that decides what belongs in one. Without it,
"should this be core, a pack, or a project skill?" is answered by taste.

The `dotnet` pack was built across six steps, and most of what it learned came from review rather
than from design: defer instead of duplicating, hedge every cross-reference, keep to the shared
severity scale, register the units or the checker will not see them. Each was found by a reviewer
noticing, not by an author following anything. More packs are anticipated — an Episerver pack, a
front-end or React pack, Python — and each would rediscover the same rules at the same cost.

## Decision

### 1. A pack exists to pin what a model would otherwise improvise

An agent's knowledge of a platform is whatever it absorbed in training, which is many versions at
once and attributed to none of them. The failure that produces is specific and familiar: guidance
that blends releases, code that hits a roadblock and gets backtracked, or worse, code that ships
looking idiomatic while violating the practices of the version actually in use.

**A pack's job is to make the version and its conventions explicit, so the agent stops
interpolating.** That is why a pack earns its place even when the model already "knows" the
technology — knowing it in general is precisely the problem.

The second half of the rationale is why packs are opt-in rather than core: a spell like
`/check-uda` is a superpower in one repository and clutter in every other. Stack-specific units
cost context on every request in a project that will never use them, so a project takes only the
packs its stack justifies.

### 2. A pack has no required shape

The minimum is one unit with a description engineered to trigger on the work it covers. Spells are
optional; a pack of pure references is a complete pack. So is a pack of one unit.

Shape follows the technology. A CMS with its own schema artifacts and editing surfaces earns
spells because there are repeatable operations to name. A language and platform mostly earns
references, because the work is writing and reviewing code that already has a home.

### 3. A pack covers one major version where majors break, and annotates where they add

The test is whether a project on an older major would get **correct** guidance from the pack:

- **No — a pack per major.** Framework majors typically break. The alias traps, API shapes and
  schema behavior that make a CMS pack worth having are facts about one release; the same pack
  pointed at an earlier major does not merely omit things, it misleads. `umbraco-17` carries its
  version in the pack name for this reason, and an `umbraco-13` would be a separate pack rather
  than a branch inside it.
- **Yes — one pack, versions annotated per feature.** Language majors typically add. A project on
  C# 9 reading the `dotnet` pack gets correct guidance provided each newer form says when it
  arrived, which is why that pack has no version in its name and tags features instead.

Both are the same underlying obligation — **make the version explicit so the agent stops
interpolating** — and only the mechanism differs. Getting it backwards is the failure worth
avoiding: a versionless pack over a breaking platform silently blends releases, which is the exact
problem packs exist to solve.

### 4. What every pack owes

These are the rules the `dotnet` increment discovered by review. They are stated here so the next
pack inherits them instead:

- **Assert what the platform decided; name what the project decides without answering it.** A
  default the platform ships is worth asserting. A choice reasonable teams differ on is named as
  the project's, with its trade-off and no verdict.
- **Defer rather than duplicate — against core and against other packs.** Core names what makes
  something a defect; a pack supplies the form that defect takes in its technology, and cites
  rather than re-argues. Where two packs can claim one rule, the more specific statement wins and
  the other stays silent. A rule held twice reaches the reader twice, and neither holder can see
  it — the duplication exists only in the merged report.
- **Hedge every cross-reference with "where installed".** A pack cannot assume its sibling is
  present, and a deferral to something absent is a silent loss of guidance.
- **Use the shared severity scale.** A pack emitting its own levels cannot be merged into one
  ranked report.
- **Never contradict core.** A pack rule that tells a reviewer to do what core forbids is worse
  than a missing rule, because it is followed.
- **Stay mutually anonymous.** A pack describes the *kind* of guidance it defers to, never another
  pack's filename — the same discipline ADR 0003 imposes on core, applied sideways.
- **Register the units.** `ROSTER_PACK`, and `PACK_SLOTS` for any slot the pack declares. An
  unregistered unit installs and verifies as though absent; contract check 13 now catches it.

## Alternatives considered

**Fold language guidance into the framework pack that uses it** — C# inside `umbraco-17`. Rejected:
it hides language content from every non-CMS project, puts language-lifetime material on a
CMS-version release cadence, and makes a C#-only fix ship as a CMS release.

**Require a fixed shape — every pack has spells, references, and starter facts.** Rejected: it
would have forced `dotnet` to invent spells it does not need. Uniformity here buys nothing and
costs content nobody wanted to write.

**Put stack guidance in core behind a detection check** — core notices the stack and adapts.
Rejected: L0 may name no technology, and a core that accumulates a branch per stack is the thing
the layer contract exists to prevent.

**A registry file declaring each pack's shape and version.** Rejected for the reason ADR 0003
rejected its cousin: machinery duplicating what descriptions and rosters already do, plus one more
thing for the update flow to reconcile.

**Leave the rules as review findings and let each pack rediscover them.** Rejected as the status
quo, at a cost this increment measured — six steps, six reviews, and most of the real findings were
about pack discipline rather than the technology being documented.

## Consequences

- **The next pack has something to read.** The rules above are prose rather than gates, so they are
  a standing authoring cost until the mechanical half exists — but a written cost beats an
  undiscovered one.
- **Several of these rules are cheap to enforce and are not enforced.** Four of the `dotnet`
  increment's findings were caught by greps run ad hoc: a pack restating core's reasoning, naming a
  sibling's path, duplicating its own contested list, drifting off the severity scale. Turning those
  into checks scales to any number of packs at no marginal cost, and is roadmapped rather than done.
- **Packs per major will duplicate across versions, and nothing mitigates that yet.** An
  `umbraco-13` alongside `umbraco-17` would restate whatever the two releases share, and the
  duplication has no home to be factored into — a shared unit would have to belong to one of them or
  to core, and core may name no technology. That cost is accepted deliberately: an agent blending two
  majors is worse than a maintainer updating two files, and the blending is invisible while the
  duplication is not.
- **`dotnet` has no version in its name, and that will need revisiting if .NET ever breaks.** The
  annotate-per-feature form holds only while majors add. A genuinely breaking release would move it
  into the other branch of the test, and the pack would need splitting rather than tagging.
- **Content evals remain unsettled.** The `dotnet` pack ships eight cases describing what a review
  of a planted defect should produce, and nothing runs them. They are most valuable while authoring
  a pack rather than as regression protection, which suggests they belong to a pack-authoring tool
  rather than to a test harness — but that follows the tool, and the tool does not exist yet.
- **A pack can now be argued about on grounds other than taste.** "Does this pin something the model
  otherwise improvises, and is it useless outside its stack?" is a question with an answer. That
  makes it possible to decline a proposed pack, which nothing before this made possible.
