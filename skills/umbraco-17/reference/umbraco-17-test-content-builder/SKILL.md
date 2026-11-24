---
name: umbraco-17-test-content-builder
description: Blueprint for the project-side builder that turns test-content recipes into QA test pages on Umbraco 17, including the stored value formats the backoffice accepts. Consult when a project adopts test-content recipes and has no builder yet, when changing an existing builder, or when a built test page refuses to open in the backoffice or a rebuild lands at a new address.
---

# Test-content builder: a blueprint for Umbraco 17

The `/test-content` spell writes recipes; this is the code that builds them. It lives in the
project, because what it builds is shaped by the project's page grid, its shared-block pattern and
its fixtures, and no package can know those. Build it once, through the normal workflow (`/spec`
then `/plan`), with this file as the design input.

`test-content-principles` states what a builder owes a recipe whatever the platform: a validator,
stable keys, freshness, a build state, isolation, removal, hand-edit protection and access control.
Read that list first. This file is how each one is met on Umbraco 17.

## Assert what the platform decided; ask what the project decides

The project decides, and the spec should record:

- **the page grid** a recipe targets: which page type a test page is, which property holds its body
  (a Block Grid, or a Block List of row blocks), which row types and row settings exist, and which
  spans a row allows. This is the recipe's layout vocabulary, mirrored in the project rules file;
- **the shared-block pattern**, if the project has one (often a content picker on an element type
  that selects a block stored as a document in a shared area), and where test copies go;
- **the test-content root**: a page in the content tree that every test page sits beneath and every
  internal link token points at;
- **which environments** may build, and **who** may (a user group, optionally narrowed by an email
  domain);
- **which real content**, if any, a recipe may place by name, such as a site-wide switcher. Configure
  it as a name-to-key map in app settings, so a recipe holds the name and never the key.

## The modules

Keep everything but the build itself pure, so it can be unit tested without a database.

| Module | Job | Umbraco 17 surface |
|---|---|---|
| Recipe model | Records mirroring the recipe format | `System.Text.Json`, values kept as `JsonElement` |
| Recipe loader | Reads every recipe embedded in the assembly, once, into a singleton | `<EmbeddedResource>` on the recipes folder; `GetManifestResourceStream` |
| Validator | Pure checks, each problem reported by its path in the recipe | none |
| Schema reader | Every property alias and every dropdown's options, for a component | `IContentTypeService` (`CompositionPropertyTypes` includes inherited ones); `IDataTypeService` (a flexible dropdown's configuration is a `ValueListConfiguration`) |
| Freshness | Compares `expects` (and each `otherComponents` entry) with the schema; lists added and removed properties and options | none |
| Stable keys | A name-based UUID (version 5) from a project namespace GUID and `"<recipe id>/<item path>"` | none |
| Build planner | Turns a recipe, its freshness and what exists into a list of operations | none |
| Value translator | Turns recipe values and tokens into stored property values | see *Stored value formats* |
| Fixtures | Ensures the test-content root, the shared test-blocks folder, the test media folder and its images, each at a derived key | `IContentService`, `IMediaService`, `MediaFileManager` |
| Build record | What the last whole build left: per recipe, its fingerprint and when it was built; per document, its update date, under a key that names the recipe | `IKeyValueService`, short values only (see *The build record*) |
| Build claim | Which build is running, who started it, its progress, and when the claim expires | `IKeyValueService.TrySetValue`, one entry |
| Legacy references | What still uses an old test item | `ITrackedReferencesService` |
| Access | Environment allow-list, then user group | `IBackOfficeSecurityAccessor`, `IWebHostEnvironment`, an options class bound from configuration |
| API | List recipes with their state; build one | a `ManagementApiControllerBase` controller under `[VersionedApiBackOfficeRoute]` |
| Dashboard | The admin screen | an `umbraco-package.json` with a `dashboard` extension in the Settings section and a `condition` extension that asks the API whether this user may build |

Register the services in an `IComposer`.

## Stable keys

Set each document's and each block's key yourself, derived from the recipe, rather than letting
Umbraco assign one. That is what lets a rebuild find what it built before, update it in place at the
same address, and leave block keys unchanged.

- A page is `For(recipeId, "page")`; a shared block `For(recipeId, "sharedBlocks/<id>")`; a
  page-type recipe's page `For(recipeId, "pages/<id>")`, keyed by the page's id rather than its
  position, so moving a page keeps its key.
- A block inside a page is keyed by its item path, and a media picker entry by its item path plus
  `/media`.
- The fixtures are keyed too, from a fixed recipe id such as `"fixtures"`: the test-content root,
  the test-blocks folder, the test media folder and each test image by its name. A rebuild then finds
  them rather than uploading the images again.
- Pin the derivation with a test of known inputs to known outputs. Changing the namespace GUID or the
  path format rebuilds every page at a new address.

## The build planner

`Plan(recipe, freshness, existing, protectHandEdits)` returns operations: create, update, skip
(protected), remove stale, take over legacy, keep legacy, skip field. Order matters:

1. **Legacy first.** Old test pages often have the new page's name, and Umbraco makes sibling names
   unique, so building before the old page is in the recycle bin gives the new one a `-1` address.
   An old item with no references outside other legacy items and the recycle bin is taken over; one
   that real content still uses is kept and reported with what uses it.
2. **Shared test blocks**, so the pages that reference them can.
3. **The test page**, then a page-type recipe's pages, **each before the pages beneath it**.
4. **Stale removal**: anything the build record lists that the recipe no longer does.

A field the recipe sets that the component no longer has becomes a skip-field operation, not a
failure, so an out-of-date recipe still builds what it can.

**Hand-edit protection.** After each save, record the document's update date in the build record.
On the next build, a document whose current update date is later than the recorded one was changed
by hand; when the administrator asks for protection, skip it and say so.

**Unchanged content is not saved.** When the translated values equal what is stored, plan a skip
rather than an update. Every save adds a version, and test pages are rebuilt often enough for
history to grow until the version cleanup runs.

## The build record

`IKeyValueService` stores short settings values, not documents, so keep every value in it short and
never grow one value with the size of a recipe:

- **one entry per built document**, keyed `<prefix>:<recipe id>:<document key>`, holding its update
  date. `FindByKeyPrefix("<prefix>:<recipe id>:")` lists what a recipe built last time, which is
  what stale removal and hand-edit protection read;
- **one entry per recipe**, holding its fingerprint and when it was built, written only when the
  build is whole;
- **one claim entry** for the running build (below), written often and kept apart from the rest.

A project that would rather keep this in its own table (a migration and a repository) can, as long
as the claim still has a compare-and-set.

## The build

- **One build at a time, across every server.** Two concurrent builds of one recipe race on the same
  keys, and an in-memory lock only stops that within one process. On a load-balanced site, run builds
  on the backoffice server, and take the claim with `TrySetValue(key, originalValue, newValue)`, which
  sets the value only if no one changed it since it was read. The claim holds an owner id and an
  expiry; the build renews the expiry as it goes, so an app restart mid-build frees the claim once it
  lapses rather than holding it forever. Try once, and refuse a second build with "a build is already
  running" rather than queueing it.
- **Run the build in the background, not inside the API request.** A recipe is tens to hundreds of
  saves and publishes, and a request that does them all can time out or be cut off mid-tree. Start
  the build, return at once, and write progress to the claim entry every few items, not on every
  one. Pass a cancellation token and check it between operations, and cap the items one build may
  touch at a number the spec sets.
- **Name who built it.** A background build has no backoffice user. Capture the key of the user who
  started it, and pass that user's id to every save and publish, so the history shows who built the
  page rather than nobody.
- **Validate, then plan, then apply.** Refuse a recipe with any validator problem, or one whose other
  components don't exist, before touching content.
- **Look content up in batches.** Find what the planner needs to know exists with one batched lookup
  by key rather than one call per document, and check tracked references only for the legacy items
  found.
- **Save, then publish every culture** (`Publish(content, ["*"])`). A save that does not publish is a
  failure, reported with the publish result.
- **Know what a publish triggers.** Each publish refreshes the content cache (and, on a
  load-balanced site, tells every server to), updates the search indexes, and runs the site's own
  notification handlers and any webhooks. List those in the spec before the first build on a shared
  environment. Exclude test content from the search indexes **at the indexer** (by its root), not
  only through a page property, which filters results but still pays for indexing. Where the project
  uses Umbraco Deploy, decide whether test content is transferred between environments or built in
  each; stable keys make the two agree, but only one should be the habit.
- **Clear what the recipe leaves out.** A page-type recipe's page sets the fields the recipe gives
  and clears the rest, so a rebuild matches the recipe.
- **Every generated page is kept out of search and the main navigation**, through whichever
  properties the project uses for that. The validator refuses a recipe that sets them.
- **Test images carry their alternative text.** Where the project's image media type has an
  alternative-text property, the fixtures set it from the rules file's list of test images, and leave
  it empty on the one marked decorative.
- **Record the fingerprint only when the build is whole.** When an item failed or a field was
  skipped, record no fingerprint, so the dashboard keeps asking for a rebuild.
- **Arrange children in recipe order**, moving only generated pages into places generated pages
  already held, so pages that aren't the recipe's keep theirs.

## Stored value formats

The backoffice is stricter than the content service. A value the content service saves without
complaint can still be refused when an editor opens the page, so write each editor's value in
exactly the form the backoffice writes it. Each row below is the form Umbraco 17 stores.

| Editor | Stored value |
|---|---|
| `Umbraco.TextBox`, `Umbraco.TextArea` | the string |
| `Umbraco.DropDown.Flexible` | a JSON array of the option text: `["Primary Tint"]` |
| `Umbraco.TrueFalse` | `1` or `0`, as the backoffice saves it. A stored `true` or `false` saves and renders locally, but was refused on Umbraco Cloud when the backoffice opened the page. Pin this with a test |
| `Umbraco.RichText` | JSON `{"markup": "<html>", "blocks": {"layout": {}, "contentData": [], "settingsData": [], "expose": []}}` |
| `Umbraco.MultiUrlPicker` | a JSON array of `{name, target, unique, type, udi, url, queryString, culture}`: `udi` for an internal link (`umb://document/<key without hyphens>`), `url` for an external one, `target` `"_blank"` for a new window, and `unique` and `type` written as `null` |
| `Umbraco.MediaPicker3` | a JSON array of `{key, mediaKey, mediaTypeAlias, crops: [], focalPoint: null}`, `key` stable per item |
| `Umbraco.MultiNodeTreePicker` | the document UDI string |
| `Umbraco.BlockList`, `Umbraco.SingleBlock` | JSON `{layout: {"<editor alias>": [{contentKey, settingsKey}]}, contentData: [{contentTypeKey, key, values: [{editorAlias, culture, segment, alias, value}]}], settingsData: [], expose: [{contentKey, culture, segment}]}`. A Single Block stores one entry under its own layout key |
| `Umbraco.BlockGrid` | the same shape under `Umbraco.BlockGrid`, with each layout entry carrying its `columnSpan`, `rowSpan` and `areas` |

An editor the translator doesn't list is refused with its alias named, which is what lets the spell
report a field it can't set instead of the builder guessing.

**Test images ship with the build.** Embed them as resources and upload them on the first build into
the test media folder: as an Image, or for an SVG as Vector Graphics (`umbracoMediaVectorGraphics`),
which some pickers require. By default, put the builder and its resources in an assembly production
does not deploy. Where they do ship, keep each image under about 100 KB (compressed, or SVG where a
picker accepts it): every environment that builds stores a copy in its media storage.

## Build state

`Decide(freshness, built, builtFingerprint, currentFingerprint)` gives, in this order: **recipe out
of date** (the component changed; rebuilding can't fix it), **never built**, **needs a rebuild** (the
recipe changed since the last build, or the last build left no fingerprint), or **up to date**. The
fingerprint hashes only what decides the build: the component, the title, the page, the pages and the
shared blocks. Rules, decisions and the legacy list are left out.

## Access

Check the environment first and the user second, and say which one refused. The dashboard's
condition and the API's endpoints share the same decision, so a hidden dashboard and a refused
request can't disagree. Keep the environment list in configuration, and leave production off it.

The dashboard lists recipes with their freshness, which needs each component's schema. Read each
content type and data type once per list request, not once per recipe that places it, and keep the
result for a short time: while a build runs, the dashboard polls only the claim entry for progress,
stops when the build ends, and pauses while its tab is hidden.

Meet the core reference's *usable admin screen* list with the backoffice's own `uui-` components (a
`uui-table`, `uui-button` with a label naming the recipe, `uui-toggle` for the hand-edit option)
rather than clickable `div`s, which gives keyboard and screen-reader support for free.

## Tests that pin it

One test class per pure module, plus one that loads every committed recipe and runs the validator
over each. That last one is the test the `/test-content` spell runs. Worth pinning in particular:

- the validator refuses a raw key or UDI anywhere in a value, an unknown token, a duplicate id, a
  span the grid doesn't allow, an `opening` section with a title, and a recipe that sets the search
  and navigation fields;
- stable keys for known inputs;
- the planner puts legacy before pages and parents before children, and removes what a recipe
  dropped;
- the translator stores a toggle as `1` or `0`;
- the planner skips content whose values are unchanged;
- a second build refused while one holds the claim, and a lapsed claim taken over;
- freshness reports an added property, a removed property and a changed dropdown option;
- the build state for each of its four cases.
