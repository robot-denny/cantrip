# Roadmap

Now / Next / Later for the toolkit itself. Consuming projects keep their own; this one is about
what Cantrip ships.

An item earns a place here when it is a decision or a piece of work someone would otherwise
rediscover. Loose ends that only matter inside one increment stay in that increment's spec.

---

## Now

**Nothing in flight.** The styleguide increment closed on 2026-09-01 and is recorded under Recently
shipped. The editor-facing guides increment it extends closed on
2026-08-29 and is archived under `_work/shipped/editor-facing-guides/`; the pack-boundary split
closed on 2026-08-17 and is archived under `_work/shipped/pack-boundaries-and-succession/`. Of what
Next now holds, the **pack-authoring meta-skill** is the highest-leverage item, because every other
pack-related cost is paid per pack until it exists.

---

## Next

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

**Two questions the styleguide increment left open**, neither of which belongs to the increment
that raised them.

- **Whether a project's showcase view can report a token it cannot resolve.** A token gets retired
  and the swatch reading it renders blank, which reads as a design decision rather than as a
  reference to something that no longer exists. It is **stated as a constraint in
  `umbraco-17-guide-scaffolding` → *The showcase element types* and enforced nowhere**, because this
  pack ships no markup — the same shape as the index's render-as-text-never-as-markup constraint
  beside it. Its scenario lands uncovered on purpose. What would close it is something that owns the
  render layer, which is the same thing the caching entry in Later is waiting for. Related but
  distinct: the **literal-versus-token drift check** already sitting on
  `_features/editor-guides.md`'s Increments list finds a value written where a token belongs, in
  project code rather than in a showcase view. Neither needs the other.
- **How a page presents a set of themes.** A project with several themes is under-served by a
  showcase that renders one and implies there are no others, and the presentation — one section per
  theme, a switcher, a single representative with the set named alongside — depends on how the
  project themes things. **Deliberately deferred to the generating agent**, which asks and decides
  from the project's own mechanism, because a rule written from the one worked example available
  would be fitted to it. The schema half is settled and needs nothing: a showcase element stores a
  name, so re-theming a region is the project's own CSS re-pointing what that name means. **Revisit
  when more worked examples exist across projects** — if they converge this becomes a rule, and if
  they do not the deferral was right. Recorded in `_work/styleguide/spec.md` and in the spell.

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

**A conformance rule for `design-system-authoring`: an editor-facing stylesheet imports the token
layer, it never mirrors its values.** Raised 2026-08-31 while specifying the styleguide, and noted
here rather than folded into that increment because it applies to every project rather than to the
ones running a styleguide.

The shape is the one that skill already teaches — *name what breaks and when*, not "use tokens".
A CMS commonly loads the rich-text editor's stylesheet into an isolated frame that cannot see the
site's own, so a token declared for the site resolves to nothing there and the values get pasted in
and kept in step by hand. Measured on the demo project: two hardcoded hex values mirroring two
declared tokens, and three comments saying to keep them in sync. **That is a choice, not a
constraint** — a stylesheet that declares or imports the token layer itself reads the tokens
normally — which is exactly what makes it a rule worth stating rather than a limitation to accept.

It pairs with the drift check on `_features/editor-guides.md`'s Increments list: the rule says what
must be true, and that check finds where it is not. Neither needs the other to ship.

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

| | 2026-08-26 | 2026-08-28 | 2026-08-31 |
|---|---|---|---|
| files scanned | 369 | 686 | ≈770 |
| check 1 alone | ≈3.0s | ≈5.4s | ≈6.0s |
| full `check-contract.sh` | ≈5.7s | ≈8.0s | ≈9.1s |
| check 1's share | 53% | ≈67% | ≈66% |

The 08-26 note projected +0.4s to +0.8s for this increment's fixtures. Actual growth over eleven
commits was +2.3s, so the estimate was low by roughly 3x — worth recording as much for the estimate
as for the number, since the fixtures arrived in trees (`.uda`, `.config`, `.cs`, dossier and audit
inputs) rather than one file per case, and file *count* is what this check charges for.

**The 08-31 column is the styleguide increment**, and its shape confirms the diagnosis rather than
adding to it: one step's three fixture cases carried 33 `.uda` files between them and moved the full
gate **+0.39s on their own**, measured by interleaving stashed and unstashed runs so the drift this
machine shows between sessions could not be mistaken for the diff. The share holds at two thirds
because both halves grew together. Nothing here is a new problem — it is the same linear charge on
file count, now with a third point on the line, and the next increment that ships fixture trees will
move it again by about as much.

Filed rather than fixed in passing: this is the gate that keeps a public repo scrubbed, and rewriting
how it collects hits deserves its own change with its own negative tests — an exemption still
honored, a planted token still caught in both the `git ls-files` and `find` branches.

**Pack spell counts are ungated.** Contract check 16 holds the core spellbook to ten workflow spells
and says nothing about packs, so a pack could ship a dozen spells and nothing would notice. Whether
that is deliberate — a pack serves one stack and its spells arrive only with it — or a gap the
ceiling implies, is unasked rather than answered.

**The guide scaffolding reference is the largest unit in any pack, and the seam is known.**
Measured 2026-08-28 at 436 lines / ~28K; **remeasured 2026-09-01 at 623 lines / 44K**, grown by the
styleguide increment's showcase element types and its `## Design tokens` slot. Against
`umbraco-17-feature-backfill` at 242 / 16K that is now 2.6x the next largest reference rather than
1.7x — and the frontmatter trigger widened with the file, so a schema-only task now pays for the
audit's report format, the document types *and* the showcase schema. The proposed seam is
`## The audit's report shape`: it documents report output rather than schema, addresses the spell
rather than someone creating document types, introduces and uses "documentable unit" entirely within
itself, and would be roughly 110 lines alone. **Held rather than split**, because that section already
says it is a candidate for extraction to the technology-agnostic layer, and splitting it into a second
`umbraco-17` unit first means a unit name, two registry entries and a docs pass — then moving it
again. Answer the core-extraction question and this falls out of it; split it sooner if a consumer
reports the load cost first.

**The `/guide` spell serves two modes from one load unit, and the seam is known.** Measured
2026-08-29 at 564 lines / 36K, when it was the largest unit in any pack. **Remeasured 2026-09-01 at
590 / 38K, and no longer the largest either way**: the scaffolding reference below it is 623 and
`/styleguide` is 607. Its own growth was slight; what changed is what sits beside it. Of that, 300 lines are the generate path, 103 are audit mode, and 116 are cross-cutting
(the script's surface, the degradation order, voice and tone, artifact disposition). So a
`/guide --audit` cast loads the whole file to use roughly two fifths of it, and a generate cast
carries audit mode it never reads — the shape [ADR 0001](adr/0001-layer-contract-and-slots.md)
rejected for a combined slot file, recurring at the spell layer. The seam is the mode boundary,
which the file already dispatches on.

**Held on 2026-08-29, deliberately**, and the reasoning is worth more than the measurement — but
**one leg of it has since gone.** The hold cited a fourth spell in a pack ADR 0015 describes as
carrying three; the pack reached four on 2026-09-01 when `/styleguide` shipped, for reasons that had
nothing to do with this file. So splitting `/guide` would now make five rather than break three, and
the count argument is spent. What remains of the hold still stands: splitting means a name, two
registry entries, and a README and changelog pass. Against that, the load cost is paid only by
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

- **2026-09-01** — The token-reading styleguide, story 1 of the guides discovery's four and the
  second caller of `umbraco-17-guide-scaffolding`: `/styleguide` writes one guide page whose showcase
  sections carry token *names*, so the palette and type scale an editor sees follow the project's
  stylesheet with no regeneration. **A design token here is a value that survives to the browser** —
  in practice a CSS custom property — which is the only definition under which the headline claim can
  be true, so a build-time-only palette is refused with a remedy rather than baked into a snapshot
  that would fail the claim while looking like it passes. **It states its precondition rather than
  assuming it**, in two halves always named met or unmet — a palette a rendered page can read, and an
  existing view to take conventions from — making it the one spell in the pack that stops on a
  project that is otherwise perfectly fine. That sharpness is deliberate: a styleguide scaffolded at
  project setup makes a color-swatch view the exemplar every real block is later copied from. Four
  states stop a run and none leaves a partial one. Ships the showcase element types and the new
  `stack.md → ## Design tokens` slot in the scaffolding reference, and `--exclude-palette` on both
  `guide.py`'s `inventory` and its `audit`, because the two derive their counts separately and a flag
  wired into one leaves the other reporting a project's showcases as undocumented forever. Adopting a
  project's own hand-built styleguide page is a **deliberate non-goal** — it would mean retyping a
  document. **One known limitation**: the exemplar half counts views broadly, so a page template or a
  partial satisfies it and a project with templates and no blocks can pass with nothing to copy; the
  spell reads `exemplarViews.examples` and says so. A `styleguide-check` suite of 10 cases plus 3 new
  `guide-check` cases, taking the harness to 110 across three suites (`_work/styleguide/spec.md`,
  `_features/editor-guides.md`)
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
