---
name: test-content-principles
description: How to decide which variations of a component a QA test page shows, the recipe format that records them, and what a project's builder owes a recipe. Consult when writing, refreshing or reviewing a test-content recipe, when editing a project's test-content rules, or when building or changing the builder that consumes recipes.
---

# Test content: what to test, and how a recipe records it

A component that editors configure has more ways to be filled in than anyone tests by hand. A
test-content page shows every meaningful one in one place, so a developer can check a component
right after building it and QA can run the same checks again at every regression pass.

This file holds the part of that work that holds for any stack: **which variations a component
earns, and how they are written down.** The part that differs by platform (how a component's schema
is read, what a page's layout vocabulary is, how a value is stored, how the builder is built) is the
stack pack's, where one is installed.

## Two halves, split by job

- **A recipe decides what to test.** It is one committed JSON file per component, written by the
  stack's `/test-content` spell with a developer in the loop. It names every variation, the value
  each one sets, where each one sits on the page, every rule applied and every gray-area answer.
- **A builder builds it.** Project code, run by an administrator from the CMS's admin UI, reads the
  committed recipes and creates or updates the test pages in each environment that allows it.

The split is what makes the pages trustworthy. A recipe is reviewed like code and reaches every
environment with the normal deploy. A rebuild gives the same pages at the same addresses. And
because the recipe records the schema it was written against, the builder can say when a recipe has
fallen behind its component, which a hand-built test page never does.

**The spell writes the recipe and nothing else.** It reads the CMS but never writes to it. A project
with no builder yet gets the recipe and a note that nothing can build it; the stack pack's builder
blueprint, where installed, is the starting point for writing one.

## Rules come from two places

- **General rules (G1 to G12)** are below. They hold for any component on any site.
- **Project rules (P1 onwards)** live in the project's test-content rules file, which **QA owns**
  and developers can edit. It holds this site's page layout (its widths and row backgrounds), its
  sample values, its item counts, and the hand-picked combinations QA knows are risky. The stack's
  spell says where the file lives. `templates/test-content-rules.md`, beside this file, is a
  starting point for a project that has none.

The spell reads the whole project rules file on every run and applies every rule in it. It never
states a project rule in the recipe as though it were general, or the other way round. Every rule a
recipe applies is listed in its `rules` array with its source, `skill` or `project`, and its number.

### General rules

- **G1. A realistic baseline.** The first variation, labeled "Baseline", fills every field an editor
  normally fills, with realistic copy and each dropdown at its default option. Every other variation
  starts from it. A required dropdown with no configured default is a gray area: propose the option
  the view falls back to when the value is empty, or the first option when it has none.
- **G2. Layout-affecting differences vary one at a time.** Each one gets its own variation,
  differing from the baseline in exactly that one setting:
  - every dropdown option other than the baseline's;
  - every toggle, flipped;
  - every optional field whose absence changes the layout (an image, a teaser), left empty.

  Its label names the difference, for example "Background: Primary Tint" or "No Image".
- **G3. Content stress is separate from layout.** Text whose absence or length only makes the
  component shorter or longer is stress, not layout. Stress cases follow the project's rule for
  combining them; they never get a variation each.
- **G4. Width-sensitive settings.** When a field's help text or the component's view says a setting
  behaves differently at some widths ("only applies at 75% to 100% of the row"), the setting is
  width-sensitive. It also appears in the layout section at those widths. Which widths is a gray
  area: ask.
- **G5. Inline by default.** Every component is placed inline on the test page. A shared (reusable)
  copy is used only when the thing under test is shared-block behavior, or a project rule asks for
  one.
- **G6. Test content references only test content.** Every link, image and shared block is a token
  (see *Values*). A real page, media item or shared block is never referenced, and the builder's
  validator refuses a raw id or key. The one exception is a piece of real content the project names
  in the builder's configuration, placed by that name and only where a project rule asks for it.
- **G7. Nested items are realistic too.** In a list of nested items (tiles, panels, cards), each item
  is a plausible one, not a copy of the first. Vary the nested items' own settings by G2 inside one
  parent, not one parent per setting, unless the setting changes the parent's layout.
- **G8. Hand-picked combinations go on top.** Add the project's combinations for this component, and
  any the developer names, after the one-at-a-time variations. Label each with every setting it
  combines.
- **G9. Common setups come first.** Before any variation, show the component the way editors most
  often use it, such as 3 in a row and 2 in a row for a card. Components that share a row get
  different images, backgrounds and amounts of text, so QA can check they line up. Where the
  components carry links, one of them uses a generic label ("Read more") beside differently labeled
  ones, so QA can check each link still says where it goes. Which setups are common is a gray area
  when the component's guide or the site's pages don't make it plain: ask.
- **G10. Mix the backgrounds.** Wherever a row isn't testing the background itself (common setups,
  the extra components that fill a layout row), give the components different background or color
  options, so the page isn't mostly one background. The first component in a layout row stays the
  baseline.
- **G11. Rich text on every background.** When a component has a rich text field and a background or
  color option, show the rich-text sample on every option. Rich-text styles (links, buttons, tables)
  that break on a dark background are a common bug.

  **Recognize a color option by what the view does with it, not by its name.** A field called
  "level", "priority" or "style" whose options map to different background or text colors is a
  color option for G10 and G11, however it is labeled.
- **G12. Interactive states and motion.** A component that opens, closes or switches (an accordion,
  tabs, a modal, a carousel) appears both in its default state and in its other state where an
  editor setting can start it there; where only a visitor can change it, the row's `description`
  tells QA what to do ("Open the first panel"). A component that moves on its own or animates gets a
  `description` telling QA to check it with reduced motion turned on, and that it can be paused.

## The shape of a run

Read the rules, read the component, find old test content, plan, ask, write, check, report. The
stack's spell supplies the commands for each step; what each step owes is the same everywhere.

1. **Read the component**: every property, inherited ones included, with its editor, whether it is
   required, its help text and every dropdown option exactly as the schema spells it. Read the view
   too: which settings change the layout (a class, a different partial) and which only change text
   answers G2 and G3 for most fields.
2. **Find the old test content to take over.** Hand-built test pages and test blocks named after the
   component usually exist already. Show the developer each candidate with its location and what
   references it, and list only the confirmed ones in `legacy`.
3. **Plan.** Show the plan as a short list (label, what differs from the baseline, the rule behind
   it) before writing anything.
4. **Ask about the gray areas** (below).
5. **Write the recipe.**
6. **Check it** with the builder's validator, and fix every problem it names in this recipe.
7. **Report** (below).

### Ask about gray areas, one at a time

Ask about every gray area instead of guessing. **Ask one question at a time**, each with the answer
you propose and why, and wait for the answer before the next. Typical gray areas:

- the widths at which a width-sensitive setting (G4) should also appear;
- whether an optional field is layout-affecting (its own variation) or stress (combined);
- an item list with no maximum;
- a required dropdown with no configured default (G1);
- a field the builder can't set yet;
- an old item found in step 2 that might be real content;
- anything the project rules don't settle for this component.

Record each answer in the recipe's `decisions` array as `{"question": "…", "answer": "…"}`, and make
the recipe's shape follow it. A rerun reads these answers back and doesn't ask again unless the
schema changed what the question was about.

## The recipe

```json
{
  "id": "cardItem",
  "component": "cardItem",
  "kind": "block",
  "title": "Card",
  "expects": {
    "properties": ["image", "imagePosition", "title", "teaser", "link", "background"],
    "options": { "imagePosition": ["Above (Default)", "Beside"] }
  },
  "rules": [ { "rule": "G2 Every dropdown option varies alone from the baseline", "source": "skill" } ],
  "decisions": [ { "question": "…", "answer": "…" } ],
  "page": {
    "name": "Card",
    "sections": [
      { "kind": "opening", "rows": [ ] },
      { "kind": "commonSetups", "title": "Common Setups", "rows": [ ] },
      { "kind": "variations", "title": "Variations", "rows": [
        { "id": "variations-1", "label": "Baseline and Primary Tint", "rowType": "…", "settings": {},
          "items": [ { "id": "baseline", "label": "Baseline", "span": 6, "type": "inline", "values": { } } ] } ] },
      { "kind": "layout", "title": "Layout", "rows": [ ] }
    ]
  },
  "sharedBlocks": [],
  "legacy": []
}
```

- **`id`** is the component's alias, or for a behavior that spans components (such as how external
  links are marked) a name for the behavior. **`title`** and **`page.name`** are the component's
  editor-facing name; the page name sets the address.
- **`kind`** is `block` for a component placed on a page, or `pageType` for a page type (see
  *Page-type recipes*).
- **`expects`** lists **every** property alias the component has, inherited ones included, and
  **every** dropdown's options exactly as the schema spells them. The builder compares it with the
  live schema to mark the recipe out of date, so a partial list is out of date on day one.
- **`otherComponents`** declares every other component the recipe places, each with its own
  `properties` and `options` exactly as `expects` does, so a change to any of them marks the recipe
  out of date too. An item of another component names it with `"component"`.
- **Row and item `id`s** are short kebab-case names, unique across the whole recipe. The builder
  derives each page's and block's key from them, so **never rename an id that already exists**: a
  renamed id is a new item, and the old one is removed.
- **`rowType`**, **`settings`**, **`span`** and the allowed item `type`s are the page's layout
  vocabulary. It belongs to the project's page grid, so the project rules file and the builder's
  validator define it, not this file. `span` counts columns of 12 unless the project says
  otherwise; where the platform expresses width as a named option rather than columns, the project
  rules map each span to its option. **Where the
  page body has no widths at all** (a single-column list of components), every item spans 12, rows
  hold one component each unless the row tests components side by side, and the recipe has no
  `layout` section unless the rows themselves have settings worth varying, such as a background.
  **Fill every row**: a component alone on a half-empty row hides how it sits next to others.
- **`sharedBlocks`** declares each shared test block, `{"id", "name", "values"}`, plus `"component"`
  when it is not of the recipe's own component. The builder creates it in its test-blocks area.
- **`legacy`** lists old hand-built test content the first build takes over: `{"key", "name"}`. The
  builder moves each to the recycle bin, or keeps it and reports it when real content still uses it.

### Sections and labels

Section kinds, in page order: `opening`, for anything that must open the page with no heading (a
theme switcher, where the project rules call for one), then `commonSetups`, `variations` and
`layout`. An `opening` section has no `title`, and the validator refuses one that has; every other
kind has one. A recipe with nothing to open the page leaves the `opening` section out.

- **Labels show on the page, and the headings never skip a level.** The page's own title is its
  level-1 heading. A section with a `title` opens with a level-2 heading, and each of its rows opens
  with its `label` as a level-3 heading. In a section with no title, each row's label is a level-2
  heading itself, which in practice means the `opening` section. A row's `description`, if any, is
  a paragraph under its heading. A row with a description must have a label, so no paragraph sits
  under a missing heading; the validator refuses one without. Any heading inside a component's own
  content (the rich-text sample's) sits one level below the row's.
- **The row headings are the test page's own, and QA expects them** in a heading outline or an
  automated heading-order check. What QA is checking is the heading level the component itself
  renders. Where an editor sets that level, vary it by G2 and name the effective level in the row's
  `description`.
- **The label names the row's focus and nothing else**: "Secondary Tint and Primary Brand", "Image
  Beside at 25%". No "Variations:" prefix; the section heading already says it.
- **Section titles and row labels are in title case**, with "Setting: Value" where a row combines two
  settings ("White: Content Width"). Descriptions are sentences.
- **Write numbers as numerals** ("3 in a Row") and **use Oxford commas** ("Primary Tint, Secondary
  Tint, and Primary Brand").
- **Add a `description` only when the label can't carry it**: what QA should look for ("all 3 should
  be the same height"), which component is which when the order doesn't make it plain, something QA
  has to do ("Open the first panel"), or an effect QA can't see ("the panel titles are level-2
  headings"). A layout variation that changes the visual order (an image beside the text, a reversed
  row) tells QA to tab through it, since the reading order may not follow. Never restate the label.

### Values

`values` maps a property alias to its value. Leave a property out to leave it empty. Plain values
are literal; anything that points at content is a token.

| Field | Value |
|---|---|
| Text | a string |
| Dropdown | the option text exactly as the schema spells it: `"Primary Tint"` |
| Toggle | `true` or `false`; leave it out for the default |
| Rich text | an HTML string, or `{"$richText": "sample"}` for the project's sample |
| Internal link | `{"$link": "test-content", "title": "Button text"}`, the test-content root page |
| External link | `{"$external": "https://example.com/", "newWindow": true, "title": "…"}` |
| Image | `{"$media": "<name>"}`, one of the builder's test images |
| Shared test block | `{"$shared": "<sharedBlocks id>"}` |
| Named real content (G6) | `{"$real": "<name>"}`, a name configured in the builder |
| Nested list | an array of objects, one per item, each following these same rules |
| A single nested component | `{"$block": "<alias>", "values": {…}}` |
| A list of components | an array of `$block` or `$shared` objects; each may carry a `span`, mapped to a width as the project rules say |

The builder may add tokens of its own (a member group, a category). The project rules file lists
them. **A token object holds exactly one token** (arrays of token objects are fine), **and a raw
id, key or CMS-internal reference is refused anywhere in a value.**

### Page-type recipes

A page type's own fields can't differ between components on one page, only between pages. So a
page-type recipe builds **a test page and a few variation pages beneath it**.

- **`page`** is the test page. When the test page can be of the type under test, it is the baseline
  and its `values` set its own fields. When it can't, it carries no `values` and the baseline is the
  first of `pages`.
- **`pages`** lists the variation pages, built beneath the test page in order. Each has an `id`, a
  short title-case `name` naming its main difference, `values` (a field left out is left empty, so
  each page repeats the baseline's values and changes only what it tests), `sections`, and
  `component` when its type is not the recipe's own. A page's own `pages` are built beneath it.
- **Keep the page count down.** Combine one-at-a-time differences onto a few pages wherever they
  can't hide each other, and label the page's first row with every setting it combines (G8). Keep a
  difference on its own page only when it would hide another, such as an empty body. Aim for 3 to 5
  pages beneath the baseline, and show the planned grouping before writing.
- **Group by what QA looks at.** Settings that remove the page's chrome fit together; fields that
  show only in the document head (SEO and social fields) fit with a heading override.
- **Every generated page is kept out of search and the main navigation.** The builder sets that on
  every page and refuses a recipe that tries to set it.
- **G3 stress** is combined with another page's differences, not given a page of its own.
- **A field that renders nowhere** is a gray area: ask.

### What the builder can't express yet

When a field's editor isn't one the builder supports, don't work around it. Ask, leave the field or
row out, record the decision, and name it in the report. A required field left empty is never
built: a page holding an invalid component can't be published, and the schema tests already prove
the field is required.

### Refreshing an existing recipe

When the recipe already exists, keep every variation that still applies with its `id` unchanged,
update `expects`, add and remove variations as the schema now requires, and keep earlier
`decisions` that still hold. Show the differences (added, changed and removed variations, and the
new `expects`) before writing.

## What the builder owes the recipe

The stack pack's builder blueprint, where installed, says how to build each of these on its
platform. Whatever the platform, a builder that consumes recipes guarantees:

- **A validator the spell can run**, as a test over every committed recipe, naming each problem by
  its path in the recipe (`cardItem: page.sections[1].rows[0].items[2].values.link`).
- **Stable keys.** Every page and block key is derived from the recipe id and the item's id path, so
  a rebuild updates in place at the same address.
- **Freshness.** It compares `expects` with the live schema and reports a recipe out of date, never
  silently building fields the component no longer has.
- **A build state per recipe**: out of date, never built, needs a rebuild (the recipe changed since
  the last build), or up to date. The fingerprint behind "needs a rebuild" covers only what decides
  the build, so rewording a rule or decision doesn't ask for one.
- **Isolation.** Test pages, test media and shared test blocks live in their own areas. Generated
  pages are kept out of search and the main navigation.
- **Removal of what a recipe no longer lists**, and the legacy takeover described under *The recipe*.
- **Optional protection for hand edits**: a page changed by hand since its last build is skipped and
  reported rather than overwritten, when the administrator asks for that.
- **Access control.** Building is limited to named environments and to administrators.
- **Safe on a shared environment.** One build at a time across every server, not just within one
  process; the build runs in the background with visible progress rather than inside one admin
  request; and what a publish triggers (search indexing, cache purges, outbound calls) is known
  before the first build there.
- **A usable admin screen**, by keyboard and with a screen reader:
  - the recipes are a real table with column headers, and each recipe's build state is text, not
    color alone;
  - every control is a native button, checkbox or link, and each one's accessible name includes its
    recipe ("Build Card", not a column of "Build"); the hand-edit option is a labeled checkbox;
  - one status region, present on the page before its text changes, announces a build's start, its
    progress at a few milestones and its result; a refusal (another build running, an access check,
    a validator problem) and a failure are announced as alerts and name what refused;
  - polling for progress updates the status text without redrawing the list, so focus stays where it
    was and the whole list isn't read out again.

## The report

Tell the developer:

- **the rules applied**, as a table of rule, source (`skill G2` or `project P4`) and the variations
  each produced;
- **the decisions**, each question with its answer;
- **the legacy items** to be taken over, and which ones real content still uses, so the build will
  keep them;
- **what was left out** because the builder can't express it yet;
- **next steps**: commit the recipe, deploy it, and build it from the builder's admin screen. A
  rebuild keeps the same addresses.
