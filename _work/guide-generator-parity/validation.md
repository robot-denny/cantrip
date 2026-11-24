# Validation log: guide generator parity

## Step 1: Deploy 17.3.1 and 17.0.1

Measured read-only, by a throwaway script that loads every `document-type__*.uda` and
`data-type__*.uda` in one source `Revision` folder per project (build-output and publish copies
of the same folder skipped) and groups the files by `__version`. It collected three sets of keys
(top level, each property including those nested in groups, each group) plus the `Permissions`
keys, then the JSON type of each key the Deploy adapter reads (`guidelib/deploy.py`).

### Counts compared

| Source | Version | Document types | Their properties | Data types |
|---|---|---|---|---|
| A production Umbraco Cloud project | 17.2.1 (accepted) | 7 | 18 | 36 |
| A production Umbraco Cloud project | 17.3.1 | 56 | 109 | 36 |
| The demo project | 17.0.1 | 42 | 63 | 21 |

The demo project's source folder holds only 17.0.1 artifacts (103 in all, every kind), so it was
compared against the production project's 17.2.1 files, the only accepted-version artifacts of
these kinds on hand. The existing comment's note that the demo project carries 17.1.0, 17.2.0 and
17.2.1 no longer describes its current checkout.

### Keys found

Document type, top level, at all three versions: `Alias`, `AllowedTemplates`,
`CompositionContentTypes`, `Dependencies`, `Description`, `HistoryCleanup`, `Icon`, `Name`,
`Parent`, `Permissions`, `PropertyGroups`, `PropertyTypes`, `Thumbnail`, `Udi`, `__type`,
`__version`. 17.0.1 also has `DefaultTemplate` (11 of 42) and `ListView` (2 of 42). The production
project has no document type with an allowed template, so `DefaultTemplate` has nothing to appear
on there. It is not a version difference.

Group, at all three: `Alias`, `Key`, `Name`, `PropertyTypes`, `SortOrder`, `Type`.

Property: `Alias`, `DataType`, `Description`, `Key`, `Mandatory`, `Name`, `SortOrder` at all
three. `ValueType` is on every 17.2.1 and 17.3.1 property and on no 17.0.1 one. Keys emitted only
when set appear on a few properties: `LabelOnTop` and `MandatoryMessage` (17.3.1, 17.0.1),
`Validation` and `ValidationMessage` (17.3.1, 2 of 109 properties).

`Permissions`: `AllowedChildContentTypes`, `IsElementType` at all three, and `AllowedAtRoot` on
the one document type in each of 17.3.1 and 17.0.1 that is allowed at root.

Data type, top level: `Configuration`, `DatabaseType`, `Dependencies`, `EditorAlias`,
`EditorUiAlias`, `Name`, `Udi`, `__type`, `__version` at all three.

JSON types of the keys the adapter reads (`Alias`, `Name`, `Description`, `Icon`, `Udi`,
`__type`, `AllowedTemplates`, `CompositionContentTypes`, `Permissions` and its three keys,
`PropertyGroups`, `PropertyTypes`, group `Alias`/`Name`/`SortOrder`/`Type`/`PropertyTypes`,
property `Alias`/`DataType`/`Description`/`Mandatory`/`Name`/`SortOrder`, data type
`Configuration`/`EditorAlias`): identical at every version where the key appears.

### Differences

- **17.3.1 against 17.2.1: a data type's top-level `Parent`.** 33 of 36 data types at 17.3.1
  carry it; none at 17.2.1 does. The adapter does not read `Parent`. The optional property keys
  above are emission-on-value, not a shape change.
- **17.0.1 against 17.2.1: no `ValueType` on properties.** The adapter does not read `ValueType`.

### Decision

Both accepted. `ACCEPTED_DEPLOY_VERSIONS` is now
`("17.0.1", "17.0.2", "17.1.0", "17.2.0", "17.2.1", "17.3.1")`.

### Tests

- New cases `deploy-version-17.3.1-read` and `deploy-version-17.0.1-read` restamp every artifact
  in the fixture tree to the version and require the golden Deploy dossier.
- RED before the change: both failed with exit 1 and "6 Deploy artifacts were not read ...
  declares __version 17.3.1" (and 17.0.1). The other 83 cases passed.
- GREEN after: 85/85 in `guide-check`. `deploy-requested-version-skipped` (16.4.0) still passes.
