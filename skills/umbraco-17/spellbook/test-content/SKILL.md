---
name: test-content
description: Write or refresh the test-content recipe for one Umbraco 17 block or page type, the committed JSON file the project's test-content builder turns into QA test pages. Reads the component's schema and view, applies the general variation rules and this project's QA-owned rules, finds the component's old hand-built test content to take over, asks about every gray area, writes the recipe, and checks it with the builder's validator. Use right after building or changing a block or page type, or when the builder marks a recipe out of date.
disable-model-invocation: true
argument-hint: "<component alias, e.g. cardItem or articlePage>"
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(python3:*), Bash(dotnet test:*), mcp__umbraco-mcp__*
---

The user's argument: **$ARGUMENTS**, the alias of the component to write a recipe for: a block's
element type, such as `cardItem`, or a page type, such as `articlePage`.

**This spell decides what to test; the project's builder builds it.** It writes one file, the
recipe, and nothing else. It reads from the CMS but never writes to it. An administrator builds the
test pages later from the builder's dashboard.

Read `test-content-principles` in full now. It holds the method this spell applies: the general
rules G1 to G12, the gray-area discipline, the recipe format, labels, value tokens, page-type
recipes, refreshing, and the report. Every step below names what it adds for Umbraco 17 and
otherwise follows that reference. `umbraco-17-test-content-builder` is the other half: what the
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
now and apply every rule in it. The rules file also defines this site's **page layout vocabulary**,
the `rowType`s, row `settings`, spans and item `type`s a recipe may use. Read it there; the builder's
validator is the authority when the two disagree, and a disagreement is worth reporting.

## Step 1 — Read the component

Where this pack's `/guide` spell is installed, its script reads a component's schema from the
project's serialized schema files. Run it from the project root, with the path relative to this
spell's own directory:

```
python3 ../guide/scripts/guide.py extract <alias> --project-root <project root>
```

It prints the component's properties (alias, editor, mandatory, help text, dropdown options,
composition) as JSON. **An empty result is a failure, not a component with no properties.** The
script skips serialized files whose format version it hasn't been verified against, says so on
stderr, and can still exit cleanly with nothing on stdout. Read stderr, and if the component didn't
come back, read the same facts another way:

- through the `umbraco-mcp` document-type and data-type tools, when they are connected;
- otherwise from the serialized schema files directly. For Deploy, the component's
  `document-type__*.uda` lists its properties under `PropertyGroups`, each naming its data type,
  and that `data-type__*.uda` holds the editor alias and its configuration (a dropdown's options
  under `items`). Follow `CompositionContentTypes` for inherited properties.

Say which way the schema was read in the report.

- **List limits are on the data type, not the property.** For each `Umbraco.BlockList` property,
  read its data type's `validationLimit` (`min`, `max`). For each `Umbraco.DropDown.Flexible`
  property, read its options from the data type's configuration, exactly as spelled.
- **Read the block's view and view model** to see which settings change the layout and which only
  change text. That answers G2 and G3 for most fields; ask about the rest.
- **The kind decides the recipe.** An element type is a block recipe (`"kind": "block"`). A document
  type is a page-type recipe (`"kind": "pageType"`). A document type that exists only once at the
  content root (a home page) can't have one: say so and stop.
- **For a page type, read every component it places too**: the element types its block editors
  offer, any picker that selects a shared block, and every page type allowed beneath it. Each goes
  in `otherComponents`.
- **A behavior that spans blocks** gets a recipe too. Its `id` names the behavior, `component` is
  the block most of the page uses, and `otherComponents` names every other block it places.

If a recipe for this alias already exists, read it too. This run refreshes it.

## Step 2 — Find the old test content to take over

Find candidates through the Management API, by name and by location:

- shared blocks in the project's shared-block area named after the component ("Card Test: …");
- pages under the test-content root, or anywhere a project keeps test pages, named after the
  component, and the pages beneath them;
- media folders named after the component.

Use the `umbraco-mcp` tools when they are connected. Otherwise a short script against the Management
API works, against a local or non-production site only, with an API user's client credentials
taken from the environment (never typed into the script or the recipe):

| Management API call | Gives |
|---|---|
| `GET /umbraco/management/api/v1/item/document/search?query=<name>&skip=0&take=100` | documents whose name matches, with `id` |
| `GET /umbraco/management/api/v1/item/media/search?query=<name>&skip=0&take=100` | the same for media |
| `GET /umbraco/management/api/v1/tree/document/ancestors?descendantId=<id>` | where a document sits, root first |
| `GET /umbraco/management/api/v1/document/<id>/referenced-by?skip=0&take=100` | what uses it |

The search and referenced-by calls are paged. When a response's `total` is more than the items
returned, ask for the next page with `skip`, so a candidate or a real reference on a later page isn't
missed.

The token comes from `POST /umbraco/management/api/v1/security/back-office/token` with
`grant_type=client_credentials`. If the site isn't running or no credentials are available, say so
and ask whether to go on with an empty `legacy` list.

Show the developer every candidate with its location and what references it, and ask which to take
over. **Never list real content the project names in the builder's configuration**, or anything
outside the component's own old test content.

## Step 3 — Plan the variations

Apply G1 to G12 and every project rule, and draft the page in the section order the reference
gives: the `opening` section if the project rules call for one, `commonSetups`, `variations`, then
`layout`. For a page type, draft the list of pages instead. Show the plan as a short list before writing anything.

## Step 4 — Ask about the gray areas

One at a time, each with a proposed answer, as the reference describes. Record each answer in
`decisions`.

## Step 5 — Write the recipe

Write `<recipes directory>/<alias>.json` in the format the reference gives, with the layout
vocabulary from the rules file. How each Umbraco 17 editor takes a value:

| Property editor | Value |
|---|---|
| `Umbraco.TextBox`, `Umbraco.TextArea` | a string |
| `Umbraco.DropDown.Flexible` | the option text: `"Primary Tint"` |
| `Umbraco.TrueFalse` | `true` or `false`; leave it out for the default |
| `Umbraco.RichText` | an HTML string, or `{"$richText": "sample"}` |
| `Umbraco.MultiUrlPicker` (one link) | `{"$link": "test-content", "title": "…"}` or `{"$external": "https://example.com/", "newWindow": true, "title": "…"}` |
| `Umbraco.MediaPicker3` | `{"$media": "<test image name>"}` |
| A content picker that selects a shared block | `{"$shared": "<sharedBlocks id>"}`, or `{"$real": "<name>"}` where a project rule allows it |
| `Umbraco.BlockList` (nested items) | an array of objects, one per item, each `{alias: value}` |
| `Umbraco.SingleBlock` | `{"$block": "<element type alias>", "values": {…}}` |

**Blocks inside rich text can't be set** by a recipe; neither can any editor the builder's value
translator doesn't support. Ask, leave the field out, record the decision, and name it in the report.

## Step 6 — Check it

Run the builder's validator test.

**Slot:** `.agents/config/stack.md` → `## Build`
**If empty:** infer the build and test commands from the repo root and state which you used; if
genuinely ambiguous, ask rather than guessing.

The validator is a plain unit test: it needs no running site and no database. It lists each problem
by its path in the recipe. Fix every problem it names in this
recipe and run it again. A failure in an unrelated test isn't this spell's to fix: report it.

## Step 7 — Report

As the reference describes. The next steps are: commit the recipe, restart the local site or deploy,
then build it from the builder's dashboard. The recipe is embedded in the build, so a dashboard on an
environment only sees a recipe once that environment has the deploy.

Next: `/commit-message` once the recipe and its validator run are clean.
