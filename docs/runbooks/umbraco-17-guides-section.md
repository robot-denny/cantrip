# Runbook: setting up a guides section from nothing

**Who this is for:** anyone setting up an Umbraco project's editor-facing guides section for the
first time. You'll want to be comfortable creating document types in the backoffice and editing a
Razor template. You don't need to have read any of the toolkit's skills.

**When you need it:** before you cast `/guide` for the first time on a project that has no guides
section yet. `/guide` writes the guide *pages* — it doesn't create the document types those pages are
built on, and it won't guess where you'd want them to live. This is everything that has to be in
place first.

**How long:** about half an hour for the schema, plus whatever your templates take.

---

## What is preset vs what you define

Most of this runbook is mechanical — the same on every project that will ever run `/guide`. The rest
is yours, and the division is intentional: *conform where it shows, standardize where it does not*.
Editors and visitors see your markup, so markup should conform to your project conventions. Nobody
ever sees a document type alias, so standardizing those lets one shared reference describe them for
everyone.

| | |
|---|---|
| **Fixed** — identical everywhere | Four document types, their aliases, their property aliases, and the rule that every property is optional |
| **Yours** | The section's name, URL and position in the tree; the markup inside two templates; which property editor your content area uses |
| **Yours, but only if overridden** | An alias, where the default is already taken by something unrelated in your project |

**About that last row.** Every alias below is a *default*, not a rule. Two document types can't share
an alias, so if one of these names is already taken in your project, pick another — and make a note
of which one, because you'll record it in Step 8. The config records what a project **used**, never
what it was supposed to use.

---

## Phase 1 — The schema (backoffice)

Four document types. Build them in this order, since each one refers to the one before it.

### Step 1 — Element type `editorGuidePropertyRow`

**Settings → Document Types → Create → Element Type.**

This is one row of a guide's property table — a single field of your component, described the way an
editor meets it.

| Property alias | Editor | What it is |
|---|---|---|
| `alias` | Textstring | The documented field's alias. **The row's identity** — rows are matched on it, ignoring case |
| `label` | Textstring | The label an editor sees |
| `required` | True/false | Whether the field is mandatory |
| `tab` | Textstring | The tab the field sits on |
| `group` | Textstring | The group within that tab |
| `information` | Rich Text Editor | What an editor needs to know about this field |

The first five get rewritten for you whenever your component's schema changes. **`information` never
does.** Once someone has written in it, it's theirs — nothing compares it, nothing suggests a
replacement, and nothing overwrites it. And if a row ever has to be removed while carrying one of
those notes, you'll be asked first rather than told afterwards.

Notice that the rows are flat. Each one carries its own `tab` and `group` as ordinary text rather
than sitting inside nested containers, which is what lets a field move from one tab to another as a
small, readable change instead of a row shuffling between containers.

### Step 2 — Document type `editorGuide`, **with a template**

**Settings → Document Types → Create → Document Type *with* Template.** Tick the template box —
Umbraco will create `editorGuide.cshtml` and name it for you, and you'll fill it in at Step 5.

This is a guide: one per component or page type you document. The same type also serves the guides
your team writes entirely by hand.

| Property alias | Editor | What it is |
|---|---|---|
| `guidePurpose` | Rich Text Editor | One sentence saying what this component is for. First on the page |
| `guideWhenToUse` | Rich Text Editor | When to reach for this component and when to reach for another |
| `guideProperties` | Block List — palette: `editorGuidePropertyRow` **only** | The property table |
| `guideExamples` | Your project's own content-area editor (Block Grid or Block List), with your **normal** block palette | Live instances of the component |
| `guideScreenshots` | Media Picker (multiple) | What a live example can't show — a property panel, a settings screen |
| `guideBlurb` | Textstring | Optional. Changes the index listing's wording only |
| `guideSource` | Textarea | The tooling's bookkeeping. See the note below |

**Leave every one of these optional — don't mark anything mandatory.** That isn't fussiness. A
required field here breaks three things that all need to work:

- An editor should be able to create a guide with nothing on it but a name, and fill in the rest
  themselves.
- A generated page gets created *before* anything is generated into it, because every write waits for
  someone to approve it. The page has to be saveable while those fields are still empty.
- An empty `guideSource` is how the tooling knows *nobody generated this page*. Make it required and
  you lose the one thing that tells a hand-written guide apart from a stale generated one.

**A note on `guideSource`.** It holds four values — which component the guide documents, what kind of
thing that is, a signature of its shape, and which source the tooling read it from — so it needs a
property that can store and hand back a small piece of JSON. A Textarea does the job; the toolkit
doesn't insist on that particular choice. Two things it *does* insist on: keep the reference in one
property and nowhere else, because two copies can drift apart and nothing afterwards can tell you
which was written last; and treat the signature as opaque, since it gets compared but never read.

**Give `guideExamples` your real block palette, not a special one.** A live example is a genuine
instance of the block, sitting in the page and rendered by your site like any other content. It isn't
a screenshot, and it isn't generated artwork.

### Step 3 — Document type `editorGuideGroup`

**Create → Document Type** (no template).

A container that marks one kind of guide. It needs a single property:

| Property alias | Editor | What it is |
|---|---|---|
| `guideKind` | Textstring | Which kind of guide this container holds |

Under **Structure**, allow `editorGuide` as a child.

Don't give it a template. Its own URL will return a 404, and that's fine — it's a shelf, not a page.
The kinds themselves are `element` for a block's guide and `document` for a page type's, and
**you won't be creating these containers yourself**: `/guide` makes the one it needs, when it needs
it.

### Step 4 — Document type `editorGuideIndex`, **with a template**

**Create → Document Type *with* Template.**

The section's landing page. It needs **no properties at all** — it works out its list of guides when
it renders.

Under **Structure**, allow `editorGuideGroup` as a child. Then open your **Home** document type (or
wherever you want the section to sit) and add `editorGuideIndex` to *its* allowed children.

There's deliberately nowhere on this type to store a list of guides. A stored list is just a second
copy of the content tree, and it goes wrong the moment anyone adds, renames, unpublishes or reorders
a guide — you'd have to run something to put it right, and in between it would be quietly wrong.
Worked out at render time instead, publishing a guide is all it takes to add it to the index.

*Optional:* once a kind holds a lot of guides, turning on a list view for `editorGuideGroup` is fine.
It only changes how the backoffice presents them — the guide pages are still children of the
container, which is all the tooling looks at.

---

## Phase 2 — The templates (code)

**The toolkit ships no views, no markup and no class names.** The approach is the one `/block` uses:
**find your closest existing template and follow it.** Your project's existing pages already show how
you handle a rich-text body and a block area, so you almost certainly have something to copy here.
Don't invent a new convention — whatever you write becomes the pattern every future guide follows.

### Step 5 — `Views/editorGuide.cshtml`

Render the purpose sentence, the when-to-use section, the property table, the live examples and the
screenshots, in whatever order and markup suits your project.

**One thing isn't up to you: the template does the grouping.** The property rows arrive flat, each
carrying its own `tab` and `group` as text, and it's your template that groups them for display.
That's what lets a property move between tabs without anything stored having to change.

**Render the alt text on your screenshots.** A screenshot in a guide is doing real work — it's often
the only place an editor will ever see a particular settings screen — so make alt text required on
the media type and put it on the page. Nothing in this toolkit creates media or could write those
words for you, and the person uploading the image is the last one who knows what it shows.

### Step 6 — `Views/editorGuideIndex.cshtml`

List the published guides by walking this node's children (the kind containers) and then their
children.

**Two rules here, and both matter:**

1. **Read only three things from each guide: its name, its URL, and its blurb-or-purpose line.** Not
   the property rows, and not the live examples. The obvious approach — ask each guide for its
   content and take a teaser from it — pulls in everything that guide holds. Forty guides with twenty
   rows each means loading **eight hundred table rows, plus every live example**, just to print forty
   names and forty sentences. Kept to three values, it's one cheap read per guide.
2. **Render that line as plain text, never as markup.** Use the blurb where a guide has one and the
   purpose sentence otherwise — one or the other, never both. The purpose sentence is rich text and
   nothing caps its length, so what comes back may contain paragraphs, lists or a link. Your index
   entry is almost certainly a link itself, and a link inside a link is broken markup: keyboard users
   can't reach it and screen readers can't make sense of it. Take the text, trim it, print that.

---

## Phase 3 — The node and the config

### Step 7 — Create and publish the section

**Content → under Home → create an `editorGuideIndex`.** Call it whatever reads well — `Guides`,
`Editor Guides`, `_guides`. Publish it.

You aren't locked into any of that. The name, the URL segment and the position in the tree stay
changeable forever. An editor can rename this node next week, and someone can move it when the tree
gets reorganized, and nothing breaks — the toolkit finds it by its stored key rather than by its
route or its name. If you'd rather it didn't show up in the main navigation, use `umbracoNaviHide` or
filter it out in your nav template. That's a rendering choice, not a reason to give the node an
awkward name.

One thing worth being clear about: this node isn't a folder that *contains* an index page. It **is**
the index page. A folder plus a separate index would leave you with one node that renders nothing and
another that nothing can link to.

### Step 8 — Record the key

Open the node, go to the **Info** tab, and copy its **GUID**.

Then add it to `.agents/config/conventions.md`:

```markdown
## Editor guides

- guides node: 8f3a1c2e-0000-0000-0000-000000000000
```

If you used all the default aliases, that single line is the whole thing — everything else falls back
correctly and there's nothing more to write down. If you had to pick a different alias anywhere in
Phase 1, record what you actually used under the same heading.

**This is the one fact only your project can supply.** `/guide` won't go hunting for the section by
name, and it won't write anything until this line exists. Searching by name can find the *wrong*
node, and writing editor-facing pages into some unrelated corner of your content tree is far worse
than finding nothing at all — because finding nothing is something it can tell you about.

### Step 9 — Serialize the schema, and check the other slot

Export your new document types however your project normally does it — uSync, or Umbraco Deploy — and
commit them.

It's worth doing this *before* your first cast rather than after. `/guide` prefers to read component
schema from files, in this order: Deploy artifacts (`*.uda`), then a uSync export, then committed
generated models. A project with none of those gets read from the running site instead. That works,
but it can never confirm that nothing has changed — so every later run will offer to regenerate
rather than simply telling you the guide is still current.

If nobody has recorded which format your project uses, add it to `.agents/config/stack.md` under
`## Schema serialization`.

---

## Phase 4 — First cast

### Step 10 — `/guide <yourComponentAlias>`

Every run goes the same way: **read, plan, show, ask, write.** Nothing reaches your CMS before the
ask.

What to expect the first time:

- It creates the **kind container** if there isn't one — an `editorGuideGroup` with `guideKind`
  filled in. Your first block guide and your first page-type guide will land in two different
  containers, both created as needed.
- It fills the seeded fields **only when the page is created**: the purpose sentence, the when-to-use
  section, and the live examples. **Skip one of those now and you won't be offered it again** — so
  give them a proper look rather than waving them through.
- It writes the stored reference **last**, after the content it describes. A page claiming a
  signature it doesn't match is worse than one claiming none at all.

Then read the purpose sentence and rewrite it in your own words. That's how it's meant to go: the
model drafts it, you rewrite it for the editors you actually work with, and nothing will ever
regenerate over your wording.

### Step 11 — `/guide --audit`

Run this once your first guides exist. From then on it's what tells you which components have no
guide yet, which guides name a component the project no longer holds, and which have gone stale.

---

## When something looks wrong

**A run fails partway through, or a page won't save.** Check that nothing from Step 1 or Step 2 is
marked mandatory. This is the most common setup mistake, and it doesn't show up until late.

**The audit says every component is undocumented.** The recorded key didn't resolve to anything — the
node was deleted, or moved, or the key belongs to another environment's copy of the site. The audit
stops rather than reporting an empty section, because an empty section and a missing one look
identical in the count and mean opposite things.

**`/guide` says two containers claim the same kind.** That's a legitimate state to end up in — an
editor can create a second container, and an import can produce one. Nothing picks between them for
you, because picking whichever was found first would file guides into whichever node happened to sort
earlier, differently from run to run. Merge or delete one, then run it again.

**A guide you wrote by hand is offered a whole property table.** Expected. A page with no
`guideSource` has no machine-owned fields at all — everything on it is yours — so the run only
proposes, and your prose is listed and kept rather than replaced. Approving the reference is what
makes that page's machine-owned columns machine-owned from then on. It's the one approval on a guide
page that editing won't undo.

**Everything looks right but nothing gets found.** Containers and guide pages are matched on their
document type, never on their name. Check the aliases rather than the labels.

---

## Where the authority lives

This runbook repeats things that are defined properly elsewhere, because you need them in one place
while you're clicking through the backoffice. Where it disagrees with any of these, **they're right**:

- [`umbraco-17-guide-scaffolding`](../../skills/umbraco-17/reference/umbraco-17-guide-scaffolding/SKILL.md)
  — the schema: which types exist, what the property row carries, where guides live, what the index
  reads, and the config slots.
- `REGISTER` in
  [`changeplan.py`](../../skills/umbraco-17/spellbook/guide/scripts/guidelib/changeplan.py) — the
  guide page's field set and what each field is for. The single source of truth for those seven
  aliases.
- [`/guide`](../../skills/umbraco-17/spellbook/guide/SKILL.md) — the run itself, and the audit.

Everything about the styleguide is left out on purpose. A guides section is complete with four
document types. The three showcase element types a styleguide needs get created by `/styleguide` the
first time you scaffold one, and not before.
