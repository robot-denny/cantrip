---
name: optimizely-12-test-content-builder
description: Blueprint for the project-side builder that turns test-content recipes into QA test pages on Optimizely CMS 12, including how content-area blocks live in each page's assets folder. Consult when an Optimizely 12 project adopts test-content recipes and has no builder yet, when changing an existing builder, or when a rebuild lands at a new address or a test page reaches search.
---

# Test-content builder: a blueprint for Optimizely CMS 12

The `/test-content` spell writes recipes; this is the code that builds them. It lives in the
project, because what it builds is shaped by the project's content areas, display options, grid and
fixtures, and no package can know those. Build it once, through the normal workflow (`/spec` then
`/plan`), with this file as the design input.

`test-content-principles` states what a builder owes a recipe whatever the platform: a validator,
stable keys, freshness, a build state, isolation, removal, hand-edit protection and access control.
Read that list first. This file is how each one is met on CMS 12.

## Assert what the platform decided; ask what the project decides

The project decides, and the spec should record:

- **the page grid** a recipe targets: which page type a test page is, and which property holds its
  body. On many sites that is a `ContentArea`, where a row is a run of blocks and a width is a
  display option. On others it is a custom grid property with sections, rows and columns stored as
  JSON; then the builder writes that structure itself, and its valid layouts and row options come
  from the project's grid configuration, not from attributes;
- **which display options stand for which widths**, and the per-block supported-options mechanism if
  the project has one;
- **the test-content root**: a page (often a folder page type) under the start page that every test
  page sits beneath and every internal link token points at;
- **which language** test content is built in, since `[CultureSpecific]` fields need a branch;
- **which environments** may build, and **who** may (a role such as the CMS administrators);
- **which real content**, if any, a recipe may place by name. Configure it as a name-to-GUID map in
  app settings, so a recipe holds the name and never the GUID.

## Blocks placed on a test page

A block in a CMS 12 content area is a reference to a block content item. To keep each test page
self-contained, **create every block the page places in that page's own assets folder** ("For This
Page"), through `ContentAssetHelper.GetOrCreateAssetFolder(pageLink)`. Deleting or rebuilding the page
then carries its blocks with it, and nothing lands in the shared block library.

A recipe's `sharedBlocks` are different: they test shared-block behavior, so they go in a dedicated
test-blocks folder in the block library. A block-typed property (a local block) is not content at
all; set its fields on the parent.

## The modules

Keep everything but the build itself pure, so it can be unit tested without a database.

| Module | Job | CMS 12 surface |
|---|---|---|
| Recipe model | Records mirroring the recipe format | `System.Text.Json`, values kept as `JsonElement` |
| Recipe loader | Reads every recipe embedded in the assembly, once, into a singleton | `<EmbeddedResource>` on the recipes folder; `GetManifestResourceStream` |
| Validator | Pure checks, each problem reported by its path in the recipe | none |
| Schema reader | Every property name and every fixed dropdown's options, for a content type | `IContentTypeRepository.Load(name)` and its `PropertyDefinitions`; the model type's attributes for selection factories and enums |
| Freshness | Compares `expects` (and each `otherComponents` entry) with the schema | none |
| Stable keys | A name-based UUID (version 5) from a project namespace GUID and `"<recipe id>/<item path>"` | set as `ContentGuid` on new content before its first save |
| Build planner | Turns a recipe, its freshness and what exists into a list of operations | none |
| Value translator | Turns recipe values and tokens into property values | see *Values* |
| Fixtures | Ensures the test-content root, the test-blocks folder, the test media folder and its images, each at a derived GUID | `IContentRepository`, `ContentAssetHelper`, `IBlobFactory` |
| Build record | What the last whole build left: per recipe, its fingerprint, when it was built and who asked; per item, its GUID and saved date | a project table (a migration and a repository); the Dynamic Data Store will do for this part, which is written once per build |
| Build job | Runs one requested build at a time, with progress and a stop | a scheduled job (see *The build*) |
| Legacy references | What still uses an old test item | `IContentRepository.GetReferencesToContent(link, false)` |
| Access | Environment allow-list, then role | `IWebHostEnvironment`, the current principal, an options class bound from configuration |
| Admin page | Lists recipes with their state; requests a build of one | an MVC controller with an `[Authorize]` policy, reached from an `IMenuProvider` menu item; the build action is a POST that validates an antiforgery token |

Register the services in the project's service configuration or an initialization module.

## Stable content GUIDs

Set `ContentGuid` yourself on every page, block and media item the builder creates, derived from the
recipe, then find existing content with `IContentRepository.Get<IContent>(guid)` (or
`TryGet`). That is what lets a rebuild update in place at the same address.

- A page is `For(recipeId, "page")`; a shared block `For(recipeId, "sharedBlocks/<id>")`; a
  page-type recipe's page `For(recipeId, "pages/<id>")`, keyed by the page's id rather than its
  position, so moving a page keeps its GUID.
- A block on a page is keyed by its item path.
- The fixtures are keyed too, from a fixed recipe id such as `"fixtures"`: the test-content root,
  the test-blocks folder, the test media folder and each test image by its name, so a rebuild finds
  them rather than uploading the images again. A page's assets folder needs no key: it is found from
  the page, and goes with it when the page is removed.
- Pin the derivation with a test of known inputs to known outputs. Changing the namespace GUID or the
  path format rebuilds every page at a new address.

## The build planner

`Plan(recipe, freshness, existing, protectHandEdits)` returns operations: create, update, skip
(protected), remove stale, take over legacy, keep legacy, skip field. Order matters:

1. **Legacy first**, so an old page with the new page's name is in the trash before its URL segment
   is claimed. An old item with no references outside other legacy items and the trash is moved
   there (`MoveToWastebasket`); one that real content still uses is kept and reported with what uses
   it.
2. **Shared test blocks**, so the pages that reference them can.
3. **The test page**, then its assets-folder blocks, then a page-type recipe's pages, **each before
   the pages beneath it**.
4. **Stale removal**: anything the build record lists that the recipe no longer does.

A field the recipe sets that the content type no longer has becomes a skip-field operation, not a
failure, so an out-of-date recipe still builds what it can.

**Hand-edit protection.** After each save, **re-read the content** and record its saved date
(`IChangeTrackable.Saved`); the object passed to `Save` may not carry the date the repository
assigned, and recording a stale one makes every page look hand-edited on the next build. Content
saved later than the recorded date was changed by hand; when the administrator asks for
protection, skip it and say so.

**Unchanged content is not saved.** When the translated values equal what is stored, plan a skip
rather than an update. Every save adds a version, and test pages are rebuilt often enough for
history to grow without bound.

## The build

- **Run the build as a scheduled job, one at a time, on the editing instance.** A recipe is tens to
  hundreds of saves, each running the site's publish handlers, so it can't run inside the admin
  request, and two builds at once race on the same GUIDs. A scheduled job (a `ScheduledJobBase`
  subclass with `[ScheduledPlugIn]`, started from the admin page through `IScheduledJobExecutor`)
  gives what a hand-rolled claim would have to build: the scheduler runs a job on one instance at a
  time, the job reports progress through `OnStatusChanged`, supports a stop, and keeps a history of
  runs. The admin page records which recipe to build in the build record, starts the job, and
  refuses with "a build is already running" when the job is. Where the site runs on several
  instances, the spec says which one runs scheduled jobs, which should be the editing instance, not
  a delivery one. Check between operations whether a stop was asked for, and cap the items one build
  may touch at a number the spec sets.
- **Name who asked for it.** A scheduled job doesn't run as the administrator who started it, so
  content shows the job as its saver. Record who requested each build in the build record and show
  it on the admin page.
- **Validate, then plan, then apply.** Refuse a recipe with any validator problem, or one whose other
  content types don't exist, before touching content.
- **Look content up in batches.** `IContentRepository` has no batch lookup by GUID, and a `TryGet` per
  GUID is one query each. Generated content all sits under known roots, so read it once: the
  descendants of the test-content root and the test-blocks folder (`IContentLoader.GetDescendents`),
  then the items in one call (`IContentLoader.GetItems`), into a map from GUID to content that the
  planner works from. Check legacy references only for the legacy items found.
- **Create with `GetDefault<T>(parentLink)`** (which applies `SetDefaultValues`), take a writable
  clone of existing content with `CreateWritableClone()`, and save with
  `IContentRepository.Save(content, SaveAction.Publish, AccessLevel.NoAccess)`. `NoAccess` skips the
  content access checks, which is safe only because the access gate has already run; never copy it
  into code an editor's request reaches.
- **Publishing runs the site's own events and validators.** An `IValidate<T>` that refuses a value
  fails the item, which is correct: report it, and let the recipe drop that variation. Publish
  handlers that index search, purge a CDN or call outside services run for test pages too. Exclude
  test content **at the indexer** (by its root), not only through a page property, which filters
  results but still pays for indexing. List what else a publish triggers in the spec, before the
  first build on a shared environment.
- **Clear what the recipe leaves out.** A page-type recipe's page sets the fields the recipe gives and
  resets the rest, so a rebuild matches the recipe.
- **Every generated page is kept out of search and navigation**, through whichever properties the
  project uses for that. The validator refuses a recipe that sets them.
- **Record the fingerprint only when the build is whole**, so a partial build keeps asking for a
  rebuild.
- **Keep child pages in recipe order** through each page's peer order (`PeerOrder`), moving only
  generated pages. Blocks in an assets folder have no sibling order; a content area's item order is
  what places them.

## Values

| Property type | Set as |
|---|---|
| `string`, `bool`, numbers, `DateTime` | the CLR value |
| A selection factory property | the `Value` of the `ISelectItem` whose `Text` matches the recipe's option |
| An enum property (often `[BackingType(typeof(PropertyNumber))]`) | the enum member whose display name matches; stored as its number |
| `XhtmlString` | `new XhtmlString(html)`; the rich-text sample is an embedded resource |
| `Url` | `new Url(...)`, built from the test-content root's URL or the external address |
| `LinkItemCollection` | `LinkItem`s with `Href`, `Text` and `Target` (`_blank` for a new window) |
| `ContentReference` | the `ContentLink` of the test image or shared test block the token names |
| `ContentArea` | a new `ContentArea` of `ContentAreaItem { ContentLink, ContentGuid, RenderSettings }`, the display option's tag under the key `ContentFragment.ContentDisplayOptionAttributeName`. Use the constant rather than a literal, and pin it with a test that round-trips a display option through the project's renderer |
| A local block | the parent's block property, its fields set one by one |
| `IList<T>` | a list of `T` deserialized from the recipe's objects |

A property type the translator doesn't list, including a third-party one, is refused with its type
named, which is what lets the spell report a field it can't set instead of the builder guessing.

**Test images ship with the build.** Embed them as resources and upload them on the first build into
the test media folder, as the project's image media type, writing the file through `IBlobFactory`.
Fill any required fields the media type has, and set its alternative text from the rules file's list
of test images, left empty on the one marked decorative. By default, put the builder and its
resources in an assembly production does not deploy. Where they do ship, keep each image under about
100 KB (compressed, or SVG where a picker accepts it): every environment that builds stores a copy
in its blob storage.

## Build state

`Decide(freshness, built, builtFingerprint, currentFingerprint)` gives, in this order: **recipe out
of date**, **never built**, **needs a rebuild**, or **up to date**. The fingerprint hashes only what
decides the build: the component, the title, the page, the pages and the shared blocks.

## Access

Check the environment first and the role second, and say which one refused. The menu item, the page
and its build action share the same decision. Keep the environment list in configuration, and leave
production off it.

The admin page lists recipes with their freshness, which needs each component's schema. Read each
content type once per page load, not once per recipe that places it. While a build runs, the page
polls only the job's status, stops when the build ends, and pauses while its tab is hidden.

Meet the core reference's *usable admin screen* list: a `main` landmark and a level-1 heading, the
recipes in a table with column headers, each build action a labeled `button` in a `form` that posts
with an antiforgery token, and the status region outside the part of the page that polling
redraws.

## Tests that pin it

One test class per pure module, plus one that loads every committed recipe and runs the validator
over each. That last one is the test the `/test-content` spell runs. Worth pinning in particular:

- the validator refuses a raw GUID or content ID anywhere in a value, an unknown token, a duplicate
  id, a display option the grid doesn't map, an `opening` section with a title, and a recipe that
  sets the search and navigation fields;
- stable GUIDs for known inputs;
- the planner puts legacy before pages and parents before children, and removes what a recipe
  dropped;
- the translator maps an option's display text to its stored value, for a selection factory and for
  an enum, and a `span` to the display option the renderer reads back;
- the planner skips content whose values are unchanged;
- a second build refused while the build job is running;
- the build action refuses a GET and a POST without an antiforgery token;
- freshness reports an added property, a removed property and a changed dropdown option;
- the build state for each of its four cases.
