---
name: guide
description: Generate or refresh an editor-facing guide page for one Umbraco component — read the component's schema from the project, plan what a regeneration would change, show it as a difference, and write only what a person approves. Use when asked to document a block or a page type for editors, to create a guide page for a component, or to refresh one after its schema changed. Pass --audit instead of an alias to report which components have no guide, which guides name a component the project no longer holds, and which have gone stale; --ignore or --unignore with an alias to change the list of components that need no guide; --mark-current with an alias to mark a stale guide up to date without regenerating it.
disable-model-invocation: true
argument-hint: "[component alias — a block or a page type | --audit | --ignore <alias> | --unignore <alias> | --mark-current <alias>]"
allowed-tools: Read, Write, Glob, Grep, Bash(python3:*), mcp__umbraco-mcp__*
---

The user's argument: **$ARGUMENTS**. It is a component alias to document, or one of the four flags
below, each of which runs a mode of its own.

**The script computes; this spell writes.** `scripts/guide.py`, shipped beside this file, owns every
deterministic step — reading the component's shape, signing it, transforming it into property rows,
deriving the live-example seed set, and saying what a regeneration would change. It writes nothing
and cannot: it has no CMS connection and no approval to act on. This spell owns the prose, the
diff-and-approve conversation, the rendering decisions read from the project's own components, and
**every write**.

So the shape of a run is: read, plan, show, ask, write. Nothing reaches the CMS before the ask.

**The argument decides the mode.** Each flag runs its own section below and none of Steps 1–9:

| `$ARGUMENTS` | Mode | What it changes |
|---|---|---|
| `--audit` | **Audit mode**: what the guides do not cover, and what has gone stale | nothing |
| `--ignore <alias>` | **Ignore mode**: add a component to the guides node's ignore list | that list, on approval |
| `--unignore <alias>` | **Ignore mode**: take a component off that list | that list, on approval |
| `--mark-current <alias>` | **Mark-current mode**: record a stale guide as up to date without regenerating it | that guide's stored reference, on approval |

Anything else is a component alias, and Steps 1–9 are that run end to end.

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
  the project actually used, `guideGenerated` and `guideIgnored` among them, and the global blocks it
  lists (`.agents/config/conventions.md`). Those two are this spell's; the third
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
| `record --page <file> [--field <name>] [--row <alias>]` | the page's record of generated text after a write, as the value to store in `guideGenerated` |
| `mark <alias> --page <file> [--ignored <alias>]` | the stored reference to write when a stale guide is marked up to date, or why it cannot be |

Exit codes, the same on every subcommand: **0** the read completed, **1** the read failed and the
message says why, **2** the call was malformed, **3** findings under `audit --strict`. A non-zero
exit is never something to work around — print the message and stop.

`record` reads the same page file `plan` reads, filled with values read back from the CMS after a
write, and prints the whole merged record. It writes nothing either; Step 8 says when to run it.
`mark` reads that page file too, and prints the new reference only when the guide is stale.
Mark-current mode says how it is used.

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
guides node is not an absent one, and an absent one is not a missing key.** Where the slot carries no
key, stop before any write and follow the slot's fallback — it asks whether the section exists at all
before asking where it is, and names the remedy where it does not. Everything up to the write —
extract, plan, the difference — still runs and is still worth showing.

**Then check the ignore list.** It is the guides node's `guideIgnored` field, or the alias the
`## Editor guides` slot records for it: the components this project has decided need no guide.
Compare the alias you were given against every entry, ignoring case. **Where it is on the list,
stop here.** Say the component is ignored, that nothing was generated or written, and that
`/guide --unignore <alias>` takes it off the list. Nothing after this step runs for it. A node with
no such field ignores nothing. Where the guides node is not recorded, the list cannot be read: say
so with the rest of this step's statement, and carry on, since no write can happen anyway.

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
  "pageVersion": 2,
  "page": "<the page's own name>",
  "source": { "alias": "…", "kind": "…", "signature": "…", "rung": "…" },
  "generated": { "recordVersion": 1, "fields": { "guidePurpose": "sha256:…" }, "rows": { "…": "sha256:…" } },
  "fields": {
    "guidePurpose": "…", "guideWhenToUse": "…", "guideExamples": "…", "name": "…",
    "guideProperties": [
      { "alias": "…", "label": "…", "required": true, "tab": "…", "group": "…", "information": "…" }
    ]
  }
}
```

`generated` is the page's **record of generated text**: a fingerprint of each prose field and row
note the tooling wrote, taken from the value the CMS stored. Read it from the `guideGenerated` field
(or the alias the `## Editor guides` slot records for it) and put the stored JSON here as an object.
Where the field is empty, write `"generated": null`. `plan` compares each fingerprint to the field's
current value, and that comparison decides which prose a run may rewrite.

Give `guideProperties` as a list of rows, one object per row with the columns above, wherever the
page stores its rows as separate values. That is what lets `plan` read each row's `information`
note against the record. A table stored as one block of markup can only be passed as that markup,
and then `plan` cannot compare the rows or their notes: it says so, and every note is kept.

Five rules the script enforces, and each refusal is a bug on this side of the seam:

- **`"source": null` and an absent `source` key are opposite facts.** Null says the page claims no
  source; absent says you did not read the property. Never omit the key to mean null.
- **`"generated": null` and an absent `generated` key are opposite facts too**, for the same reason.
  A version-2 file without the key is refused. Read as "no record", it would keep every field the
  record says may be refreshed.
- **`fields` must be present**, even empty. Absent means "no fields were read", which would report a
  page's whole content as gone.
- **Do not put the stored reference or the record inside `fields`.** Each is stated once,
  structurally, as `source` and `generated`.
- **Translate the field names.** The register's names (`guidePurpose`, `guideProperties`, …) are
  defaults; the project may have used others, and the `## Editor guides` slot records which. The page
  file speaks the register's vocabulary, and this spell maps both ways — reading and writing.

Three cases, and the third is the one worth reading twice:

| The page | The page file | What `plan` reports |
|---|---|---|
| exists and carries a reference | its reference, its record or `null`, and its fields | a regeneration |
| exists and carries none | `"source": null`, its record or `null`, and its fields | an adoption — propose-only |
| **does not exist yet** | the reference you intend to write, with `"signature": null`, then `"generated": null` and `"fields": {}` | a regeneration whose signature is not comparable |

An adoption never reads the record. A page somebody wrote by hand has no machine-owned text, so
nothing on it is rewritten whatever its `guideGenerated` field holds.

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
`owed` by declaration. A prose field becomes `owed` only when the page's record shows it still holds
exactly what the tooling wrote: `plan` then moves it into `machineOwned` with `generatedState:
asGenerated` and `proposed: null`, because the words are yours to write in Step 5.

Every prose field the page carries is marked with a `generatedState`, and the three states decide
what happens to it:

| `generatedState` | What it means | Where `plan` puts it |
|---|---|---|
| `asGenerated` | the value still matches its recorded fingerprint, so nobody has edited it | `machineOwned`, with `proposal: owed`. Rewrite it |
| `edited` | the value differs from its fingerprint, by any amount | `leftAlone`. Keep it |
| `noRecord` | the record holds no fingerprint for it | `leftAlone`. Keep it |

Row notes carry the same states, in the `rowChanges` of the `guideProperties` entry. A note to
rewrite is a row whose `generatedState` is `asGenerated` and whose `state` is not `removed`. An
`added` row has no state, because its note does not exist yet. `guideExamples` never carries a
state: live examples are seeded once and never refreshed. On a no-op nothing carries a state,
because nothing is proposed.

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
  would use.
- **the when-to-use section** — when to reach for this component and when to reach for another.
  How a shipped implementation renders it differs by component sort;
  `umbraco-17-guide-scaffolding`'s field-set table records one, as a worked example rather than a
  rule.
- **each property row's `information` note** — what this field does, which option to pick and why,
  and any recommendation. Its raw material is the row's `description` and `options` from the dossier.

You write each of them on two occasions, and on no others:

1. **When it does not exist yet.** On a creation run, the purpose sentence and the when-to-use
   section are the fields `plan` names under `unwritten`. A row the plan reports as `added` does not
   exist yet either, so its note is written with it. A page created without its prose is never
   offered it again, which is why the creation path must write it.
2. **When `plan` marks it `asGenerated`.** The text is still exactly what the tooling wrote, nobody
   has made it theirs, and the component has changed since. Write it again from the current dossier.
   For a prose field that is a `machineOwned` entry with `proposal: owed`; for a note it is a
   `rowChanges` entry whose `generatedState` is `asGenerated` and whose `state` is not `removed`.

**Everything else stays as it stands.** A field or note marked `edited` is somebody's writing. One
marked `noRecord` may be too, and the absence of a record is never read as permission. A seeded
field the page never got (`unwritten` on an existing page) stays empty, as the plan says.

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
- **"Required" is text.** A color, an asterisk, or a border weight can carry it as well, but not
  instead — an editor who cannot distinguish the styling still has to know which fields they must
  fill in.

Where the closest exemplar does neither, follow it in every other respect and do these two anyway.
That is not a license to redesign: it is the one place where matching the project exactly would ship
a guide an editor cannot use, and a guide an editor cannot use is not a guide.

## Step 7 — Show the difference, and write nothing

**Everything you are about to present already exists.** The two steps above come first for this
reason: a person cannot approve a sentence nobody has written, and the plan document does not carry
your prose. An owed field's `proposed` is null, and a row's `information` note is excluded from the
machine columns by design. So every piece of prose this run would write is drafted in full before
this step begins: first-time prose, every added row's note, and every field and note marked
`asGenerated`. Approval by category, where the words arrive afterwards, is the approval theater
this whole model exists to avoid.

Present, in this order: the no-op if there is one (and then stop), the statements the plan carries,
then field by field — the field, its current value, and what is proposed, offered, or drafted for
it. **For text being rewritten, show the current text and your new draft one after the other**, so
the person sees exactly what is replaced. Print values **whole**: never wrapped, never truncated. A
diff nobody can read is approval theater.

Name what is kept, too. Every prose field and note marked `edited` or `noRecord` is listed with its
state and its current value, so the person can see which text the run leaves alone and why.

Say plainly which of these the person is agreeing to, because they are different agreements:

- machine-owned fields being **rewritten** — reversible by editing
- prose and row notes the tooling wrote and nobody has edited being **rewritten** — reversible by
  editing, and the current text is the tooling's own, not a person's
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
— read as approval for the machine-owned rewrites, the rewritten and first-time prose, and nothing
further. A row
removal that takes somebody's note with it, and the reference write, each need their own answer,
because a person who has not distinguished them has not agreed to them. If the answer is partial,
write the approved part and report the rest as declined — by name, so the next run's operator knows
what is still outstanding.

## Step 8 — Write, after approval

**Re-read each field immediately before writing it.** Time passes between the plan and the yes, and
an editor may change a field in it. Compare the value you just read to the value in the page file
`plan` read. Where they differ, **skip that field**: do not write it, and report it as "changed
after the plan". The approval covered a change to the text the person was shown, and that text is
no longer there. A page being created has nothing to re-read, so this applies only to fields that
existed when the plan ran.

Write through MCP, in this order, and confirm each before the next:

1. **The page**, where it does not exist — under the kind container for this component's kind.
   Which container that is, when to create one, and what to do where two of them claim the same kind
   are all settled in `umbraco-17-guide-scaffolding`, in *Where guides live*. Follow it; none of it
   is restated here.
2. **The seeded-once fields, at creation only** — the purpose sentence, the when-to-use section, and
   the live examples. A seeded field skipped here is never offered again.
3. **The property rows**, where approved. Each row's note is the new draft for an `added` row, your
   rewrite for a note marked `asGenerated`, and otherwise exactly the note the row already carries.
4. **The refreshed prose**: each prose field marked `asGenerated` and approved, with your rewrite.
5. **The record of generated text**, into `guideGenerated` (or the slot's alias for it), described
   below. It is written whenever this run wrote any prose or row note: on a creation, on a refresh,
   and on a regeneration whose only new prose is an added row's note.
6. **The stored reference, last.** It is the value that says "this page is now generated", and
   writing it before the content it describes leaves a page claiming a signature it does not match.
   So where the property rows were skipped as changed after the plan, do not write the reference
   either. A skipped prose field does not hold it back.
7. **Nothing else.** Never touch the page's name, address, visibility settings, index blurb, main
   body content, media, or any field the register does not name. Live examples are seeded at
   creation and never refreshed, and `guideExamples` is never recorded.

**How to build the record.** After the read-back below has confirmed every field written so far,
write a fresh page file in Step 3's shape from those read-back values, with `generated` holding the
record as the page carries it now (`null` on a page being created). Then run:

```bash
python3 scripts/guide.py record --page written.json \
  --field guidePurpose --field guideWhenToUse --row "<property alias>" --row "<property alias>"
```

Pass `--field` for each prose field written this run and `--row` for each property row whose note
was written this run, and nothing else. A field skipped as changed after the plan is not passed, so
its old fingerprint stays and the next run reads it as `edited`. Where the page stores its table
as one block of markup, pass no `--row`: `record` cannot find a note inside markup and refuses, and
those notes stay unrecorded, so they are kept. `record` keeps every other entry
the page already held and drops entries for rows the table no longer holds. It fingerprints the
read-back value, not what you sent, because a rich-text field can reformat markup on save, and a
fingerprint of the sent text would read as edited on the very next run. Write the JSON it prints,
whole, into `guideGenerated`.

**A creation run must write the record.** Every word on a new page was written by the tooling, so
pass both prose fields and every row note that was written. A page created without its record holds
prose with no fingerprint, and that prose is kept, as `noRecord`, on every later run. **An adoption
writes no prose and no record**: a page somebody wrote is theirs, and the only write it can receive
is the reference.

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

**A rich-text field that came back reformatted is accepted.** The rich-text editor normalizes
markup on save: it wraps text in paragraphs, reorders attributes, changes whitespace and entity
spelling. For a rich-text prose field or row note, compare the visible text, with tags removed and
runs of whitespace collapsed to one space. Where that matches what you sent, the write landed: say
the field was reformatted on save, continue, and let `record` fingerprint the value as stored,
which is what it is for. Where the visible text itself differs, it is a real difference and the
rule below applies. Nothing else gets this allowance: the stored reference, the record, a
plain-text field, and the property rows' aliases, labels and order are compared exactly.

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
Rewritten: <prose fields and row notes rewritten because they were still as generated, or "none">
Kept as edited: <prose fields and row notes kept because somebody edited them, or "none">
Kept, no record: <prose fields and row notes kept because nothing records who wrote them, or "none">
Changed after the plan: <fields skipped because they changed between the plan and the write, or "none">
Record: <guideGenerated written | not written, and why>
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
  "guidesVersion": 2,
  "ignored": ["<an alias on the guides node's ignore list>"],
  "guides": [
    { "page": "<the page's own name>",
      "source": { "alias": "…", "kind": "…", "signature": "…", "rung": "…" } },
    { "page": "<a guide nobody generated>", "source": null }
  ]
}
```

`ignored` is the guides node's ignore list, read from its `guideIgnored` field (or the slot's alias
for it), one alias per entry. Where the field is empty, or the node has no such field, write
`"ignored": []`. The audit reports an ignored component in a section of its own, never as
undocumented or stale, and its guide is not an orphan. An entry naming no component in the project
is listed as naming nothing, so a stale list shows.

The rules are Step 3's, applied to many pages instead of one, and two are worth naming again here:

- **`"source": null` and an absent `source` key are opposite facts**, and the script refuses the
  whole file over an absent one. Never omit the key to mean null.
- **Translate the property names** through the `## Editor guides` slot, the same as Step 3.

Three rules of its own:

- **Write `ignored` on every version-2 file, even empty.** The script refuses a version-2 file
  without it: an absent list cannot be told from one nobody read, and reading it as empty would put
  every ignored component back among the findings. It refuses a version-1 file that carries
  `ignored` too, because version 1 has no list and the file contradicts itself.
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

Add `--global-block <alias>` once for each global block the `## Editor guides` slot lists, here and on
any `inventory` run; a slot listing none adds none.

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

## Ignore mode — `/guide --ignore <alias>` and `/guide --unignore <alias>`

**Some components will never need a guide**: a spacer, a wrapper only developers place, a type kept
for old content. Ignoring one takes it out of the audit's findings, and `/guide <alias>` then stops
on it rather than generating. Un-ignoring puts it back. Each is one change to one field on the
guides node, shown first and written only on approval.

The list lives in the guides node's `guideIgnored` field, or the alias the `## Editor guides` slot
records for it. It travels with that node between environments, so a dashboard and this spell read
the same list. `umbraco-17-guide-scaffolding` declares the field and the form it stores the list in.

### I1 — Resolve the guides node and read the list

Resolve the locations, the adapter and the guides node exactly as Step 1 does. **This mode writes,
so an unrecorded guides node stops it**: follow the slot's fallback and ask, and change nothing.

Then read the node's `guideIgnored` field. **Where the node has no such field, stop.** Say that the
guides node has no ignore list yet, and point at `umbraco-17-guide-scaffolding` for the field to add
to the guides node's document type. Do not add it yourself: this spell writes content, never
schema. Where the field exists and is empty, the list is empty, and that is a normal start.

### I2 — Work out the changed list

Compare aliases ignoring case, as the audit does.

- **`--ignore`, on an alias the project does not hold: refuse.** Run `extract "<alias>"` as in
  Step 2, and on exit 1 relay its message and stop. An entry naming no component would only appear
  in the next audit as naming nothing. On the live rung, ask MCP for a document type or element type
  with that alias instead.
- **`--ignore`, on an alias already on the list: stop.** Say it is already ignored. Nothing to write.
- **`--ignore` otherwise:** the new list is the current one with the alias added, spelled as the
  dossier's `alias` spells it.
- **`--unignore`, on an alias not on the list: stop.** Say it is not ignored. Nothing to write.
- **`--unignore` otherwise:** the new list is the current one without every entry matching the
  alias. Do not check the project for it: an entry naming nothing is exactly the kind a person
  wants to remove.

### I3 — Show the change, and ask

Print the list as it stands and the list as it would be, whole, one entry per line. Then say what
the change does:

- **Ignoring** takes the component out of the audit's undocumented and stale findings. Its guide,
  if it has one, is not an orphan and is left as it is. `/guide <alias>` will stop on it.
- **Un-ignoring** puts it back: the next audit reports it as undocumented or stale again, wherever
  that is what it is.

Say whether the node will be republished, following the publish rule in I4, so the yes covers that
too. **No write happens before an explicit yes.**

### I4 — Write, then save and publish by rule

Re-read `guideIgnored` immediately before writing. Where it differs from what I1 read, somebody
changed the list in between: write nothing, report it as changed after the read, and ask for a fresh
run. Otherwise write the new list into that field and nothing else on the node, in the form the
field already stores it in. Read it back. Where the read-back differs, report what was sent beside
what came back and stop.

**The publish rule**, shared with Mark-current mode:

- **The node was published and had no other unpublished changes:** save and republish it. Its
  public address already exists, so this creates no new one, and the change reaches the
  environments the node is transferred to.
- **The node had other unpublished changes:** save it and do not publish. Publishing would put
  somebody's unfinished work live along with this change. Say that it was saved, not published,
  and why: the change takes effect when that work is published.
- **The node was never published:** save it and leave it so. Publishing it would create a public
  address, which is a separate decision.

Check the state before the write, from the same read as the re-read above. After the write, the
node shows pending changes whatever its state was, so a check made then cannot tell your change
from somebody else's.

### I5 — Report

```
Ignore list: <added <alias> | removed <alias> | unchanged — <why>>
Now ignored: <the list as written, or "nothing">
Saved: <yes | no — declined | no — changed after the read>
Published: <yes | no — other unpublished changes on the guides node | no — never published>
Next: /guide --audit   (see the change in the report)
```

## Mark-current mode — `/guide --mark-current <alias>`

**A guide can be reported stale and still be right.** A content sync can re-sign a component
without changing anything an editor sees, and someone may have already updated the guide by hand.
Marking it up to date records the component's current signature on the guide, so the audit stops
calling it stale. **It changes the stored signature and nothing else.** Rows, prose, live examples
and the record of generated text stay exactly as they are, and **schema changes since the last
generation are not added**. Where the guide is actually behind, the remedy is `/guide <alias>`,
which shows the difference.

The script decides whether a guide can be marked, so every refusal is tested rather than described.
Only a guide whose stored signature **differs** from the source's current one is marked.

### M1 — Resolve, and read the ignore list

Resolve the locations, the adapter and the guides node as Step 1 does. An unrecorded guides node
stops this mode, as it stops I1, because it writes. Read the ignore list from `guideIgnored` too.
Where the node has no such field, the list is empty. An ignored component is refused in M3, not here, so the refusal is the script's.

### M2 — Find the guide page, and write the page file

Walk to the guide exactly as Step 3 does, and write the page file in Step 3's shape and under its
rules. **Where there is no guide page for the alias, stop.** Say the component has no guide, so there
is nothing to mark, and that `/guide <alias>` creates one.

### M3 — Run `mark`

```bash
python3 scripts/guide.py mark "<alias>" --page page.json --project-root "<project root>" \
  --ignored "<ignored alias>" --ignored "<ignored alias>"
```

Pass `--ignored` once for each entry on the ignore list, and none where it is empty. On the live
rung, build the dossier as Step 2 describes and pass it with `--dossier`.

On exit 0, `mark` prints the new `source` as JSON. That is the value to write, verbatim. **On exit 1
it printed nothing to write**, and the message says why. Relay it and stop. It refuses when:

- the component is on the ignore list
- the page's stored reference names a different component from the alias given
- the page carries no stored reference, because it was written by hand. Recording a source on it is
  an adoption, which `/guide <alias>` offers for approval
- the guide is already up to date
- the stored signature was taken at another rung, or the schema cannot be read, or the read
  produced no signature of its own. With no comparison possible, writing the current signature
  would record a check nobody made

### M4 — Show what changes and what does not, and ask

Print the stored reference as it is and as `mark` proposes it, whole. Only `signature` differs.
Then say, in these terms, what the person is agreeing to:

- **Only the stored signature changes**, to the component's current one.
- **Schema changes since the last generation are not added to the guide.** Rows, prose, examples and
  every other field stay as they are.
- The next audit reports this guide as current.

To show what would be left out, run `plan` against the same page file and print its human report
beside the proposal as "what a refresh would have changed". Say the publish rule's outcome, as I3
does. **No write happens before an explicit yes.**

### M5 — Write only `guideSource`, then save and publish by rule

Re-read `guideSource` (or the slot's alias for it) immediately before writing. Where it differs from
the page file, write nothing and report it as changed after the plan. Otherwise write the JSON
`mark` printed into that field, in the form Step 8 writes the reference, and touch no other field.
Read it back, and where it differs, report both values and stop. Then save and publish by the
publish rule in I4, applied to the guide page.

### M6 — Report

```
Guide: <Page Name> (<componentAlias>, <element|document>)
Marked current: <signature written | refused — <the script's reason> | declined>
Not added: schema changes since the last generation, as shown above
Published: <yes | no — other unpublished changes on the guide | no — never published>
Next: /guide --audit   (confirm the guide reads as current)
```

## The degradation order

**What degrades is the prose, never the table.** The property rows, the machine-owned values, the
signature, the seed set and every count are a deterministic transform that needs no model service
anywhere in reach. So the capability has three rungs rather than an on/off switch:

| What is available | What a run produces |
|---|---|
| a model service and a writable CMS | full generation — Steps 1–9, and every mode, as written |
| a model service, no writable CMS | every field rendered to files instead — files written, no page created and no reference stored; audit mode still runs, since it only reads, and the ignore and mark-current modes do not, since they only write |
| no model service at all | the script alone: property rows, machine-owned values, and a named gap where each prose field would go |

**The middle rung is a staged write, and it must say so.** Render the rows in the project's markup
and draft the prose as Steps 5 and 6 describe, then write files rather than pages. Say plainly that
no page was created and no reference was written, so the component is still undocumented and the
audit will still report it — that is accurate, not a bug to work around.

**The bottom rung is the script on its own**, run by a person or a scheduled job: `extract`,
`inventory`, `plan` and `audit` all work with no model in the picture, and their output is a real
deliverable. What it cannot produce is a sentence. `plan` names those fields under `unwritten` and
proposes them nowhere, and the dossier's `gaps` name the columns the rung could not fill.

**One trap at that rung, and it is one-way.** A prose field is written when the page is created,
and rewritten later only while the page's record shows the tooling wrote it (Step 5). A page created
by hand from the script's output — table filled in, reference written, prose left empty — has spent
the only occasion the tooling had to write words: a later run reads the page as existing and offers
nothing, and an adopted page's prose is a person's by definition. So where the intent is for a model-capable run to write the prose later, **keep the
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
- **Only text nobody has edited is ever rewritten.** Prose and row notes are written at creation,
  and rewritten later only while the page's record shows they are still exactly what the tooling
  wrote. Edited text and text with no record are kept. The accepted cost is that guidance somebody
  rewrote can go stale after a schema change and nothing offers to refresh it; the plan reports it
  rather than fixing it silently.
- **Every run that writes prose writes the record**, from the values read back, just before the
  stored reference.
- **The script's report is the source of truth for what changed.** Do not re-derive a diff, a count,
  or a seed set that `plan` already computed — two implementations of one answer will disagree.
- **A read that found nothing is a failure, not an empty result.** Relay the message and stop.
- Every alias — document type, property, guides node, global block — comes from the
  `## Editor guides` slot or its default. Never hardcode one.
- A guide is not done when the fields are full; it is done when an editor can pick the right
  component from it without opening the backoffice.
