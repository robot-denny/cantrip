---
name: guide
description: Generate or refresh an editor-facing guide page for one Umbraco component — read the component's schema from the project, plan what a regeneration would change, show it as a difference, and write only what a person approves. Use when asked to document a block or a page type for editors, to create a guide page for a component, or to refresh one after its schema changed.
disable-model-invocation: true
argument-hint: "[component alias — a block or a page type]"
allowed-tools: Read, Write, Glob, Grep, Bash(python3:*), mcp__umbraco-mcp__*
---

The user wants a guide for the component: **$ARGUMENTS**

**The script computes; this spell writes.** `scripts/guide.py`, shipped beside this file, owns every
deterministic step — reading the component's shape, signing it, transforming it into property rows,
deriving the live-example seed set, and saying what a regeneration would change. It writes nothing
and cannot: it has no CMS connection and no approval to act on. This spell owns the prose, the
diff-and-approve conversation, the rendering decisions read from the project's own components, and
**every write**.

So the shape of a run is: read, plan, show, ask, write. Nothing reaches the CMS before the ask.

## What this spell does not decide

`umbraco-17-guide-scaffolding` is the schema half of this capability and the authority on all of it.
Read it before the first step. It states, and this file deliberately does not restate:

- the four document types, the guide page's field set, and the property row's six columns
- the three ownership classes, and that ownership follows the **page's provenance** rather than a
  field's declaration
- the stored reference, what its four values mean, and why every machine-populated field is optional
- where guides live, how the guides node and the kind containers are found, and what the index reads
- **the two slots a guides section needs**, in *The two slots a guides section needs* — which
  serialization adapter runs (`.agents/config/stack.md`), and the guides node's key plus the aliases
  the project actually used (`.agents/config/conventions.md`). Both are declared there **and nowhere
  else**, fallback and detection recipe included. Read them there and follow what they say; do not
  re-declare them here or anywhere downstream.

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

**The reference gets its own question, on every path.** Where the plan carries `consequence` on the
offered reference, print it verbatim; where it does not — a page being created, which reaches this
step as `notComparable` — say the same thing in the plan's own terms: writing this reference is what
makes the page's machine-owned columns machine-owned from then on, and no later edit undoes it. Ask
about it separately from everything else, and treat silence about it as no.

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
