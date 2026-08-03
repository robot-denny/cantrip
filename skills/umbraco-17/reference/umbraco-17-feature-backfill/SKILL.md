---
name: umbraco-17-feature-backfill
description: How to reverse-engineer behavioral documentation from Umbraco 17 code — locating the .uda schema artifact, the generated model, and the Razor view for a document type or element type, parsing the .uda's property structure and compositions, and mapping data-type UDIs and editor aliases to readable field types. Consult when documenting an Umbraco capability that has no spec, plan, or tests, when backfilling feature docs on an existing Umbraco site, or when resolving a document-type alias or block name to its implementation.
---

# Backfilling behavioral docs from Umbraco 17 code

Supplements the generic from-code mode with where Umbraco keeps the three code sources, and how to
read them.

## The three sources, for Umbraco

### 1. The `.uda` schema artifact

Find the matching `document-type__*.uda` or `element-type__*.uda` under the Deploy revision
directory. Parse its JSON for:

- `Name` — the human-readable capability name
- `Alias` — the identifier, and the basis for the doc's slug
- `Description` / `Icon` — context
- Every `PropertyGroups[].PropertyTypes[]` entry — each property's `Name` (label), `Alias`,
  `DataType` UDI, `Mandatory` flag, and per-property `Description` (help text)
- `CompositionContentTypes` — inherited property groups, resolved recursively via their UDIs

Reading `.uda` structure: groups with `"Type": 1` are tabs; groups without a `Type` use
`tabAlias`/`groupAlias` as their `Alias`.

### 2. The generated model

Read the matching `*.generated.cs` if the project commits generated models. **Use the generated C#
property types as the primary signal for what each property is** — a strongly-typed
`IHtmlEncodedString`, `bool`, `MediaWithCrops`, or `IEnumerable<IPublishedElement>` is more
reliable and more repo-native than reverse-mapping a `umb://data-type/...` UDI.

Fall back to the UDI table below only when the model is absent or the C# type is ambiguous.

**Slot:** `.agents/config/stack.md` → `## Models`
**If empty:** check whether `*.generated.cs` files are committed. If they are absent, models are
generated at runtime and unavailable to read — rely on the `.uda` plus the UDI table instead.

### 3. The Razor view

Find the `.cshtml` that renders it. Page templates live at the views root; block components live
under the shared block-components folder, with editor-specific folders for anything genuinely
restricted to one editor.

Read it for **conditional branches** — `if`/`else`, null and empty checks,
`@if (Model.X.Any())`, toggle guards — and write one scenario per branch found.

**Slot:** `.agents/config/paths.md` → `## Umbraco`
**If empty:** locate the Deploy revision directory by searching for `*.uda` files, and the views by
searching for `*.cshtml` matching the alias. If the project has no committed `.uda` files, it is
not using Deploy — read schema from the running instance via MCP instead.

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
