#!/usr/bin/env bash
#
# Regenerate the guide-check suite — fixtures for the /guide spell's script.
#
# Generated rather than hand-built, for the reason tests/make-fixtures.sh records: a
# malformed fixture fails exactly like a real bug, and the debugging goes to the wrong
# place first. Regenerating is how you clear that suspicion.
#
# Each case is a minimal fake project tree plus an `expect` file. Minimal means: only the
# files the adapter under test has to read. A Deploy tree therefore carries data-type
# artifacts (the editor alias is reachable only by resolving a `DataType` UDI), while the
# uSync tree carries just the one data type whose option list is needed (a uSync property
# already names its editor inline in `<Type>`).
#
# The element and attribute shapes of both formats come from
# skills/umbraco-17/reference/umbraco-17-feature-backfill/SKILL.md, which was verified
# against real projects. Two shapes are NOT covered there and are marked in place below.
#
# Usage:  tests/make-guide-fixtures.sh

set -euo pipefail
cd "$(dirname "$0")" || exit 2

CASES="guide-check"
rm -rf "$CASES"
mkdir -p "$CASES"

# The suite's `subject` names the executable under test — a script that does not exist yet.
# Every case therefore fails as "subject missing or not executable", which is this suite's
# RED signal until Step 3 lands. `subject` is regenerated here because this script wipes the
# directory it lives in; a hand-placed one would vanish on the next run and every case would
# then fail pointing nowhere near its cause.
printf 'skills/umbraco-17/spellbook/guide/scripts/guide.py\n' > "$CASES/subject"

# --- stable fake identifiers ---------------------------------------------------
# Deploy writes UDIs with the dashes stripped; uSync writes canonical dashed GUIDs. Same
# entity, two spellings, so both forms are declared here and paired by name. None of them
# reaches the dossier — the dossier is normalized on the alias — so a fixture may use
# obviously-fake values, which also makes a mis-resolved reference readable at a glance.
U_BANNER=aaaa1111aaaa1111aaaa111111111111 ; G_BANNER=aaaa1111-aaaa-1111-aaaa-111111111111
U_BASE=bbbb2222bbbb2222bbbb222222222222   ; G_BASE=bbbb2222-bbbb-2222-bbbb-222222222222
U_TEXT=dddd1111dddd1111dddd111111111111   ; G_TEXT=dddd1111-dddd-1111-dddd-111111111111
U_TOGGLE=dddd2222dddd2222dddd222222222222 ; G_TOGGLE=dddd2222-dddd-2222-dddd-222222222222
U_DROP=dddd3333dddd3333dddd333333333333   ; G_DROP=dddd3333-dddd-3333-dddd-333333333333
U_AREA=dddd4444dddd4444dddd444444444444   ; G_AREA=dddd4444-dddd-4444-dddd-444444444444
# A second identity for the same alias, used only by the duplicate-alias refusal case.
U_OTHER=cccc9999cccc9999cccc999999999999

DEPLOY_ARTIFACT_TYPE='Umbraco.Deploy.Infrastructure,Umbraco.Deploy.Infrastructure.Artifacts.ContentType.DocumentTypeArtifact'
DEPLOY_DATATYPE_TYPE='Umbraco.Deploy.Infrastructure,Umbraco.Deploy.Infrastructure.Artifacts.DataTypeArtifact'
# One of the three versions observed side by side in the demo project. A version check is
# per artifact under Deploy, so a fixture asserting the happy path must use a real value.
DEPLOY_VERSION='17.2.0'

# ==============================================================================
# The component both formats describe
# ==============================================================================
#
#   alertBanner (element type, composes baseSettings)
#     tab  content  "Content"                 sort 10
#       group content/message "Message"       sort 10
#         alertHeading      Umbraco.TextBox           REQUIRED   sort 10
#         alertDismissible  Umbraco.TrueFalse         optional   sort 20
#     tab  settings "Settings"                sort 20
#         alertSeverity     Umbraco.DropDown.Flexible optional   sort 10
#                           options Info | Warning | Critical, Info the default
#   baseSettings (element type)
#     tab  seo      "SEO"                     sort 100
#         metaDescription   Umbraco.TextArea          optional   sort 10
#       group seo/social "Social"             sort 20
#         metaKeywords      Umbraco.TextBox           optional   sort 10
#
# A property lives directly on a tab in one place and inside a group in another, because
# both occur in real projects and the two levels are the thing a reader most wants the
# dossier to keep straight.
#
# The two levels are also referenced two ways on purpose. Under uSync a property names its
# owner with a BARE alias twice: metaDescription names a TAB (`seo`), metaKeywords names a
# GROUP (`social`, whose declared alias is the path `seo/social`). The reference measured 164
# bare references in one project, of which 114 resolved to a group -- so both outcomes have
# to be reachable here, or an adapter reading "no slash means tab" passes the suite while
# being wrong in the majority case.

# --- Deploy: a revision directory of .uda artifacts ----------------------------
deploy_tree() {  # deploy_tree <case-root>
  local rev="$1/src/Web/umbraco/Deploy/Revision"
  mkdir -p "$rev"

  # Groups carrying "Type": 1 are tabs. A group without `Type` is a group, and its `Alias`
  # is the `tabAlias/groupAlias` path. `Mandatory` and `Description` are emitted only when
  # they have something to say, which is why the optional properties below simply omit
  # `Mandatory` — an adapter has to read it as a truthiness test, exactly as it must read
  # `Permissions.IsElementType`.
  cat > "$rev/document-type__$U_BANNER.uda" <<EOF
{
  "Name": "Alert Banner",
  "Alias": "alertBanner",
  "AllowedTemplates": [],
  "HistoryCleanup": {},
  "Icon": "icon-alert color-red",
  "Thumbnail": "folder.png",
  "Description": "A banner that announces something time-sensitive at the top of a page.",
  "Permissions": {
    "IsElementType": true,
    "AllowedChildContentTypes": []
  },
  "CompositionContentTypes": [
    "umb://document-type/$U_BASE"
  ],
  "PropertyGroups": [
    {
      "Key": "aaaa1111-0001-4000-8000-000000000001",
      "Name": "Content",
      "SortOrder": 10,
      "Type": 1,
      "Alias": "content",
      "PropertyTypes": []
    },
    {
      "Key": "aaaa1111-0002-4000-8000-000000000002",
      "Name": "Message",
      "SortOrder": 10,
      "Alias": "content/message",
      "PropertyTypes": [
        {
          "Key": "aaaa1111-0101-4000-8000-000000000101",
          "Alias": "alertHeading",
          "DataType": "umb://data-type/$U_TEXT",
          "ValueType": "System.String",
          "Mandatory": true,
          "Description": "The line an editor reads first.",
          "Name": "Alert Heading",
          "SortOrder": 10
        },
        {
          "Key": "aaaa1111-0102-4000-8000-000000000102",
          "Alias": "alertDismissible",
          "DataType": "umb://data-type/$U_TOGGLE",
          "ValueType": "System.Boolean",
          "Description": "Let a visitor close the banner for the rest of the session.",
          "Name": "Alert Dismissible",
          "SortOrder": 20
        }
      ]
    },
    {
      "Key": "aaaa1111-0003-4000-8000-000000000003",
      "Name": "Settings",
      "SortOrder": 20,
      "Type": 1,
      "Alias": "settings",
      "PropertyTypes": [
        {
          "Key": "aaaa1111-0103-4000-8000-000000000103",
          "Alias": "alertSeverity",
          "DataType": "umb://data-type/$U_DROP",
          "ValueType": "System.String",
          "Description": "How loudly the banner presents itself.",
          "Name": "Alert Severity",
          "SortOrder": 10
        }
      ]
    }
  ],
  "PropertyTypes": [],
  "Udi": "umb://document-type/$U_BANNER",
  "Dependencies": [
    {
      "Udi": "umb://data-type/$U_TEXT",
      "Ordering": true
    },
    {
      "Udi": "umb://data-type/$U_TOGGLE",
      "Ordering": true
    },
    {
      "Udi": "umb://data-type/$U_DROP",
      "Ordering": true
    },
    {
      "Udi": "umb://document-type/$U_BASE",
      "Ordering": true
    }
  ],
  "__type": "$DEPLOY_ARTIFACT_TYPE",
  "__version": "$DEPLOY_VERSION"
}
EOF

  cat > "$rev/document-type__$U_BASE.uda" <<EOF
{
  "Name": "Base Settings",
  "Alias": "baseSettings",
  "AllowedTemplates": [],
  "HistoryCleanup": {},
  "Icon": "icon-settings color-black",
  "Thumbnail": "folder.png",
  "Description": "Fields every block carries.",
  "Permissions": {
    "IsElementType": true,
    "AllowedChildContentTypes": []
  },
  "CompositionContentTypes": [],
  "PropertyGroups": [
    {
      "Key": "bbbb2222-0001-4000-8000-000000000001",
      "Name": "SEO",
      "SortOrder": 100,
      "Type": 1,
      "Alias": "seo",
      "PropertyTypes": [
        {
          "Key": "bbbb2222-0101-4000-8000-000000000101",
          "Alias": "metaDescription",
          "DataType": "umb://data-type/$U_AREA",
          "ValueType": "System.String",
          "Description": "Summary used by search engines.",
          "Name": "Meta Description",
          "SortOrder": 10
        }
      ]
    },
    {
      "Key": "bbbb2222-0002-4000-8000-000000000002",
      "Name": "Social",
      "SortOrder": 20,
      "Alias": "seo/social",
      "PropertyTypes": [
        {
          "Key": "bbbb2222-0102-4000-8000-000000000102",
          "Alias": "metaKeywords",
          "DataType": "umb://data-type/$U_TEXT",
          "ValueType": "System.String",
          "Description": "Terms this page should be found by.",
          "Name": "Meta Keywords",
          "SortOrder": 10
        }
      ]
    }
  ],
  "PropertyTypes": [],
  "Udi": "umb://document-type/$U_BASE",
  "Dependencies": [
    {
      "Udi": "umb://data-type/$U_AREA",
      "Ordering": true
    },
    {
      "Udi": "umb://data-type/$U_TEXT",
      "Ordering": true
    }
  ],
  "__type": "$DEPLOY_ARTIFACT_TYPE",
  "__version": "$DEPLOY_VERSION"
}
EOF

  deploy_data_type "$rev" "$U_TEXT"   "Textstring" "Umbraco.TextBox"  "Umb.PropertyEditorUi.TextBox"  "Nvarchar" '{}'
  deploy_data_type "$rev" "$U_TOGGLE" "True/false" "Umbraco.TrueFalse" "Umb.PropertyEditorUi.Toggle"  "Integer"  '{}'
  deploy_data_type "$rev" "$U_AREA"   "Textarea"   "Umbraco.TextArea" "Umb.PropertyEditorUi.TextArea" "Ntext"    '{}'

  # The option list lives on the data type, in both formats — a content type only points at
  # it. `items` and `multiple` are the keys a real Flexible Dropdown carries. `default` is
  # the key Umbraco's own toggle configuration uses, borrowed here so the fixture can state
  # which option is the default; a stock dropdown does not carry it, so an adapter must read
  # it as optional and mark no default when it is absent. Confirm this key against a real
  # project before treating the default marker as something a genuine export supplies -- it
  # is the one dossier feature here with no verified source.
  deploy_data_type "$rev" "$U_DROP" "Alert Severity" "Umbraco.DropDown.Flexible" \
    "Umb.PropertyEditorUi.Dropdown" "Nvarchar" '{
    "items": [
      "Info",
      "Warning",
      "Critical"
    ],
    "multiple": false,
    "default": "Info"
  }'
}

deploy_data_type() {  # deploy_data_type <rev-dir> <udi> <name> <editor> <ui> <dbtype> <config-json>
  cat > "$1/data-type__$2.uda" <<EOF
{
  "Name": "$3",
  "EditorAlias": "$4",
  "EditorUiAlias": "$5",
  "DatabaseType": "$6",
  "Configuration": $7,
  "Udi": "umb://data-type/$2",
  "Dependencies": [],
  "__type": "$DEPLOY_DATATYPE_TYPE",
  "__version": "$DEPLOY_VERSION"
}
EOF
}

# --- uSync: the same component as XML -----------------------------------------
usync_tree() {  # usync_tree <case-root>
  local root="$1/uSync/v17"
  mkdir -p "$root/ContentTypes" "$root/DataTypes"

  # Declared once per project, and `format` is the thing to gate on — it numbers separately
  # from both the package version and the folder name.
  cat > "$root/usync.config" <<'EOF'
<uSync version="17.0.4.0" format="10.7.0" />
EOF

  # Filenames are the lowercased alias. The alias itself is an attribute on the root
  # element, never an <Info> child. <IsElement> is always written, so it is read as a
  # boolean — the opposite of Deploy's truthiness test on an absent key.
  #
  # Every property names its owner with <Tab Alias="...">, which may be a `tab/group` path
  # or a bare alias naming either level. alertSeverity below uses the bare form to name a
  # TAB, so an adapter that infers the level from the presence of a slash gets it wrong.
  # Captions repeat freely and are never keys.
  cat > "$root/ContentTypes/alertbanner.config" <<EOF
<?xml version="1.0" encoding="utf-8"?>
<ContentType Key="$G_BANNER" Alias="alertBanner" Level="1">
  <Info>
    <Name>Alert Banner</Name>
    <Icon>icon-alert color-red</Icon>
    <Thumbnail>folder.png</Thumbnail>
    <Description><![CDATA[A banner that announces something time-sensitive at the top of a page.]]></Description>
    <AllowAtRoot>False</AllowAtRoot>
    <IsListView>False</IsListView>
    <Variations>Nothing</Variations>
    <IsElement>true</IsElement>
    <Compositions>
      <Composition Key="$G_BASE">baseSettings</Composition>
    </Compositions>
    <DefaultTemplate></DefaultTemplate>
    <AllowedTemplates />
  </Info>
  <Structure />
  <GenericProperties>
    <GenericProperty>
      <Key>aaaa1111-0101-4000-8000-000000000101</Key>
      <Name>Alert Heading</Name>
      <Alias>alertHeading</Alias>
      <Definition>$G_TEXT</Definition>
      <Type>Umbraco.TextBox</Type>
      <Mandatory>true</Mandatory>
      <Validation></Validation>
      <Description><![CDATA[The line an editor reads first.]]></Description>
      <SortOrder>10</SortOrder>
      <Tab Alias="content/message">Message</Tab>
      <Variations>Nothing</Variations>
    </GenericProperty>
    <GenericProperty>
      <Key>aaaa1111-0102-4000-8000-000000000102</Key>
      <Name>Alert Dismissible</Name>
      <Alias>alertDismissible</Alias>
      <Definition>$G_TOGGLE</Definition>
      <Type>Umbraco.TrueFalse</Type>
      <Mandatory>false</Mandatory>
      <Validation></Validation>
      <Description><![CDATA[Let a visitor close the banner for the rest of the session.]]></Description>
      <SortOrder>20</SortOrder>
      <Tab Alias="content/message">Message</Tab>
      <Variations>Nothing</Variations>
    </GenericProperty>
    <GenericProperty>
      <Key>aaaa1111-0103-4000-8000-000000000103</Key>
      <Name>Alert Severity</Name>
      <Alias>alertSeverity</Alias>
      <Definition>$G_DROP</Definition>
      <Type>Umbraco.DropDown.Flexible</Type>
      <Mandatory>false</Mandatory>
      <Validation></Validation>
      <Description><![CDATA[How loudly the banner presents itself.]]></Description>
      <SortOrder>10</SortOrder>
      <Tab Alias="settings">Settings</Tab>
      <Variations>Nothing</Variations>
    </GenericProperty>
  </GenericProperties>
  <Tabs>
    <Tab>
      <Key>aaaa1111-0001-4000-8000-000000000001</Key>
      <Caption>Content</Caption>
      <Alias>content</Alias>
      <Type>Tab</Type>
      <SortOrder>10</SortOrder>
    </Tab>
    <Tab>
      <Key>aaaa1111-0002-4000-8000-000000000002</Key>
      <Caption>Message</Caption>
      <Alias>content/message</Alias>
      <Type>Group</Type>
      <SortOrder>10</SortOrder>
    </Tab>
    <Tab>
      <Key>aaaa1111-0003-4000-8000-000000000003</Key>
      <Caption>Settings</Caption>
      <Alias>settings</Alias>
      <Type>Tab</Type>
      <SortOrder>20</SortOrder>
    </Tab>
  </Tabs>
</ContentType>
EOF

  cat > "$root/ContentTypes/basesettings.config" <<EOF
<?xml version="1.0" encoding="utf-8"?>
<ContentType Key="$G_BASE" Alias="baseSettings" Level="1">
  <Info>
    <Name>Base Settings</Name>
    <Icon>icon-settings color-black</Icon>
    <Thumbnail>folder.png</Thumbnail>
    <Description><![CDATA[Fields every block carries.]]></Description>
    <AllowAtRoot>False</AllowAtRoot>
    <IsListView>False</IsListView>
    <Variations>Nothing</Variations>
    <IsElement>true</IsElement>
    <Compositions />
    <DefaultTemplate></DefaultTemplate>
    <AllowedTemplates />
  </Info>
  <Structure />
  <GenericProperties>
    <GenericProperty>
      <Key>bbbb2222-0101-4000-8000-000000000101</Key>
      <Name>Meta Description</Name>
      <Alias>metaDescription</Alias>
      <Definition>$G_AREA</Definition>
      <Type>Umbraco.TextArea</Type>
      <Mandatory>false</Mandatory>
      <Validation></Validation>
      <Description><![CDATA[Summary used by search engines.]]></Description>
      <SortOrder>10</SortOrder>
      <Tab Alias="seo">SEO</Tab>
      <Variations>Nothing</Variations>
    </GenericProperty>
    <GenericProperty>
      <Key>bbbb2222-0102-4000-8000-000000000102</Key>
      <Name>Meta Keywords</Name>
      <Alias>metaKeywords</Alias>
      <Definition>$G_TEXT</Definition>
      <Type>Umbraco.TextBox</Type>
      <Mandatory>false</Mandatory>
      <Validation></Validation>
      <Description><![CDATA[Terms this page should be found by.]]></Description>
      <SortOrder>10</SortOrder>
      <Tab Alias="social">Social</Tab>
      <Variations>Nothing</Variations>
    </GenericProperty>
  </GenericProperties>
  <Tabs>
    <Tab>
      <Key>bbbb2222-0001-4000-8000-000000000001</Key>
      <Caption>SEO</Caption>
      <Alias>seo</Alias>
      <Type>Tab</Type>
      <SortOrder>100</SortOrder>
    </Tab>
    <Tab>
      <Key>bbbb2222-0002-4000-8000-000000000002</Key>
      <Caption>Social</Caption>
      <Alias>seo/social</Alias>
      <Type>Group</Type>
      <SortOrder>20</SortOrder>
    </Tab>
  </Tabs>
</ContentType>
EOF

  # Only the dropdown is serialized here: a uSync property already names its editor inline,
  # so the DataTypes folder is needed for the option list and nothing else.
  #
  # NOT COVERED by umbraco-17-feature-backfill: the reference documents uSync content types
  # and the `usync.config` gate, and the block spell records that a data type's palette lives
  # in its `<Config>` payload — but the surrounding <DataType>/<Info> element names are from
  # neither. Confirm this shape against a real uSync export when one is available; the
  # `<Config>` JSON is the part the adapter reads.
  cat > "$root/DataTypes/alertseverity.config" <<EOF
<?xml version="1.0" encoding="utf-8"?>
<DataType Key="$G_DROP" Alias="alertSeverity" Level="1">
  <Info>
    <Name>Alert Severity</Name>
    <EditorAlias>Umbraco.DropDown.Flexible</EditorAlias>
    <EditorUiAlias>Umb.PropertyEditorUi.Dropdown</EditorUiAlias>
    <DatabaseType>Nvarchar</DatabaseType>
    <SortOrder>0</SortOrder>
  </Info>
  <Config><![CDATA[{
  "items": [
    "Info",
    "Warning",
    "Critical"
  ],
  "multiple": false,
  "default": "Info"
}]]></Config>
</DataType>
EOF
}

# A property-less twin of alertBanner, for the two refusal cases. It is deliberately the
# thinner of the pair: a refusal that only ever saw identical copies would pass while the
# real hazard -- a stale empty artifact winning over a full one -- went unnoticed.
duplicate_banner() {  # duplicate_banner <path> <udi>
  cat > "$1" <<EOF
{
  "Name": "Alert Banner",
  "Alias": "alertBanner",
  "AllowedTemplates": [],
  "HistoryCleanup": {},
  "Icon": "icon-alert color-red",
  "Thumbnail": "folder.png",
  "Description": "A banner that announces something time-sensitive at the top of a page.",
  "Permissions": {
    "IsElementType": true,
    "AllowedChildContentTypes": []
  },
  "CompositionContentTypes": [],
  "PropertyGroups": [],
  "PropertyTypes": [],
  "Udi": "umb://document-type/$2",
  "Dependencies": [],
  "__type": "$DEPLOY_ARTIFACT_TYPE",
  "__version": "$DEPLOY_VERSION"
}
EOF
}

expect() {  # expect <case-root> <lines...>
  local root=$1; shift
  printf '%s\n' "$@" > "$root/expect"
}

# ==============================================================================
# The expected dossier — hand-authored, and the suite's real specification
# ==============================================================================
#
# Written from the component sketched above, BY HAND, before any implementation exists to
# capture output from. That direction matters: a golden file captured from a run asserts only
# that the code still does what it did, while one authored from intent asserts that the code
# does what was asked. Nothing here was produced by running anything.
#
# It replaces a list of substring assertions, which could not do this job. `contains` finds a
# value anywhere in the output, so a dossier with `mandatory` transposed between two
# properties, or the default marker on the wrong option, satisfied every assertion the first
# version of this suite made -- both were demonstrated against stub implementations. Field
# binding, nesting, and array order are all only assertable against the whole document.
#
# `sourceSignature` is masked in the comparison. It is a hash the subject computes, so it
# cannot be hand-authored, and writing one in here would assert the implementation against
# itself. Its equality ACROSS the two formats is Step 4's claim, asserted there with
# `same_stdout_as` over the `signature` subcommand.
#
# This file therefore also fixes the dossier's serialization: two-space-indented JSON, a
# space after each colon, keys in the order below, `null` for an absent inheritance, and an
# empty array rather than an omitted key.
expected_dossier() {  # expected_dossier <case-root> <rung>
  cat > "$1/expected-dossier.json" <<EOF
{
  "dossierVersion": 1,
  "rung": "$2",
  "alias": "alertBanner",
  "name": "Alert Banner",
  "kind": "element",
  "icon": "icon-alert color-red",
  "description": "A banner that announces something time-sensitive at the top of a page.",
  "structureAvailable": true,
  "compositions": [
    "baseSettings"
  ],
  "tabs": [
    {
      "alias": "content",
      "name": "Content",
      "sortOrder": 10,
      "properties": [],
      "groups": [
        {
          "alias": "content/message",
          "name": "Message",
          "sortOrder": 10,
          "properties": [
            {
              "alias": "alertHeading",
              "name": "Alert Heading",
              "description": "The line an editor reads first.",
              "editor": "Umbraco.TextBox",
              "mandatory": true,
              "sortOrder": 10,
              "options": [],
              "inheritedFrom": null
            },
            {
              "alias": "alertDismissible",
              "name": "Alert Dismissible",
              "description": "Let a visitor close the banner for the rest of the session.",
              "editor": "Umbraco.TrueFalse",
              "mandatory": false,
              "sortOrder": 20,
              "options": [],
              "inheritedFrom": null
            }
          ]
        }
      ]
    },
    {
      "alias": "settings",
      "name": "Settings",
      "sortOrder": 20,
      "properties": [
        {
          "alias": "alertSeverity",
          "name": "Alert Severity",
          "description": "How loudly the banner presents itself.",
          "editor": "Umbraco.DropDown.Flexible",
          "mandatory": false,
          "sortOrder": 10,
          "options": [
            {
              "value": "Info",
              "default": true
            },
            {
              "value": "Warning",
              "default": false
            },
            {
              "value": "Critical",
              "default": false
            }
          ],
          "inheritedFrom": null
        }
      ],
      "groups": []
    },
    {
      "alias": "seo",
      "name": "SEO",
      "sortOrder": 100,
      "properties": [
        {
          "alias": "metaDescription",
          "name": "Meta Description",
          "description": "Summary used by search engines.",
          "editor": "Umbraco.TextArea",
          "mandatory": false,
          "sortOrder": 10,
          "options": [],
          "inheritedFrom": "baseSettings"
        }
      ],
      "groups": [
        {
          "alias": "seo/social",
          "name": "Social",
          "sortOrder": 20,
          "properties": [
            {
              "alias": "metaKeywords",
              "name": "Meta Keywords",
              "description": "Terms this page should be found by.",
              "editor": "Umbraco.TextBox",
              "mandatory": false,
              "sortOrder": 10,
              "options": [],
              "inheritedFrom": "baseSettings"
            }
          ]
        }
      ]
    }
  ],
  "sourceSignature": "<computed>"
}
EOF
}

# The `expect` file carries only what differs between the two cases, plus the assertions
# worth stating in human terms for a readable failure. Everything structural is the golden
# file's job -- restating it here would mean two places to edit and one of them going stale.
#
# The rung is the one legitimate difference between the cases, and it is asserted both ways
# round: positively for its own value, negatively for the other's. The negative half catches
# an adapter that read one format and labelled the dossier with the other -- which every
# positive assertion in the suite would otherwise pass.
COMMON=(
  "exit: 0"
  "args: extract alertBanner"
  "stdout_matches: expected-dossier.json"
  'mask: "sourceSignature":'
  'contains: "alias": "alertBanner"'
  'contains: "kind": "element"'
)

# --- the two cases -------------------------------------------------------------

C="$CASES/deploy-dossier"; mkdir -p "$C"; deploy_tree "$C"; expected_dossier "$C" deploy
expect "$C" "${COMMON[@]}" \
  'contains: "rung": "deploy"' \
  'not_contains: "rung": "usync"'

C="$CASES/usync-dossier";  mkdir -p "$C"; usync_tree "$C";  expected_dossier "$C" usync
expect "$C" "${COMMON[@]}" \
  'contains: "rung": "usync"' \
  'not_contains: "rung": "deploy"'

# --- two refusals, each guarding a behavior a review found missing --------------
#
# Both are the same rule seen twice: a read that cannot be answered unambiguously must say
# so rather than produce a thinner dossier. Both were reachable before, and both produced a
# valid-looking document with exit 0 — the silent-empty shape the ladder exists to prevent.

# Two shapes of the same ambiguity, because they trip different guards and both occur.
#
# A stale revision folder beside a live one is a COPY: same entity, so same UDI. The stale
# copy carries no properties, so whichever the walk reached first decided the answer, and it
# reliably picked the empty one.
C="$CASES/deploy-duplicate-udi"; mkdir -p "$C"
deploy_tree "$C"
STALE="$C/stale-export/umbraco/Deploy/Revision"; mkdir -p "$STALE"
duplicate_banner "$STALE/document-type__$U_BANNER.uda" "$U_BANNER"
expect "$C" \
  "exit: 1" \
  "args: extract alertBanner" \
  "contains: declare the same UDI" \
  "contains: stale-export" \
  'not_contains: "dossierVersion"'

# A type recreated rather than copied is a DIFFERENT entity wearing the same alias, so the
# UDI guard never sees it and the alias index is what has to refuse. This is the path that
# produced the observed empty dossier, since a lookup is by alias.
C="$CASES/deploy-duplicate-alias"; mkdir -p "$C"
deploy_tree "$C"
OTHER="$C/second-export/umbraco/Deploy/Revision"; mkdir -p "$OTHER"
duplicate_banner "$OTHER/document-type__$U_OTHER.uda" "$U_OTHER"
expect "$C" \
  "exit: 1" \
  "args: extract alertBanner" \
  "contains: declare the same alias" \
  "contains: second-export" \
  'not_contains: "dossierVersion"'

# The content type is exported and one data type it points at is not. The property is real,
# so the earlier reading kept it with an empty editor -- but a property table whose whole job
# is to say what an editor types into a field cannot report the field and not its type, and
# `structureAvailable` would have claimed true while saying so.
C="$CASES/deploy-missing-data-type"; mkdir -p "$C"
deploy_tree "$C"
rm "$C/src/Web/umbraco/Deploy/Revision/data-type__$U_DROP.uda"
expect "$C" \
  "exit: 1" \
  "args: extract alertBanner" \
  "contains: the export is partial" \
  "contains: $U_DROP" \
  'not_contains: "dossierVersion"'

echo "regenerated $(find "$CASES" -mindepth 1 -maxdepth 1 -type d | wc -l | tr -d ' ') fixtures"
