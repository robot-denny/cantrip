---
name: test-content
description: Write or refresh the test-content recipe for one Optimizely CMS 12 block or page type, the committed JSON file the project's test-content builder turns into QA test pages. Reads the content type's class and views, applies the general variation rules and this project's QA-owned rules, finds the component's old hand-built test content to take over, asks about every gray area, writes the recipe, and checks it with the builder's validator. Use right after building or changing a block or page type, or when the builder marks a recipe out of date.
disable-model-invocation: true
argument-hint: "<content type class name, e.g. CardBlock or ArticlePage>"
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(dotnet test:*)
---

The user's argument: **$ARGUMENTS**, the content type to write a recipe for: a block type, such as
`CardBlock`, or a page type, such as `ArticlePage`.

**This spell decides what to test; the project's builder builds it.** It writes one file, the
recipe, and nothing else. It never writes to the CMS. An administrator builds the test pages later
from the builder's admin page.

Read `test-content-principles` in full now. It holds the method this spell applies: the general
rules G1 to G12, the gray-area discipline, the recipe format, labels, value tokens, page-type
recipes, refreshing, and the report. Every step below names what it adds for Optimizely CMS 12 and
otherwise follows that reference. `optimizely-12-test-content-builder` is the other half: what the
builder does with a recipe, and how to build one.

## Step 0 — Find the recipes, the rules and the builder

**Slot:** `.agents/config/paths.md` → `## Test content`
**If empty:** look for a recipes directory (a folder named `Recipes` beside the builder's code) and a
rules file at `.agents/config/test-content.md`. With no builder, stop and say so: nothing can build
a recipe yet, and this pack's builder blueprint is where to start. With a builder but no rules file,
offer to copy the starter rules from the `test-content-principles` template, and stop until QA has
confirmed them.

The slot names three things: the **recipes directory**, the **project rules file**, and the
**builder's validator test** (the test that loads every committed recipe). Read the whole rules file
now and apply every rule in it. The rules file also defines this site's **page layout vocabulary**:
which content area or grid property a row is, which display options stand for which widths, and
which row settings exist. Read it there; the builder's validator is the authority when the two
disagree, and a disagreement is worth reporting.

## Step 1 — Read the component

In CMS 12 the schema is code. Find the class whose `[ContentType]` attribute or name matches the
argument, and read it with every base class it inherits from, since inherited properties are part of
`expects`. For each public `virtual` property not marked `[Ignore]`, note:

- its **name** (the property alias a recipe uses) and its **type**;
- `[Display(Name, Description, GroupName, Order)]`: the description is the help text, and image
  size hints usually live there in free text;
- `[Required]`, `[CultureSpecific]`, `[StringLength]`, `[AllowedTypes]` (which may name an
  interface, so find every type that implements it), `[UIHint]`;
- **list limits**: the CMS has no single attribute for a content area's or list's maximum item
  count, so find how this project enforces one (often its own validation attribute or an
  `IValidate<T>`), and read the maximum from there. With none, the list has no maximum;
- **dropdowns**, in any of their forms: `[SelectOne]` or `[SelectMany]` with a selection factory
  (read the factory for its options), an enum property (read the enum's members and their display
  names), or a project attribute that wraps either;
- **defaults** set in `SetDefaultValues`, which is what the baseline's untouched fields will hold.

Then:

- **Read the views** for this type, one per display option or rendering tag where the project uses
  them, to see which settings change the layout and which only change text. That answers G2 and G3
  for most fields; ask about the rest.
- **Read the display options the block supports.** A project may register display options globally
  and let each block narrow them. Its supported options are the widths its layout rows can use.
- **A selection factory that calls a service at edit time** has no fixed option list. Its options
  can't go in `expects`: ask how to treat it, and record the decision.
- **The kind decides the recipe.** A `BlockData` type is a block recipe (`"kind": "block"`). A
  `PageData` type is a page-type recipe (`"kind": "pageType"`). The start page can't have one: say so
  and stop.
- **For a page type, read every component it places too**: the block types its content areas allow,
  any block-typed property (a local block), and every page type allowed beneath it. Each goes in
  `otherComponents`.
- **A behavior that spans blocks** gets a recipe too. Its `id` names the behavior, `component` is the
  block most of the page uses, and `otherComponents` names every other block it places.

If a recipe for this type already exists, read it too. This run refreshes it.

## Step 2 — Find the old test content to take over

This spell has no CMS connection, so ask the developer. Ask them to look in the edit UI for:

- shared blocks in the block library named after the component ("Card Test: …");
- pages under the test-content root, or anywhere the project keeps test or training pages, named
  after the component, and the pages beneath them;
- media folders named after the component.

For each candidate, ask for its content ID (shown in the edit UI) and whether anything outside old
test content uses it. The builder reports references again when it builds, so this list only needs
the developer's confirmation. Add the confirmed ones to `legacy` as `{"key": "<content GUID>",
"name": "<name>"}`. **Never list real content the project names in the builder's configuration**, or
anything outside the component's own old test content. If the developer has none to name, go on
with an empty `legacy` list.

## Step 3 — Plan the variations

Apply G1 to G12 and every project rule, and draft the page in the section order the reference
gives: the `opening` section if the project rules call for one, `commonSetups`, `variations`, then
`layout`. For a page type, draft the list of pages instead. Show the plan as a short list before writing anything.

**Widths are display options here.** A layout row's `span` maps to the display option the project
rules name for it (`<the option the rules file maps to 12>`, and so on), and only the options the
block supports can appear. A width the block doesn't support is left out and said so, not forced.

## Step 4 — Ask about the gray areas

One at a time, each with a proposed answer, as the reference describes. Record each answer in
`decisions`. Gray areas particular to CMS 12:

- a selection factory whose options come from a service;
- a third-party or custom property type the builder may not translate;
- which language a `[CultureSpecific]` field is built in, when the rules file doesn't say;
- a project validator (`IValidate<T>`) that would refuse a variation, such as two images where one
  is allowed. A variation the site refuses to publish is left out and its rule named.

## Step 5 — Write the recipe

Write `<recipes directory>/<ClassName>.json` in the format the reference gives, with the layout
vocabulary from the rules file. How each CMS 12 property type takes a value:

| Property type | Value |
|---|---|
| `string` | a string |
| `bool` | `true` or `false`; leave it out for the default |
| `int`, `double` | a number |
| `DateTime` | an ISO 8601 string |
| A selection (`[SelectOne]`, an enum) | the option's display text exactly as the editor sees it; the builder maps it to the stored value |
| `[SelectMany]` | an array of option display texts |
| `XhtmlString` | an HTML string, or `{"$richText": "sample"}` |
| `Url`, a link property | `{"$link": "test-content", "title": "…"}` or `{"$external": "https://example.com/", "newWindow": true, "title": "…"}` |
| `LinkItemCollection` | an array of `$link` or `$external` objects |
| `ContentReference` with an image hint | `{"$media": "<test image name>"}` |
| `ContentReference` to a block | `{"$shared": "<sharedBlocks id>"}`, or `{"$real": "<name>"}` where a project rule allows it |
| `ContentArea` (on a block or a page field, not the test page's body) | an array of `{"$block": "<ClassName>", "values": {…}}` or `{"$shared": "<sharedBlocks id>"}` objects, each with an optional `span` the rules file maps to a display option |
| A block-typed property (a local block) | `{"$block": "<ClassName>", "values": {…}}`, with the block's own fields |
| `IList<T>` of plain objects | an array of objects, one per item, each `{name: value}` |

**Blocks inside rich text can't be set** by a recipe; neither can any property type the builder's
value translator doesn't support. Ask, leave the field out, record the decision, and name it in the
report.

## Step 6 — Check it

Run the builder's validator test.

**Slot:** `.agents/config/stack.md` → `## Build`
**If empty:** infer the build and test commands from the repo root and state which you used; if
genuinely ambiguous, ask rather than guessing.

The validator is a plain unit test: it needs no running site and no database. It lists each problem
by its path in the recipe. Fix every problem it names in this
recipe and run it again. A failure in an unrelated test isn't this spell's to fix: report it.

## Step 7 — Report

As the reference describes. The next steps are: commit the recipe, deploy, then build it from the
builder's admin page. The recipe is embedded in the build, so an environment's admin page only sees
a recipe once that environment has the deploy.

Next: `/commit-message` once the recipe and its validator run are clean.
