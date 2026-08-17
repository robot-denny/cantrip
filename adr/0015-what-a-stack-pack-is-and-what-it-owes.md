# 0015. What a stack pack is, and what it owes

**Status:** Accepted
**Date:** 2026-08-15 — amended 2026-08-17

> **Amended, not superseded.** Splitting `umbraco-17` into three packs exercised this record and
> found four rules missing rather than wrong: a pack can be incorrect for a project by **variant**
> as well as by version (§4), a pack is **replaced** rather than merged when a platform moves on
> (§5), portable criteria and stack-specific detection recipes **split at the grep** (§6), and every
> reader of a shared slot must be registered (§7). Sections 1–3 stand exactly as written. Nothing
> here reverses a claim, so this is an amendment; had it reversed one, the convention in
> [adr/README.md](README.md) would require a new record instead.

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

### 4. A pack can be wrong for a project by variant, not only by version

§3's test varies the project's *version*. Ask it a second time with the version held fixed:

> **Would a project on this exact major, but a different host or a different licensed product, get
> correct guidance from the pack?**

If the answer is no, the difference is a **variant axis**, and the content that depends on it owes
its own pack for the same reason a breaking major does.

The worked example is Umbraco Deploy. `/check-uda` and the Deploy artifact facts are correct on
Umbraco 17 *only if* the project uses Deploy. A self-hosted install without it has no artifact
directory to read, so the guidance does not merely fail to apply — it names files the project does
not have and prescribes a remediation path it cannot take. Both units therefore ship in
`umbraco-cloud` rather than in the CMS pack.

Two properties distinguish a variant axis from the version axis, and both change what the resulting
pack looks like:

- **It is orthogonal to version.** Deploy's behavior spans CMS majors, so a pack cut on it takes
  §3's *majors add* branch: versionless, annotating per feature where a release changed something.
  A variant axis and a version axis can therefore cut the same body of content in different
  directions, which is why one platform can justify two packs.
- **It is not a question about the host.** Deploy is licensed standalone for on-premise, so "does
  this project use Deploy?" and "is this project on Cloud?" have different answers. **Write the
  pack's description about the product the content is about, not about the place the product is
  usually found** — a description scoped to the host silently excludes paying licensees who are not
  on it. The pack directory keeps the host-shaped name because that is where a reader looks first;
  the description is what decides whether the model offers the guidance, and it is the description
  that must be about Deploy.

**Where the line falls.** Not every optional dependency is a variant axis. The discriminator is
whether a project on the other side of the difference would be *misled* or merely *uninterested*.
An unused unit costs context, which §1 already accepts as the price of installing a pack. A unit
that describes a mechanism the project does not have costs a wrong action, and that is what earns a
separate pack.

### 5. A pack is replaced, never merged, and the names decide whether that is cheap

The succession question is what happens to a project when its platform moves a major. The answer is
a swap — uninstall the old pack, install the new one, leave every other pack alone — and four rules
make that swap mechanical rather than a migration:

- **A version-pinned pack carries its major in the pack name.** The test: *reading the pack
  directory name alone, can you tell which major it pins?* `umbraco-17` passes. If a pack fails it,
  either the name is wrong or the pack belongs in §3's annotate-per-feature branch and should say
  so. This is the rule the existing name already satisfied, which is why nothing was renamed when it
  was written down.
- **References carry the version in their name; spells do not.** A reference is model-invoked, so
  its name is internal plumbing — version-prefixing costs a reader nothing and makes the pinned
  major visible everywhere the unit is cited. A spell name is typed by a person and is repeated in
  project docs, scripts, and habit. The test: *after a hypothetical major upgrade, which of this
  pack's names would a human have to retype?* Those names may not carry a version. `/block` is
  still `/block` on the next major.
- **One major of a platform is installed at a time.** Two packs pinning different majors of the same
  platform are not installed together, which is what makes the bare spell names safe: the collision
  that would otherwise force `/block-17` cannot arise. The reasoning is that a migration is not one
  codebase holding two majors — it is a new codebase on the new major that *references* the old one,
  each with its own install and its own packs. The test: *would this pack still be correct if a pack
  pinning a different major of the same platform were installed beside it?* If the honest answer is
  that the two would contradict each other, the constraint is doing load-bearing work and the pack may
  rely on it — but it must not also assume both can be present.
- **An upgrade must touch exactly one pack.** The test that tells you the boundaries were cut on the
  right axes: *if moving a major forces a change in more than one pack, either the packs are cut on
  the wrong axis, or one of them holds version-bound content it should not.*

Worked through, a project on `umbraco-17` plus `umbraco-cloud` moving to Umbraco 18 replaces the CMS
pack with `umbraco-18`; the Cloud pack is untouched, because Deploy's axis is not version; the
reference names change with the pack and no human notices, because nobody types them; `/block` and
`/check-uda` are cast by the same names as before; and the L2 slots are unaffected, because they
hold project facts and a project's paths did not change when its CMS did.

### 6. Portable criteria and stack-specific recipes split at the grep

A unit may hold judgement that outlives its stack. The audit references are the case: what a
lifecycle stage is, which categories of documentation exist, what resilience means, and how a score
is anchored are claims about codebases rather than about a platform. Those files are **seam files** —
they sit in a pack but are written to L0's no-technology standard, so promoting them to core later is
a `git mv` and a roster edit rather than a rewrite.

Applying that standard to a *whole* reference is where it breaks, and the rule that resolves it is:

> **A judgement criterion is portable and stays in the seam file. A detection recipe is inherently
> stack-specific and moves to the pack-side file. The test for any one sentence: would it still say
> something true if read against a codebase in another language?**

A criterion survives that reading. A grep pattern does not, because **a search that names no
technology matches everything** — sanitizing one logging search from `Serilog\|UseSerilog\|ILogger<`
down to `logger\|logging` took a real repository from 8 hits to 25, which is not a portable signal,
it is noise. The recipe belongs where naming the technology is allowed; the criterion it serves stays
where the judgement is.

Two constraints follow:

- **A seam file may not name the pack-side file it pairs with**, because the filename itself
  contains the technology. It describes the *kind* of file, and the unit's own guide does the
  routing — the mutual anonymity §7 imposes between packs, applied between two files inside one
  unit.
- **The split needs a gate or it closes silently.** One CMS-specific scoring anchor is all it takes
  for four long references to stop being movable, and noticing it costs a reviewer four full reads.
  Contract check 14 holds the four files by basename, so it follows them through the move it exists
  to protect, and reports a named file that has gone missing rather than passing on its absence.
  It earned its keep immediately: the pass that moved the recipes out wrote the pack-side filename
  into a seam file, and the gate failed on it before review saw it.

### 7. What every pack owes

These are the rules the `dotnet` increment discovered by review, plus one the pack split found in a
shell loop. They are stated here so the next pack inherits them instead:

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
- **Register every reader of a slot, and dedup the registration on `file|heading`.** Splitting a
  pack produced the first slot with readers in two packs — `.agents/config/paths.md → ## Umbraco` is
  read by a CMS planning unit and by the Deploy drift check — and both halves of that sentence are
  load-bearing, because getting either wrong produced a bug:
  - Registration is what makes the checker survey a slot at all, and it is conditional on the
    *registered* reader being installed. A slot registered for one of its two readers is never
    surveyed in a project that installed only the other, so the project is told nothing about a slot
    the unit it did install depends on.
  - The survey appends one entry per reader, so registering the second reader without a dedup counts
    the slot twice and reports a total that is wrong rather than incomplete — a worse failure than
    the gap it was fixing, because a wrong total looks authoritative.

  The test: for each slot the pack declares, grep every unit for the declaration and count the
  readers. The registration must have one entry per reader, and the survey must still print one line
  per slot. The `shared-slot-two-packs` fixture holds both halves.

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

The alternatives below were considered when §§4–7 were added.

**Rename `umbraco-17` so the naming rule arrives with a demonstration.** Rejected: the pack name is
in the install command and in the path a consumer's lockfile pins, so a rename breaks every existing
install for a cosmetic gain. §5's rule is instead phrased so the existing name already complies,
which is a stronger position — the rule was derived from a name that was right rather than imposed on
one that was wrong.

**Scope the Deploy pack's description to Umbraco Cloud**, matching its directory name. Rejected for
the reason §4 records: Deploy is licensed standalone for on-premise, so a Cloud-scoped description
would refuse to fire for a project that has the artifacts, the drift, and the licence. The directory
name stays host-shaped because that is where a reader looks; the description is written about the
product.

**Version the spell names too** — `/block-17`, `/umbraco-edit-17`. Rejected: it makes a major upgrade
a find-and-replace across the consuming project's docs, scripts, and habits, and buys nothing, since
§5's one-major-at-a-time constraint means the names it would disambiguate never coexist.

**Support two majors of one platform installed side by side.** Rejected: it is what would force the
versioned spell names above, it would put a version into slot headings as well, and the case it
serves does not occur — a migration is a new codebase referencing the old one, not one codebase
holding both.

**Promote the seam-cut audit references to core now** rather than holding them to L0's standard in
place. Rejected: L0 may name no technology, so the detection recipes would have to be deleted rather
than relocated, and the core-asks-a-pack contract of ADR 0003 has no form yet for an audit that needs
a stack's signals. Holding the four files to the rule where they sit gets the option without paying
for it.

**Exempt the detection recipes from the gate instead of moving them.** Rejected: the exemption
mechanism is per-pattern with a stated reason, and a file whose greps are all exempted is not
portable — it is merely unchecked, which is worse, because it reads as if it passed.

**A separate ADR for succession rather than an amendment here.** Rejected: §5 is the same question
§3 asks, carried one step forward, and splitting them would leave the version test in one record and
its variant twin in another. Nothing in §§4–7 reverses a claim in §§1–3, which is the line the ADR
convention draws between amending and superseding.

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

Added with §§4–7:

- **Three packs where there was one, and an Umbraco Cloud project installs all three.** The install
  list grows once per axis a platform is cut on. That is the intended trade — a Deploy-only project
  and a CMS-only project each take exactly what applies — but it is paid by every project that wants
  the whole set, and there is no meta-package.
- **A unit that changes packs breaks a path an existing install pinned.** A lockfile naming
  `skills/umbraco-17/reference/architecture-audit/SKILL.md` now names nothing, and neither the
  installer nor `/update-toolkit` detects a move as distinct from a deletion. The remedy is a manual
  reinstall from the new pack, and the roadmap carries it.
- **Both boundary tests are applied by hand.** §3's version test and §4's variant test classify units
  by *subject*, and nothing mechanizes that. This increment tried two proxies and both misreported —
  a spell that names no version while depending on an API introduced at v14 reads as versionless by
  either measure. A gate here would need to understand what a unit is about, so the honest position
  is a written test and a human applying it.
- **§6's split is protected for exactly four files, by name.** A fifth portable reference gets no
  protection until someone adds it to check 14's list, which is hand-maintained — the same shape as
  checks 11 and 13, and the same failure waiting in it.
