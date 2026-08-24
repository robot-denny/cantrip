# Roadmap

Now / Next / Later for the toolkit itself. Consuming projects keep their own; this one is about
what Cantrip ships.

An item earns a place here when it is a decision or a piece of work someone would otherwise
rediscover. Loose ends that only matter inside one increment stay in that increment's spec.

---

## Now

**Nothing in flight.** The pack-boundary split closed on 2026-08-17 and is archived under
`_work/shipped/pack-boundaries-and-succession/`. Next opens with the uSync rung, which is both the
smallest item there and the one the guides work depends on.

---

## Next

**Schema extraction has one rung missing.** `umbraco-17-feature-backfill` guards the absence of
`.uda` files and routes straight to MCP against a running instance — but a uSync project serializes
the same tabs, groups, sort order, and compositions to disk, so the guidance sends it to a live API
for something already in the repository. Adding the uSync rung is a paragraph in an existing
reference and is worth doing before anything else reads schema, since everything below inherits the
gap. The two formats carry the same information in different shapes: compositions arrive as aliases
under uSync and as UDIs under Deploy, so whatever reads either should normalize on the alias.

**Editor-facing guides for a CMS project.** A styleguide, a component guide, and per-component
how-to guides are what a client actually receives, and they cost enough per project to be first
against the wall when scope tightens — which is the argument for automating them rather than for
cutting them. The shape that makes them cheap: one extraction producing a structured dossier per
component, two renderings from it (a short entry for the component guide, the full property tables
for the how-to guide), and an inventory audit reconciling what exists in code against what is
documented. The audit is the half that survives contact with a real project — on a new site the
report stays short, and on an existing one its first run is the backlog. Extraction is an adapter
seam rather than a Deploy requirement, per [ADR 0006](adr/0006-no-unguarded-preconditions.md):
`.uda`, uSync, live API, then a degraded read from generated models, with an adapter that finds no
properties failing loudly rather than reporting an empty set — a silent-empty read is what makes an
audit report no drift on a project it could not parse. Which adapter runs is a `stack.md` slot with
a `**Detect:**` recipe ([ADR 0014](adr/0014-dotnet-pack-and-the-detection-line.md)). Property tables
are a deterministic transform and must never depend on a model; only purpose, when-to-use, and
warnings need one, which is what lets the whole thing degrade to files when an AI service is absent.

**A spell for tests.** The gap the spell budget was raised for. A feature doc already carries a Test
Coverage table mapping each scenario to a test file and a status, which is the contract such a spell
would serve: read the scenarios, find what is uncovered, write and run, update the table. That makes
it a pair with `/feature` — both operate on the living doc — rather than a new stage in the chain,
and it would be the first QA-owned verb in the spellbook. Whether it is a ninth spell or a mode on
`/feature` is the open question, and the answer decides whether the count goes to nine or stays at
eight.

**Pack-authoring meta-skill.** The direct parallel to `design-system-authoring`: a model-invoked
reference that fires when someone sets out to add a pack, turning [ADR
0015](adr/0015-what-a-stack-pack-is-and-what-it-owes.md)'s rules into something followed rather than
remembered. This is the highest-leverage item here, because every other pack-related cost is paid
per pack until it exists — and the ADR now carries four more rules than it did, since splitting a
pack surfaced the variant axis, the replacement operation, the criteria-versus-recipes seam, and
shared-slot registration. Two of the boundary tests are applied by hand and cannot be gated, so the
authoring skill is where they get read. It is also where one sentence settles whether a pack may be
cut on an organization's own conventions and kept private — a question that costs a sentence there
and would cost an ADR anywhere else.

**A moved unit breaks an install silently.** Renaming `architecture-audit` to `codebase-audit` and
moving it to another pack left every existing lockfile pinning a path that no longer resolves, and
neither the installer nor `/update-toolkit` tells a move apart from a deletion. Today's remedy is a
manual reinstall from the new pack, which nobody is told to run. Worth deciding whether the fix is a
migration note per release, a redirect the checker understands, or an accepted cost of vendoring —
left open in `_work/shipped/pack-boundaries-and-succession/spec.md`.

**Structural gate checks for pack discipline.** Four of the `dotnet` increment's real findings were
caught by greps run by hand — a pack restating core's reasoning instead of citing it, naming a
sibling pack's file path, duplicating its own project-owned list across two units, drifting off the
shared severity scale. Each is deterministic and cheap, and each currently depends on a reviewer
happening to think of it. As checks they run on every commit and cost nothing per additional pack.

**A contributor path for packs.** The intent is that people outside this repository write packs for
the stacks and versions they work in — an `umbraco-13` beside the `umbraco-17`, an Episerver, a
Python. That makes two things load-bearing that are currently optional: the authoring skill above,
and something a contributor can run to check their pack before proposing it. Worth deciding how far
that goes — a template and a checklist, or a conformance script, or an accepted-packs list.

---

## Later

**Resolve the content evals.** `dotnet-review-rules` ships eight cases describing what a review of a
planted defect should produce, and nothing runs them. Their value is highest while authoring a pack
and lowest as regression protection, so the answer probably falls out of the authoring skill above
rather than being a separate piece of work. Until then they are a specification for a test, and the
feature doc says so.

**Pack spell counts are ungated.** Contract check 16 holds the core spellbook to ten workflow spells
and says nothing about packs, so a pack could ship a dozen spells and nothing would notice. Whether
that is deliberate — a pack serves one stack and its spells arrive only with it — or a gap the
ceiling implies, is unasked rather than answered.

**A pack conformance check.** `scripts/check-pack.sh` — could someone outside this repository ship a
pack that works? Only worth building if third-party packs are ever a goal; noted so the question is
asked deliberately rather than answered by drift.

**Backfill the capability docs.** `_features/dotnet-guidance.md` and `_features/code-review.md` are
both thin by design and say so. `/feature`'s from-code mode is the intended remedy. Neither is
urgent; both get less accurate as the units they describe grow.

**An evidence convention.** Two increments have now finished by asking whether their captured
before-and-after artifacts earn a commit, and answered differently — `review-failure-modes` committed
140K, `dotnet-pack` left 364K uncommitted and said why. Whatever the rule turns out to be, the two
should end up consistent. Recorded in `_work/shipped/review-failure-modes/spec.md` with the reasoning
on both sides.

---

## Settled, no work outstanding

- **How a pack declares the version it targets** — [ADR 0015](adr/0015-what-a-stack-pack-is-and-what-it-owes.md)
  §3. One pack per major where majors break, per-feature annotation where they add, decided by
  whether a project on an older major would get *correct* guidance from the pack. `umbraco-17` and
  `dotnet` were both already right; the rule that made them right was not written down.
- **Which axis a pack is cut on** — [ADR 0015](adr/0015-what-a-stack-pack-is-and-what-it-owes.md) §4.
  A pack can be wrong for a project by host or product with the version held fixed, and Deploy
  guidance on a non-Deploy install is the worked example. A pack cut on a product axis is versionless
  and is described for the product rather than for the place the product usually runs.
- **How a pack is replaced when its platform moves a major** —
  [ADR 0015](adr/0015-what-a-stack-pack-is-and-what-it-owes.md) §5. A swap, not a merge: a
  version-pinned pack carries its major in the pack name, references carry the version and spells
  never do, one major of a platform is installed at a time, and an upgrade that touches more than one
  pack means the boundaries were cut wrong. No rename was needed to adopt it — the rule is phrased so
  the name that existed already complied.
- **Where portable criteria end and stack-specific detection recipes begin** —
  [ADR 0015](adr/0015-what-a-stack-pack-is-and-what-it-owes.md) §6, gated by contract check 14. The
  criterion is portable and stays; the grep names a technology by necessity and moves to the pack
  side. Settled empirically, after sanitizing a recipe rather than relocating it cost real signal.
- **Registering a slot that two packs read** — [ADR 0015](adr/0015-what-a-stack-pack-is-and-what-it-owes.md)
  §7. Every reader is registered, and registration dedups on file-plus-heading. Both halves produced
  a real bug before they were written down, and the `shared-slot-two-packs` fixture holds them.

---

## Recently shipped

- **2026-08-24** — The spell budget as a working ceiling of ten rather than a stated aim of 6–8,
carried into `AGENTS.md` and held by contract check 16 ([ADR 0010](adr/0010-skills-not-commands.md),
amended), plus the README corrections that prompted it
- **2026-08-17** — Pack boundaries and succession: one pack holding three subjects became three packs,
  a versionless `umbraco-cloud` for Deploy and the codebase audit into `dotnet`, plus the naming rule
  that lets a future pack replace a current one and a gate holding the audit's portable half portable
  (`_work/shipped/pack-boundaries-and-succession/spec.md`,
  [ADR 0015](adr/0015-what-a-stack-pack-is-and-what-it-owes.md) §§4–7)
- **2026-08-15** — The `dotnet` pack: authoring and review guidance for C#, an optional detection
  line letting a pack tell `/setup` how to read an answer from the repository, and a gated pack
  roster that had drifted to two of eight units
  (`_work/shipped/dotnet-pack/spec.md`, [ADR 0014](adr/0014-dotnet-pack-and-the-detection-line.md))
- **2026-08-13** — Two language-agnostic review failure modes into core, and the domain boundary that
  stops one defect drawing two rows in a merged report
  (`_work/shipped/review-failure-modes/spec.md`)
