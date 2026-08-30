---
name: umbraco-17-feature-backfill
description: How to reverse-engineer behavioral documentation from Umbraco 17 code — locating the serialized schema artifact (Deploy .uda or uSync .config), the generated model, and the Razor view for a document type or element type, parsing the serialized property structure and compositions from either format, and mapping data-type UDIs and editor aliases to readable field types. Consult when documenting an Umbraco capability that has no spec, plan, or tests, when backfilling feature docs on an existing Umbraco site, or when resolving a document-type alias or block name to its implementation.
---

# Backfilling behavioral docs from Umbraco 17 code

Supplements the generic from-code mode with where Umbraco keeps the three code sources, and how to
read them.

## The three sources, for Umbraco

### 1. The serialized schema artifact

Find the matching `document-type__*.uda` under the Deploy revision directory. **There is no
`element-type__*.uda`** — Deploy serializes element types as `document-type__*.uda` too, with the
same `DocumentTypeArtifact` type, so the kind is never in the filename. Parse its JSON for:

- `Name` — the human-readable capability name
- `Alias` — the identifier, and the basis for the doc's slug
- `Description` / `Icon` — context
- Every `PropertyGroups[].PropertyTypes[]` entry — each property's `Name` (label), `Alias`,
  `DataType` UDI, `Mandatory` flag, and per-property `Description` (help text)
- `CompositionContentTypes` — inherited property groups, resolved recursively via their UDIs
- `Permissions.IsElementType` — **the only signal for the kind.** It is emitted *only when true*, so
  its absence means "not an element type" and a reader must treat this as a truthy check rather than
  a field it can read and trust. Verified across two Deploy projects: 171 of 240 document types
  carried the key, and the remaining 69 carried a `Permissions` object without it

Reading `.uda` structure: groups with `"Type": 1` are tabs; groups without a `Type` use
`tabAlias`/`groupAlias` as their `Alias`.

**Each artifact carries its own `__version`, and one project holds a mix.** `__version` tracks the
Deploy package at the time that artifact was last serialized — not the CMS version, and not the
project. One project observed running Umbraco 17.5.3 held artifacts stamped 17.0.2, 17.1.0, 17.2.0,
and 17.2.1 side by side, because artifacts only re-serialize when touched. **So a version check
belongs per file, not per project**; refusing a whole read over one stale artifact would reject the
normal case. `__type` names the artifact class and is the reliable discriminator where the filename
prefix is ambiguous — the prefix set is open, and packages contribute their own.

**Under uSync the same schema is already on disk, in a different shape.** A project running uSync
rather than Deploy serializes content types to `uSync/*/ContentTypes/*.config` — XML instead of
JSON, carrying the same tabs, groups, sort order, and compositions. Do not send it to a live API
for something the repository already holds; read the equivalents:

| What you need | Deploy (`.uda`, JSON) | uSync (`.config`, XML) |
|---|---|---|
| Name, icon, description | `Name`, `Icon`, `Description` | `<Info>` children of the same names |
| Alias | `Alias` | **`Alias` attribute on the root `<ContentType>`**, not an `<Info>` child |
| Properties | `PropertyGroups[].PropertyTypes[]` | `<GenericProperties>` → `<GenericProperty>` |
| A property's editor | `DataType` UDI — resolve via the table below | `<Type>` — already the editor alias; look it up in that table's left column |
| Whether it is required | `Mandatory` | `<Mandatory>` |
| Tabs and groups | `PropertyGroups[]`, `"Type": 1` marking a tab | `<Tabs>` → `<Tab>`, discriminated by `<Type>Tab</Type>` vs `<Type>Group</Type>` — see below |
| Sort order | `SortOrder`, on groups and properties alike | `<SortOrder>`, on tabs and properties alike |
| Compositions | `CompositionContentTypes` UDIs | `<Info>` → `<Compositions>` → `<Composition>`, alias as the element text |
| The kind | `Permissions.IsElementType`, **present only when true** | `<IsElement>`, **always present**, `true` or `false` |
| Root-placeable | `Permissions.AllowedAtRoot`, **present only when true** | `<Info>` → `<AllowAtRoot>`, **always present** |
| Allowed children | `Permissions.AllowedChildContentTypes` UDIs | `<Structure>` → `<ContentType>`, `Key` attribute **and** the alias as element text |
| Template assignment | `DefaultTemplate` and `AllowedTemplates` UDIs | `<Info>` → `<DefaultTemplate>` and `<AllowedTemplates>`, alias as element text |

**The two formats express the kind asymmetrically, and a reader must branch.** uSync always writes
`<IsElement>`, so read the boolean. Deploy writes `Permissions.IsElementType` only when true, so
test for truthiness and treat absence as false. A reader that assumes symmetry finds no element
types on one format or none on the other, and reports an empty inventory on a project full of
blocks — the silent-empty shape this guidance exists to prevent.

**The same asymmetry appears a second time, on `AllowedAtRoot`.** Deploy emits it only when true;
uSync always writes `<AllowAtRoot>`. Whatever you do for the kind flag, do for this one — the two
fields are the same shape of trap, and a reader that branches for one and not the other reads every
Deploy content type as unplaceable at the root.

**Allowed children resolve differently, and uSync gives more.** Deploy lists a child by UDI alone, so
a reference to a type the export does not hold resolves to nothing. uSync writes the alias as the
element's own text beside the `Key`, so the same broken reference still yields a name. A consumer
that treats reachability as evidence rather than as a gate is unaffected; one that counts reachable
types will count differently on the two formats for the same *broken* export.

## The block-editor palette

**A block editor's palette lives on its data type, never on a content type.** Both formats carry the
same JSON payload — Deploy in `Configuration`, uSync inside the `<Config>` CDATA — and inside it a
`blocks[]` array whose entries name content types by **two explicit keys**:

| Key | What it names |
|---|---|
| `contentElementTypeKey` | the block an editor places — **the documentable unit** |
| `settingsElementTypeKey` | the settings half of that block, not a block of its own |

Both are dashed GUIDs, while a Deploy `Udi` strips the dashes, so folding the two spellings is the
reader's job. Measured on two projects: Deploy carried 7 palettes across `Umbraco.BlockList` and
`Umbraco.BlockGrid`; uSync carried 26, all `Umbraco.BlockList`. An entry may also carry grid layout
keys — `areas`, `columnSpanOptions`, `rowMinSpan`, `allowInAreas`, `groupKey` — and an entry naming
neither element type offers nothing to place.

**Read the palette, never the element-type flag, to decide what an editor can place.** On one
measured project the flag matched 34 of 68 content types while the palette named 23; on another it
matched 125 of 174 while the palette named 52. The same element type appears in several palettes, so
deduplicate on the resolved alias, and compute the settings-only set as a **difference** — a type can
be one block's settings half and another block's content block.

**A palette key that resolves to nothing is not necessarily a broken export.** An element type is a
database row rather than a class, so a package that creates one at boot can be absent from a
project's own export: the export may ignore that package's schema deliberately, the environment may
not be a schema source at all, or the type may exist only where nobody booted locally. Report it;
do not refuse over it. A data type whose payload cannot be *parsed* is the opposite case and does
stop the read.

**Resolving a uSync property to its tab and group takes two steps.** Tabs and groups both appear as
`<Tab>` entries inside `<Tabs>`, told apart only by `<Type>Tab</Type>` or `<Type>Group</Type>`. A
property names its owner as `<Tab Alias="content/content">`, which is a `tab/group` path — but
sometimes it is a bare alias instead, and a bare alias may name *either* a group or a tab. In one
project: 235 path-form references, 164 bare, of which 114 resolved to a group and 50 to a tab. **So
resolve every property's `Tab Alias` against the `<Tabs>` list and read that entry's `<Type>`; never
infer the level from whether the alias contains a slash.** Captions repeat freely — a "Content" tab
routinely holds a "Content" group — so the caption is not a key.

**uSync content-type filenames are the lowercased alias — and data-type filenames are not.** An
`alertBanner` element type serializes to `ContentTypes/alertbanner.config`; across 174 content types
in one project there were no exceptions, so a known content-type alias can be read as a single file
provided the lookup case-folds, and a full folder scan is needed only when enumerating without a
known alias.

**The same rule fails completely one folder over.** In the same project, 0 of 150
`DataTypes/*.config` filenames were the lowercased alias. A data type's alias is a display name with
spaces (below), and the filename is that alias with spaces and punctuation removed and its original
casing kept — `Alias="Alert Severity"` serializes to `AlertSeverity.config`. So **resolve a data
type by its `Key`, never by constructing a filename**; a property's `<Definition>` gives you that
key, and a folder scan indexed by key is the reliable read.

**uSync declares its format version once per project**, in `uSync/<v>/usync.config`:

```xml
<uSync version="17.0.4.0" format="10.7.0" />
```

`format` is the serialization shape and the thing to gate on. Note that it sits on its own numbering
line — the project above ran uSync 17.3.6 in a `uSync/v17/` folder with `format="10.7.0"`, so
neither the package version nor the folder name tells you the format. **Because it is declared once,
a uSync version check is a single up-front gate on the whole read** — the opposite of Deploy's
per-artifact `__version`.

**A uSync `<DataType>` carries fewer elements than you would guess.** Verified across 150 data
types in one project:

```xml
<DataType Key="dddd3333-dddd-3333-dddd-333333333333" Alias="Alert Severity" Level="2">
  <Info>
    <Name>Alert Severity</Name>
    <EditorAlias>Umbraco.DropDown.Flexible</EditorAlias>
    <EditorUIAlias>Umb.PropertyEditorUi.Dropdown</EditorUIAlias>
    <Folder>Dropdowns</Folder>
  </Info>
  <Config><![CDATA[{ "multiple": false }]]></Config>
</DataType>
```

- The root element carries `Key`, `Alias` and `Level`. **`Alias` is a display name containing
  spaces** — 143 of the 150 — so it is not a code identifier and must not be treated as one.
- `<Info>` carries `Name`, `EditorAlias`, and **`EditorUIAlias` with a capital UI** (not
  `EditorUiAlias` — Deploy's JSON spells the equivalent key `EditorUiAlias`, and the two formats
  genuinely differ). `<Folder>` appears when the data type sits in a backoffice folder, on 91 of the
  150; `Level` tracks that nesting.
- **There is no `DatabaseType` and no `SortOrder`** on a `<DataType>` element. Do not read for them.
- `<Config>` holds the editor's configuration as a JSON payload — the option list, a block editor's
  palette, and everything else editor-specific. It is the same payload Deploy puts in an artifact's
  `Configuration` object, so a reader can normalize it once for both formats.
- Not every file in `DataTypes/` is a `<DataType>`. One of the 150 was
  `<Empty … Change="Rename" />`, a marker uSync leaves behind. **Confirm each file by its root
  element** rather than trusting the folder.

**Normalize compositions on the alias, whichever format you read.** Deploy gives UDIs and uSync
gives aliases, so a reader that keeps whichever form it found works on one project and breaks on
the other. Resolve to the alias at the point of reading and everything downstream stays
format-blind.

### 2. The generated model

Read the matching `*.generated.cs` if the project commits generated models. **Use the generated C#
property types as the primary signal for what each property is** — a strongly-typed
`IHtmlEncodedString`, `bool`, `MediaWithCrops`, or `IEnumerable<IPublishedElement>` is more
reliable and more repo-native than reverse-mapping a `umb://data-type/...` UDI.

Fall back to the UDI table below only when the model is absent or the C# type is ambiguous.

**Slot:** `.agents/config/stack.md` → `## Models`
**If empty:** check whether `*.generated.cs` model files are committed to the repo. If they are,
the project regenerates them manually; if they are absent, models are generated at build or run
time and cannot be read from source.

Where models cannot be read from source, rely on the serialized schema — the `.uda` plus the UDI
table below, or uSync's `<Type>` editor alias read directly.

### 3. The Razor view

Find the `.cshtml` that renders it. Page templates live at the views root; block components live
under the shared block-components folder, with editor-specific folders for anything genuinely
restricted to one editor.

Read it for **conditional branches** — `if`/`else`, null and empty checks,
`@if (Model.X.Any())`, toggle guards — and write one scenario per branch found.

**Slot:** `.agents/config/paths.md` → `## Umbraco`
**If empty:** locate each by search — the Deploy revision directory by its `*.uda` files,
views by their `*.cshtml` files, and the extension root by its `umbraco-package.json`. If no
`*.uda` files exist, check `uSync/*/ContentTypes/*.config` for the same schema before falling
back to MCP; a folder with no matching file is a partial export, not an empty schema.

## Data-type UDI → readable field type

Only needed when the generated model doesn't disambiguate a property. Map its `DataType` UDI, or a
known editor alias, to a readable type — and then to a generic field kind for scenario derivation:

| Editor alias / UDI hint | Readable type | Generic field kind |
|---|---|---|
| `Umbraco.RichText`, `Umbraco.TinyMCE` | Rich Text | Optional text or rich text |
| `Umbraco.TextBox`, `Umbraco.TextArea` | Text | Optional text or rich text |
| `Umbraco.MediaPicker3`, `Umbraco.MediaPicker` | Media Picker | Media or asset reference |
| `Umbraco.TrueFalse` | Toggle | Boolean / toggle |
| `Umbraco.BlockList` | Block List | Collection of child items |
| `Umbraco.BlockGrid` | Block Grid | Collection of child items |
| `Umbraco.ContentPicker`, `Umbraco.MultiNodeTreePicker` | Content / Node Picker | Reference to other content |
| `Umbraco.DropDown.Flexible` | Dropdown | Optional text or rich text |
| `Umbraco.Integer`, `Umbraco.Decimal` | Number | Optional text or rich text |
| `Umbraco.DateTime` | Date/Time | Optional text or rich text |

A `Mandatory: true` property takes the **Required** field kind regardless of its editor.

Unrecognized → call it "Content" and flag it for human input.

## Umbraco-specific gotchas when backfilling

- **Compositions carry properties too.** A document type's own `PropertyGroups` is not the full
  picture — resolve `CompositionContentTypes` recursively or you will miss inherited fields, and the
  doc will under-describe the capability.
- **A block may have no view of its own.** Shared, editor-agnostic block views mean one view can
  serve both Block List and Block Grid. If no view resolves under the alias, check the shared
  components folder before concluding the view is missing.
- **Element types are as documentable as document types.** A block's element type declares
  author-editable fields and renders standing behavior, so it earns a feature doc on the same terms
  as a page type.
- **`.uda` files regenerate on local startup.** Treat whatever is committed as the schema of record;
  do not read meaning into uncommitted churn.
