# Discovery: Editor-facing guides for a CMS project

_Discovery input for `/spec` — produced by `/explore` on 2026-08-24. Scope: lightweight._

Builds on a prior exploration conversation captured before this session. **That note names the
source repositories directly and must not be committed** — its substance is carried here in
scrubbed form.

## Problem framing

**Who is affected.** Content editors need to know which blocks exist and how to fill them. Team
members and QA need a property-level reference. The client receives all three artifacts as a
deliverable.

**What the current situation costs.** The guides are built by hand, per project, and kept current by
hand. They cost enough that they are first against the wall when scope tightens — which is the
argument for automating them rather than for cutting them.

**Observed, not assumed.** Two working implementations already exist in the source repos: the client
project derives editor-facing HTML from serialized schema; the demo project drives a CMS-writing CLI
with signature-based drift detection. The cost is paid, not hypothetical. What neither has is
portability — both hardcode project-specific paths and markup.

**What is worth keeping.** Humans review and edit the guides in the CMS, and that is not a
workaround. Editor-authored prose, screenshots, and block arrangements are the part that makes a
guide good. Any automation must preserve them, not route around them.

**The problem in one sentence.** Editor-facing guides are valuable, expensive to create and keep
current by hand, and rebuilt from scratch on every project — yet their *content* is derivable from
code while their *rendering* is irreducibly project-specific.

## Outcomes sought

Four stories true when this ships:

1. Automate creation of a **styleguide** assembling sitewide elements (type, color, buttons, lists,
   tables) that reflects current styles accurately.
2. Generate a CMS-editable **component guide** page showing blocks and variations alongside
   rich-text descriptions.
3. Generate **how-to guides** revealing all properties of a block or page type.
4. Run an **audit** finding features that exist in code but are documented by neither.

Success also means: first-pass generation comes from code and humans refine in the CMS; re-running
never silently overwrites human work; and the whole thing works on a project whose front-end stack
Cantrip knows nothing about. The audit report is short on a healthy project, and its first run on an
existing project *is* the backlog.

## The organizing principle

**Skills define what a guide must show. The codebase defines how it renders.** Cantrip ships no
markup, no CSS classes, and no front-end patterns. This was the decisive reframe of the session and
every option below is downstream of it.

## Options considered

### Where the per-project rendering template lives

- **A project-owned L2 skill** in the `design-system-authoring` mould — *rejected.*
- **A `stack.md` slot naming a template path** — *rejected;* indirection that rots.
- **No template artifact at all** — **chosen.** `/block` Step 5 already encodes this: *"find the
  closest existing block and follow it exactly. The existing blocks are the specification; this
  spell is not."* Step 4 solves the BlockList/BlockGrid question the same way — read the data types
  whose `Configuration.blocks[]` is the palette, via serialized schema then MCP.
  **Worse at:** nothing portable to review; correctness depends on the project having exemplars, so
  the greenfield case must be guarded explicitly.

### When each artifact is invoked

- **Scaffold everything at project setup** — *rejected,* and `/block` says why: *"The first block in
  a project defines its conventions whether or not anyone decided to."* Scaffolding the styleguide
  at setup makes a color-swatch view the exemplar every real block is copied from.
- **Split the timing by artifact** — **chosen.** The audit is available from day one (no markup, no
  schema; reports "nothing yet" on greenfield, correctly and cheaply). The how-to guides and
  component guide are self-gating — they need blocks to exist before there is anything to document.
  The styleguide is invoked explicitly and only once a design system exists, with a stated
  precondition rather than a silent one.
  **Worse at:** loses the "it was there from the start so it never rotted" effect; relies on the
  audit's nagging instead.

### Spell shape

- **One spell with four modes** / **four separate spells** — *rejected.*
- **Two spells, cut on the source they read** — **chosen.**
  - `/guide <alias>` — extract the dossier once, write the component-guide entry *and* the how-to
    guide from it. `--audit` is a mode here, over the same inventory.
  - `/styleguide` — scaffold the guide-page doc type, three token-reading element types, and the
    page; delegate view authoring to `/block`.
  **Worse at:** takes the pack from two spells to four, and `/styleguide` is thin — it runs rarely
  and hands the interesting half to `/block`. A reference was the live alternative.

Shared scaffolding (the guide-page doc type, the section grid, the auto-derived TOC) belongs in a
reference both spells cite, not duplicated across them.

### Non-destructive update

- **Regenerate the page** — *rejected;* one unannounced overwrite of hand-written prose and the team
  stops running the tool, which is guides being cut from scope by another road.
- **Declared per-field ownership** — **chosen.** Three kinds:
  - **Machine-owned** — regenerated on signature change, shown as a diff, approved before writing.
  - **Seeded-once** — written at creation, never touched again; reported if stale, never replaced.
  - **Never-touched** — page name, slug, visibility toggles.
  **Worse at:** staleness accumulates exactly where the tool will not fix it. Keeping guides current
  stays partly a human job *by design*.

## Trade-offs & second-order effects

**Rung-relative completeness.** The extraction ladder's rung 4 (generated models) yields aliases and
names but no tabs, groups, required flags, or option lists. Flagging every rung-4 guide as
incomplete makes the report fully red on day one and permanently — the mirror of the silent-empty
failure the fail-loudly rule exists to prevent. So **the dossier records the rung it was read at,
and the audit judges completeness relative to that rung.** Structural thinness is one project-level
header line ("schema is being read from generated models; install uSync or commit Deploy artifacts
for full structure"), not N per-guide findings. Cost: two projects get different reports for the
same underlying gap, so the header must be prominent rather than a footnote.

**Scope discipline on the audit.** The audit's benefit is story 4 — undocumented features. Ranked
against that: *orphaned guides* is the same set difference read backwards and comes free; *machine-
owned drift* is a signature compare whose mechanism already exists and is what makes `/guide`
re-runnable; *seeded-once staleness* collapses into drift, because a changed signature already
signals the example may be stale. **Prose staleness in never-touched fields is a deliberate
non-goal** — detecting "prose names a property that no longer exists" needs either fuzzy matching
(false positives, and a noisy audit gets ignored) or a model call on every guide on every run. The
latter puts a model in the one path that most needs to stay cheap and deterministic, against the
grain of the property-tables-need-no-model split. Additive later if it proves to matter.

**Guides with no code source are a third tier, and the audit must know it.** Prior art's inventory
merges auto-discovered blocks with a hand-curated list of global features — but even the curated tier
is code-backed, carrying `sources` that feed the signature. Purely editorial guides (image sizing
standards, cross-system syncing) carry none, and QA must be able to hand-author them. Nothing in this
direction prevents that; one thing misfires on it. The audit's guide-to-code (orphan) check would flag
every editorial guide, permanently — the same permanently-red report that rung-relative completeness
exists to prevent. **Fix, needing no new field: the orphan check fires only on guides that claim a
source.** A guide with no generation metadata is editorial by definition and out of scope for orphan
reporting. Contained to the guide-to-code direction; story 4's code-to-guide direction is untouched.
No mode is needed for creating editorial guides — QA creates a page of the right doc type in the
backoffice, and the guides section is a place rather than a generated artifact.

**Indirect benefits.** Fixing the extraction ladder repairs `/feature`'s from-code mode on the same
projects. A component guide that is cheap to stand up makes the block inventory legible to people
who never open the backoffice.

**Interactions.** `/styleguide` depends on `/block` rather than duplicating it, which makes `/block`
load-bearing for a second caller. The audit is the reporting surface for all three ownership kinds,
so its output contract should be settled before either writer is built.

## Direction

**Chosen.** Two spells cut on source — `/guide <alias>` (with `--audit`) for everything derived from
backoffice schema, `/styleguide` for the token-derived one — over a shared dossier that records its
extraction rung, with declared per-field ownership and split-by-artifact timing. Cantrip ships the
content contract; the project's own codebase supplies every rendering decision.

The rationale that carried it: the front-end-agnostic constraint looked like it needed new
machinery, and did not. The pack already resolves "how does this render here" by reading the
codebase, and reusing that seam is what makes all four stories portable.

**Sequencing note, not a decision.** `/styleguide` is the only story requiring new element types,
new views, and a pre-existing design system. If the increment needs splitting, it is the natural cut
line — stories 2–4 share one machine and one dossier; story 1 shares only the guide-page scaffolding.

## Open questions for /spec

- **Which uSync format versions the adapter supports**, and how it refuses an unrecognized one. The
  fail-loudly rule gives the shape; the version set is unresolved, and the uSync element names in
  the existing reference are still marked unverified.
- **Whether `/styleguide` is a spell or a reference.** Decided as a spell on the verbs-are-spells
  convention, but it was close, and it is the choice that moves the pack's spell count.
- **The audit's output contract** — exact categories, exit codes, and how the rung header renders.
  Both writers depend on it.
- **Whether the inventory widens to document types.** A page type carries properties, tabs, and
  groups exactly as an element type does, and the extraction reference already reads both — but prior
  art's auto-discovery walks only block components, so page types would land in the curated list by
  default. The curated entries' `doc-type:` source prefix shows the mechanism already exists.
- **How a guide is matched to its feature** — by slug convention or by stored metadata. If by slug, a
  guide whose metadata is wiped still reads as documented to the code-to-guide check while silently
  never being drift-checked again, which is a silent-pass shape. The same decision is what makes
  editorial guides distinguishable.
- **Overlap with the `/test` roadmap item.** Both operate on derived documentation of existing
  behavior. Worth checking for a shared seam before either is built.
- **Where the voice/tone guidance resolves from.** Settled in principle as a ladder — discover or be
  pointed at project references, else use CMS-native AI contexts where they exist, else a generic
  descriptor shipped in the skill. The rungs are agreed; the discovery mechanism is not specified.
