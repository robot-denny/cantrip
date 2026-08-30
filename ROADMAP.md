# Roadmap

Now / Next / Later for the toolkit itself. Consuming projects keep their own; this one is about
what Cantrip ships.

An item earns a place here when it is a decision or a piece of work someone would otherwise
rediscover. Loose ends that only matter inside one increment stay in that increment's spec.

---

## Now

**Nothing in flight.** The editor-facing guides increment closed on 2026-08-29 and is archived
under `_work/shipped/editor-facing-guides/`; the pack-boundary split closed on 2026-08-17 and is
archived under `_work/shipped/pack-boundaries-and-succession/`. Of what Next now holds, the **pack-authoring
meta-skill** is the highest-leverage item, because every other pack-related cost is paid per pack
until it exists.

---

## Next

**The styleguide, cut from the guides increment on 2026-08-25 and still owed a spec.** Story 1 of
discovery's four: a page whose showcase sections read the project's design tokens live, so it
reflects current styles without a regeneration. It was the cut line because stories 2–4 share one
dossier and one audit while this one shares only the guide-page scaffolding — and because it is the
only story that has to *invent* rendering rather than copy it. Every other story reads a structure a
typical project already demonstrates; the token-reading swatch blocks have no analogue anywhere in
one.

**The groundwork is done, which is what makes this the cheapest thing in Next.** The guides
increment shipped the guide page type, its containers, the derived index, and the shared
`umbraco-17-guide-scaffolding` reference whose second caller this was always meant to be — so the
styleguide inherits a working section rather than standing one up, and inherits provenance-based
content ownership unchanged.

**Do not re-derive what was already settled.** Five decisions, three drafted scenarios and the
acceptance criterion they proved are carried verbatim in
`_work/shipped/editor-facing-guides/notes/deferred-styleguide.md`, written as carry-forward material
rather than as a spec. The load-bearing ones: it is a **spell, not a reference**, with the case
against it recorded and answered; it **states its design-system precondition** instead of producing
plausible output from nothing; and greenfield refusal matters more here than anywhere else in the
capability, because a styleguide scaffolded at project setup makes a color-swatch view the exemplar
every real block is later copied from. Start its spec from that file.

**A spell for tests.** The gap the spell budget was raised for. A feature doc already carries a Test
Coverage table mapping each scenario to a test file and a status, which is the contract such a spell
would serve: read the scenarios, find what is uncovered, write and run, update the table. That makes
it a pair with `/feature` — both operate on the living doc — rather than a new stage in the chain,
and it would be the first QA-owned verb in the spellbook.

**Decided 2026-08-25: a ninth spell, not a mode on `/feature`.** So the count goes to nine, leaving
one under ADR 0010's ceiling of ten. The decision was forced by an unrelated increment —
`editor-facing-guides` ships an audit that reports documentation gaps, and whether that report shape
belonged in core or in a pack depended on this answer. A separate spell means the two share no
machinery and the gap-report shape stays with its own caller, so that increment keeps its report
shape local while writing it as a self-contained section, extractable later if the shapes converge.

**Two questions the guides increment left open**, both stated the same way in
`_work/shipped/editor-facing-guides/spec.md` under *Still open*, and repeated here because neither belongs
to the increment that raised them. The spec's bullet on the second one carried a half that has
since closed — whether the report shape survived the inventory determiner, which it did — and was
corrected on 2026-08-29 rather than left to disagree with this entry.

- **Which format-version values a schema adapter accepts.** Where a version lives and how refusal
  works are settled and verified in both on-disk formats — one stamps a version per artifact and so
  skips per file, the other declares one per export and so gates the whole read. The **accepted set
  itself** is the open part: the evidence base is three projects, all on one CMS major, two of them
  on one host, which is narrow for a claim about portability. It widens by meeting a project that
  refuses, and the refusal names the version it found, so the cost of being wrong is a report rather
  than a silent misread. Both sets sit in `guidelib/__init__.py`, one place, with a comment recording
  how narrow the evidence is.
- **Whether the audit's report shape belongs in core.** The shape shipped and survived contact with
  the inventory determiner, which was the open half — the determiner's count and rule went into the
  report header, ahead of the findings, so a wrong determiner is visible before a hundred guides are
  proposed. It is written as a self-contained section of `umbraco-17-guide-scaffolding` naming no
  CMS, no serialization format and no file, so extraction is a move rather than a rewrite. What
  stays open is whether a second caller ever arrives: the planned test spell was the candidate, and
  the decision above to make it a separate spell means the two share no machinery. **Answer this and
  the scaffolding reference's size entry in Later falls out of it** — the same section is the seam
  both questions point at.

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
A fifth candidate arrived with the uSync rung: no shipped file should route to a live API for schema
without first naming the on-disk formats. It was not built as a one-off, because the guides work was
about to grow the ladder a fourth rung and would have forced the check to be rewritten — that rung
shipped on 2026-08-29, so the reason for waiting has expired and the check is now buildable against a
settled ladder. Check 9 is not a substitute
for it, and the rung proved so: the first fix was applied to the four gated fallbacks and missed an
ungated prose paragraph eighteen lines from one of them, which review caught and no gate would
have.

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

**Check 1 greps file by file, and it is now two thirds of the commit gate.** The scrub check spawns
two or three `grep` processes per scanned file, unconditionally, so its cost tracks file *count*
rather than content. One batched `grep` over the same list finished in under 0.01s, with per-file
exemption filtering then needed only for files that actually produced a hit, normally none.

Measured twice, and the projection did not survive contact:

| | 2026-08-26 | 2026-08-28 |
|---|---|---|
| files scanned | 369 | 686 |
| check 1 alone | ≈3.0s | ≈5.4s |
| full `check-contract.sh` | ≈5.7s | ≈8.0s |
| check 1's share | 53% | ≈67% |

The 08-26 note projected +0.4s to +0.8s for this increment's fixtures. Actual growth over eleven
commits was +2.3s, so the estimate was low by roughly 3x — worth recording as much for the estimate
as for the number, since the fixtures arrived in trees (`.uda`, `.config`, `.cs`, dossier and audit
inputs) rather than one file per case, and file *count* is what this check charges for.

Filed rather than fixed in passing: this is the gate that keeps a public repo scrubbed, and rewriting
how it collects hits deserves its own change with its own negative tests — an exemption still
honored, a planted token still caught in both the `git ls-files` and `find` branches.

**Pack spell counts are ungated.** Contract check 16 holds the core spellbook to ten workflow spells
and says nothing about packs, so a pack could ship a dozen spells and nothing would notice. Whether
that is deliberate — a pack serves one stack and its spells arrive only with it — or a gap the
ceiling implies, is unasked rather than answered.

**The guide scaffolding reference is the largest unit in any pack, and the seam is known.**
Measured 2026-08-28: 436 lines / ~28K, against `umbraco-17-feature-backfill` at 242 / 16K — 1.7x the
next largest, with a frontmatter trigger broad enough that a schema-only task pays for the audit's
report format and an audit task pays for the document types. The proposed seam is
`## The audit's report shape`: it documents report output rather than schema, addresses the spell
rather than someone creating document types, introduces and uses "documentable unit" entirely within
itself, and would be roughly 110 lines alone. **Held rather than split**, because that section already
says it is a candidate for extraction to the technology-agnostic layer, and splitting it into a second
`umbraco-17` unit first means a unit name, two registry entries and a docs pass — then moving it
again. Answer the core-extraction question and this falls out of it; split it sooner if a consumer
reports the load cost first.

**The `/guide` spell serves two modes from one load unit, and the seam is known.** Measured
2026-08-29 at 564 lines / 36K — the largest unit in any pack, past the guide scaffolding reference
below it. Of that, 300 lines are the generate path, 103 are audit mode, and 116 are cross-cutting
(the script's surface, the degradation order, voice and tone, artifact disposition). So a
`/guide --audit` cast loads the whole file to use roughly two fifths of it, and a generate cast
carries audit mode it never reads — the shape [ADR 0001](adr/0001-layer-contract-and-slots.md)
rejected for a combined slot file, recurring at the spell layer. The seam is the mode boundary,
which the file already dispatches on.

**Held on 2026-08-29, deliberately**, and the reasoning is worth more than the measurement. A spell
is a unit: splitting means a name, two registry entries, a README and changelog pass, and a fourth
spell in a pack ADR 0015 describes as carrying three. Against that, the load cost is paid only by
someone who cast `/guide` on purpose — `disable-model-invocation: true` means nobody else pays
anything. And the 116 cross-cutting lines have no clean home: duplicating them is debt this repo
already tracks, and hoisting them into the scaffolding reference grows the file directly below this
entry to roughly 490 lines, trading one outlier for a worse one. **Revisit when audit mode next
grows**, which is the trigger that would tip it — not the line count on its own.

**Nothing tells a project to cache a derived guides index.** `umbraco-17-review-rules` already treats
a stable, expensive, frequently-rendered listing with no caching as a finding in its own right, and a
guides index derived at render time is exactly that shape. The scaffolding reference scopes what the
index may resolve per guide — the fix for the over-fetch — but says nothing about caching, on the
grounds that it ships no template and caching sits a layer below a schema reference. That reasoning
holds only until something ships that owns the render layer; whatever does, owes the caching sentence.

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

- **2026-08-29** — Editor-facing guides: `/guide` writes a guide page per component from the schema
  the component already declares and audits which components have none, with
  `umbraco-17-guide-scaffolding` describing the document types a guides section needs. **The
  extraction adapter this item was waiting on was built here**, rather than consumed from elsewhere:
  the increment decided to ship the deterministic half — extraction, the dossier, the inventory
  determiner, the audit's arithmetic, the change plan — as a Python script inside the spell, leaving
  the spell the prose, the diff-and-approve conversation, and every CMS write. Four rungs, Deploy →
  uSync → live instance → generated models, with a read that finds nothing failing loudly and the
  same component read through two adapters producing the same signature. Property tables never
  depend on a model, which is what lets the whole thing degrade to files. The audit warns and never
  blocks — exit zero whatever it found, `--strict` the only opt-in — and it reports the inventory
  and the rule that produced it before acting on it, because a determiner reading the element-type
  flag rather than the block palettes over-counts by 1.5x to 2.4x on the two projects measured. Two
  new slots, `stack.md → ## Schema serialization` and `conventions.md → ## Editor guides`, both
  declared in the reference and nowhere else. Ships an 80-case test suite, taking the harness to 97
  across two suites (`_work/shipped/editor-facing-guides/spec.md`, `_features/editor-guides.md`)
- **2026-08-24** — The uSync rung in schema extraction: four pack files across `umbraco-17` and
  `umbraco-cloud` stopped sending a uSync project to a live API for schema already in its repository,
  a Deploy-to-uSync field mapping and the normalize-on-the-alias rule landed in
  `umbraco-17-feature-backfill`, and the ladder routes on a matching file so a partial export reports
  itself instead of reading as an empty schema. The uSync element names are marked unverified pending
  a real uSync project
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
