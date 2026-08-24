# Discovery: Pack Boundaries and Succession

_Discovery input for `/spec` — produced by `/explore` on 2026-08-16. Scope: lightweight._

## Problem framing

**Who is affected:** projects adopting the toolkit *from here forward*. Rescuing the existing
project-local forks is explicitly **out of scope** — see "Deliberately excluded" below.

**The problem in one sentence:** pack membership currently reflects how units were authored rather
than what they are about, and nothing describes how one pack replaces another as versions and stacks
move on.

**Observed versus assumed — stated honestly:**

- **Assumed.** The headline pain ("an Umbraco 13 project can't get `check-uda`") has *no observed
  instance*. Both real projects are Umbraco 17 **and** Umbraco Cloud. There is no non-Cloud or
  non-v17 project in play today.
- **Also assumed, and corrected during discovery.** An early claim that mis-scoping *forces* a
  project to install wrong-version facts is false — units install individually. The real cost is
  discovery and coherence, which is smaller.
- **Observed.** `architecture-audit` is installed in both projects and tracked in **neither** —
  absent from the demo site's lockfile (18 entries, zero occurrences), and the second project has
  no lockfile at all. The most-adopted unit of the Umbraco pack has escaped the pack system
  entirely.
- **Observed.** `frontend-design` appears in the demo-site lockfile with **no `skillPath`**.

**Worth keeping from the status quo:** the flat, name-addressed install (`.agents/skills/<name>`).
It is what lets a project take a single unit without its pack, which is how `architecture-audit`
reached both projects. The fix should not make units harder to adopt individually.

## Outcomes sought

Core stays technology-free; packs hold the technology facts; every unit sits where its subject says
it belongs. Success is that **a future pack can replace a current one as a version or stack moves
on** — and that the swap is a documented operation rather than an improvisation.

## Options considered

**A. Three tiers — versionless `umbraco` + `umbraco-cms-17` + `umbraco-cloud`.** Rejected. Splitting
CMS guidance across a versionless and a version-pinned pack was judged complicated to manage over
time, and it forces every future major to decide the split again.

**B. Two packs, `architecture-audit` stays put.** Rejected. Leaves the defect half-fixed and would
have the ADR describe a rule the repo itself breaks.

**C. Self-contained CMS pack per major, plus orthogonal packs (chosen).** `umbraco-cms-<major>` holds
everything version-bound — facts, references, best practices, and the block-building spells.
`umbraco-cloud` holds Deploy and Cloud knowledge. `architecture-audit` leaves the Umbraco pack
entirely.

**Naming, within C.** Version-prefixed reference names (`umbraco-17-planning`) and bare spell names
(`/block`) — which is what the pack already does, undocumented and possibly by accident. It is
correct: references are model-invoked so their names are internal plumbing, and version-prefixing
makes a project's pinned major visible; spells are typed by humans, so `/block` must survive an
upgrade intact.

**`umbraco-cloud` versioning, within C.** Versionless with per-feature annotation — ADR 0015 §3's
"majors add" branch, as `dotnet` already takes. Evidence agrees on both measures: `check-uda`,
`cloud-remediation.md`, and `deploy-schema.md` carry **zero** CMS-major-bound prose, and their
subject matter (Deploy artifact mechanics, Cloud dashboard behavior) is orthogonal to CMS majors.

**`architecture-audit`, within C.** Extract to `skills/dotnet/reference/codebase-audit/`, sanitized,
with the agnostic half **seam-cut**: `lifecycle-stages.md`, `documentation-and-onboarding.md`,
`resilience-and-ops.md`, and `scoring-rubric.md` held to L0's no-technology-names rule from day one,
so promoting them to core later is a move plus a roster edit rather than a rewrite. Language-agnostic
placement in core was rejected *for now* because L0 may name no technology — it would cost
`dotnet-hygiene.md` and every concrete signal in `collect-signals.sh`, and it depends on the
core→pack delegation contract, which does not exist.

## Trade-offs & second-order effects

**The decisive constraint, accepted deliberately:** bare spell names mean **two CMS majors can never
be installed side by side.** Confirmed as fair — a migration means a new codebase on the new version
referencing the old one, each with its own packs, not one codebase holding both.

**What versionless `umbraco-cloud` is worse at:** if Umbraco Deploy ever breaks across a major, the
pack silently blends releases — the exact failure packs exist to prevent. The mitigation is
annotation discipline, which is prose, not a gate.

**Indirect benefit:** the v17→v18 upgrade becomes a worked demonstration of succession — swap
`umbraco-cms-17` for `umbraco-cms-18`, leave `umbraco-cloud` untouched. The version-pinned part
moves, the stable part stays.

**New problem created:** renaming `umbraco-17` → `umbraco-cms-<major>` breaks the install path for
`umbraco-17-demo-site`, whose lockfile pins four units under `skills/umbraco-17/...`.

**Measurement caveat for whoever specs this.** Version-boundness was measured twice and both proxies
were weak. A first pass counting `\b1[0-9]\b` matched bare numbers ("17 entities") and wildly
over-reported. A precise pass under-reports, because `umbraco-edit` shows *zero* version mentions
while its subject — the Management API — only exists from v14. **Subject matter beats mention-count.**
Classify by hand.

## Direction

Option **C**, with all four sub-decisions above confirmed: self-contained `umbraco-cms-<major>`;
versionless `umbraco-cloud`; `architecture-audit` extracted to `dotnet` as a seam-cut
`codebase-audit`; version-prefixed references and bare spells, with one major installed at a time.

## Deliberately excluded

**The fork-to-slot adoption path.** Both projects carry `check-uda` as `.claude/commands/check-uda.md`,
and demo-site declined the Cantrip version to keep project-specific learnings. Inspection showed
Cantrip's version is the *generalized descendant* of demo-site's, with slots already declared for the
project facts the fork hardcodes — `.agents/config/paths.md → ## Umbraco` and
`.agents/config/conventions.md → ## Block palette parity`, the latter carrying a fallback that reads
*"Replace this filter with the configured peer group once the slot is filled."* The learnings were
mostly harvested; nobody filled the config.

This is a real and separate problem, and moving `check-uda` into `umbraco-cloud` does **not** solve
it — the fork stays, and the new pack ships to nobody today. The operation actually needed is closer
to *rebasing a fork onto upstream* than to anything in the current spellbook: map each hardcoded fact
to the slot that already declares it, write them into `.agents/config/`, swap the fork for the
upstream unit, verify nothing was lost. **Not `/retrofit`**, which handles a change that skipped the
spec → plan → implement flow — a different shape. The nearest existing machinery is
`/update-toolkit`'s "reverted local tailoring" detection, which catches the same tension from the
opposite direction: an update whose diff removes content upstream never had.

## Open questions for /spec

1. **Does the rename happen?** `umbraco-17` → `umbraco-cms-17` was requested; the cost is a broken
   install path for demo-site's four pinned units. If yes, the increment owes a migration note.
2. **Where does `deploy-schema.md` land?** It currently sits inside
   `umbraco-17-starter-facts/references/` but its subject is `.uda` mechanics and Cloud dashboard
   behavior. Moving it to `umbraco-cloud` overlaps `check-uda/references/cloud-remediation.md` —
   decide whether they merge.
3. **`block` cross-references `/check-uda`**, which becomes cross-pack. Needs ADR 0015's
   "where installed" hedge.
4. **`umbraco-edit` needs a v14+ annotation** — its subject is version-bound in a way its prose never
   states.
5. **What returns to the CMS pack from `architecture-audit`?** `umbraco-version-agnostic.md` (13
   Umbraco mentions, cross-major by design) and the Umbraco-specific parts of
   `headless-suitability.md` (7).
6. **Does ADR 0015 get amended, or does succession earn its own ADR?** The variant axis (host and
   product, not just version) and the replacement operation are both currently absent.
7. **Does `check-uda` keep its bare name** in a versionless pack, and does the pack's description
   mention Deploy-on-premise? `.uda` files can exist without Cloud — Deploy is also licensed
   standalone — which affects the trigger wording, not the placement.
