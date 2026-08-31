---
name: guide
description: Generate or refresh an editor-facing guide page for one Umbraco component — read the component's schema from the project, plan what a regeneration would change, show it as a difference, and write only what a person approves. Use when asked to document a block or a page type for editors, to create a guide page for a component, or to refresh one after its schema changed. Pass --audit instead of an alias to report which components have no guide, which guides name a component the project no longer holds, and which have gone stale.
disable-model-invocation: true
argument-hint: "[component alias — a block or a page type | --audit]"
allowed-tools: Read, Write, Glob, Grep, Bash(python3:*), mcp__umbraco-mcp__*
---

The user's argument: **$ARGUMENTS** — a component alias to document, or `--audit` for the mode
below, which answers about the whole guide set rather than about one component.

**The script computes; this spell writes.** `scripts/guide.py`, shipped beside this file, owns every
deterministic step — reading the component's shape, signing it, transforming it into property rows,
deriving the live-example seed set, and saying what a regeneration would change. It writes nothing
and cannot: it has no CMS connection and no approval to act on. This spell owns the prose, the
diff-and-approve conversation, the rendering decisions read from the project's own components, and
**every write**.

So the shape of a run is: read, plan, show, ask, write. Nothing reaches the CMS before the ask.

**Two modes, and the argument decides.** `--audit` in `$ARGUMENTS` asks about the whole guide set
rather than about one component: run **Audit mode** below and none of Steps 1–9. Anything else is a
component alias, and Steps 1–9 are that run end to end.

## What this spell does not decide

`umbraco-17-guide-scaffolding` is the schema half of this capability and the authority on all of it.
Read it before the first step. It states, and this file deliberately does not restate:

- the document types a guides section needs — four of them, plus three more a styleguide adds that
  this spell never touches — the guide page's field set, and the property row's six columns
- the three ownership classes, and that ownership follows the **page's provenance** rather than a
  field's declaration
- the stored reference, what its four values mean, and why every machine-populated field is optional
- where guides live, how the guides node and the kind containers are found, and what the index reads
- **the slots a guides section needs**, in *The three slots a guides section needs* — which
  serialization adapter runs (`.agents/config/stack.md`), and the guides node's key plus the aliases
  the project actually used (`.agents/config/conventions.md`). Those two are this spell's; the third
  is the styleguide's design-token slot, which this spell neither reads nor needs. All of them are
  declared there **and nowhere else**, fallback and detection recipe included. Read them there and
  follow what they say; do not re-declare them here or anywhere downstream.

The field set is declared in exactly one place too, and it is not the reference either: `REGISTER` in
`scripts/guidelib/changeplan.py`. Read it for what a field is **for**, never for permission to write
it — provenance decides that.

## The script's surface

Every path below is relative to this skill's own directory. `scripts/guide.py` is the only file to
call; `scripts/guidelib/` is its internals and nothing here imports from it.

| Call | What it answers |
|---|---|
| `extract <alias>` | one component's dossier, as JSON on stdout |
| `signature <alias>` | that dossier's source signature and nothing else |
| `plan <alias> --page <file>` | what regenerating one guide page would change |
| `inventory` | which components are documentable, and the rule that decided |
| `audit --guides <file>` | what the guides do not cover, and what has gone stale |

Exit codes, the same on every subcommand: **0** the read completed, **1** the read failed and the
message says why, **2** the call was malformed, **3** findings under `audit --strict`. A non-zero
exit is never something to work around — print the message and stop.

Both `plan` and `audit` accept their input from a file (`--dossier`, `--inventory`, `--page`,
`--guides`) instead of from the project. That is the seam this spell reads a running instance
through, and it is why nothing downstream is duplicated.

## Step 1 — Resolve the locations, then the adapter

Which serialization format is authoritative is the `## Schema serialization` slot, declared in
`umbraco-17-guide-scaffolding`. Follow its fallback: look for all three markers, record every format
found, and read from the most faithful one. `guide.py` performs that detection itself when
`--adapter` is not given, so passing the project root is usually enough — pass `--adapter` only to
confirm a disagreement, and say why in the report if you do.

Where the *locations* are is a different question, and it is an existing slot:

**Slot:** `.agents/config/paths.md` → `## Umbraco`
**If empty:** locate each by search — the Deploy revision directory by its `*.uda` files,
views by their `*.cshtml` files, and the extension root by its `umbraco-package.json`. If no
`*.uda` files exist, check `uSync/*/ContentTypes/*.config` for the same schema before falling
back to MCP; a folder with no matching file is a partial export, not an empty schema.

Then resolve the guides section from the `## Editor guides` slot, per the reference. **An unrecorded
guides node is not an absent one.** Where the slot does not carry a key, stop before any write, say
that the section's key is the one fact only the project can supply, and ask for it. Everything up to
the write — extract, plan, the difference — still runs and is still worth showing.

State what you resolved before going on: the rung, the project root, and the guides node or its
absence. A wrong adapter produces a plausible guide about the wrong shape, and this is the cheapest
place to catch it.

## Step 2 — Extract the component's shape

```bash
python3 scripts/guide.py extract "<alias>" --project-root "<project root>"
```

**A block and a page type are read the same way**, which is why this spell takes one alias and not a
type. The dossier reports which it is in `kind` — `element` for a block, `document` for a page type —
and the only thing downstream that changes is the wording of the prose you write in Step 5.

Save the dossier to a file and pass it on with `--dossier`. `plan` will read the project itself, but
one extract reused is cheaper than two reads, and it guarantees the plan and the prose describe the
same read.

On exit 1 the message names the alias, the folders searched, and how many components *were* found
there. Relay it and stop. A misspelled alias and a partial export look identical from here, and
guessing between them is how a guide gets written about the wrong component.

**When the project holds none of the three on-disk formats**, the running instance is the last rung
and it is this spell's to read, because it needs a base URL and credentials the script has neither of.
Read the component's document type through MCP, write a dossier file in the shape `extract` emits —
same keys, same nesting, aliases normalized the same way — with `"rung": "live"`, and hand it to
`plan --dossier`. Two consequences to state rather than hide:

- **Omit `sourceSignature`.** The signature's format belongs to the extractor and recomputing it here
  would be a second implementation that could disagree with the first. `plan` accepts its absence and
  reports it — `this read produced no signature of its own` — so a live run always proposes and
  **can never prove a no-op.**
- A live read reports more than any file rung, not less, so nothing is marked as a gap for it.

## Step 3 — Find the guide page, and write the page file

Walk to the guide from the guides node exactly as the reference describes — the recorded key, its
children, their children, matched on document type and never on name. Then write a page file for
`plan`, in this shape:

```json
{
  "pageVersion": 1,
  "page": "<the page's own name>",
  "source": { "alias": "…", "kind": "…", "signature": "…", "rung": "…" },
  "fields": { "guideWhenToUse": "…", "guideExamples": "…", "name": "…" }
}
```

Four rules the script enforces, and each refusal is a bug on this side of the seam:

- **`"source": null` and an absent `source` key are opposite facts.** Null says the page claims no
  source; absent says you did not read the property. Never omit the key to mean null.
- **`fields` must be present**, even empty. Absent means "no fields were read", which would report a
  page's whole content as gone.
- **Do not put the stored reference inside `fields`.** It is stated once, structurally, as `source`.
- **Translate the field names.** The register's names (`guidePurpose`, `guideProperties`, …) are
  defaults; the project may have used others, and the `## Editor guides` slot records which. The page
  file speaks the register's vocabulary, and this spell maps both ways — reading and writing.

Three cases, and the third is the one worth reading twice:

| The page | The page file | What `plan` reports |
|---|---|---|
| exists and carries a reference | its reference and its fields | a regeneration |
| exists and carries none | `"source": null` and its fields | an adoption — propose-only |
| **does not exist yet** | the reference you intend to write, with `"signature": null`, and `"fields": {}` | a regeneration whose signature is not comparable |

**Why the creation path declares a reference for a page that has none.** A page file with
`"source": null` is read as somebody's hand-written work, and the adoption path deliberately derives
no live-example seed set — the reference explains why. A creation run needs that set, and it needs to
be told which prose fields are still unwritten. Declaring the reference you are about to write, with
no signature yet because nothing has been generated into the page, is the truthful description of the
page you are creating, and `plan` answers it with everything the creation needs: the property rows,
the seed set, and `unwritten` naming the prose fields to write. Say in the report that the page was
created rather than refreshed, so nobody reads `notComparable` as a stale guide.

## Step 4 — Run `plan`, and branch before reading `rule`

```bash
python3 scripts/guide.py plan "<alias>" --page page.json --dossier dossier.json --json
```

Read `--json` for the decisions and the human report for the conversation; both render from one
document, so they cannot disagree.

Branch on `comparison` **first**:

| `comparison` | What it means | What to do |
|---|---|---|
| `matched` | the stored signature equals the source's | **stop.** `noop` is true and `modelCallNeeded` false: nothing changed shape, so there is nothing to propose and no model call to make. Report the no-op |
| `differs` | the component changed shape after the page was generated | regenerate: the machine-owned path below |
| `notComparable` | no stored signature, or one signed at another rung | regenerate, and say the run proposes rather than proving anything |
| `noReference` | the page carries no stored reference | the adoption path below |

**`rule` carries different keys on the two paths and they share none.** A regeneration's `rule` holds
`machineOwned` / `seededOnce` / `neverTouched` / `unwritten` — all four, always; an
adoption's holds `humanOwned` / `offered` / `kept`. **Reach for `rule` only inside the branch, or a
hand-written page raises a KeyError.** The asymmetry is deliberate: the three class rules describe a
page that carries a reference, and quoting them at a page that carries none would state a rule that
does not apply to it.

**On a regeneration** — walk `machineOwned` for what to propose, `leftAlone` for what is untouched,
`unwritten` for seeded fields the page never got, and `seeding` for the live-example set. Each
machine-owned entry declares its `proposal` kind: `computed` is a value to write as it stands,
`content` is rows for you to render in the project's markup, `owed` is prose. No register entry is
`owed` today — every prose field on a guide page is seeded once — so a regeneration's model call is
for markup, not words, and the plan's own statement says so.

**On an adoption** — `machineOwned` is present and **empty**, which is a positive claim rather than
an omission: this page has nothing the tooling may replace. `proposeOnly` is true. Every entry in
`offered` carries `pendingApproval` and `proposedOnApproval` instead of `proposed`, so there is no
key in the whole document that reads as a value to write. And the offered reference carries
`consequence` — **show it, verbatim.** Approving the reference is what makes that page's
machine-owned columns machine-owned from then on, and it is the one approval on a guide page that
editing cannot undo. Every other yes here can be reverted by a person changing a field back.

## Step 5 — Write only the content a model owes

Three things, and nothing else, come from you rather than from the script:

- **the purpose sentence** — one sentence saying what this component is for, in the words an editor
  would use. **Seeded once, at page creation only.** A page that already carries one never has it
  regenerated, and a page created without one is never offered one again — which is why the creation
  path must write it.
- **the when-to-use section** — when to reach for this component and when to reach for another.
  Seeded once, on the same terms. How a shipped implementation renders it differs by component
  sort; `umbraco-17-guide-scaffolding`'s field-set table records one, as a worked example rather
  than a rule.
- **each property row's `information` note** — what this field does, which option to pick and why,
  and any recommendation. Its raw material is the row's `description` and `options` from the dossier.
  **Seeded when the row is created and never afterwards**: a row the plan reports as `added` does not
  exist yet, so its note is written with it; a row reported as `changed` or `unchanged` already
  carries whatever somebody wrote, and nothing here touches it.

Warnings belong inside that prose, next to the thing being warned about — a required field with a
non-obvious consequence, a property that changes another's behavior, an option that is not reversible
once content exists.

**Never write around a gap.** A dossier read at a thin rung says which columns it could not fill,
and the plan carries them as `gaps`. Print the gap as a gap; a plausible sentence invented in its
place is worse than a blank, because an editor cannot tell it from a read one.

## Step 6 — Render the rows in the project's own markup

The property rows are a deterministic transform and the script already did it: alias, label,
required, tab, group, one row per property. What is not deterministic is the markup around them, and
**this toolkit ships none** — no template, no class names, no view conventions.

So read the project's own components and take the shape from them. **Find the closest existing
component of the same sort and follow it exactly** — its markup structure, its class or token
conventions, its file placement, its naming. The existing components are the specification; this
spell is not.

**If the project has no components to read from** — a greenfield build — do not invent a convention
here, because the first guide would set one by accident that every later guide inherits. In order:

1. **Ask whether another codebase should be the reference.** A sibling project or a starter the team
   already trusts is a far better source than invention. If one is named, read it and say which
   conventions you took from it.
2. **Otherwise say plainly that you are establishing a convention rather than following one**, keep
   it minimal, and propose recording it in `.agents/config/paths.md` so the second guide has an
   exemplar.

**Two things neither branch gets to skip.** A guide's property table is read by editors, some of them
with a screen reader — so a copied convention that fails them fails them on every guide this spell
ever writes, and a convention established here would set that failure as the project's standard:

- **The table's structure is conveyed in the markup, not by appearance alone** — a real table with
  real header cells, or a list whose grouping is in the elements rather than in the styling. A grid
  of divs that looks like a table is not one to anybody who cannot see it.
- **"Required" is text.** A colour, an asterisk, or a border weight can carry it as well, but not
  instead — an editor who cannot distinguish the styling still has to know which fields they must
  fill in.

Where the closest exemplar does neither, follow it in every other respect and do these two anyway.
That is not a licence to redesign: it is the one place where matching the project exactly would ship
a guide an editor cannot use, and a guide an editor cannot use is not a guide.

## Step 7 — Show the difference, and write nothing

**Everything you are about to present already exists.** The two steps above come first for this
reason: a person cannot approve a sentence nobody has written, and the plan document does not carry
your prose — no register entry owes it, and a row's `information` note is excluded from the machine
columns by design. So the purpose sentence, the when-to-use section and every added row's note are
drafted, in full, before this step begins. Approval by category, where the words arrive afterwards,
is the approval theatre this whole model exists to avoid.

Present, in this order: the no-op if there is one (and then stop), the statements the plan carries,
then field by field — the field, its current value, and what is proposed, offered, or drafted for
it. Print values **whole**: never wrapped, never truncated. A diff nobody can read is approval
theatre.

Say plainly which of these the person is agreeing to, because they are different agreements:

- machine-owned fields being **rewritten** — reversible by editing
- prose and row notes being **written for the first time** — reversible by editing, and seeded once,
  so this is the only run that will ever offer them
- rows being **removed**, where the plan says a removed row carries an `information` note — that note
  goes with it, so name every such row individually
- the stored reference being **written** on a page that had none — **not reversible by editing**

**The reference gets its own question, on every path.** The plan carries `consequence` on the
reference entry wherever that write is a *first* write — offered on an adoption, and proposed on a
page being created, which reaches this step as `notComparable`. **Print it verbatim.** Do not
paraphrase it and do not supply wording of your own: the plan holds one canonical text for both
paths precisely so an irreversible fact is never stated two ways. The report prints it too, under
the reference's own line, so the person reading either rendering is warned.

Where the entry carries **no** `consequence`, the page already holds a reference and this write is
not the irreversible one — it belongs with the reversible rewrites above. **That is not the same as
`notComparable` meaning a creation.** A signature stored at another rung, or with no rung recorded,
also reads `notComparable`, and those pages already carry a reference: the absence of `consequence`
is the answer, not a gap in the plan. Ask about the reference separately from everything else, and
treat silence about it as no.

Then ask about the rest. **No CMS write happens before an explicit yes.**

**An unscoped yes covers the reversible sections and nothing else.** "Yes", "looks good", "go ahead"
— read as approval for the machine-owned rewrites, the first-time prose, and nothing further. A row
removal that takes somebody's note with it, and the reference write, each need their own answer,
because a person who has not distinguished them has not agreed to them. If the answer is partial,
write the approved part and report the rest as declined — by name, so the next run's operator knows
what is still outstanding.

## Step 8 — Write, after approval

Write through MCP, in this order, and confirm each before the next:

1. **The page**, where it does not exist — under the kind container for this component's kind.
   Which container that is, when to create one, and what to do where two of them claim the same kind
   are all settled in `umbraco-17-guide-scaffolding`, in *Where guides live*. Follow it; none of it
   is restated here.
2. **The seeded-once fields, at creation only** — the purpose sentence, the when-to-use section, and
   the live examples. A seeded field skipped here is never offered again.
3. **The machine-owned fields** that were approved — the property rows, then the stored reference.
   **The reference goes last**: it is the value that says "this page is now generated", and writing it
   before the content it describes leaves a page claiming a signature it does not match.
4. **Nothing else.** Never touch the page's name, address, visibility settings, index blurb, media,
   or any field the register does not name.

**Live examples are content, not markup.** Seed each one as a real instance of the component placed
in the page's own content area, so the site renders it exactly as it renders the component anywhere
else. A seed sets only the values the plan names; where the plan set nothing, let the CMS apply its
own defaults rather than choosing values for it. On a page that already carries an arrangement,
**seed nothing** — an arrangement is somebody's work, and the plan prints the derived set to be read
beside it rather than written over it.

**This tooling never generates or writes media.** Screenshots are uploaded by a person, always, and
the media they upload carries its own alt text. Where a guide needs one, say which screen it should
show and leave the field empty.

**Never create a public URL without confirmation.** Save the page rather than publishing it, and ask
before publishing — publishing a guide puts a URL on the public site, and on the index too, since the
index derives its list from what is published.

Then read each written field back. A successful request means the write was accepted, not that the
value is what you intended — a rich-text field can normalize markup, an editor can hold a lock, and a
property alias can resolve to something other than the field you meant.

**Where a read-back differs, stop writing and report the difference.** Print what you sent beside
what came back, name the field, and do not retry: a second write against a value the CMS already
changed once is how a field ends up holding neither version. Do not touch anything further in the
sequence — a page half written is a page a person can finish, and a page written past a failure
nobody was told about is not. The report block says which fields were written and which were not.

## Step 9 — Report

```
Guide: <Page Name> (<componentAlias>, <element|document>)
Rung: <deploy|usync|models|live>   Signature: <matched|differs|notComparable|noReference>
Outcome: <created | refreshed | adopted — reference written on a page somebody wrote | no-op — source unchanged>
Written: <fields written, or "nothing — declined">
Left alone: <count> fields   Rows: <+added / -removed / ~changed>
Seeded: <live examples seeded, or "none — page already arranged">
Awaiting a person: <screenshots, curated example combinations, publishing>
Next: /guide <nextAlias>   (document the next component)
```

## Audit mode — `/guide --audit`

**One question, about the whole guide set rather than about one component**: what the guides do not
cover, and what has gone stale. The script does the arithmetic and this spell supplies the guide
set, because the guides live in the CMS and the script has no connection to it.

The report's shape — the three counted sections, the header and its rung statement, how an item is
named to a person, the closing line — is declared in `umbraco-17-guide-scaffolding`, in *The
audit's report shape*. **That is the authority, and none of it is restated here.** Read it before
rendering or relaying anything.

### A1 — Resolve the locations, the adapter, and the guides node

Exactly as Step 1, including the guides node from the `## Editor guides` slot. An audit writes
nothing, so an unrecorded node blocks nothing — but it is still the difference between "this
project has no guides" and "the guides were never found", and reporting the first when the second
is true sends a team to write pages that already exist. Where the slot carries no key, say so and
ask, exactly as Step 1 does.

**A key that no longer resolves is the same mistake wearing a configuration.** A recorded key whose
node the CMS cannot return is not an empty guides section, and walking it yields zero pages exactly
as a real empty section does — so the two are indistinguishable in the count and opposite in what
they mean. Stop rather than audit: report the key, say it did not resolve, and ask whether the node
moved, was deleted, or belongs to another environment. An audit against a node that is not there
reports every component in the project as undocumented, which is a report nobody should act on.

### A2 — Read the guide set out of the CMS

Walk from the guides node through the kind containers to every guide page — matched on document
type, never on name, as the reference describes. Then write one file:

```json
{
  "guidesVersion": 1,
  "guides": [
    { "page": "<the page's own name>",
      "source": { "alias": "…", "kind": "…", "signature": "…", "rung": "…" } },
    { "page": "<a guide nobody generated>", "source": null }
  ]
}
```

The rules are Step 3's, applied to many pages instead of one, and two are worth naming again here:

- **`"source": null` and an absent `source` key are opposite facts**, and the script refuses the
  whole file over an absent one. Never omit the key to mean null.
- **Translate the property names** through the `## Editor guides` slot, the same as Step 3.

Two rules of its own:

- **Include the pages that claim no source.** A hand-written guide is neither orphaned nor stale
  and closes no gap, so it appears in none of the three sections — but the header counts it, and a
  guide set that leaves it out understates what was read.
- **No `fields` key.** An audit reads references and nothing else; a page's prose is not its
  business.

A refusal is a bug on this side of the seam. The script refuses a whole guides file rather than
skipping one entry, because a dropped entry moves a documented component into the undocumented
list and nothing in the report would say so.

**Where the project holds none of the three on-disk formats**, the inventory is this spell's to
read, as in Step 2 — build the document `inventory --json` emits and pass it as `--inventory`. Same
seam as `--dossier`, for the same reason.

**An audit cannot degrade to files.** The generate path has a lower rung to fall to; this mode does
not, because the guide set exists nowhere but the CMS. Where it cannot be read, say that no audit
was performed — an audit run against a guide set you could not read would report every documented
component as undocumented.

### A3 — Run it, and lead with the inventory and the rule

```bash
python3 scripts/guide.py audit --guides guides.json --project-root "<project root>"
```

**Relay the report in the order it came, and lead with the header** — the documentable count and
the determiner's rule beside it, before a single finding and before a single guide is proposed. The
determiner is where this capability is most plausibly wrong: counted from the element-type flag
instead of from the project's own block-editor palettes, it over-counts by half again on one
measured project and by 2.4x on another, and every over-count becomes a page somebody is told to
write. Stated first, a wrong rule costs one line to spot. Stated after the findings, it is a
hundred items nobody can tell from real work.

So where the count does not match what the team believes it has, **stop and run `inventory` for the
rule in full** — the audit's header says as much itself — and settle the count before proposing
anything.

Then relay the sections and the closing line as the script printed them. **Do not re-derive a
count, re-sort a list, or summarize a section away**: the report is the interface, and a second
rendering of it is a second answer that can disagree.

### A4 — Warns, never blocks

**A completed audit exits 0 whatever it found.** Findings are a backlog, not a gate. `--strict` is
the only path to a non-zero exit, and the whole of it *is* the exit code: the report is computed
and printed first and is identical either way, so a team that gates its build reads exactly what a
team that does not reads. Findings under `--strict` exit **3** — never 1, which means the read
failed. Pass it only when the caster asked for a gate, and never to make a run look decisive.

**This is not a defect to fix, and nobody should "correct" it.** An audit that failed a build by
default would fail it hardest in the projects that wired the audit in early, which is how guides
get cut from scope again — the outcome this whole capability exists to prevent. A team that wants
the gate passes `--strict`. A run that exits non-zero without it did not complete, and the message
says why.

**An audit proposes nothing and writes nothing.** The remedy for an undocumented item is a
`/guide <alias>` run of its own, with its own approval conversation; for an orphan, a person
deciding whether the page goes; for a stale guide, a refresh that shows its diff. Close with the
first one as the `Next:` line and let a person cast it.

**Say in your own words that findings are work to schedule, and say it whenever there are any.**
The script writes that reassurance into `Findings: none.` and into nothing else — a clean result
carries two sentences explaining what it means, and `Findings: 39 undocumented, 0 orphaned, 0
stale.` carries none. So the branch that already reads as good news is the only one the report
comforts, and the branch a person is likely to meet on a first run is the one that reads like a
failure. Close that gap yourself: one sentence, phrased however the conversation warrants.

Two things it must do and one it must not. It must say the count is a backlog rather than a fault
— on a project that never had guides, thirty-nine undocumented components is the expected reading
of a healthy codebase, not a problem discovered. It must say nothing has been written and nothing
will be without a separate cast. And it must **never call a finding an error, a failure, or a
problem**: the exit code is zero because that is what the result means, and prose that contradicts
it teaches a reader to distrust one or the other.

## The degradation order

**What degrades is the prose, never the table.** The property rows, the machine-owned values, the
signature, the seed set and every count are a deterministic transform that needs no model service
anywhere in reach. So the capability has three rungs rather than an on/off switch:

| What is available | What a run produces |
|---|---|
| a model service and a writable CMS | full generation — Steps 1–9, and audit mode, as written |
| a model service, no writable CMS | every field rendered to files instead — files written, no page created and no reference stored; audit mode still runs, since it only reads |
| no model service at all | the script alone: property rows, machine-owned values, and a named gap where each prose field would go |

**The middle rung is a staged write, and it must say so.** Render the rows in the project's markup
and draft the prose as Steps 5 and 6 describe, then write files rather than pages. Say plainly that
no page was created and no reference was written, so the component is still undocumented and the
audit will still report it — that is accurate, not a bug to work around.

**The bottom rung is the script on its own**, run by a person or a scheduled job: `extract`,
`inventory`, `plan` and `audit` all work with no model in the picture, and their output is a real
deliverable. What it cannot produce is a sentence. `plan` names those fields under `unwritten` and
proposes them nowhere, and the dossier's `gaps` name the columns the rung could not fill.

**One trap at that rung, and it is one-way.** Every prose field on a guide page is seeded once, at
creation (Step 5). A page created by hand from the script's output — table filled in, reference
written, prose left empty — has spent the only occasion the tooling had to write words: a later run
reads the page as existing and offers nothing, and an adopted page's prose is a person's by
definition. So where the intent is for a model-capable run to write the prose later, **keep the
rendered files and do not create the page yet.** Where somebody wants the page anyway, say that
sentence to them first and name the fields that will stay theirs.

## Voice and tone

Every sentence Step 5 asks for is written **as the project writes**, and the project is the
authority on that. Resolve it by ladder, taking the first rung that answers **and reading rung 3
regardless** — it is the only one that says what not to write, which no other rung supplies and no
later rung can be reached to correct:

1. **The project's own editor-facing writing, where it is discoverable.** Guides already published,
   backoffice help text, an editorial style guide, a design-system skill with a writing section.
   **Find the closest existing piece of writing aimed at the same reader and follow it** — its
   person, its tense, its tolerance for jargon, how it names what an editor sees on screen.
2. **A reference somebody points at.** Where nothing is discoverable, ask whether another codebase,
   a documentation site, or a published page is the reference; if one is named, read it and say in
   the report which conventions you took from it.
3. **The platform's own AI contexts, where the platform provides them.** On Umbraco AI these are
   real records rather than a hope: a context's `Resources` carry either a `brand-voice` entry —
   tone description, target audience, style guidelines, patterns to avoid — or a `text` entry whose
   settings hold the guidance verbatim. They serialize alongside the rest of the schema, so look
   for them where Step 1 resolved that: on Deploy they are `umbraco-ai-context__*.uda` artifacts in
   the same revision directory, and a running instance answers for them through MCP. **This rung is
   cheap and structured — read it even when rung 1 answered**, because it is the only one that
   states what *not* to write; where the two disagree, say so rather than blending them.
4. **Otherwise the descriptor below** — this spell's fallback, and nothing more.

**If the project has no editor-facing writing, no AI context, and nothing named** — a greenfield
build — use the descriptor and **say in the report that the voice was read from nowhere**, so the
first editor to see a guide corrects it once rather than forty times:

> Second person, present tense, one idea per sentence. Say what the editor does and what happens
> when they do it. Name things exactly as the backoffice labels them, and where a technical term is
> unavoidable, define it the first time. No marketing language, and no "simply" or "just" — an
> editor reading a guide is stuck, and a sentence implying the answer is obvious makes that worse.
> A warning states the consequence before the instruction.

## Where a report or a rendered file lands

Both file outputs above follow the toolkit's artifact-disposition convention: **ask whether the
output is durable or temporal**, and let the location carry the answer, so commit status is not a
second decision to remember. The `workflow` skill is the authority on the layout and on what a
project has overridden.

- **The audit's report** — durable → the project's audit directory, dated:
  `docs/audits/<YYYY-MM-DD>-guide-audit.md` by default. Temporal → a git-ignored scratch location.
  **Date the filename either way.** An audit is a point-in-time snapshot against a schema that
  moves, and an undated one gets read as current truth. Write the report as the script printed it,
  not a rewrite of it — the same rule A3 states for relaying it.
- **Guides rendered to files** — a staging artifact, so **temporal by default**: they exist to be
  written into the CMS, and a committed copy is a second source of truth for something the CMS
  owns. Where the answer is durable, say what makes it so — a project publishing its guides from
  files rather than from the CMS is a different capability, not a staged write.

**Print first, write only when asked.** An audit belongs in the conversation; a spell that leaves a
file behind on every cast trains its user to ignore the files. Where a file *is* wanted — and for a
scheduled or repeated audit it usually is — ask the durable-or-temporal question rather than
choosing for them.

## Conventions

- **Nothing is written before a person says yes**, and a yes to one section is not a yes to another.
- **No prose on a guide page is ever regenerated.** Every prose field is seeded once, at creation.
  The accepted cost is that guidance can go stale after a schema change and nothing offers to refresh
  it; the plan reports it rather than fixing it silently.
- **The script's report is the source of truth for what changed.** Do not re-derive a diff, a count,
  or a seed set that `plan` already computed — two implementations of one answer will disagree.
- **A read that found nothing is a failure, not an empty result.** Relay the message and stop.
- Every alias — document type, property, guides node — comes from the `## Editor guides` slot or its
  default. Never hardcode one.
- A guide is not done when the fields are full; it is done when an editor can pick the right
  component from it without opening the backoffice.
