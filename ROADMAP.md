# Roadmap

Now / Next / Later for the toolkit itself. Consuming projects keep their own; this one is about
what Cantrip ships.

An item earns a place here when it is a decision or a piece of work someone would otherwise
rediscover. Loose ends that only matter inside one increment stay in that increment's spec.

---

## Now

**Slimming this file.** The roadmap had grown into a lab notebook: 508 lines, of which about 120
were historical record duplicated from `CHANGELOG.md` and ADR 0015, and most open entries carried
their own measurement history inline rather than a current figure and a decision. The work is the
four factual corrections, moving the measurement history to `docs/measurements.md`, and a gate that
holds a stated spell count to the one contract check 16 computes.

**Of what Next holds, the pack-authoring meta-skill is the highest-leverage item** — every other
pack-related cost is paid per pack until it exists. Closed increments are in `CHANGELOG.md` and
under `_work/shipped/`; this section names what is open, not what is done.

---

## Next

**Two questions the guides increment left open**, both stated the same way in
`_work/shipped/editor-facing-guides/spec.md` under *Still open*, and repeated here because neither belongs
to the increment that raised them. The spec's bullet on the second one carried a half that has
since closed — whether the report shape survived the inventory determiner, which it did — and was
corrected on 2026-08-29 rather than left to disagree with this entry. That bullet moved again on
2026-09-01 when the second caller arrived; **this entry is the current statement of it**, and the
archived spec is a snapshot of the question as it was raised.

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
  stayed open was whether a second caller would ever arrive, and the planned test spell was the named
  candidate. **It arrived on 2026-09-01**: `/testify audit` sweeps every capability doc, ranks them by
  how much of each nothing proves, and reports drift in both directions. So the question is no longer
  whether a second caller exists — it is whether the two are the same shape. That increment
  **deliberately did not answer it**, writing its report independently so convergence could be judged
  from two real shapes rather than predicted from one; both now exist, and the next move is to read
  them side by side and either extract the common section to core or record that they only looked
  alike. **Answer this and the scaffolding reference's size entry in Later falls out of it** — the
  same section is the seam both questions point at.

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
  they do not the deferral was right. Recorded in `_work/shipped/styleguide/spec.md` and in the spell.

**Two questions the coverage spell leaves open**, both about the Test Coverage table rather than
about `/testify`, which is why neither belongs to the increment that raised them. The rest of that
increment's *Open Questions* stay in `_work/shipped/testify/spec.md`, because they only matter to
somebody working on that spell.

- **Five statuses may mean the Status column is doing two jobs.** A row now reads `Covered`, `Test
  failing`, `Not covered`, `Not covered (code-derived)`, or `Ruled out — <reason>`, which encodes two
  independent facts in one cell: whether a test exists, and what its last run established. Split into
  two columns and `Test failing` falls out of the pair rather than needing a name of its own —
  [ADR 0016](adr/0016-coverage-status-names-an-observation.md) records why it got one anyway. **Not
  done in that increment** because it rewrites every coverage table in every consuming project, which
  is a migration rather than an edit. Worth deciding **before a sixth status is proposed**, because
  each one added makes the split more expensive and the column harder to read.
- **Nothing re-reads a coverage row, so every status is only as good as the last time something
  looked.** Three shapes of the same question:
    - A `Test failing` row **understates** once the work that would make it pass lands and nobody
      re-runs it.
    - A `Covered` row **overstates** the moment its test starts failing.
    - A `Ruled out` reason — "this toolkit ships no rendering layer" — stops being true the day
      something owns the render layer, and skipping that row forever is the failure mode the status
      was introduced to create.

  `/plan`'s final step and a re-run of `/testify` are both candidates
  for noticing, and neither is obliged. **The overstating direction costs more**, and whatever closes
  it has to answer the question audit mode deliberately dodged: **who may run a project's tests, and
  when.** A sweep that quietly executed a suite would be neither cheap nor read-only, and on a project
  whose tests create and delete real content it would mutate what it reports on. Cheaper partial
  answers exist and are not decided either — the audit reporting `Ruled out` rows separately as claims
  to re-check, or a reason carrying a date so it goes stale visibly.

**One question the runbook increment leaves open, and the pilot answers it.**
[ADR 0017](adr/0017-when-a-gap-earns-a-runbook.md) deferred rather than rejected a **first-run branch
in `/guide`** that would create a guides section's four document types under a scoped approval. The
precedent exists — `/styleguide` already creates element types and a palette that way — and the
`## Editor guides` fallback now names the state that would trigger it.

- **The case for it is correctness, not time.** Building four document types by hand is twenty
  minutes once per project, which would not pay for a branch in the largest spell in the pack. What
  would pay for it is that the all-optional rule and the exact aliases are the two things people get
  wrong, and **neither fails at the point of the mistake** — a mandatory `guideSource` surfaces weeks
  later as a run that dies halfway. That is ADR 0017's part 3, and a machine cannot forget to untick
  *mandatory*.
- **The shape to build is the narrow one: create the schema, and leave the node and the key to a
  person.** Recording the key is what would make this dangerous, because **the absent key is
  currently the guard** — it is what stops `/guide` writing anything, and it is load-bearing well
  beyond its stated job. A branch that records it hands back a section whose templates are still
  empty, and guides written into it render blank while the audit counts them as present: a stop
  traded for a silent failure, which is the trade the ADR exists to refuse. Leaving the key to a
  person keeps it as the *I have seen this render* signal. A precondition checking that templates are
  non-empty was considered and is worse — non-empty is not the property being guarded, and a check
  that cannot express its property is [ADR 0006](adr/0006-no-unguarded-preconditions.md)'s lesson
  repeating.
- **It cannot live in `SKILL.md`.** `/guide` was measured at 564 lines when it was the largest unit
  in any pack, and an `--audit` cast already loads the whole file to use just under half of it. A
  branch that fires **once in a project's lifetime** is dead weight on every later cast, and the
  script cannot hold it either — `scripts/guide.py` has no CMS connection and no approval to act on,
  by design. So it belongs in an asset the spell loads only on that branch, which is the same
  reasoning that kept the setup sequence out of the reference.
- **What it does not fix.** A project with no blocks and no page templates has nothing for guide
  templates to be copied from, so it would create four document types and land on the same stop one
  step later. Greenfield-with-no-exemplars stays a stop, correctly.
- **The pilot answers whether to build it at all, and the question is specific: did anyone mark a
  field mandatory?** If nobody does — if the runbook carries people through Phase 1 without incident
  — the silent-failure case evaporates and this stays deferred permanently. **Expect the runbook to
  shrink if it ships**: automating the schema retires ADR 0017's part 2 for that half, so two-thirds
  of `docs/runbooks/umbraco-17-guides-section.md` would stop earning its place. That is the test
  working, not a cost.

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

**An installed project receives no human-facing documentation at all.** Installs are subpath-scoped,
so only `skills/` ships — `README.md`, `docs/`, `adr/`, and `LICENSE` never reach a consumer
(`docs/layout.md` states this, and it is correct). What a consumer gets is `SKILL.md` per unit plus
the assets those units load. Those files carry roughly 7,800 lines of real detail, but they are
written in second person to an agent, and nothing in an installed project tells a person they are
readable at all.

**The 2026-09-01 README split narrowed this by exactly nothing**, which is worth stating plainly: it
moved prose from one unshipped file to another and linked the catalogue to the units. That helps
somebody evaluating the toolkit on GitHub and does nothing for somebody who already installed it —
the population that has committed to it. Options, none costed: ship a short per-unit README beside
each `SKILL.md` (they would vendor, but 32 hand-written files is the maintenance the split was trying
to avoid); ship one orientation file per pack; have `/setup` write a pointer into the consuming
project; or decide the installed surface is deliberately agent-only and say so where a consumer will
read it. **Deciding is cheap and is the actual blocker** — the fix follows from whichever answer.

**Narrowed 2026-09-02, not closed.** [ADR 0017](adr/0017-when-a-gap-earns-a-runbook.md) takes a fifth
option for the *content* question: a human-facing runbook per genuine wall, earned by a three-part
test, rather than a file per unit or per pack. The first one exists
(`docs/runbooks/umbraco-17-guides-section.md`). What stays open is **delivery** — runbooks live outside
`skills/`, so nothing carries them into a consuming project and the pilot copies by hand. The
remaining options are unchanged; the difference is that there is now something to deliver.

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

**Check 10 is narrower than it reads, in two places.** *Exemplar instructions handle having no
exemplar* is the forcing function ADR 0006's principle needs, and its own comment says why it exists:
"a principle without a forcing function gets applied when the author happens to remember." Two
patterns in it under-match, both found and verified while writing `/testify` on 2026-09-01:

- `ABSENCE_PAT` groups `there is no` inside an `if (...)` alternation, so it only matches after a
  literal *if*. A clause reading "**there is no** existing test to be closest to" — the natural way to
  write it — does not satisfy the check, and the instruction it guards is reported as unguarded.
- `EXEMPLAR_PAT` matches `follow it exactly` and not `following it exactly`, so the same instruction
  in a participial sentence is not seen at all. That is the worse of the two: an under-matching
  *trigger* passes silently, where an under-matching *absence clause* at least fails loudly.

Both are a few characters of regex, but they belong to their own increment rather than to whatever
work notices them next: the fix is to a **gate**, so it needs its own negative tests — a bare "there
is no…" clause now accepted, a participial exemplar instruction now caught, and the existing passes
and failures unchanged — and a gate quietly loosened in passing is how a forcing function stops
forcing anything.

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

**Check 1 greps file by file, and it is two thirds of the commit gate.** The scrub check spawns two
or three `grep` processes per scanned file, so its cost tracks file *count* rather than content — one
batched `grep` over the same list finished in under 0.01s. At 936 files the full gate is ≈9.4s and
still growing linearly with every fixture tree an increment ships. Figures, and the projection that
came in 3x low, in [docs/measurements.md](docs/measurements.md#the-commit-gate--scriptscheck-contractsh).

Filed rather than fixed in passing: this is the gate that keeps a public repo scrubbed, and rewriting
how it collects hits deserves its own change with its own negative tests — an exemption still
honored, a planted token still caught in both the `git ls-files` and `find` branches.

**Pack spell counts are ungated.** Contract check 16 holds the core spellbook to a ceiling of ten
and says nothing about packs, so a pack could ship a dozen spells and nothing would notice. Whether
that is deliberate — a pack serves one stack and its spells arrive only with it — or a gap the
ceiling implies, is unasked rather than answered.

**And the census stated in prose is ungated in the other direction.** Check 16 *computes* the count
to enforce the ceiling; nothing holds the number written in `README.md`, `CHANGELOG.md`, or ADR 0010
to what it computes. The `/testify` increment shipped with the README corrected and ADR 0010 left
saying "the workflow set is eight" — caught in review, on a pass whose whole purpose was hunting
stale counts, because the verification grep looked for *"eight workflow spells"* and the ADR says
*"workflow set is eight"*. **A grep for one phrasing of a fact is not a check for the fact.** The
gateable version is check 17's shape applied to a number rather than a vocabulary: read what check 16
computes, and fail if a shipped document states a different figure. Cheap, and it removes a class of
error that has now recurred twice.

**The guide scaffolding reference is the largest unit in any pack, and the seam is known.** 623
lines, 2.6x the next largest reference, and its frontmatter trigger widened with it — a schema-only
task now pays for the audit's report format as well. The seam is `## The audit's report shape`,
roughly 110 lines that document report output rather than schema. **Held rather than split**, because
that section already says it is a candidate for extraction to the technology-agnostic layer, and
splitting it into a second `umbraco-17` unit first means a unit name, two registry entries and a docs
pass — then moving it again. Answer the core-extraction question and this falls out of it; split it
sooner if a consumer reports the load cost first. Sizes in
[docs/measurements.md](docs/measurements.md#the-guide-scaffolding-reference).

**A mode-forked spell serves two modes from one load unit, and the seam is known.** Two instances
now — `/guide` in a pack, `/testify` in core — so this is a question about the shape rather than about
either file: whether a spell that hard-forks on its argument should be two units by rule. An audit
cast of `/guide` loads the whole file to use just under half of it; `/testify` wastes proportionally
less. The seam in both is the mode boundary the file already dispatches on. Sizes in
[docs/measurements.md](docs/measurements.md#mode-forked-spells).

**Held, and two of the three reasons still stand.** *Spent:* the count argument for `/guide` — its
pack reached four spells on 2026-09-01 for unrelated reasons, so splitting would make five rather than
break three. *Standing:* splitting costs a name, two registry entries, and a README and changelog
pass; and the load cost is paid only by someone who cast the spell on purpose, since
`disable-model-invocation: true` means nobody else pays anything.

**The count argument does not transfer to `/testify`, and there it is worse.** A pack has no stated
ceiling; core does — ADR 0010 sets ten and the spellbook stands at nine. Audit mode is a
deliberately-cast, side-effectful action, so it could not ship as a Reference-posture unit: splitting
it means a **tenth workflow spell**, spending the last slot under the ceiling on a mode that already
has a home. Weigh that before the line counts.

**Revisit when either spell's audit mode next grows** — that is the trigger, not the line count on
its own. If a third instance appears, stop revisiting and write the rule.

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

Recorded here so they are not reopened; the reasoning lives in the ADR, not in a second copy of it.
All five are [ADR 0015](adr/0015-what-a-stack-pack-is-and-what-it-owes.md), which carries the worked
example that settled each.

- **How a pack declares the version it targets** — §3
- **Which axis a pack is cut on**, when version is not the thing that makes it wrong — §4
- **How a pack is replaced when its platform moves a major** — §5: a swap, never a merge
- **Where portable criteria end and stack-specific detection recipes begin** — §6, gated by check 14
- **Registering a slot that two packs read** — §7, held by the `shared-slot-two-packs` fixture

---

## Recently shipped

- **2026-09-01** — **The coverage spell, `/testify`.** The ninth workflow spell and the first
  QA-owned verb: it reads a capability doc's Test Coverage table as a work queue, reports what
  nothing proves, then writes and runs tests only for the rows a person approves. A pair with
  `/feature` over one document rather than a new stage in the chain. Full detail in `CHANGELOG.md`;
  the decision it rests on is [ADR 0016](adr/0016-coverage-status-names-an-observation.md).

- **2026-09-01** — **The token-reading styleguide, `/styleguide`.** A guide page whose showcase
  sections carry token *names*, so what an editor sees follows the project's stylesheet and stays
  current with no regeneration. Story 1 of the guides discovery's four, and the second caller of the
  guides scaffolding. Full detail in `CHANGELOG.md`.

- **2026-08-29** — **Editor-facing guides, `/guide`.** One guide page per component, written from
  the schema the component already declares, plus an audit of which components have none. The
  deterministic half is a script; the prose half is the model's. Full detail in `CHANGELOG.md`.

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
