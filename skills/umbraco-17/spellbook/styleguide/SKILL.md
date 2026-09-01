---
name: styleguide
description: Generate a styleguide page in an Umbraco guides section that reads the project's design tokens live — check the precondition, read the token layers the project holds, group with a person what the script will not name, scaffold the showcase element types and their palette, and write only what is approved. Use when asked to create a styleguide, a design-system page, a palette or type-scale page for editors, or a page showing what the design system offers.
disable-model-invocation: true
argument-hint: "[optional — a name for the styleguide page]"
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(python3:*), mcp__umbraco-mcp__*
---

The user's argument: **$ARGUMENTS** — a name for the styleguide page, or nothing, in which case
propose one in the project's own wording and let the person settle it.

**The script computes; this spell writes.** `scripts/styleguide.py`, shipped beside this file, owns
every deterministic step — finding the stylesheets, reading the custom-property declarations out of
them, classifying each one by the shape of its value, and answering whether this project may have a
styleguide generated for it at all. It writes nothing and cannot: it has no CMS connection and no
approval to act on. This spell owns the prose, the grouping conversation, the arrangement of the
page, and **every write**.

So the shape of a run is: check, read, group, show, ask, write. **Nothing reaches the CMS, and
nothing reaches the project's config, before the ask.**

**A styleguide is a guide page that documents the system rather than a component.** It sits in the
same section as every other guide, under a kind container of its own, and what makes it a styleguide
is what its content area holds. It carries **no stored source reference**, and what follows from
that — for the fields on it and for what the guide audit says about it — is in the reference, at
*Ownership is a consequence of provenance*.

## What this spell does not decide

`umbraco-17-guide-scaffolding` is the schema half of this capability and the authority on all of it.
Read it before the first step. It states, and this file deliberately does not restate:

- **the three showcase element types** — their aliases, what each one stores, the optional caption
  and what it is for, and the requirements a project's own view has to honor. All of it is in
  *The showcase element types*, together with the decision the rest of it follows from: **a showcase
  element stores a name, never a value.**
- that **themes need no property on a showcase element**, and why adding one would be the mistake —
  same section. Step 6 below acts on that; it does not re-argue it.
- that this pack **ships no view** for any of the three, and that a project with nothing to copy
  conventions from is a stop rather than a gap in the schema.
- **where guides live** — the recorded key, the walk from it, kind containers matched on document
  type and never on name, and what a kind with no container means.
- that a page carrying no stored reference has **no machine-owned fields at all**, in *Ownership is
  a consequence of provenance*.
- **the showcase palette and the exclusion it buys**, in *The showcase element types* and again in
  the slot table — including that both readings of a project take that exclusion, and that its
  default is a default for creating a palette rather than for assuming one.
- **the slots this spell reads** — `.agents/config/conventions.md` → `## Editor guides` for the
  guides node's key, the aliases the project actually used, and the showcase palette; and
  `.agents/config/stack.md` → `## Design tokens` for the token layer. Both are declared there
  **and nowhere else**, fallback and detection recipe included. Read them there and follow what they
  say; do not re-declare either here or anywhere downstream.

The detection recipe behind the token slot is not in the reference either, and that is deliberate:
it is implemented and argued line by line in this skill's own `scripts/styleguide.py` module
docstring — which files are walked and which are skipped, which sigil marks which layer, why a
utility framework's theme configuration is not a layer of its own, and why a build-time-only layer
is refused rather than baked. Read it there.

## The script's surface

Every path below is relative to this skill's own directory. `scripts/styleguide.py` is the only file
to call.

| Call | What it answers |
|---|---|
| `tokens` | which token layers the project holds, which one is authoritative, and every custom property it declares with its group |
| `precheck` | whether both halves of the precondition are met — a palette a rendered page can read, and an existing view to take conventions from |

Both accept `--project-root DIR`, defaulting to the current directory, and each prints one JSON
document on stdout and nothing else.

Exit codes, the same on both: **0** the read completed, **1** the read failed and the message says
why, **2** the call was malformed, **3** the read completed and the answer is negative. What
"negative" means is the one thing the two do not share — for `tokens` it is a project holding token
layers of which none can be read at render time; for `precheck` it is either half of the
precondition unmet.

**On 0 and on 3 the document prints before the exit**, so a caller stopping on 3 already holds the
finding and its remedy: there is nothing to re-derive and nothing to work around. **On 1 and 2 there
is no document at all** — a message on stderr and nothing on stdout, because the read never reached
the point of having something to report. Do not wait for JSON that is not coming; relay the message.

`tokens` carries `tokensVersion: 3`, `declarationsFrom`, `authoritativeLayer`, a `refusal` that is
null on a positive read, `stylesheetsRead`, a `counts` object, and four tables — `layers`, `byFile`,
`byPreprocessorFile`, `declarations`.

**Read `counts` before you read `declarations`, and the reason is not tidiness.** `counts` carries
`declarations` and `names` as separate numbers because they answer different questions: the
`declarations` table has one row per *declaration*, so a token re-declared across ten files or twenty
media queries is ten or twenty rows carrying one name. On a measured project that is 22,247 rows over
318 names, nine tenths of it one vendored dependency re-stating a handful of names. A palette is the
*names*; the row count is how many places each was written. Step 4 works from the names.
`precheck` carries `precheckVersion: 1`, `preconditionMet`, a `halves` table whose rows each carry
`half`, `met`, `statement` and `remedy`, plus `tokenLayers`, `authoritativeLayer` and
`exemplarViews`. **Read the version key rather than sniffing for keys** — it is there to tell you
the document's shape changed.

## Step 1 — Check the precondition, and stop where it is not met

```bash
python3 scripts/styleguide.py precheck --project-root "<project root>"
```

**This runs first, before anything is resolved and long before anything is created.** The two halves
it answers are the two things a styleguide cannot be generated without, and both are cheaper to find
out about now than after a section has been half scaffolded.

**Both halves are always named, met or unmet — say both.** "This project has blocks and no palette"
and "this project has neither" are different situations with different remedies, and a report that
prints only the failure leaves the person unable to tell them apart.

On exit **0** both halves are met: go on to Step 2.

On exit **3** either half is unmet. **Stop, having created nothing.** Relay the unmet half's
`statement` and its `remedy` **verbatim**, and say the other half was met if it was.

On exit **1** the read itself failed. Relay the message and stop; a failed read and a negative
answer are different facts and this spell never collapses them.

**Relay a refusal, never re-derive it and never soften it.** The statement and the remedy are held
in one place so that a person meets one wording of them however they arrived, and this spell's whole
value is that a page it produces reads the system live. A run that carried on past a refusal would
produce a page of values it invented or baked — right on the day it shipped, silently wrong from the
first palette edit onward, and indistinguishable from a good one at a glance.

## Step 2 — Resolve the guides node, then the styleguide's container

The guides node comes from the `## Editor guides` slot in `.agents/config/conventions.md`, declared
in `umbraco-17-guide-scaffolding`. Resolve it **by its recorded key** — never by route, never by
path, and never by name. *Where guides live* argues why, and the argument is not repeated here.

**The key is the one fact only the project can supply.** Where the slot carries none, the node is
*not recorded*, which is not the same as not existing. Stop before any write, say so, and ask for
it — do not go looking for the section by name.

Then walk from that node to its children and find the container for the styleguide's kind, matched
on **document type, never on name**, exactly as the reference describes.

- **A kind with no container is a container to create.** Where no child of the guides node carries
  the kind, that container does not exist yet, and a similarly-named node is not a fallback — it is
  how a styleguide ends up filed under something unrelated. Propose creating one, and let the
  person name it; the name is copy, and the kind value is what the index groups by.
- **Two containers carrying one kind is reported, and nothing picks between them.** Say which kind
  is duplicated and stop writing into that kind. An ambiguity a person resolves in a minute is not
  one a tool should resolve by accident.

Say what you resolved before going on — the guides node, the container or its absence, and what the
container already holds. A styleguide written into the wrong place is a page nobody finds, and this
is the cheapest point to catch it.

## Step 3 — Read the token layers

```bash
python3 scripts/styleguide.py tokens --project-root "<project root>"
```

Read `authoritativeLayer` and say plainly which layer the swatches will read from. Then **name every
other layer the report found**, because that is normally where a person edits the palette: the
common good shape is a preprocessor palette that emits a runtime block, and a person told only about
the runtime layer will go looking for the wrong file to change a color.

`declarationsFrom` names the layer the `declarations` table was parsed out of, which is the only
layer whose values this script reads at all. `byFile` says which file each declaration came from —
**keep that visible**, because it is the only way to tell a committed framework's palette from the
project's own, and guessing by path would take a project fact this pack must not hold.

An exit **3** here is the same refusal `precheck` already gave, arrived at by the same question
asked of the same reading. If Step 1 passed and this exits 3, something changed between the two
reads: say that rather than picking whichever answer is more convenient.

A read that completed and found no declarations at all is not a failure and not a refusal — but it
is also not a page. `precheck` has already turned that state into a stop; if it did not, trust it
over this reading and say the two disagree.

## Step 4 — Group what the script would not name, with a person

The report puts every declaration in one of two groups and there is no third: `color`, where the
whole declared value is unambiguously a color, and `unclassified`, which carries its declared value
so a person can work from the report. **The absence of a third group is the point.** A name-based
classifier files a spacing token under colors and a swatch grid built from that output is wrong in a
way that looks deliberate, so the script names the one group whose value shape cannot be
misread and leaves every other grouping to a person.

**Work from the names, not the rows.** Take the distinct names out of `declarations` — `counts.names`
is how many there are — and present those. A name declared in twelve places is one token to the
person you are asking; say that it is declared in twelve places, and where, if it matters. Presenting
a row per declaration buries a project's own palette under its dependencies' repetitions, and the
person who most needs to read the report is the one least able to.

**Where a name is declared more than once, its group is already resolved for you.** The script
classifies a name as a color if any of its declarations is one, and reports every declaration
regardless — the cascade is the browser's question, not this spell's. Take the group as given and do
not re-derive it from one row you happened to read first.

That person is not you. **Present both groups and ask** — propose a grouping if you have one, say
what suggested it, and never write a grouping in as though it had been read:

- **The colors** are ready to become swatches, but which of them a page should show is editorial.
  *The showcase element types* leaves the number deliberately open and says why; ask rather than
  defaulting to one swatch per token.
- **The unclassified set** is everything else — spacing, radii, shadows, type scale, layering, and
  whatever else the project keeps in its palette. Show it by name with its declared value, grouped as
  you read it and marked as a proposal.
- **The type specimens come out of that set.** A type specimen stores a token's name and the sample
  words to set in it, so both are decisions here: which levels of the scale the page shows, and what
  each one says. **Never invent a token name that was not in the report** — a specimen naming a
  token the project does not declare renders nothing and reads as a design choice.
- **An alias is reported, never resolved.** A declaration whose value points at another token comes
  back verbatim with `aliasOf` naming its target, and the chain is not walked to a literal. Show the
  name that was declared. In a two-tier system the role token is the one a theme re-points and the
  one a person would write, so it is the name a swatch should carry — not the fixed entry beneath it.

Whatever the person groups, say back what you understood before it becomes a page. A grouping is the
vocabulary every reader of that page will use afterwards.

## Step 5 — Decide what the common-elements showcase covers

The third showcase element type stores **which of the common elements to include**, and choosing
that list is this step. The reference names the sorts — buttons, links, lists, tables, blockquotes,
form fields — and stops there, because which of them a project actually has is a project fact.

**The styles an editor can apply belong in that list.** Where the CMS offers editors a menu of named
styles to pick from as they write, that menu is how you know which ones matter: somebody curated it
for the people writing the content, so a style on it is a style that will appear on the site, and a
style absent from it is one no editor can reach.

**They are not a section of their own.** A named style an editor applies is the design system's
style, shown to the people who apply it — the same system the swatches and the specimens are
showing, arriving through a different door. Giving it a heading beside the colors and the type scale
would say the project has two systems, and the second one would be the one editors actually use.

**Where the list includes form fields, ask for their labels here.** A field's label is the one piece
of a specimen that has nowhere else to come from: the reference gives the showcase element an optional
caption for exactly this, and calls it the case where an empty one costs more than a missing sentence.
Every other caption on this page is editorial — what a token is *for* — and an empty one costs a
sentence. An unlabelled field is a control nobody using a screen reader or voice control can name, on
the page every later block is copied from. So ask at the same moment you ask which elements to
include, and carry the answer into Step 7 with the rest.

**A literal that traces back to no token is drift to report, not a style to showcase.** Where an
editor-facing stylesheet sets a value outright rather than reading it from the palette, that value
has already left the system: it will not follow a re-theme, and putting it on a page whose whole
claim is that it reads the system live would make the page lie about itself. Name what you found and
where you found it, in the report, and stop there. **Reporting that drift properly is a later
increment and not this spell's job** — do not build a reconciliation into this run. Do not quietly
drop the style either: a silent omission is the same page with one fewer thing anybody can check.

## Step 6 — Ask whether the project themes, and let its own mechanism answer how

**Ask whether the project themes its blocks.** Where it does not, this step is one line in the
report and nothing more.

Where it does, one thing is settled and one is not.

**Settled: the showcase element needs no theme property, and adding one would be the mistake.** The
reference argues that at *The showcase element types* and it is not re-argued here. What follows
from it is what this step acts on — a swatch carries a token's *name*, so it is re-pointed by
whatever the project already uses to theme a region, and the showcase inherits that mechanism the
same way it inherits spacing and visibility: by copying the closest existing block, exactly as
`/block` Step 5 says to. If the project has no block to copy from, Step 1 has already stopped this
run, and there was no theme mechanism to inherit either.

**Not settled, and deliberately not prescribed here: how the page demonstrates the set.** One
section repeated per theme, a switcher, or a single representative with the whole set named beside
it are all defensible, and which one is right depends on how that project themes at all — a rule
written into this file would be fitted to whichever project its author had in front of them. Decide
from the project's own mechanism, say which you chose and what in the project decided it, and let
the person say no.

**This is your judgement at generation time, and it is the same deferral this spell already makes
for markup.** It is expected to be refined once there are more worked examples than there are today.
Until then, a run that states its reasoning is one somebody can correct, and a run that picks
silently is one nobody can.

## Step 7 — Show the whole page, and write nothing

**Everything you are about to present already exists.** The four steps above come first for that
reason: the grouping, the swatch set, the specimen words, the elements list and the theme decision
are all made before this step begins. Approval by category, where the substance arrives afterwards,
is the approval theatre this model exists to avoid.

Present, in this order and whole — never truncated, never summarized into a count:

**What "whole" means, since Step 4 has already reduced rows to names.** Never truncate the thing being
approved: every swatch, every specimen, every element, every line to be written. The rule exists so a
person is not asked to approve "the palette" and shown a number — that is the theatre it names. It was
never a promise to echo incidental repetition: a name declared in twelve places is one item on this
list, with its twelve noted beside it. Reducing a dependency's duplication to a count is not
summarizing what is being approved; **replacing a swatch set with "18 swatches" is.**

1. the layers found, and which is authoritative
2. the swatch set, each with the token name it will carry
3. the type specimens, each with its token name and its sample words
4. the common elements the specimen will include, the labels for any form fields among them, and
   any drift Step 5 turned up
5. how the themes are presented, and what decided it
6. the element types and the palette to be created, under the aliases the slot records or the
   defaults the reference gives
7. the line to be written into the project's config, quoted exactly as it will be written
8. the page itself — its name, its container, and what its content area will hold

**Say plainly which of these the person is agreeing to, because they are different agreements:**

- **element types and a palette being created** — schema in the project's CMS, and the thing here
  that changes what other tooling sees afterwards
- **the palette's name being recorded in the project's config** — an edit to a file outside the CMS,
  and the whole of what makes the exclusion work
- **a page being created and arranged** — content, and reversible by a person deleting it
- **the grouping and the wording** — the vocabulary every later reader of that page will use

**Nothing is written before a person says yes, and a yes to one section is not a yes to another.**
An unscoped yes — "looks good", "go ahead" — covers the page and its content. It does not cover
creating schema, and it does not cover editing a file in the repository; ask about those two
separately, and read silence about either as no. Where the answer is partial, do the approved part
and report the rest as declined, by name, so the next run's operator knows what is outstanding.

## Step 8 — Write, after approval

In this order, confirming each before the next:

1. **The three showcase element types**, under the aliases the `## Editor guides` slot records, or
   the reference's defaults where it records none. The slot records what a project *used*, never
   what it should use, so where an alias is already taken by something unrelated, pick another,
   say so, and record what you picked.
2. **The palette** — a block-editor palette of their own, holding those three and nothing else. Not a
   general palette, and *The showcase element types* gives the reason. **Of their own** is the part
   that matters operationally: the exclusion drops what this palette *alone* offers, so anything else
   put here that no other palette offers leaves the count too — while a component this palette shares
   with a general one stays counted, which is the behaviour that makes sharing safe.
3. **The palette's name, written into the `## Editor guides` slot.** This is the whole of the fix
   above, and it is not optional. **Both readings of the project take the exclusion** — the
   inventory report and the audit build their counts separately — so one recorded name is what makes
   both correct, and neither of them falls back to the default when the slot is empty. The reference
   argues that at the slot itself: a project that has not recorded the palette gets a wrong line
   rather than a wrong count, and the line is only wrong until somebody writes this.
4. **The page**, under the styleguide's kind container. **Do not write a stored source reference
   onto it.** A styleguide documents the system rather than a component, so there is no source to
   record and no signature to compare; a reference written here would put the page into the audit's
   staleness comparison against a component that does not exist.
5. **The content** — the showcase elements, in the page's own content area, in the arrangement that
   was approved. Leave a caption empty where nobody wrote one; nothing regenerates it and nothing is
   reported when it is missing — **except a form field's label**, which is not an editorial caption
   but the only name that control will ever have. Where the specimen includes form fields and no
   label was given, write the rest and **name that gap in the report**. It is the one empty caption
   on this page that leaves something unusable rather than merely undescribed.
6. **Nothing else.** Not the page's name after it is created, not its address or visibility
   settings, and not any other page in the section.

Then **read each written value back**. A successful request means the write was accepted, not that
the value is what you intended — an alias can resolve to something other than the field you meant,
and a palette can be saved with a block list the CMS reordered.

**Where a read-back differs, stop writing and report the difference.** Print what you sent beside
what came back, name the thing, and do not retry: a second write against a value the CMS already
changed once is how something ends up holding neither version. A section half written is one a
person can finish; a section written past a failure nobody was told about is not.

**Never create a public URL without confirmation.** Save the page rather than publishing it, and ask
before publishing — publishing puts it on the public site and on the derived index both.

**No view is written in this step, and none anywhere in this spell.** Views are Step 9's territory,
and it writes none either — it hands them to `/block`.

## Step 9 — Hand the views to `/block`

**This pack ships no view for any of the three showcase element types**, and this spell writes none.
The reference says why at *The showcase element types*: the element type and its fields are the
schema, and the markup that renders one belongs to the project, taken from the conventions its own
blocks already carry.

So authoring those views is `/block`'s work, at its Step 5 — and **this spell suggests that cast
rather than making it.** Spells in this spellbook chain by suggestion and none invokes another: a
spell a person did not cast is one they did not agree to and did not see the reasoning of.

Two things to say when you hand it over, because whoever writes the view has to know them and
neither is enforceable by anything in this pack:

- **The element types and the palette already exist** — Step 8 created them. The cast that follows
  is for the views, not for the creation steps, or it will propose making what is already there.
- **Two requirements the reference puts on these views specifically**: a swatch has to render its
  token's name as text, and a specimen has to keep the semantics of what it shows. Both are argued
  at *The showcase element types*, and both are enforced nowhere — this pack ships no markup, so
  nothing in it can check them. They are written down so a page failing them fails a review rather
  than a run, and that only works if the person writing the view has read them.

## Step 10 — Report

```
Styleguide: <Page Name>   Container: <the kind container, created or found>
Layers: <every layer found>   Authoritative: <the one the page reads>
Tokens: <N> colors, <N> unclassified (<N> grouped with you, <N> left ungrouped)
Scaffolded: <element types created> in palette <name>
Recorded: <the slot line written, or "not recorded — the audit will report these as undocumented">
Showcase: <N> swatches, <N> type specimens, <N> element specimen
Themes: <how the set is presented, and what decided it — or "the project does not theme its blocks">
Drift: <editor-facing styles setting literals that trace back to no token, or "none found">
Written: <what reached the CMS, or "nothing — declined">
Awaiting a person: <views, captions, publishing>
Next: /block <the swatch showcase element>   (author its view — the element type and its palette already exist)
```
