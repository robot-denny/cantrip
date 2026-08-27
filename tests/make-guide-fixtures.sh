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
# against real projects — including the uSync <DataType> shape, measured on a real export's
# 150 data types and marked in place below.
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
# A component nobody asks for, used only by the mixed-version case: it exists to be the one
# artifact the read refuses, so it must not be reachable from any other fixture's component.
U_STALE=cccc8888cccc8888cccc888888888888
U_PAGE=eeee1111eeee1111eeee111111111111   ; G_PAGE=eeee1111-eeee-1111-eeee-111111111111
G_VIS=ffff3333-ffff-3333-ffff-333333333333
# The two components that legitimately have no properties. Both shapes were observed on the
# demo project's 68 document types, which is why they are fixtures rather than hypotheses.
U_TAG=ffff1111ffff1111ffff111111111111    ; G_TAG=ffff1111-ffff-1111-ffff-111111111111
U_VIS=ffff2222ffff2222ffff222222222222    ; G_VIS=ffff2222-ffff-2222-ffff-222222222222
# The inventory determiner's own cast. Six element types and two block-editor data types,
# because that is the smallest project in which the palette rule and the element-type flag
# give DIFFERENT answers -- six carry the flag and three are content blocks.
U_NOTICE=a11a1111a11a1111a11a111111111111  ; G_NOTICE=a11a1111-a11a-1111-a11a-111111111111
U_MEDIA=a22a2222a22a2222a22a222222222222   ; G_MEDIA=a22a2222-a22a-2222-a22a-222222222222
U_SLIDE=a33a3333a33a3333a33a333333333333   ; G_SLIDE=a33a3333-a33a-3333-a33a-333333333333
U_MSET=a44a4444a44a4444a44a444444444444    ; G_MSET=a44a4444-a44a-4444-a44a-444444444444
U_FOOTER=a55a5555a55a5555a55a555555555555  ; G_FOOTER=a55a5555-a55a-5555-a55a-555555555555
U_SPACING=a66a6666a66a6666a66a666666666666 ; G_SPACING=a66a6666-a66a-6666-a66a-666666666666
U_PBODY=d55d5555d55d5555d55d555555555555   ; G_PBODY=d55d5555-d55d-5555-d55d-555555555555
U_PHERO=d66d6666d66d6666d66d666666666666   ; G_PHERO=d66d6666-d66d-6666-d66d-666666666666
# The three shapes no structural flag tells apart: a page, a folder, and an abstract base.
U_TOPIC=b11b1111b11b1111b11b111111111111   ; G_TOPIC=b11b1111-b11b-1111-b11b-111111111111
U_PBASE=b22b2222b22b2222b22b222222222222   ; G_PBASE=b22b2222-b22b-2222-b22b-222222222222

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
#                           options Info | Warning | Critical
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
  # it. `items` and `multiple` are the keys a real Flexible Dropdown carries, and they are the
  # only two: verified 2026-08-26 across two projects in both formats, where 11 Deploy data
  # types and 26 uSync ones carried `items[]` and NONE of the 37 carried a `default`. An
  # earlier version of this fixture borrowed `default` from Umbraco's toggle configuration so
  # it could state which option was the default; the dossier no longer carries that marker,
  # because on this evidence it could only ever have been false.
  deploy_data_type "$rev" "$U_DROP" "Alert Severity" "Umbraco.DropDown.Flexible" \
    "Umb.PropertyEditorUi.Dropdown" "Nvarchar" '{
    "items": [
      "Info",
      "Warning",
      "Critical"
    ],
    "multiple": false
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
  # VERIFIED 2026-08-26 against a real uSync export's 150 data types, which is what this
  # shape now reproduces: the root element carries Key, Alias and Level; <Info> carries Name,
  # EditorAlias and EditorUIAlias — capital UI, not EditorUiAlias — plus <Folder> on 91 of the
  # 150; and <Config> carries the JSON payload. **There is no <DatabaseType> and no
  # <SortOrder> on a real DataType element.** An earlier version of this fixture invented both
  # and mis-spelled EditorUIAlias, because the shape had never been checked.
  #
  # Two details below look like mistakes and are the measured truth, so leave them alone. A
  # DataType's `Alias` is a DISPLAY NAME containing spaces — 143 of the 150 — which a review
  # once "corrected" to camelCase here, making the fixture less faithful rather than more.
  # And the filename is NOT the lowercased alias the way a ContentType's is: that rule held
  # 174 of 174 times for content types and 0 of 150 for data types, where the name is the
  # alias with spaces and punctuation removed and its casing kept. The adapter resolves a data
  # type by its Key and never by its filename, so being faithful here costs nothing.
  cat > "$root/DataTypes/AlertSeverity.config" <<EOF
<?xml version="1.0" encoding="utf-8"?>
<DataType Key="$G_DROP" Alias="Alert Severity" Level="2">
  <Info>
    <Name>Alert Severity</Name>
    <EditorAlias>Umbraco.DropDown.Flexible</EditorAlias>
    <EditorUIAlias>Umb.PropertyEditorUi.Dropdown</EditorUIAlias>
    <Folder>Dropdowns</Folder>
  </Info>
  <Config><![CDATA[{
  "items": [
    "Info",
    "Warning",
    "Critical"
  ],
  "multiple": false
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

# --- a page type, in each format -----------------------------------------------
#
# Its whole job is the kind. Every other fixture component is an element type, so reading
# the kind flag wrongly — Deploy's key is emitted ONLY when true, uSync's is always written
# and must be read as a boolean — produced a correct answer by luck: `element` is what you
# get from a truthiness test, a presence test, or a coin toss when the value is always true
# and always present. A review demonstrated that mutating uSync's read to a presence test
# passed all seven cases. These two are the cases that mutation fails.
#
# Deliberately minimal: one tab, one property, no compositions, no option lists. Anything
# more would duplicate coverage the alertBanner pair already carries.
deploy_page_type() {  # deploy_page_type <case-root>
  local rev="$1/src/Web/umbraco/Deploy/Revision"
  mkdir -p "$rev"
  # No `Permissions.IsElementType` at all — Deploy omits the key on a document type rather
  # than writing false, which is why a reader has to treat its absence as the answer.
  cat > "$rev/document-type__$U_PAGE.uda" <<EOF
{
  "Name": "Article Page",
  "Alias": "articlePage",
  "AllowedTemplates": [
    "umb://template/eeee1111eeee1111eeee111111111111"
  ],
  "DefaultTemplate": "umb://template/eeee1111eeee1111eeee111111111111",
  "HistoryCleanup": {},
  "Icon": "icon-article color-blue",
  "Thumbnail": "folder.png",
  "Description": "A page carrying one article.",
  "Permissions": {
    "AllowedChildContentTypes": []
  },
  "CompositionContentTypes": [],
  "PropertyGroups": [
    {
      "Key": "eeee1111-0001-4000-8000-000000000001",
      "Name": "Content",
      "SortOrder": 10,
      "Type": 1,
      "Alias": "content",
      "PropertyTypes": [
        {
          "Key": "eeee1111-0101-4000-8000-000000000101",
          "Alias": "articleHeading",
          "DataType": "umb://data-type/$U_TEXT",
          "ValueType": "System.String",
          "Mandatory": true,
          "Description": "The headline.",
          "Name": "Article Heading",
          "SortOrder": 10
        }
      ]
    }
  ],
  "PropertyTypes": [],
  "Udi": "umb://document-type/$U_PAGE",
  "Dependencies": [
    {
      "Udi": "umb://data-type/$U_TEXT",
      "Ordering": true
    }
  ],
  "__type": "$DEPLOY_ARTIFACT_TYPE",
  "__version": "$DEPLOY_VERSION"
}
EOF
  deploy_data_type "$rev" "$U_TEXT" "Textstring" "Umbraco.TextBox" \
    "Umb.PropertyEditorUi.TextBox" "Nvarchar" '{}'
}

usync_page_type() {  # usync_page_type <case-root>
  local root="$1/uSync/v17"
  mkdir -p "$root/ContentTypes"
  cat > "$root/usync.config" <<'EOF'
<uSync version="17.0.4.0" format="10.7.0" />
EOF
  # <IsElement> is written either way, so here it says false — the value a presence test
  # cannot see.
  cat > "$root/ContentTypes/articlepage.config" <<EOF
<?xml version="1.0" encoding="utf-8"?>
<ContentType Key="$G_PAGE" Alias="articlePage" Level="1">
  <Info>
    <Name>Article Page</Name>
    <Icon>icon-article color-blue</Icon>
    <Thumbnail>folder.png</Thumbnail>
    <Description><![CDATA[A page carrying one article.]]></Description>
    <AllowAtRoot>False</AllowAtRoot>
    <IsListView>False</IsListView>
    <Variations>Nothing</Variations>
    <IsElement>false</IsElement>
    <Compositions />
    <DefaultTemplate>articlePage</DefaultTemplate>
    <AllowedTemplates>
      <Template Key="eeee1111-eeee-1111-eeee-111111111111">articlePage</Template>
    </AllowedTemplates>
  </Info>
  <Structure />
  <GenericProperties>
    <GenericProperty>
      <Key>eeee1111-0101-4000-8000-000000000101</Key>
      <Name>Article Heading</Name>
      <Alias>articleHeading</Alias>
      <Definition>$G_TEXT</Definition>
      <Type>Umbraco.TextBox</Type>
      <Mandatory>true</Mandatory>
      <Validation></Validation>
      <Description><![CDATA[The headline.]]></Description>
      <SortOrder>10</SortOrder>
      <Tab Alias="content">Content</Tab>
      <Variations>Nothing</Variations>
    </GenericProperty>
  </GenericProperties>
  <Tabs>
    <Tab>
      <Key>eeee1111-0001-4000-8000-000000000001</Key>
      <Caption>Content</Caption>
      <Alias>content</Alias>
      <Type>Tab</Type>
      <SortOrder>10</SortOrder>
    </Tab>
  </Tabs>
</ContentType>
EOF
}

# --- the two components that have no properties and are not broken ---------------
#
# A component with no properties is the shape a refusal rule is most tempting to write and
# most expensive to get wrong, because BOTH of these are real. Each was found on the demo
# project's 68 document types, so neither is a hypothetical the fixtures invented:
#
#   topicTag        a taxonomy-style node: no compositions, no tabs, no groups, no
#                   properties. Only a name, an icon and a description. The dossier's tabs
#                   list comes out empty, which is the most extreme shape a completed read
#                   can produce -- and the one an over-eager "empty means broken" rule
#                   refuses first.
#   pageVisibility  a type declaring one tab and nothing in it. It contributes STRUCTURE and
#                   no fields, which is exactly what an editor sees: a tab that a composition
#                   or a later change is expected to fill.
#
# Both must extract with exit 0. A refusal here would refuse a fifth of the demo project's
# document types, so these cases exist to pin the permissive half of the line as deliberately
# as the refusal cases pin the other half. A refusal rule with no case proving what it does
# NOT refuse is how the next increment tightens it by accident.
deploy_propertyless() {  # deploy_propertyless <case-root>
  local rev="$1/src/Web/umbraco/Deploy/Revision"
  mkdir -p "$rev"

  # No `Permissions.IsElementType`, so this reads as a document type. `PropertyGroups` and
  # `PropertyTypes` are both written as empty arrays, which is what Deploy does -- all 68
  # of the demo project's artifacts carry both keys, including the property-less ones.
  cat > "$rev/document-type__$U_TAG.uda" <<EOF
{
  "Name": "Topic Tag",
  "Alias": "topicTag",
  "AllowedTemplates": [],
  "HistoryCleanup": {},
  "Icon": "icon-tag color-blue",
  "Thumbnail": "folder.png",
  "Description": "A tag an editor picks when classifying an article.",
  "Permissions": {
    "AllowedChildContentTypes": []
  },
  "CompositionContentTypes": [],
  "PropertyGroups": [],
  "PropertyTypes": [],
  "Udi": "umb://document-type/$U_TAG",
  "Dependencies": [],
  "__type": "$DEPLOY_ARTIFACT_TYPE",
  "__version": "$DEPLOY_VERSION"
}
EOF

  cat > "$rev/document-type__$U_VIS.uda" <<EOF
{
  "Name": "Page Visibility",
  "Alias": "pageVisibility",
  "AllowedTemplates": [],
  "HistoryCleanup": {},
  "Icon": "icon-eye color-grey",
  "Thumbnail": "folder.png",
  "Description": "A tab every page carries, filled in by whatever composes this.",
  "Permissions": {
    "IsElementType": true,
    "AllowedChildContentTypes": []
  },
  "CompositionContentTypes": [],
  "PropertyGroups": [
    {
      "Key": "ffff2222-0001-4000-8000-000000000001",
      "Name": "Visibility",
      "SortOrder": 30,
      "Type": 1,
      "Alias": "visibility",
      "PropertyTypes": []
    }
  ],
  "PropertyTypes": [],
  "Udi": "umb://document-type/$U_VIS",
  "Dependencies": [],
  "__type": "$DEPLOY_ARTIFACT_TYPE",
  "__version": "$DEPLOY_VERSION"
}
EOF
}

# The uSync twin of topicTag, and the only one of the pair worth serializing twice: the
# taxonomy node is the extreme shape, so if the permissive rule lives in the shared layer
# rather than in one adapter, this is where that shows. `<GenericProperties />` and `<Tabs />`
# are the empty containers -- present and empty, not absent.
usync_propertyless() {  # usync_propertyless <case-root>
  local root="$1/uSync/v17"
  mkdir -p "$root/ContentTypes"
  cat > "$root/usync.config" <<'EOF'
<uSync version="17.0.4.0" format="10.7.0" />
EOF
  cat > "$root/ContentTypes/topictag.config" <<EOF
<?xml version="1.0" encoding="utf-8"?>
<ContentType Key="$G_TAG" Alias="topicTag" Level="1">
  <Info>
    <Name>Topic Tag</Name>
    <Icon>icon-tag color-blue</Icon>
    <Thumbnail>folder.png</Thumbnail>
    <Description><![CDATA[A tag an editor picks when classifying an article.]]></Description>
    <AllowAtRoot>False</AllowAtRoot>
    <IsListView>False</IsListView>
    <Variations>Nothing</Variations>
    <IsElement>false</IsElement>
    <Compositions />
    <DefaultTemplate></DefaultTemplate>
    <AllowedTemplates />
  </Info>
  <Structure />
  <GenericProperties />
  <Tabs />
</ContentType>
EOF

  # A tab declared with nothing referencing it. Deploy's twin of this is a PropertyGroup with
  # an empty PropertyTypes array; here it is a <Tab> that no <GenericProperty> names. The tab
  # has to survive into the dossier either way -- the backoffice shows it -- and the two
  # adapters reach that answer through completely different parsing, which is why this shape
  # needs a case per format rather than one shared case.
  cat > "$root/ContentTypes/pagevisibility.config" <<EOF
<?xml version="1.0" encoding="utf-8"?>
<ContentType Key="$G_VIS" Alias="pageVisibility" Level="1">
  <Info>
    <Name>Page Visibility</Name>
    <Icon>icon-eye color-grey</Icon>
    <Thumbnail>folder.png</Thumbnail>
    <Description><![CDATA[A tab every page carries, filled in by whatever composes this.]]></Description>
    <AllowAtRoot>False</AllowAtRoot>
    <IsListView>False</IsListView>
    <Variations>Nothing</Variations>
    <IsElement>true</IsElement>
    <Compositions />
    <DefaultTemplate></DefaultTemplate>
    <AllowedTemplates />
  </Info>
  <Structure />
  <GenericProperties />
  <Tabs>
    <Tab>
      <Key>ffff3333-0001-4000-8000-000000000001</Key>
      <Caption>Visibility</Caption>
      <Alias>visibility</Alias>
      <Type>Tab</Type>
      <SortOrder>30</SortOrder>
    </Tab>
  </Tabs>
</ContentType>
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
# version of this suite made -- both were demonstrated against stub implementations. (The
# dossier carried an option-default marker then and no longer does; the demonstration stands
# as the reason this file states a whole document rather than a bag of values.) Field
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
            "Info",
            "Warning",
            "Critical"
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

# --- format-blindness: one component, two serializations, one signature ---------
#
# The claim the whole adapter seam exists to make: a component read through two formats is
# the same component, so the signature over it is the same string. Neither case asserts WHAT
# that string is -- a hash cannot be hand-authored, and pasting one in would assert the
# implementation against itself. `same_stdout_as` asserts the equality directly, which is the
# only form the claim has.
#
# Both cases read the SAME project tree, carrying both serializations side by side, and each
# forces its own adapter. Two separate trees would let the pair pass while the two fixtures
# described two subtly different components; one tree cannot.
#
# `not_contains: dossierVersion` is how "the signature alone" is stated: the subcommand
# prints one line, so any dossier field reaching the output means it printed the document too
# and the byte comparison above would be comparing dossiers rather than signatures.
signature_project() {  # signature_project <case-root>
  deploy_tree "$1"
  usync_tree "$1"
}

C="$CASES/signature-deploy"; mkdir -p "$C"; signature_project "$C"
expect "$C" \
  "exit: 0" \
  "args: signature alertBanner --adapter deploy" \
  "contains: sha256:" \
  "not_contains: dossierVersion"

C="$CASES/signature-usync"; mkdir -p "$C"; signature_project "$C"
expect "$C" \
  "exit: 0" \
  "args: signature alertBanner --adapter usync" \
  "contains: sha256:" \
  "not_contains: dossierVersion" \
  "same_stdout_as: signature-deploy"

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

# --- the kind, asserted where it can actually be wrong -------------------------
#
# `kind` is a single top-level field and the assertion names both values, so a substring
# match is exact here: "document" must appear and "element" must not. A golden file would
# add a second document to maintain for one field's sake.
PAGE_KIND=(
  "exit: 0"
  "args: extract articlePage"
  'contains: "alias": "articlePage"'
  'contains: "kind": "document"'
  'not_contains: "kind": "element"'
)

C="$CASES/deploy-page-type"; mkdir -p "$C"; deploy_page_type "$C"
expect "$C" "${PAGE_KIND[@]}" 'contains: "rung": "deploy"'

C="$CASES/usync-page-type";  mkdir -p "$C"; usync_page_type "$C"
expect "$C" "${PAGE_KIND[@]}" 'contains: "rung": "usync"'

# --- a read that finds nothing, and a read that finds nothing to find -----------
#
# Two halves of one line, and the line is what the whole increment turns on.
#
# The REFUSING half: a serialization folder that exists, is readable, and holds no artifact
# for the requested alias. The read cannot be completed, so it must not produce a document.
# Both formats get a case, because "the two adapters answer the same question the same way" is
# the ladder's claim and a wording that drifted between them would be invisible otherwise.
#
# The PERMITTING half, below: a component that genuinely has no properties. The artifact is
# there, every reference in it resolved, and the answer is "no fields". That is a fact about
# the component, not about the export, and refusing it would refuse real components.
#
# What separates them is whether anything was left UNRESOLVED, never how thin the result is.
# Thinness is not evidence: the thinnest possible dossier and a perfectly healthy taxonomy
# node are the same document.

MISSING_ALIAS=(
  "exit: 1"
  "args: extract alertBanner"
  # The alias asked for, so the operator can see it is the one they typed.
  "contains: alertBanner"
  # The folder searched, and that it was read rather than skipped -- one component was found
  # there, just not this one. This is the difference between "nothing to read" and "read, and
  # your component is not in it", and only the second is worth a re-export.
  "contains: 1 component"
  "contains: the export is partial"
  # What to do next, in both readings: fix the export, or point the read somewhere else.
  "contains: re-export"
  "contains: --project-root"
  # No dossier. Asserting the message alone would pass on a run that printed a document AND
  # complained about it, which is the silent-empty shape with a warning stapled on.
  'not_contains: "dossierVersion"'
)

C="$CASES/deploy-missing-alias"; mkdir -p "$C"; deploy_page_type "$C"
expect "$C" "${MISSING_ALIAS[@]}" \
  "contains: Deploy/Revision"

C="$CASES/usync-missing-alias"; mkdir -p "$C"; usync_page_type "$C"
expect "$C" "${MISSING_ALIAS[@]}" \
  "contains: uSync/v17/ContentTypes"

# The permitting half. `exit: 0` plus the golden file says the dossier was printed; the note
# says the emptiness was reported rather than left for a reader to interpret; and
# `not_contains` is the assertion that stops a later increment tightening this into a refusal
# by accident.
PROPERTYLESS=(
  "exit: 0"
  "stdout_matches: expected-dossier.json"
  'mask: "sourceSignature":'
  "contains: declares no editable properties"
  "not_contains: the export is partial"
)

propertyless_node_dossier() {  # propertyless_node_dossier <case-root> <rung>
  cat > "$1/expected-dossier.json" <<EOF
{
  "dossierVersion": 1,
  "rung": "$2",
  "alias": "topicTag",
  "name": "Topic Tag",
  "kind": "document",
  "icon": "icon-tag color-blue",
  "description": "A tag an editor picks when classifying an article.",
  "structureAvailable": true,
  "compositions": [],
  "tabs": [],
  "sourceSignature": "<computed>"
}
EOF
}

C="$CASES/deploy-propertyless"; mkdir -p "$C"; deploy_propertyless "$C"
propertyless_node_dossier "$C" deploy
expect "$C" "${PROPERTYLESS[@]}" \
  "args: extract topicTag" \
  'contains: "rung": "deploy"'

C="$CASES/usync-propertyless"; mkdir -p "$C"; usync_propertyless "$C"
propertyless_node_dossier "$C" usync
expect "$C" "${PROPERTYLESS[@]}" \
  "args: extract topicTag" \
  'contains: "rung": "usync"'

# The second shape: structure with nothing in it. The tab has to survive into the dossier --
# the backoffice shows it, so a guide that omitted it would describe a screen the editor does
# not see -- while the component still counts as having no properties.
empty_tab_dossier() {  # empty_tab_dossier <case-root> <rung>
  cat > "$1/expected-dossier.json" <<EOF
{
  "dossierVersion": 1,
  "rung": "$2",
  "alias": "pageVisibility",
  "name": "Page Visibility",
  "kind": "element",
  "icon": "icon-eye color-grey",
  "description": "A tab every page carries, filled in by whatever composes this.",
  "structureAvailable": true,
  "compositions": [],
  "tabs": [
    {
      "alias": "visibility",
      "name": "Visibility",
      "sortOrder": 30,
      "properties": [],
      "groups": []
    }
  ],
  "sourceSignature": "<computed>"
}
EOF
}

C="$CASES/deploy-empty-tab"; mkdir -p "$C"; deploy_propertyless "$C"
empty_tab_dossier "$C" deploy
expect "$C" "${PROPERTYLESS[@]}" \
  "args: extract pageVisibility"

C="$CASES/usync-empty-tab"; mkdir -p "$C"; usync_propertyless "$C"
empty_tab_dossier "$C" usync
expect "$C" "${PROPERTYLESS[@]}" \
  "args: extract pageVisibility"

# --- item 1: the note must never reach stdout, asserted where it could ----------
#
# `signature` prints one line and nothing else, because the format-blindness pair compares
# stdout byte for byte. Every existing signature case reads a component WITH properties, so
# the note branch in cmd_signature never ran under test: reordering the print and the note,
# or routing the note to stdout, would have passed the whole suite. This case is that branch.
#
# `stdout_matches` is what carries the claim -- it sees stdout alone, so a note that leaked
# there would fail even though `contains` (which sees both streams merged) would not notice.
C="$CASES/signature-propertyless"; mkdir -p "$C"; deploy_propertyless "$C"
printf 'sha256:<computed>\n' > "$C/expected-stdout.txt"
expect "$C" \
  "exit: 0" \
  "args: signature topicTag" \
  "stdout_matches: expected-stdout.txt" \
  'mask: sha256:' \
  "contains: declares no editable properties" \
  "not_contains: the export is partial"

# --- version refusal, in the two shapes the formats force ----------------------
#
# One rule -- "never read a serialization shape you have not been verified against" -- and two
# cases, because the two formats declare the version in places that force different answers.
# Implementing either shape alone encodes the wrong single rule, so both are asserted.
#
# uSync declares ONE `format` for the whole export, in `usync.config`. So the check is a
# single gate up front: an unrecognized format refuses the entire read and no component is
# touched. Refusing per file would be arbitrary -- every file in the export shares the one
# declaration.
#
# Deploy stamps `__version` on EVERY artifact, and one project holds a mix: the demo project
# carries 17.1.0 on 47 document types, 17.2.0 on 16 and 17.2.1 on 5, because artifacts only
# re-serialize when touched. So the check is per file: the unrecognized artifact is named as
# unread and the rest of the read continues. Refusing the whole read would reject the normal
# case -- there is no project whose artifacts all carry one version.

# Rewrite one artifact's `__version` in place. A project's spread is whatever its edit
# history was, so a fixture reproduces one by restamping rather than by generating a whole
# second tree per version.
restamp() {  # restamp <artifact> <version>
  local tmp="$1.restamped"
  sed 's/"__version": "[^"]*"/"__version": "'"$2"'"/' "$1" > "$tmp" && mv "$tmp" "$1"
}

# Rewrite the export's one format declaration. Same shape as the real file, which the
# extraction reference records verbatim -- `format` numbers separately from both the package
# version and the folder name, so a fixture must be able to vary it on its own.
usync_format() {  # usync_format <case-root> <format>
  printf '<uSync version="17.0.4.0" format="%s" />\n' "$2" > "$1/uSync/v17/usync.config"
}

# A document type stamped with a version this adapter has never been verified against. It is
# deliberately a component NOBODY asks for and nothing composes: the assertion is that the
# rest of the read completes, and a stale artifact the requested component depended on would
# instead have to fail loudly, which is the missing-data-type case's job.
stale_artifact() {  # stale_artifact <path> <udi> <alias> <version>
  cat > "$1" <<EOF
{
  "Name": "Legacy Promo",
  "Alias": "$3",
  "AllowedTemplates": [],
  "HistoryCleanup": {},
  "Icon": "icon-bullhorn color-yellow",
  "Thumbnail": "folder.png",
  "Description": "A component last serialized by a version of the package this adapter does not know.",
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
  "__version": "$4"
}
EOF
}

# The whole read refused, up front. `not_contains` carries the two halves that a message-only
# assertion would miss: no dossier was printed, and no component was read -- a run that
# printed the document AND complained about the format would satisfy `contains` alone.
C="$CASES/usync-format-refused"; mkdir -p "$C"; usync_tree "$C"
usync_format "$C" "9.1.0"
expect "$C" \
  "exit: 1" \
  "args: extract alertBanner" \
  "contains: usync.config" \
  "contains: 9.1.0" \
  "contains: 10.7.0" \
  'not_contains: "dossierVersion"' \
  "not_contains: alertHeading"

# Both halves, in one case, because either alone is a rule that looks implemented and is not.
#
# The skipped half: the stale artifact is named, with the version found on it, so an operator
# can re-serialize the right file.
#
# The still-read half: `stdout_matches` against the SAME golden dossier every other Deploy
# case uses. Three recognized versions are spread across this tree's artifacts -- the
# requested type, the composition it inherits from, and the data type carrying the option
# list -- so a run that refused the whole read over one stale file, or that let a version
# check drop a recognized artifact, cannot produce this document.
C="$CASES/deploy-mixed-versions"; mkdir -p "$C"; deploy_tree "$C"
REV="$C/src/Web/umbraco/Deploy/Revision"
restamp "$REV/document-type__$U_BASE.uda" "17.2.1"
restamp "$REV/data-type__$U_DROP.uda"     "17.1.0"
stale_artifact "$REV/document-type__$U_STALE.uda" "$U_STALE" "legacyPromo" "16.4.0"
expected_dossier "$C" deploy
expect "$C" \
  "exit: 0" \
  "args: extract alertBanner" \
  "stdout_matches: expected-dossier.json" \
  'mask: "sourceSignature":' \
  "contains: document-type__$U_STALE.uda" \
  "contains: 16.4.0" \
  "contains: was not read" \
  'contains: "inheritedFrom": "baseSettings"'

# The same skip, but the requested component is the one that was skipped. This is the likely
# real trigger -- an operator asks for a component whose artifact happens to be stale -- and
# it used to be the case that said least: the note explaining exactly why the lookup found
# nothing was computed, queued, and discarded when the lookup then raised. All the operator
# got was "either the alias is misspelled, or the export is partial".
#
# So the assertions are the refusal AND the note, together. Asserting the refusal alone is
# what passed before.
C="$CASES/deploy-requested-version-skipped"; mkdir -p "$C"; deploy_tree "$C"
REV="$C/src/Web/umbraco/Deploy/Revision"
restamp "$REV/document-type__$U_BANNER.uda" "16.4.0"
expect "$C" \
  "exit: 1" \
  "args: extract alertBanner" \
  "contains: was not read" \
  "contains: 16.4.0" \
  "contains: document-type__$U_BANNER.uda" \
  "contains: declares the alias" \
  'not_contains: "dossierVersion"'


# ==============================================================================
# The lowest rung: committed generated model classes, and nothing else
# ==============================================================================
#
# A project with NO serialization folders at all -- no `*.uda`, no `uSync/` -- and one
# committed `*.generated.cs` per content type. That is a real shape: ModelsBuilder in
# `SourceCodeManual` mode writes these into the repo, and a project that neither runs Deploy
# nor commits its uSync export still has them. It is also the *only* rung a project in that
# state has, so refusing to read it would mean no guides at all.
#
# The component is the SAME alertBanner every other case describes, deliberately, so the two
# documents can be read side by side: the models-rung dossier must be a strict subset -- same
# alias, same kind, same property aliases, same composition -- carrying strictly fewer facts.
# A fixture describing a different component could not state that.
#
# The shape below is not invented. It follows Umbraco.ModelsBuilder.Embedded v17.5.3 output as
# committed in two real projects (78 model files in one, 182 in the other), including the
# details a parser gets wrong:
#
#   - `[PublishedModel("<alias>")]` immediately above the class declaration is the alias. The
#     class NAME is not: the generator mangles casing (an alias of `sEOControls` becomes a
#     class `SEocontrols`), so a reader deriving the alias from the file or class name is
#     wrong on any alias whose first two letters are capitals.
#   - The base class is the kind: `PublishedElementModel` for an element type,
#     `PublishedContentModel` for a document type. A class may also derive from ANOTHER model
#     class -- 18 of one project's 164 do -- and the kind is then whatever the chain ends at.
#   - A mixin (composition) file holds BOTH an interface and a class. The interface carries
#     `// Mixin Content Type with alias "<alias>"` directly above it, and the composing class
#     names the interface in its base list.
#   - A property's own doc summary is `Name: Description` on ONE line -- 439 and 972 summary
#     blocks measured across the two projects, none of them wrapped -- so the split is on the
#     first `: ` and a component with no description has no colon at all.
#   - A property contributed by a mixin is RE-DECLARED in the composing class, delegating to
#     the mixin's static getter through its fully-qualified name. That delegation is the only
#     signal for `inheritedFrom` at this rung, and it is why the mixin's own properties
#     (`GetX(this, ...)`, unqualified) must not be read as inherited from itself.
#   - Every property is followed by a `public static ... GetX(...)` getter carrying its own
#     one-line summary. It has no `[ImplementPropertyType]`, and a parser that keys on the
#     summary rather than on that attribute reads each property twice.
#
# What this fixture cannot state, because ModelsBuilder does not emit it: a namespaced or
# generic property type (`global::...IHtmlEncodedString`, `IEnumerable<string>`) for any
# editor in the component sketched at the top of this file -- a text box, a toggle and a
# single-value dropdown all generate `string` or `bool`. Those forms are verified against the
# two real projects instead, where 15 of one project's 17 distinct property types carry a
# namespace.
# --- generated-model builders for the branches the happy-path tree cannot reach ---
#
# Four cases, chosen to cover nine untested branches rather than one each. The chain case
# carries the document kind, the multi-hop base walk and cross-hop inheritedFrom together,
# because they are the same walk seen from three angles. The two refusals cover the resolution
# machinery that the unresolved-base and unresolved-delegate refusals also run through. And the
# stale-dump case guards a SKIP_DIRS entry that is a CORRECTNESS gate, not hygiene: without it
# a duplicate-alias refusal fires on a project that is perfectly well formed.

models_header() {  # models_header <file>
  cat > "$1" <<'EOF'
//------------------------------------------------------------------------------
// <auto-generated>
//   This code was generated by a tool.
//
//    Umbraco.ModelsBuilder.Embedded v17.5.3+a9649da
//
//   Changes to this file will be lost if the code is regenerated.
// </auto-generated>
//------------------------------------------------------------------------------

using System;
using Umbraco.Cms.Core.Models.PublishedContent;
using Umbraco.Cms.Core.PublishedCache;
using Umbraco.Cms.Infrastructure.ModelsBuilder;
using Umbraco.Cms.Core;
using Umbraco.Extensions;

namespace Umbraco.Cms.Web.Common.PublishedModels
{
EOF
}

# A two-hop chain: articlePage -> SitePageBase -> PublishedContentModel. The kind has to come
# from the far end of the walk, and articlePage inherits a field declared on the middle class.
models_page_chain() {  # models_page_chain <case-root>
  local gen="$1/src/Web/Models/Generated"
  mkdir -p "$gen"

  models_header "$gen/SitePageBase.generated.cs"
  cat >> "$gen/SitePageBase.generated.cs" <<'EOF'
	/// <summary>Site Page Base</summary>
	[PublishedModel("sitePageBase")]
	public partial class SitePageBase : PublishedContentModel
	{
		public new const string ModelTypeAlias = "sitePageBase";

		///<summary>
		/// Page Title: Shown in the browser tab.
		///</summary>
		[ImplementPropertyType("pageTitle")]
		public virtual string PageTitle => this.Value<string>(_publishedValueFallback, "pageTitle");
	}
}
EOF

  models_header "$gen/ArticlePage.generated.cs"
  cat >> "$gen/ArticlePage.generated.cs" <<'EOF'
	/// <summary>Article Page</summary>
	[PublishedModel("articlePage")]
	public partial class ArticlePage : SitePageBase
	{
		public new const string ModelTypeAlias = "articlePage";

		///<summary>
		/// Article Heading: The headline.
		///</summary>
		[ImplementPropertyType("articleHeading")]
		public virtual string ArticleHeading => this.Value<string>(_publishedValueFallback, "articleHeading");
	}
}
EOF
}

# The derived class deliberately does NOT re-declare pageTitle. Measured across 182 real
# generated models: of the 18 classes deriving from another generated model, ZERO re-declare a
# property alias their base already declares -- a base class's fields are simply inherited in
# C#, so the generator has nothing to emit. A first draft of this fixture invented the
# re-declaration and the adapter correctly refused it as a duplicate alias, which is how the
# invention was caught. `inheritedFrom` therefore comes from the base walk, not from a
# delegating getter as it does for a mixin.

# A class implementing a mixin interface no model file declares. The fields that interface
# contributes cannot be attributed, so the read refuses rather than under-describing.
models_unresolved_mixin() {  # models_unresolved_mixin <case-root>
  local gen="$1/src/Web/Models/Generated"
  mkdir -p "$gen"
  models_header "$gen/AlertBanner.generated.cs"
  cat >> "$gen/AlertBanner.generated.cs" <<'EOF'
	/// <summary>Alert Banner</summary>
	[PublishedModel("alertBanner")]
	public partial class AlertBanner : PublishedElementModel, IBaseSettings
	{
		public new const string ModelTypeAlias = "alertBanner";

		///<summary>
		/// Alert Heading: The line an editor reads first.
		///</summary>
		[ImplementPropertyType("alertHeading")]
		public virtual string AlertHeading => this.Value<string>(_publishedValueFallback, "alertHeading");
	}
}
EOF
}

# Two classes claiming one alias. Resolving by walk order would answer with whichever file the
# scan reached first, which is the same ambiguity the two serialization rungs refuse.
models_duplicate_alias() {  # models_duplicate_alias <case-root>
  local gen="$1/src/Web/Models/Generated"
  mkdir -p "$gen"
  models_header "$gen/AlertBanner.generated.cs"
  cat >> "$gen/AlertBanner.generated.cs" <<'EOF'
	/// <summary>Alert Banner</summary>
	[PublishedModel("alertBanner")]
	public partial class AlertBanner : PublishedElementModel
	{
		///<summary>
		/// Alert Heading: The line an editor reads first.
		///</summary>
		[ImplementPropertyType("alertHeading")]
		public virtual string AlertHeading => this.Value<string>(_publishedValueFallback, "alertHeading");
	}
}
EOF
  models_header "$gen/AlertBannerLegacy.generated.cs"
  cat >> "$gen/AlertBannerLegacy.generated.cs" <<'EOF'
	/// <summary>Alert Banner</summary>
	[PublishedModel("alertBanner")]
	public partial class AlertBannerLegacy : PublishedElementModel
	{
	}
}
EOF
}

models_tree() {  # models_tree <case-root>
  local gen="$1/src/Web/Models/Generated"
  mkdir -p "$gen"

  # The composition. Interface first, then the class -- the order ModelsBuilder writes, and
  # the reason the mixin comment sits above the INTERFACE rather than above the class.
  cat > "$gen/BaseSettings.generated.cs" <<'EOF'
//------------------------------------------------------------------------------
// <auto-generated>
//   This code was generated by a tool.
//
//    Umbraco.ModelsBuilder.Embedded v17.5.3+a9649da
//
//   Changes to this file will be lost if the code is regenerated.
// </auto-generated>
//------------------------------------------------------------------------------

using System;
using System.Linq.Expressions;
using Umbraco.Cms.Core.Models.PublishedContent;
using Umbraco.Cms.Core.PublishedCache;
using Umbraco.Cms.Infrastructure.ModelsBuilder;
using Umbraco.Cms.Core;
using Umbraco.Extensions;

namespace Umbraco.Cms.Web.Common.PublishedModels
{
	// Mixin Content Type with alias "baseSettings"
	/// <summary>Base Settings</summary>
	public partial interface IBaseSettings : IPublishedElement
	{
		/// <summary>Meta Description</summary>
		[global::System.CodeDom.Compiler.GeneratedCodeAttribute("Umbraco.ModelsBuilder.Embedded", "17.5.3+a9649da")]
		[global::System.Diagnostics.CodeAnalysis.MaybeNull]
		string MetaDescription { get; }

		/// <summary>Meta Keywords</summary>
		[global::System.CodeDom.Compiler.GeneratedCodeAttribute("Umbraco.ModelsBuilder.Embedded", "17.5.3+a9649da")]
		[global::System.Diagnostics.CodeAnalysis.MaybeNull]
		string MetaKeywords { get; }
	}

	/// <summary>Base Settings</summary>
	[PublishedModel("baseSettings")]
	public partial class BaseSettings : PublishedElementModel, IBaseSettings
	{
		// helpers
#pragma warning disable 0109 // new is redundant
		[global::System.CodeDom.Compiler.GeneratedCodeAttribute("Umbraco.ModelsBuilder.Embedded", "17.5.3+a9649da")]
		public new const string ModelTypeAlias = "baseSettings";
		[global::System.CodeDom.Compiler.GeneratedCodeAttribute("Umbraco.ModelsBuilder.Embedded", "17.5.3+a9649da")]
		public new const PublishedItemType ModelItemType = PublishedItemType.Content;
#pragma warning restore 0109

		private IPublishedValueFallback _publishedValueFallback;

		// ctor
		public BaseSettings(IPublishedElement content, IPublishedValueFallback publishedValueFallback)
			: base(content, publishedValueFallback)
		{
			_publishedValueFallback = publishedValueFallback;
		}

		// properties

		///<summary>
		/// Meta Description: Summary used by search engines.
		///</summary>
		[global::System.CodeDom.Compiler.GeneratedCodeAttribute("Umbraco.ModelsBuilder.Embedded", "17.5.3+a9649da")]
		[global::System.Diagnostics.CodeAnalysis.MaybeNull]
		[ImplementPropertyType("metaDescription")]
		public virtual string MetaDescription => GetMetaDescription(this, _publishedValueFallback);

		/// <summary>Static getter for Meta Description</summary>
		[global::System.CodeDom.Compiler.GeneratedCodeAttribute("Umbraco.ModelsBuilder.Embedded", "17.5.3+a9649da")]
		[return: global::System.Diagnostics.CodeAnalysis.MaybeNull]
		public static string GetMetaDescription(IBaseSettings that, IPublishedValueFallback publishedValueFallback) => that.Value<string>(publishedValueFallback, "metaDescription");

		///<summary>
		/// Meta Keywords: Terms this page should be found by.
		///</summary>
		[global::System.CodeDom.Compiler.GeneratedCodeAttribute("Umbraco.ModelsBuilder.Embedded", "17.5.3+a9649da")]
		[global::System.Diagnostics.CodeAnalysis.MaybeNull]
		[ImplementPropertyType("metaKeywords")]
		public virtual string MetaKeywords => GetMetaKeywords(this, _publishedValueFallback);

		/// <summary>Static getter for Meta Keywords</summary>
		[global::System.CodeDom.Compiler.GeneratedCodeAttribute("Umbraco.ModelsBuilder.Embedded", "17.5.3+a9649da")]
		[return: global::System.Diagnostics.CodeAnalysis.MaybeNull]
		public static string GetMetaKeywords(IBaseSettings that, IPublishedValueFallback publishedValueFallback) => that.Value<string>(publishedValueFallback, "metaKeywords");
	}
}
EOF

  # The component. Three own properties, two re-declared from the mixin, and no trace
  # anywhere in the file of which tab any of them sits on.
  cat > "$gen/AlertBanner.generated.cs" <<'EOF'
//------------------------------------------------------------------------------
// <auto-generated>
//   This code was generated by a tool.
//
//    Umbraco.ModelsBuilder.Embedded v17.5.3+a9649da
//
//   Changes to this file will be lost if the code is regenerated.
// </auto-generated>
//------------------------------------------------------------------------------

using System;
using System.Linq.Expressions;
using Umbraco.Cms.Core.Models.PublishedContent;
using Umbraco.Cms.Core.PublishedCache;
using Umbraco.Cms.Infrastructure.ModelsBuilder;
using Umbraco.Cms.Core;
using Umbraco.Extensions;

namespace Umbraco.Cms.Web.Common.PublishedModels
{
	/// <summary>Alert Banner</summary>
	[PublishedModel("alertBanner")]
	public partial class AlertBanner : PublishedElementModel, IBaseSettings
	{
		// helpers
#pragma warning disable 0109 // new is redundant
		[global::System.CodeDom.Compiler.GeneratedCodeAttribute("Umbraco.ModelsBuilder.Embedded", "17.5.3+a9649da")]
		public new const string ModelTypeAlias = "alertBanner";
		[global::System.CodeDom.Compiler.GeneratedCodeAttribute("Umbraco.ModelsBuilder.Embedded", "17.5.3+a9649da")]
		public new const PublishedItemType ModelItemType = PublishedItemType.Content;
		[global::System.CodeDom.Compiler.GeneratedCodeAttribute("Umbraco.ModelsBuilder.Embedded", "17.5.3+a9649da")]
		[return: global::System.Diagnostics.CodeAnalysis.MaybeNull]
		public new static IPublishedContentType GetModelContentType(IPublishedContentTypeCache contentTypeCache)
			=> PublishedModelUtility.GetModelContentType(contentTypeCache, ModelItemType, ModelTypeAlias);
#pragma warning restore 0109

		private IPublishedValueFallback _publishedValueFallback;

		// ctor
		public AlertBanner(IPublishedElement content, IPublishedValueFallback publishedValueFallback)
			: base(content, publishedValueFallback)
		{
			_publishedValueFallback = publishedValueFallback;
		}

		// properties

		///<summary>
		/// Alert Heading: The line an editor reads first.
		///</summary>
		[global::System.CodeDom.Compiler.GeneratedCodeAttribute("Umbraco.ModelsBuilder.Embedded", "17.5.3+a9649da")]
		[global::System.Diagnostics.CodeAnalysis.MaybeNull]
		[ImplementPropertyType("alertHeading")]
		public virtual string AlertHeading => this.Value<string>(_publishedValueFallback, "alertHeading");

		///<summary>
		/// Alert Dismissible: Let a visitor close the banner for the rest of the session.
		///</summary>
		[global::System.CodeDom.Compiler.GeneratedCodeAttribute("Umbraco.ModelsBuilder.Embedded", "17.5.3+a9649da")]
		[ImplementPropertyType("alertDismissible")]
		public virtual bool AlertDismissible => this.Value<bool>(_publishedValueFallback, "alertDismissible");

		///<summary>
		/// Alert Severity: How loudly the banner presents itself.
		///</summary>
		[global::System.CodeDom.Compiler.GeneratedCodeAttribute("Umbraco.ModelsBuilder.Embedded", "17.5.3+a9649da")]
		[global::System.Diagnostics.CodeAnalysis.MaybeNull]
		[ImplementPropertyType("alertSeverity")]
		public virtual string AlertSeverity => this.Value<string>(_publishedValueFallback, "alertSeverity");

		///<summary>
		/// Meta Description: Summary used by search engines.
		///</summary>
		[global::System.CodeDom.Compiler.GeneratedCodeAttribute("Umbraco.ModelsBuilder.Embedded", "17.5.3+a9649da")]
		[global::System.Diagnostics.CodeAnalysis.MaybeNull]
		[ImplementPropertyType("metaDescription")]
		public virtual string MetaDescription => global::Umbraco.Cms.Web.Common.PublishedModels.BaseSettings.GetMetaDescription(this, _publishedValueFallback);

		///<summary>
		/// Meta Keywords: Terms this page should be found by.
		///</summary>
		[global::System.CodeDom.Compiler.GeneratedCodeAttribute("Umbraco.ModelsBuilder.Embedded", "17.5.3+a9649da")]
		[global::System.Diagnostics.CodeAnalysis.MaybeNull]
		[ImplementPropertyType("metaKeywords")]
		public virtual string MetaKeywords => global::Umbraco.Cms.Web.Common.PublishedModels.BaseSettings.GetMetaKeywords(this, _publishedValueFallback);
	}
}
EOF
}

# The dossier this rung owes -- deliberately thin, and saying so.
#
# Every field the two higher rungs fill and this one cannot is named in `structureGaps`,
# because a reader has to be able to tell a missing option list from an empty one. Absence
# alone cannot say that: `"options": []` is the same three characters whether the component
# offers no options or the source could not report them. `structureAvailable: false` says
# something is missing; the list says WHAT, per field, in the dossier itself rather than in a
# comment somewhere the consumer will not read.
#
# The five properties are in ALIAS order, not declaration order. Every sortOrder is 0 here, so
# the alias is the only tiebreak left -- which means the order is deterministic and states
# nothing about the backoffice, exactly as the gap list says.
models_dossier() {  # models_dossier <case-root>
  cat > "$1/expected-dossier.json" <<'EOF'
{
  "dossierVersion": 1,
  "rung": "models",
  "alias": "alertBanner",
  "name": "Alert Banner",
  "kind": "element",
  "icon": "",
  "description": "",
  "structureAvailable": false,
  "structureGaps": [
    "description (component): not recorded. A generated model's class summary carries the display name and nothing else.",
    "description (property): recorded, but as ModelsBuilder escaped it: line breaks collapsed to spaces, and angle brackets rewritten as braces.",
    "editor: the generated C# property type, not the data type's editor alias.",
    "icon: not recorded. The backoffice icon is not generated into a model.",
    "mandatory: not recorded. Every property reads false; required flags are not generated.",
    "options: not recorded. Every option list reads empty; an option list lives on the data type, which this rung does not read.",
    "sortOrder: not recorded. Every property reads 0, and the unnamed bucket is in alias order.",
    "tabs: not recorded. A generated model carries no tab or group structure, so every property is in the one unnamed bucket."
  ],
  "compositions": [
    "baseSettings"
  ],
  "tabs": [
    {
      "alias": "",
      "name": "",
      "sortOrder": 0,
      "properties": [
        {
          "alias": "alertDismissible",
          "name": "Alert Dismissible",
          "description": "Let a visitor close the banner for the rest of the session.",
          "editor": "bool",
          "mandatory": false,
          "sortOrder": 0,
          "options": [],
          "inheritedFrom": null
        },
        {
          "alias": "alertHeading",
          "name": "Alert Heading",
          "description": "The line an editor reads first.",
          "editor": "string",
          "mandatory": false,
          "sortOrder": 0,
          "options": [],
          "inheritedFrom": null
        },
        {
          "alias": "alertSeverity",
          "name": "Alert Severity",
          "description": "How loudly the banner presents itself.",
          "editor": "string",
          "mandatory": false,
          "sortOrder": 0,
          "options": [],
          "inheritedFrom": null
        },
        {
          "alias": "metaDescription",
          "name": "Meta Description",
          "description": "Summary used by search engines.",
          "editor": "string",
          "mandatory": false,
          "sortOrder": 0,
          "options": [],
          "inheritedFrom": "baseSettings"
        },
        {
          "alias": "metaKeywords",
          "name": "Meta Keywords",
          "description": "Terms this page should be found by.",
          "editor": "string",
          "mandatory": false,
          "sortOrder": 0,
          "options": [],
          "inheritedFrom": "baseSettings"
        }
      ],
      "groups": []
    }
  ],
  "sourceSignature": "<computed>"
}
EOF
}

# Three assertions here carry more than they look.
#
# The rung is asserted negatively as well as positively: a project with neither serialization
# folder must not be read by an adapter that then labels the dossier with a format it did not
# find. Every positive assertion in this case would pass that.
#
# The thinness note and the gap statement must not BOTH fire. They are different claims --
# the note is about a component that has no fields, the gap list is about structure the source
# cannot report -- and this component has five fields, so only the gap list applies. Without
# `not_contains: declares no editable properties`, an implementation that flattened the
# properties somewhere `count_properties` cannot see them would print a note contradicting the
# document above it.
#
# And a partial read is still a refusal at this rung: the composition has to resolve, so
# `not_contains: the export is partial` says this one did.
C="$CASES/models-only-rung"; mkdir -p "$C"; models_tree "$C"; models_dossier "$C"
expect "$C" \
  "exit: 0" \
  "args: extract alertBanner" \
  "stdout_matches: expected-dossier.json" \
  'mask: "sourceSignature":' \
  'contains: "rung": "models"' \
  'contains: "structureAvailable": false' \
  'not_contains: "rung": "deploy"' \
  'not_contains: "rung": "usync"' \
  "not_contains: declares no editable properties" \
  "not_contains: the export is partial"

# `signature` at the lowest rung, where the canonical subset it hashes is a different SHAPE
# rather than merely thinner -- `structureGaps` is a field the other two rungs do not emit at
# all. So the one thing worth asserting here is what the subcommand's contract has always
# been: one line on stdout, whatever the rung. A signature that could not be taken over a
# models-rung dossier would leave the audit unable to say anything about a project that has
# only this rung, which is the project the rung exists for.
C="$CASES/signature-models"; mkdir -p "$C"; models_tree "$C"
printf 'sha256:<computed>\n' > "$C/expected-stdout.txt"
expect "$C" \
  "exit: 0" \
  "args: signature alertBanner" \
  "stdout_matches: expected-stdout.txt" \
  'mask: sha256:' \
  'not_contains: "dossierVersion"' \
  "not_contains: structureGaps"

# --- the models rung's untested branches ----------------------------------------

# Two hops of base chain, a document kind at the far end, and a field inherited across the
# middle hop. Every other models fixture is a single-hop element type, so the walk itself --
# which the module names among the things a parser gets wrong -- ran nowhere under test.
C="$CASES/models-page-chain"; mkdir -p "$C"; models_page_chain "$C"
expect "$C" \
  "exit: 0" \
  "args: extract articlePage" \
  'contains: "rung": "models"' \
  'contains: "kind": "document"' \
  'not_contains: "kind": "element"' \
  'contains: "alias": "articleHeading"' \
  'contains: "alias": "pageTitle"' \
  'contains: "inheritedFrom": "sitePageBase"' \
  'contains: "compositions"'

# A mixin interface nothing declares. The fields it contributes cannot be attributed, so this
# refuses -- the same rule the two higher rungs apply to a dangling composition.
C="$CASES/models-unresolved-mixin"; mkdir -p "$C"; models_unresolved_mixin "$C"
expect "$C" \
  "exit: 1" \
  "args: extract alertBanner" \
  "contains: IBaseSettings" \
  "contains: partial" \
  'not_contains: "dossierVersion"'

# One alias, two classes. Answering by walk order is the ambiguity both serialization rungs
# already refuse; this rung has to refuse it too or the three disagree.
C="$CASES/models-duplicate-alias"; mkdir -p "$C"; models_duplicate_alias "$C"
expect "$C" \
  "exit: 1" \
  "args: extract alertBanner" \
  "contains: alertBanner" \
  "contains: AlertBannerLegacy" \
  'not_contains: "dossierVersion"'

# The stale in-memory dump a real project carries beside its models: a full duplicate copy of
# every class, from an older generator. SKIP_DIRS excluding it is a CORRECTNESS gate -- without
# it the duplicate-alias refusal above fires on a healthy project and the rung reads nothing at
# all. Nothing asserted that until this case.
C="$CASES/models-stale-dump"; mkdir -p "$C"; models_tree "$C"
STALE="$C/src/Web/umbraco/Data/TEMP/InMemoryAuto"; mkdir -p "$STALE"
cat "$C/src/Web/Models/Generated/AlertBanner.generated.cs" \
    "$C/src/Web/Models/Generated/BaseSettings.generated.cs" > "$STALE/models.generated.cs"
models_dossier "$C"
expect "$C" \
  "exit: 0" \
  "args: extract alertBanner" \
  "stdout_matches: expected-dossier.json" \
  'mask: "sourceSignature":' \
  'contains: "rung": "models"' \
  "not_contains: declare the same"

# ==============================================================================
# The inventory determiner — the step where the count stops being the file count
# ==============================================================================
#
# Every case above reads ONE named component. These read the whole project and decide which
# of its components an editor can actually place, which is a different question with a
# different failure mode: not a wrong dossier but a right-looking count that is two to three
# times too big, feeding an audit that reports a hundred components nobody wanted documented.
#
# So the fixture project is built to make the two candidate rules disagree by construction.
# Six element types carry the flag; three are offered as content blocks. A determiner reading
# `IsElementType` scores 6, a determiner reading the palette scores 3, and no assertion on a
# single component could tell them apart.
#
# The palette schema below is measured, not guessed. Both formats carry the same JSON payload
# in a block-editor data type — Deploy in `Configuration`, uSync in `<Config>` — and inside a
# `blocks[]` entry the role of each element type is stated by its own KEY:
#
#     contentElementTypeKey    the block an editor places  -> a documentable unit
#     settingsElementTypeKey   the settings half           -> excluded
#
# Verified 2026-08-27 on both source projects: the demo project's 7 palettes hold 58
# `contentElementTypeKey` and 45 `settingsElementTypeKey` entries across `Umbraco.BlockList`
# and `Umbraco.BlockGrid`; the client project's 26 hold 62 and 38. No entry in either project
# names an element type this rule could not resolve. **The keys are dashed GUIDs in both
# formats**, while a Deploy `Udi` strips the dashes — so a fixture that wrote them undashed
# would let a broken normalizer pass.
#
# Three shapes in the cast exist because each one breaks a rule that looks correct:
#
#   mediaRow      is a content block in BOTH palettes, so a determiner that counts entries
#                 rather than distinct components scores 4 instead of 3. (Entry counts and
#                 component counts differ on both real projects for exactly this reason.)
#   heroSlide     is the SETTINGS half of one palette entry and a CONTENT block in the other.
#                 "Settings model" is therefore a set difference, never a per-type flag, and a
#                 determiner that excludes anything named as settings loses a real block.
#   sharedFooter  and spacingProperties appear in no palette at all, and each is composed by a
#   spacingProperties  block that does. They are schema a guide READS and never schema a guide
#                 documents, which is the spec's composition rule.

INV_PALETTE_A='[BlockList] Page Body'
INV_PALETTE_B='[BlockGrid] Hero Slides'

# --- Deploy: six element types, two palettes -----------------------------------

# One property each, which is the minimum that makes the component real: the inventory
# extracts every documentable unit through the shared catalog, so each one has to resolve.
inv_deploy_element() {  # inv_deploy_element <rev> <udi> <alias> <name> <prop-alias> <prop-name> [composition-udi]
  local comp="" key="${2:0:8}"
  if [[ -n "${7:-}" ]]; then
    comp="
    \"umb://document-type/$7\"
  "
  fi
  cat > "$1/document-type__$2.uda" <<EOF
{
  "Name": "$4",
  "Alias": "$3",
  "AllowedTemplates": [],
  "HistoryCleanup": {},
  "Icon": "icon-brick color-blue",
  "Thumbnail": "folder.png",
  "Permissions": {
    "IsElementType": true,
    "AllowedChildContentTypes": []
  },
  "CompositionContentTypes": [$comp],
  "PropertyGroups": [
    {
      "Key": "$key-0001-4000-8000-000000000001",
      "Name": "Content",
      "SortOrder": 10,
      "Type": 1,
      "Alias": "content",
      "PropertyTypes": [
        {
          "Key": "$key-0101-4000-8000-000000000101",
          "Alias": "$5",
          "DataType": "umb://data-type/$U_TEXT",
          "ValueType": "System.String",
          "Description": "",
          "Name": "$6",
          "SortOrder": 10
        }
      ]
    }
  ],
  "PropertyTypes": [],
  "Udi": "umb://document-type/$2",
  "Dependencies": [
    {
      "Udi": "umb://data-type/$U_TEXT",
      "Ordering": true
    }
  ],
  "__type": "$DEPLOY_ARTIFACT_TYPE",
  "__version": "$DEPLOY_VERSION"
}
EOF
}

# A block-editor data type, written directly rather than through `deploy_data_type`, because a
# real palette artifact carries `"DatabaseType": null` and a multi-line `blocks[]` payload.
inv_deploy_palette() {  # inv_deploy_palette <rev> <udi> <name> <editor> <ui> <blocks-json>
  cat > "$1/data-type__$2.uda" <<EOF
{
  "Name": "$3",
  "EditorAlias": "$4",
  "EditorUiAlias": "$5",
  "DatabaseType": null,
  "Configuration": {
    "blocks": $6,
    "useLiveEditing": false
  },
  "Udi": "umb://data-type/$2",
  "Dependencies": [],
  "__type": "$DEPLOY_DATATYPE_TYPE",
  "__version": "$DEPLOY_VERSION"
}
EOF
}

inv_deploy_tree() {  # inv_deploy_tree <case-root>
  local rev="$1/src/Web/umbraco/Deploy/Revision"
  mkdir -p "$rev"

  inv_deploy_element "$rev" "$U_NOTICE" noticeBar "Notice Bar" \
    noticeHeading "Notice Heading" "$U_FOOTER"
  inv_deploy_element "$rev" "$U_MEDIA" mediaRow "Media Row" \
    mediaCaption "Media Caption" "$U_SPACING"
  inv_deploy_element "$rev" "$U_SLIDE" heroSlide "Hero Slide" \
    slideHeading "Slide Heading"
  inv_deploy_element "$rev" "$U_MSET" mediaRowSettings "Media Row Settings" \
    settingsWidth "Settings Width"
  inv_deploy_element "$rev" "$U_FOOTER" sharedFooter "Shared Footer" \
    footerNote "Footer Note"
  inv_deploy_element "$rev" "$U_SPACING" spacingProperties "Spacing Properties" \
    spacingTop "Spacing Top"

  deploy_data_type "$rev" "$U_TEXT" "Textstring" "Umbraco.TextBox" \
    "Umb.PropertyEditorUi.TextBox" "Nvarchar" '{}'

  inv_deploy_palette "$rev" "$U_PBODY" "$INV_PALETTE_A" \
    "Umbraco.BlockList" "Umb.PropertyEditorUi.BlockList" "[
      {
        \"contentElementTypeKey\": \"$G_NOTICE\"
      },
      {
        \"contentElementTypeKey\": \"$G_MEDIA\",
        \"settingsElementTypeKey\": \"$G_SLIDE\"
      }
    ]"

  inv_deploy_palette "$rev" "$U_PHERO" "$INV_PALETTE_B" \
    "Umbraco.BlockGrid" "Umb.PropertyEditorUi.BlockGrid" "[
      {
        \"contentElementTypeKey\": \"$G_SLIDE\",
        \"settingsElementTypeKey\": \"$G_MSET\"
      },
      {
        \"contentElementTypeKey\": \"$G_MEDIA\"
      }
    ]"
}

# --- uSync: the same six element types and the same two palettes ---------------

inv_usync_element() {  # inv_usync_element <root> <key> <alias> <name> <prop-alias> <prop-name> [comp-key] [comp-alias]
  local comp="<Compositions />"
  if [[ -n "${7:-}" ]]; then
    comp="<Compositions>
      <Composition Key=\"$7\">${8:-}</Composition>
    </Compositions>"
  fi
  cat > "$1/ContentTypes/$(printf '%s' "$3" | tr '[:upper:]' '[:lower:]').config" <<EOF
<?xml version="1.0" encoding="utf-8"?>
<ContentType Key="$2" Alias="$3" Level="1">
  <Info>
    <Name>$4</Name>
    <Icon>icon-brick color-blue</Icon>
    <Thumbnail>folder.png</Thumbnail>
    <Description></Description>
    <AllowAtRoot>False</AllowAtRoot>
    <IsListView>False</IsListView>
    <Variations>Nothing</Variations>
    <IsElement>true</IsElement>
    $comp
    <DefaultTemplate></DefaultTemplate>
    <AllowedTemplates />
  </Info>
  <Structure />
  <GenericProperties>
    <GenericProperty>
      <Key>${2:0:8}-0101-4000-8000-000000000101</Key>
      <Name>$6</Name>
      <Alias>$5</Alias>
      <Definition>$G_TEXT</Definition>
      <Type>Umbraco.TextBox</Type>
      <Mandatory>false</Mandatory>
      <Validation></Validation>
      <Description></Description>
      <SortOrder>10</SortOrder>
      <Tab Alias="content">Content</Tab>
      <Variations>Nothing</Variations>
    </GenericProperty>
  </GenericProperties>
  <Tabs>
    <Tab>
      <Key>${2:0:8}-0001-4000-8000-000000000001</Key>
      <Caption>Content</Caption>
      <Alias>content</Alias>
      <Type>Tab</Type>
      <SortOrder>10</SortOrder>
    </Tab>
  </Tabs>
</ContentType>
EOF
}

# The <DataType> shape is the one measured on a real export: Key/Alias/Level on the root,
# Name/EditorAlias/EditorUIAlias (capital UI) under <Info>, and no <DatabaseType>.
inv_usync_palette() {  # inv_usync_palette <root> <key> <file> <name> <editor> <ui> <blocks-json>
  cat > "$1/DataTypes/$3.config" <<EOF
<?xml version="1.0" encoding="utf-8"?>
<DataType Key="$2" Alias="$4" Level="2">
  <Info>
    <Name>$4</Name>
    <EditorAlias>$5</EditorAlias>
    <EditorUIAlias>$6</EditorUIAlias>
  </Info>
  <Config><![CDATA[{
  "blocks": $7,
  "useLiveEditing": false
}]]></Config>
</DataType>
EOF
}

inv_usync_tree() {  # inv_usync_tree <case-root>
  local root="$1/uSync/v17"
  mkdir -p "$root/ContentTypes" "$root/DataTypes"
  cat > "$root/usync.config" <<'EOF'
<uSync version="17.0.4.0" format="10.7.0" />
EOF

  inv_usync_element "$root" "$G_NOTICE" noticeBar "Notice Bar" \
    noticeHeading "Notice Heading" "$G_FOOTER" sharedFooter
  inv_usync_element "$root" "$G_MEDIA" mediaRow "Media Row" \
    mediaCaption "Media Caption" "$G_SPACING" spacingProperties
  inv_usync_element "$root" "$G_SLIDE" heroSlide "Hero Slide" \
    slideHeading "Slide Heading"
  inv_usync_element "$root" "$G_MSET" mediaRowSettings "Media Row Settings" \
    settingsWidth "Settings Width"
  inv_usync_element "$root" "$G_FOOTER" sharedFooter "Shared Footer" \
    footerNote "Footer Note"
  inv_usync_element "$root" "$G_SPACING" spacingProperties "Spacing Properties" \
    spacingTop "Spacing Top"

  inv_usync_palette "$root" "$G_PBODY" BlockListPageBody "$INV_PALETTE_A" \
    "Umbraco.BlockList" "Umb.PropertyEditorUi.BlockList" "[
    {
      \"contentElementTypeKey\": \"$G_NOTICE\"
    },
    {
      \"contentElementTypeKey\": \"$G_MEDIA\",
      \"settingsElementTypeKey\": \"$G_SLIDE\"
    }
  ]"

  inv_usync_palette "$root" "$G_PHERO" BlockGridHeroSlides "$INV_PALETTE_B" \
    "Umbraco.BlockGrid" "Umb.PropertyEditorUi.BlockGrid" "[
    {
      \"contentElementTypeKey\": \"$G_SLIDE\",
      \"settingsElementTypeKey\": \"$G_MSET\"
    },
    {
      \"contentElementTypeKey\": \"$G_MEDIA\"
    }
  ]"
}

# --- the expected inventory — hand-authored, and the determiner's specification ---
#
# Written from the cast above BY HAND, before any inventory code existed to capture output
# from. The direction is the point: a captured file asserts that the code still does what it
# did, an authored one asserts that the code does what was asked. The number 3 in
# `"components"` is the whole reason this step exists, and it was decided here.
#
# The rung is the only difference between the two formats' expectations, which is the
# inventory's half of the format-blindness claim: the same project read two ways yields the
# same three components, the same settings model, and the same two compositions.
#
# `signature` is masked in the comparison. It is a hash the subject computes, so it cannot be
# hand-authored, and pasting one in would assert the implementation against itself.
expected_inventory() {  # expected_inventory <case-root> <rung>
  cat > "$1/expected-inventory.json" <<EOF
{
  "inventoryVersion": 1,
  "rung": "$2",
  "contentTypesRead": 6,
  "elementFlagged": 6,
  "documentTypesRead": 0,
  "palettesRead": 2,
  "rule": {
    "components": "A content type named as a palette entry's content block, in one of the project's block-editor data types. Read from the palette, never from the element-type flag.",
    "settingsModels": "An element type named only as a palette entry's settings model and never as a content block. The settings half of a block already counted, not a block of its own.",
    "unpalettedElementTypes": "An element type no palette offers. Read into an owning component's property table as a composition, never documented on its own.",
    "unresolvedPaletteEntries": "A palette offers a content type this export does not hold, so its name and its fields cannot be read and it is counted here rather than among the components. An element type is a database row, never a class, so a package that creates one at boot can legitimately leave it out: the export may ignore that package's schema deliberately, the environment may not be a schema source at all, or the type may exist only where nobody booted locally. Re-export from an environment that holds it to document these.",
    "pageTypesProposed": "PROPOSED, not decided. No flag separates a page type from a folder, a container, or an abstract base, so a document type is proposed when it carries a template or matches the project's own page-naming convention. Tree reachability is read as evidence and is not a gate, because a folder is reachable by definition."
  },
  "namingConvention": {
    "suffix": null,
    "templated": 0,
    "matched": 0,
    "why": "not derived. 0 document types carry a template, and at least 2 are needed to measure a shared suffix."
  },
  "palettes": [
    {
      "name": "$INV_PALETTE_B",
      "editor": "Umbraco.BlockGrid",
      "contentBlocks": 2,
      "settingsModels": 1
    },
    {
      "name": "$INV_PALETTE_A",
      "editor": "Umbraco.BlockList",
      "contentBlocks": 2,
      "settingsModels": 1
    }
  ],
  "components": [
    {
      "alias": "heroSlide",
      "name": "Hero Slide",
      "kind": "element",
      "palettes": [
        "$INV_PALETTE_B"
      ],
      "signature": "sha256:<computed>"
    },
    {
      "alias": "mediaRow",
      "name": "Media Row",
      "kind": "element",
      "palettes": [
        "$INV_PALETTE_B",
        "$INV_PALETTE_A"
      ],
      "signature": "sha256:<computed>"
    },
    {
      "alias": "noticeBar",
      "name": "Notice Bar",
      "kind": "element",
      "palettes": [
        "$INV_PALETTE_A"
      ],
      "signature": "sha256:<computed>"
    }
  ],
  "settingsModels": [
    {
      "alias": "mediaRowSettings",
      "name": "Media Row Settings"
    }
  ],
  "unpalettedElementTypes": [
    {
      "alias": "sharedFooter",
      "name": "Shared Footer"
    },
    {
      "alias": "spacingProperties",
      "name": "Spacing Properties"
    }
  ],
  "unresolvedPaletteEntries": 0,
  "pageTypesProposed": [],
  "notProposed": []
}
EOF
}

# --- the two palette cases ------------------------------------------------------
#
# One project tree carrying BOTH serializations, each case forcing its own adapter — the shape
# the signature pair already uses. Two separate trees would let the pair pass while the two
# fixtures described two subtly different projects; one tree cannot.
#
# `--json` because the claim is which alias lands in which list, and `contains` cannot state
# that: "mediaRowSettings" contains "mediaRow", and every excluded alias is NAMED in the human
# report by design. Only a whole-document comparison can say that mediaRowSettings sits under
# `settingsModels` and not under `components`.
inv_palette_project() {  # inv_palette_project <case-root>
  inv_deploy_tree "$1"
  inv_usync_tree "$1"
}

INV_PALETTE_EXPECT=(
  "exit: 0"
  "stdout_matches: expected-inventory.json"
  'mask: "signature":'
)

C="$CASES/inventory-palette"; mkdir -p "$C"
inv_palette_project "$C"; expected_inventory "$C" deploy
expect "$C" "${INV_PALETTE_EXPECT[@]}" \
  "args: inventory --json --adapter deploy"

C="$CASES/inventory-palette-usync"; mkdir -p "$C"
inv_palette_project "$C"; expected_inventory "$C" usync
expect "$C" "${INV_PALETTE_EXPECT[@]}" \
  "args: inventory --json --adapter usync"

# --- one of everything, because "1 content types read" reads as a broken tool -----
#
# A project with exactly one content type. Every other inventory fixture has several, so every
# count in the report header was plural and the singular branch printed "1 content types read:
# 1 carry the element-type flag, 1 do not" -- three disagreements in one line, in a report
# whose entire job is to be believed. The naming-convention line a few lines below already
# inflected correctly, which is what made the header's silence about it a gap rather than a
# decision.
C="$CASES/inventory-singular"; mkdir -p "$C"; deploy_page_type "$C"
expect "$C" \
  "exit: 0" \
  "args: inventory --adapter deploy" \
  "contains: 1 content type read:" \
  "contains: 1 does not." \
  "not_contains: 1 content types read" \
  "not_contains: 1 do not."

# --- a palette offering something this export does not hold ---------------------
#
# Counted in its own category, exit 0 -- NOT refused, and that was a deliberate reversal. The
# first version raised, on the reasoning that a block nobody can read is a component missing
# from the inventory with nothing to say so. But an element type is a database row rather than
# a class, so a package that creates one at boot can legitimately be absent from a project's
# own export: the export may ignore that package's schema on purpose, the environment may not
# be a schema source at all, or the type may exist only where nobody booted locally. Refusing
# would take the whole inventory down over any of those, and dropping it silently would
# under-count the one thing this command exists to count.
#
# Verified against both real projects before deciding: every palette key resolved in each, so
# this path is a guard rather than a routine one -- which is exactly why it needs a fixture.
C="$CASES/inventory-unresolved-entry"; mkdir -p "$C"
inv_deploy_tree "$C"
REV="$C/src/Web/umbraco/Deploy/Revision"
inv_deploy_palette "$REV" "eeee7777eeee7777eeee777777777777" "Ghost Palette" \
  "Umbraco.BlockList" "Umb.PropertyEditorUi.BlockList" '[
      {
        "contentElementTypeKey": "99999999-9999-9999-9999-999999999999"
      }
    ]'
expect "$C" \
  "exit: 0" \
  "args: inventory --adapter deploy" \
  "contains: Offered by a palette, absent from this export: 1" \
  "contains: is a database row, never a class" \
  "contains: Re-export from an environment that holds it" \
  "not_contains: unresolved"

# --- a data type whose payload cannot be parsed ---------------------------------
#
# This one DOES refuse, and the contrast with the case above is the point: a file that is
# present and unreadable is a different fact from a reference to something absent. The first is
# a broken export and nothing downstream can be trusted; the second is a normal consequence of
# how packages create schema. Same rule as `usync-format-refused` -- a file that exists and
# cannot be understood stops the read.
C="$CASES/inventory-unreadable-palette"; mkdir -p "$C"
inv_usync_tree "$C"
BAD="$C/uSync/v17/DataTypes/BrokenPalette.config"
cat > "$BAD" <<'EOF'
<?xml version="1.0" encoding="utf-8"?>
<DataType Key="eeee8888-eeee-8888-eeee-888888888888" Alias="Broken Palette" Level="1">
  <Info>
    <Name>Broken Palette</Name>
    <EditorAlias>Umbraco.BlockList</EditorAlias>
    <EditorUIAlias>Umb.PropertyEditorUi.BlockList</EditorUIAlias>
  </Info>
  <Config><![CDATA[{ "blocks": [ {"contentElementTypeKey": ]}]]></Config>
</DataType>
EOF
expect "$C" \
  "exit: 1" \
  "args: inventory --adapter usync" \
  "contains: not readable JSON" \
  "contains: BrokenPalette.config" \
  'not_contains: "inventoryVersion"'

# --- the zero that would be a lie if it were silent ----------------------------
#
# A project carrying element types and NO block-editor data type. The palette rule gives 0
# components, which is the correct answer for a project whose blocks are all compositions and
# the WRONG answer — indistinguishably — for a project whose block-editor data types were left
# out of the export. Reading it as "this project has no blocks" is the silent-empty failure the
# whole ladder exists to refuse, so the read says which of the two it cannot tell apart.
#
# A note and exit 0, not a refusal: refusing would refuse a true answer. The fixture reuses the
# dossier tree, whose two element types are exactly this shape.
C="$CASES/inventory-no-palette"; mkdir -p "$C"; deploy_tree "$C"
expect "$C" \
  "exit: 0" \
  "args: inventory --adapter deploy" \
  "contains: no block-editor data type in this project declares a blocks[] palette" \
  "contains: not as 'this project has none'" \
  "contains: Components an editor can place: 0" \
  "contains: Excluded, offered by no palette: 2"

# ==============================================================================
# Page types — the judgment that must be proposed rather than decided
# ==============================================================================
#
# Three document types no structural flag tells apart, which is the spec's claim measured on
# real projects: on the client project only 9 of 49 non-element types carried a template while
# 21 were recognizably pages, and 45 of the 49 were reachable in the content tree because a
# folder is reachable by definition. Neither signal decides alone.
#
#   articlePage   carries a template, and topicFolder allows it as a child  -> PROPOSED
#   topicFolder   no template, allowed at root, so reachable               -> a folder
#   pageBase      no template, reachable from nowhere, composed by the page -> an abstract base
#
# The report is asserted whole, rather than by substring, for the same reason the palette cases
# use `--json`: every one of the three aliases appears in the output, so a substring assertion
# cannot say WHICH section each one landed in — and that is the entire behavior.
#
# Deploy and uSync disagree on the root flag exactly as they disagree on the kind flag: Deploy
# writes `Permissions.AllowedAtRoot` only when true (1 of the demo project's 68 artifacts),
# uSync always writes `<AllowAtRoot>`. Both cases exist because a reader that assumes symmetry
# passes one and fails the other.

inv_deploy_page_tree() {  # inv_deploy_page_tree <case-root>
  local rev="$1/src/Web/umbraco/Deploy/Revision"
  mkdir -p "$rev"

  cat > "$rev/document-type__$U_PAGE.uda" <<EOF
{
  "Name": "Article Page",
  "Alias": "articlePage",
  "AllowedTemplates": [
    "umb://template/$U_PAGE"
  ],
  "DefaultTemplate": "umb://template/$U_PAGE",
  "HistoryCleanup": {},
  "Icon": "icon-article color-blue",
  "Thumbnail": "folder.png",
  "Permissions": {
    "AllowedChildContentTypes": []
  },
  "CompositionContentTypes": [
    "umb://document-type/$U_PBASE"
  ],
  "PropertyGroups": [
    {
      "Key": "eeee1111-0001-4000-8000-000000000001",
      "Name": "Content",
      "SortOrder": 10,
      "Type": 1,
      "Alias": "content",
      "PropertyTypes": [
        {
          "Key": "eeee1111-0101-4000-8000-000000000101",
          "Alias": "articleHeading",
          "DataType": "umb://data-type/$U_TEXT",
          "ValueType": "System.String",
          "Mandatory": true,
          "Description": "",
          "Name": "Article Heading",
          "SortOrder": 10
        }
      ]
    }
  ],
  "PropertyTypes": [],
  "Udi": "umb://document-type/$U_PAGE",
  "Dependencies": [],
  "__type": "$DEPLOY_ARTIFACT_TYPE",
  "__version": "$DEPLOY_VERSION"
}
EOF

  # No template, no properties, and it is the only artifact carrying `AllowedAtRoot` — which
  # Deploy emits only when true, so a reader has to treat its absence as the answer.
  cat > "$rev/document-type__$U_TOPIC.uda" <<EOF
{
  "Name": "Topic Folder",
  "Alias": "topicFolder",
  "AllowedTemplates": [],
  "HistoryCleanup": {},
  "Icon": "icon-folder color-black",
  "Thumbnail": "folder.png",
  "Permissions": {
    "AllowedAtRoot": true,
    "AllowedChildContentTypes": [
      "umb://document-type/$U_PAGE"
    ]
  },
  "CompositionContentTypes": [],
  "PropertyGroups": [],
  "PropertyTypes": [],
  "Udi": "umb://document-type/$U_TOPIC",
  "Dependencies": [],
  "__type": "$DEPLOY_ARTIFACT_TYPE",
  "__version": "$DEPLOY_VERSION"
}
EOF

  cat > "$rev/document-type__$U_PBASE.uda" <<EOF
{
  "Name": "Page Base",
  "Alias": "pageBase",
  "AllowedTemplates": [],
  "HistoryCleanup": {},
  "Icon": "icon-settings color-black",
  "Thumbnail": "folder.png",
  "Permissions": {
    "AllowedChildContentTypes": []
  },
  "CompositionContentTypes": [],
  "PropertyGroups": [
    {
      "Key": "b22b2222-0001-4000-8000-000000000001",
      "Name": "SEO",
      "SortOrder": 100,
      "Type": 1,
      "Alias": "seo",
      "PropertyTypes": [
        {
          "Key": "b22b2222-0101-4000-8000-000000000101",
          "Alias": "metaDescription",
          "DataType": "umb://data-type/$U_TEXT",
          "ValueType": "System.String",
          "Description": "",
          "Name": "Meta Description",
          "SortOrder": 10
        }
      ]
    }
  ],
  "PropertyTypes": [],
  "Udi": "umb://document-type/$U_PBASE",
  "Dependencies": [],
  "__type": "$DEPLOY_ARTIFACT_TYPE",
  "__version": "$DEPLOY_VERSION"
}
EOF

  deploy_data_type "$rev" "$U_TEXT" "Textstring" "Umbraco.TextBox" \
    "Umb.PropertyEditorUi.TextBox" "Nvarchar" '{}'
}

inv_usync_page_tree() {  # inv_usync_page_tree <case-root>
  local root="$1/uSync/v17"
  mkdir -p "$root/ContentTypes"
  cat > "$root/usync.config" <<'EOF'
<uSync version="17.0.4.0" format="10.7.0" />
EOF

  cat > "$root/ContentTypes/articlepage.config" <<EOF
<?xml version="1.0" encoding="utf-8"?>
<ContentType Key="$G_PAGE" Alias="articlePage" Level="2">
  <Info>
    <Name>Article Page</Name>
    <Icon>icon-article color-blue</Icon>
    <Thumbnail>folder.png</Thumbnail>
    <Description></Description>
    <AllowAtRoot>False</AllowAtRoot>
    <IsListView>False</IsListView>
    <Variations>Nothing</Variations>
    <IsElement>false</IsElement>
    <Compositions>
      <Composition Key="$G_PBASE">pageBase</Composition>
    </Compositions>
    <DefaultTemplate>articlePage</DefaultTemplate>
    <AllowedTemplates>
      <Template Key="$G_PAGE">articlePage</Template>
    </AllowedTemplates>
  </Info>
  <Structure />
  <GenericProperties>
    <GenericProperty>
      <Key>eeee1111-0101-4000-8000-000000000101</Key>
      <Name>Article Heading</Name>
      <Alias>articleHeading</Alias>
      <Definition>$G_TEXT</Definition>
      <Type>Umbraco.TextBox</Type>
      <Mandatory>true</Mandatory>
      <Validation></Validation>
      <Description></Description>
      <SortOrder>10</SortOrder>
      <Tab Alias="content">Content</Tab>
      <Variations>Nothing</Variations>
    </GenericProperty>
  </GenericProperties>
  <Tabs>
    <Tab>
      <Key>eeee1111-0001-4000-8000-000000000001</Key>
      <Caption>Content</Caption>
      <Alias>content</Alias>
      <Type>Tab</Type>
      <SortOrder>10</SortOrder>
    </Tab>
  </Tabs>
</ContentType>
EOF

  # <AllowAtRoot> is written either way, so here it says True — the value Deploy expresses by
  # writing the key at all. <Structure> is uSync's allowed-children list.
  cat > "$root/ContentTypes/topicfolder.config" <<EOF
<?xml version="1.0" encoding="utf-8"?>
<ContentType Key="$G_TOPIC" Alias="topicFolder" Level="1">
  <Info>
    <Name>Topic Folder</Name>
    <Icon>icon-folder color-black</Icon>
    <Thumbnail>folder.png</Thumbnail>
    <Description></Description>
    <AllowAtRoot>True</AllowAtRoot>
    <IsListView>False</IsListView>
    <Variations>Nothing</Variations>
    <IsElement>false</IsElement>
    <Compositions />
    <DefaultTemplate></DefaultTemplate>
    <AllowedTemplates />
  </Info>
  <Structure>
    <ContentType Key="$G_PAGE" SortOrder="0">articlePage</ContentType>
  </Structure>
  <GenericProperties />
  <Tabs />
</ContentType>
EOF

  cat > "$root/ContentTypes/pagebase.config" <<EOF
<?xml version="1.0" encoding="utf-8"?>
<ContentType Key="$G_PBASE" Alias="pageBase" Level="1">
  <Info>
    <Name>Page Base</Name>
    <Icon>icon-settings color-black</Icon>
    <Thumbnail>folder.png</Thumbnail>
    <Description></Description>
    <AllowAtRoot>False</AllowAtRoot>
    <IsListView>False</IsListView>
    <Variations>Nothing</Variations>
    <IsElement>false</IsElement>
    <Compositions />
    <DefaultTemplate></DefaultTemplate>
    <AllowedTemplates />
  </Info>
  <Structure />
  <GenericProperties>
    <GenericProperty>
      <Key>b22b2222-0101-4000-8000-000000000101</Key>
      <Name>Meta Description</Name>
      <Alias>metaDescription</Alias>
      <Definition>$G_TEXT</Definition>
      <Type>Umbraco.TextBox</Type>
      <Mandatory>false</Mandatory>
      <Validation></Validation>
      <Description></Description>
      <SortOrder>10</SortOrder>
      <Tab Alias="seo">SEO</Tab>
      <Variations>Nothing</Variations>
    </GenericProperty>
  </GenericProperties>
  <Tabs>
    <Tab>
      <Key>b22b2222-0001-4000-8000-000000000001</Key>
      <Caption>SEO</Caption>
      <Alias>seo</Alias>
      <Type>Tab</Type>
      <SortOrder>100</SortOrder>
    </Tab>
  </Tabs>
</ContentType>
EOF
}

# The human report, hand-authored. It is the deliverable this step's own validation reads, so
# it is asserted as a whole document: the counts, the rule that produced them, and the word
# PROPOSED beside the one section that is a proposal.
#
# Nothing here was captured from a run. The three classifications were decided from the cast
# above, and the wording states the rule so a wrong determiner is visible in the output rather
# than after a hundred guides have been proposed.
expected_page_report() {  # expected_page_report <case-root> <rung>
  cat > "$1/expected-report.txt" <<EOF
Inventory of documentable units, read at the $2 rung.
  3 content types read: 0 carry the element-type flag, 3 do not.
  0 block-editor data types carry a block list.

Components an editor can place: 0
  A content type named as a palette entry's content block, in one of the project's
  block-editor data types. Read from the palette, never from the element-type flag.

Page types PROPOSED for a human to confirm: 1 of 3 document types
  PROPOSED, not decided. No flag separates a page type from a folder, a container, or an
  abstract base, so a document type is proposed when it carries a template or matches the
  project's own page-naming convention. Tree reachability is read as evidence and is not a
  gate, because a folder is reachable by definition.
  Naming convention: not derived.
    1 document type carries a template, and at least 2 are needed to measure a shared
    suffix.
    articlePage (Article Page): template, reachable

  Not proposed, a folder or a container: 1
    Reachable in the content tree, but carries no template and matches no naming convention.
      topicFolder (Topic Folder)

  Not proposed, an abstract base or a composition: 1
    Neither reachable in the content tree nor carrying a template.
      pageBase (Page Base)

Documentable: 0 components + 1 proposed page type = 1.
EOF
}

inv_page_project() {  # inv_page_project <case-root>
  inv_deploy_page_tree "$1"
  inv_usync_page_tree "$1"
}

INV_PAGE_EXPECT=(
  "exit: 0"
  "stdout_matches: expected-report.txt"
)

C="$CASES/inventory-page-types-proposed"; mkdir -p "$C"
inv_page_project "$C"; expected_page_report "$C" deploy
expect "$C" "${INV_PAGE_EXPECT[@]}" \
  "args: inventory --adapter deploy" \
  "contains: PROPOSED, not decided"

C="$CASES/inventory-page-types-usync"; mkdir -p "$C"
inv_page_project "$C"; expected_page_report "$C" usync
expect "$C" "${INV_PAGE_EXPECT[@]}" \
  "args: inventory --adapter usync" \
  "contains: PROPOSED, not decided"

# --- the rung that cannot answer the question ----------------------------------
#
# A generated model carries no palette, no template assignment and no tree structure, so the
# models rung can answer neither half of the inventory. Returning an empty set would read as
# "this project has no blocks", which is the silent-empty failure the whole ladder exists to
# prevent — and it would be indistinguishable from the truth on a project that genuinely has
# none. So it refuses, and says which of its own limits made it refuse.
#
# `not_contains: "components"` is how "no document was printed" is stated: a refusal that also
# emitted a report would have answered the question it just said it could not.
C="$CASES/inventory-models-refused"; mkdir -p "$C"; models_tree "$C"
expect "$C" \
  "exit: 1" \
  "args: inventory --adapter models" \
  "contains: carries no block-editor palette" \
  'not_contains: "components"' \
  "not_contains: Components an editor can place"

# ==============================================================================
# The audit — arithmetic over an inventory and a set of guide pages
# ==============================================================================
#
# Every case above answers a question about a project. These answer a question about the gap
# between a project and its published guides, so each one needs a second input: a guides file,
# which is JSON the spell reads out of the CMS. The script never touches a CMS — that keeps the
# arithmetic testable here rather than only against a running instance.
#
# The three sections are the spec's, and a fixture exists per section because each has a
# neighbouring case it is easy to conflate with:
#
#   undocumented   a unit in the inventory that no guide's stored reference names
#   orphaned       a guide naming an alias this project no longer declares
#   stale          a guide whose stored signature differs from its source's current one
#
# A guide claiming NO source is in none of them, which `audit-orphan-and-sourceless` asserts
# in both directions at once: the deleted component must be named, and the hand-written guide
# must not be — and no substring can say the second thing, so the report is compared whole.
#
# **A signature cannot be hand-authored**, which shapes two of these cases. A guides file
# stating a plausible-looking hash would make every guide in it stale, so the project-backed
# cases store no signature and assert the "not compared" count instead. The comparison itself
# is asserted by `audit-signature-mismatch`, which supplies the inventory as a file too — then
# both sides of the comparison are hand-authored strings, a matching pair and a differing pair
# side by side, and no hash is involved anywhere.

# --- fourteen blocks, thirteen guides ------------------------------------------
#
# The spec's scenario, with the numbers it names. Fourteen is not decoration: a set difference
# implemented backwards (naming the thirteen that ARE documented) produces a report of the same
# shape, and only a count this lopsided makes the two impossible to confuse in a failure.
#
# One palette offering all fourteen, so every one of them is a documentable unit by the
# determiner Step 8 built — this case asserts the audit's arithmetic, not the determiner's.
audit_fourteen_blocks() {  # audit_fourteen_blocks <case-root>
  local rev="$1/src/Web/umbraco/Deploy/Revision" i two guid guids=() blocks
  mkdir -p "$rev"
  deploy_data_type "$rev" "$U_TEXT" "Textstring" "Umbraco.TextBox" \
    "Umb.PropertyEditorUi.TextBox" "Nvarchar" '{}'
  for i in $(seq 1 14); do
    two=$(printf '%02d' "$i")
    # Deploy writes a UDI with the dashes stripped and a palette key with them kept. The
    # undashed form is DERIVED from the dashed one rather than written out a second time: the
    # first version of this fixture spelled both by hand, they did not agree, and fourteen
    # palette entries resolved to nothing.
    guid="${two}aaaaaa-${two}aa-${two}aa-${two}aa-${two}aaaaaaaaaa"
    guids+=("$guid")
    inv_deploy_element "$rev" "${guid//-/}" "block$two" "Block $two" \
      "block${two}Heading" "Block $two Heading"
  done
  blocks=$(printf '      { "contentElementTypeKey": "%s" },\n' "${guids[@]}")
  inv_deploy_palette "$rev" "$U_PBODY" "$INV_PALETTE_A" \
    "Umbraco.BlockList" "Umb.PropertyEditorUi.BlockList" "[
${blocks%,}
    ]"
}

# Thirteen guides, one per block except the fourteenth. `signature: null` is a stored reference
# that records no signature, which is a real shape — a reference written before the signature
# existed, or one an editor cleared — and it is the only shape a fixture can state, since the
# current signature is a hash this file cannot compute.
audit_thirteen_guides() {  # audit_thirteen_guides <case-root>
  local i two entries
  entries=$(for i in $(seq 1 13); do
    two=$(printf '%02d' "$i")
    printf '    {\n      "page": "Block %s",\n      "source": { "alias": "block%s", "kind": "element", "signature": null, "rung": "deploy" }\n    },\n' \
      "$two" "$two"
  done)
  cat > "$1/guides.json" <<EOF
{
  "guidesVersion": 1,
  "guides": [
${entries%,}
  ]
}
EOF
}

C="$CASES/audit-undocumented"; mkdir -p "$C"
audit_fourteen_blocks "$C"; audit_thirteen_guides "$C"
# Hand-authored from the two inputs above. The counts are arithmetic over a cast decided here,
# and the one named item is the block deliberately left out of the guides file.
cat > "$C/expected-report.txt" <<'EOF'
Guide audit, read at the deploy rung.
  14 documentable units: 14 components + 0 proposed page types.
  Counted from the project's own block-editor palettes and the page types it proposes,
  never from the element-type flag. Run inventory for that rule in full, with its own
  counts.
  13 guide pages read: 13 claim a source, 0 claim none.
  Not compared: 13 guides record no stored signature.

Undocumented, present in code with no guide page: 1
  A documentable unit that no guide page's stored reference names: a component an editor
  can place from a block-editor palette, or a document type proposed as a page. Matched
  on the alias, case-insensitively, never on a page's name or its address.
    block14 (Block 14)

Orphaned, claiming a source this project no longer holds: 0

Stale, whose stored signature no longer matches its source: 0

Findings: 1 undocumented, 0 orphaned, 0 stale.
EOF
expect "$C" \
  "exit: 0" \
  "args: audit --guides guides.json --adapter deploy" \
  "stdout_matches: expected-report.txt" \
  "contains: block14 (Block 14)" \
  "not_contains: block13 (Block 13)"

# --- an orphan and a hand-written guide, asserted in one report ------------------
#
# The two shapes that look identical from the guide side and are opposite findings: both pages
# document something absent from the inventory, and only the stored reference tells them apart.
#
#   a guide for testimonialSlider   the component was deleted from the codebase  -> ORPHAN
#   "Image Sizing Standards"        source: null, written by a person by hand    -> neither
#
# Reusing the three-component palette project from the inventory cases, with a guide for each of
# its three components, so both findings are read against a project with nothing else wrong: 0
# undocumented is part of the claim, or an orphan could be mistaken for a coverage gap.
#
# The report is compared whole because "the second appears in NEITHER list" is not a substring
# claim. `not_contains: Image Sizing` states half of it — that the page is named nowhere — and
# even that cannot say the counts were not inflated by it. The golden file can.
C="$CASES/audit-orphan-and-sourceless"; mkdir -p "$C"
inv_deploy_tree "$C"
cat > "$C/guides.json" <<'EOF'
{
  "guidesVersion": 1,
  "guides": [
    {
      "page": "Hero Slide",
      "source": { "alias": "heroSlide", "kind": "element", "signature": null, "rung": "deploy" }
    },
    {
      "page": "Media Row",
      "source": { "alias": "mediaRow", "kind": "element", "signature": null, "rung": "deploy" }
    },
    {
      "page": "Notice Bar",
      "source": { "alias": "noticeBar", "kind": "element", "signature": null, "rung": "deploy" }
    },
    {
      "page": "Testimonial Slider",
      "source": {
        "alias": "testimonialSlider",
        "kind": "element",
        "signature": null,
        "rung": "deploy"
      }
    },
    {
      "page": "Image Sizing Standards",
      "source": null
    }
  ]
}
EOF
# Hand-authored. The orphan is named `alias (the page's own name)` because the source it claims
# is gone and has no display name left to print — the page is what the operator acts on.
cat > "$C/expected-report.txt" <<'EOF'
Guide audit, read at the deploy rung.
  3 documentable units: 3 components + 0 proposed page types.
  Counted from the project's own block-editor palettes and the page types it proposes,
  never from the element-type flag. Run inventory for that rule in full, with its own
  counts.
  5 guide pages read: 4 claim a source, 1 claims none.
  Not compared: 3 guides record no stored signature.

Undocumented, present in code with no guide page: 0

Orphaned, claiming a source this project no longer holds: 1
  A guide whose stored reference names an alias no content type in this read declares. A
  guide claiming no source at all is never an orphan, because a hand-written guide
  documents something that was never in the schema. Each is named as alias (the guide
  page's own name), since the source it claims has no name left to print.
    testimonialSlider (Testimonial Slider)

Stale, whose stored signature no longer matches its source: 0

Findings: 0 undocumented, 1 orphaned, 0 stale.
EOF
expect "$C" \
  "exit: 0" \
  "args: audit --guides guides.json --adapter deploy" \
  "stdout_matches: expected-report.txt" \
  "contains: testimonialSlider (Testimonial Slider)" \
  "contains: 1 claims none." \
  "not_contains: Image Sizing"

# --- the signature comparison, with both sides hand-authored ---------------------
#
# The one case that supplies the INVENTORY as a file too, and the reason is that a signature is
# a hash: a fixture cannot state the current one, so a project-backed case can only ever assert
# the not-compared path. Supplied on both sides, the comparison becomes hand-authorable in both
# directions at once, which is what this case needs — a mismatch reported AND a match not
# reported. A case that only asserted the mismatch would pass against an implementation that
# called every signature-bearing guide stale.
#
# The seam is not invented for the test. It is the plan's rung-3 seam: the running instance's
# management API belongs to the spell, which reads it through MCP and hands the inventory back
# as JSON. This case is also the only coverage that seam has.
#
# `signature` values here are deliberately not plausible hashes. They are compared as opaque
# strings and never parsed, and writing `sha256:` plus 64 hex digits would invite a reader to
# think the format mattered.
C="$CASES/audit-signature-mismatch"; mkdir -p "$C"
cat > "$C/inventory.json" <<'EOF'
{
  "inventoryVersion": 1,
  "rung": "deploy",
  "contentTypesRead": 3,
  "elementFlagged": 2,
  "documentTypesRead": 1,
  "palettesRead": 1,
  "components": [
    {
      "alias": "noticeBar",
      "name": "Notice Bar",
      "kind": "element",
      "palettes": ["[BlockList] Page Body"],
      "signature": "sha256:currentnoticebar"
    },
    {
      "alias": "mediaRow",
      "name": "Media Row",
      "kind": "element",
      "palettes": ["[BlockList] Page Body"],
      "signature": "sha256:currentmediarow"
    }
  ],
  "settingsModels": [],
  "unpalettedElementTypes": [],
  "unresolvedPaletteEntries": 0,
  "pageTypesProposed": [
    {
      "alias": "articlePage",
      "name": "Article Page",
      "kind": "document",
      "signals": ["template", "reachable"],
      "signature": "sha256:currentarticlepage"
    }
  ],
  "notProposed": []
}
EOF
# noticeBar's stored signature matches and mediaRow's does not, so exactly one of two guides
# stored the same way is named. articlePage is stored at a rung this read is not, which is the
# comparison that must NOT fire: two rungs sign one component differently by design, so
# comparing across them would report every guide in a re-serialized project as stale.
cat > "$C/guides.json" <<'EOF'
{
  "guidesVersion": 1,
  "guides": [
    {
      "page": "Notice Bar",
      "source": {
        "alias": "noticeBar",
        "kind": "element",
        "signature": "sha256:currentnoticebar",
        "rung": "deploy"
      }
    },
    {
      "page": "Media Row",
      "source": {
        "alias": "mediaRow",
        "kind": "element",
        "signature": "sha256:mediarowasgenerated",
        "rung": "deploy"
      }
    },
    {
      "page": "Article Page",
      "source": {
        "alias": "articlePage",
        "kind": "document",
        "signature": "sha256:articlepagefromthemodels",
        "rung": "models"
      }
    }
  ]
}
EOF
# Hand-authored from the two files above. A stale item is named `alias (Display Name)` — its
# source is still there, so its display name is the one an editor knows it by.
cat > "$C/expected-report.txt" <<'EOF'
Guide audit, read at the deploy rung.
  3 documentable units: 2 components + 1 proposed page type.
  Counted from the project's own block-editor palettes and the page types it proposes,
  never from the element-type flag. Run inventory for that rule in full, with its own
  counts.
  3 guide pages read: 3 claim a source, 0 claim none.
  Not compared: 1 was stored at another rung, or at none this read can name.

Undocumented, present in code with no guide page: 0

Orphaned, claiming a source this project no longer holds: 0

Stale, whose stored signature no longer matches its source: 1
  A guide whose stored signature differs from its source's current signature, so the
  source changed shape after the guide was generated. Compared only where the guide
  records a signature and was stored at this read's rung: two rungs sign one component
  differently by design, so comparing across them would report every guide as stale.
    mediaRow (Media Row)

Findings: 0 undocumented, 0 orphaned, 1 stale.
EOF
expect "$C" \
  "exit: 0" \
  "args: audit --guides guides.json --inventory inventory.json" \
  "stdout_matches: expected-report.txt" \
  "contains: mediaRow (Media Row)" \
  "contains: 1 was stored at another rung" \
  "not_contains: noticeBar" \
  "not_contains: articlePage"

# --- what a guides file may not be trusted to be --------------------------------
#
# The guides file is the one input this command cannot check by re-reading the project, and it
# is produced by another process. So the three cases below fix where the refuse/permit line
# falls, in both directions — a refusal with no case proving what it does NOT refuse is how the
# next increment tightens it by accident.
#
# Each pairs its guides file with a supplied inventory rather than a project tree: the subject
# under test here is the reading of the guides file, and a fourteen-artifact tree beside it
# would only add a second thing that could fail.
audit_tiny_inventory() {  # audit_tiny_inventory <case-root>
  cat > "$1/inventory.json" <<'EOF'
{
  "inventoryVersion": 1,
  "rung": "deploy",
  "contentTypesRead": 1,
  "elementFlagged": 1,
  "documentTypesRead": 0,
  "palettesRead": 1,
  "components": [
    {
      "alias": "noticeBar",
      "name": "Notice Bar",
      "kind": "element",
      "palettes": ["[BlockList] Page Body"],
      "signature": "sha256:currentnoticebar"
    }
  ],
  "settingsModels": [],
  "unpalettedElementTypes": [],
  "unresolvedPaletteEntries": 0,
  "pageTypesProposed": [],
  "notProposed": []
}
EOF
}

# A guides file that is not JSON. Refused whole, with no report printed: a file half-read
# reports the components its dropped entries documented as undocumented, and nothing in the
# output would say so. `not_contains: Guide audit` is how "no report was printed" is stated.
C="$CASES/audit-guides-unreadable"; mkdir -p "$C"; audit_tiny_inventory "$C"
cat > "$C/guides.json" <<'EOF'
{ "guides": [ { "page": "Notice Bar", "source": { "alias":
EOF
expect "$C" \
  "exit: 1" \
  "args: audit --guides guides.json --inventory inventory.json" \
  "contains: not readable JSON" \
  "contains: guides.json" \
  "not_contains: Guide audit"

# An entry with no `source` key at all. Refused, and this is the subtle one: `"source": null`
# means "this page carries no stored reference", which is a fact about the CMS, while an absent
# key is a fact about the producer. Defaulting the second to the first would turn a spell that
# failed to read the property into a report saying every guide was hand-written — every orphan
# and every stale guide silently gone from the report whose job is to name them.
C="$CASES/audit-guides-no-source-key"; mkdir -p "$C"; audit_tiny_inventory "$C"
cat > "$C/guides.json" <<'EOF'
{
  "guidesVersion": 1,
  "guides": [
    {
      "page": "Notice Bar"
    }
  ]
}
EOF
expect "$C" \
  "exit: 1" \
  "args: audit --guides guides.json --inventory inventory.json" \
  "contains: has no 'source' key" \
  "contains: Notice Bar" \
  "contains: cannot be told from a reference the producer failed to read" \
  "not_contains: Guide audit"

# --- the refusals the module documents and nothing exercised ---------------------
#
# Seven guides-file shapes are refused, and the first pass fixtured two of them. An untested
# refusal is exposed to regressing exactly the way an untested permit is: tests/README.md's own
# rule cuts both ways. Each of these was hand-verified to refuse before it was written down.

C="$CASES/audit-guides-not-object"; mkdir -p "$C"; audit_tiny_inventory "$C"
cat > "$C/guides.json" <<'EOF'
{
  "guidesVersion": 1,
  "guides": [
    "noticeBar"
  ]
}
EOF
expect "$C" \
  "exit: 1" \
  "args: audit --guides guides.json --inventory inventory.json" \
  "contains: is str, not an object" \
  'not_contains: Guide audit'

C="$CASES/audit-guides-wrong-version"; mkdir -p "$C"; audit_tiny_inventory "$C"
cat > "$C/guides.json" <<'EOF'
{
  "guidesVersion": 99,
  "guides": []
}
EOF
expect "$C" \
  "exit: 1" \
  "args: audit --guides guides.json --inventory inventory.json" \
  "contains: guidesVersion" \
  "contains: 99" \
  'not_contains: Guide audit'

C="$CASES/audit-guides-source-no-alias"; mkdir -p "$C"; audit_tiny_inventory "$C"
cat > "$C/guides.json" <<'EOF'
{
  "guidesVersion": 1,
  "guides": [
    {
      "page": "Notice Bar",
      "source": {
        "kind": "element",
        "signature": "sha256:whatever"
      }
    }
  ]
}
EOF
expect "$C" \
  "exit: 1" \
  "args: audit --guides guides.json --inventory inventory.json" \
  "contains: alias" \
  "contains: Notice Bar" \
  'not_contains: Guide audit'

C="$CASES/audit-guides-non-string-field"; mkdir -p "$C"; audit_tiny_inventory "$C"
cat > "$C/guides.json" <<'EOF'
{
  "guidesVersion": 1,
  "guides": [
    {
      "page": "Notice Bar",
      "source": {
        "alias": "noticeBar",
        "kind": "element",
        "signature": 12345
      }
    }
  ]
}
EOF
expect "$C" \
  "exit: 1" \
  "args: audit --guides guides.json --inventory inventory.json" \
  "contains: non-string" \
  "contains: signature" \
  'not_contains: Guide audit'

# --- the inventory side, which got none of this validation at all -----------------
#
# `--inventory` is the seam the spell uses to hand back a live read, and it checked four
# top-level keys and stopped. An item with a name and no alias produced a raw KeyError
# traceback rather than a refusal — on the one input path a human never writes by hand.

C="$CASES/audit-inventory-item-no-alias"; mkdir -p "$C"
cat > "$C/guides.json" <<'EOF'
{
  "guidesVersion": 1,
  "guides": []
}
EOF
cat > "$C/inventory.json" <<'EOF'
{
  "inventoryVersion": 1,
  "rung": "deploy",
  "components": [
    {
      "name": "Notice Bar"
    }
  ],
  "pageTypesProposed": []
}
EOF
expect "$C" \
  "exit: 1" \
  "args: audit --guides guides.json --inventory inventory.json" \
  "contains: names no alias" \
  "contains: components[0]" \
  "not_contains: Traceback" \
  'not_contains: Guide audit'

# Two entries differing only in case. Counted once, so the header's own arithmetic holds --
# it read "1 documentable unit: 2 components + 0 proposed page types" before.
C="$CASES/audit-inventory-duplicate-alias"; mkdir -p "$C"
cat > "$C/guides.json" <<'EOF'
{
  "guidesVersion": 1,
  "guides": []
}
EOF
cat > "$C/inventory.json" <<'EOF'
{
  "inventoryVersion": 1,
  "rung": "deploy",
  "components": [
    {
      "alias": "noticeBar",
      "name": "Notice Bar"
    },
    {
      "alias": "noticebar",
      "name": "Notice Bar Again"
    }
  ],
  "pageTypesProposed": []
}
EOF
expect "$C" \
  "exit: 0" \
  "args: audit --guides guides.json --inventory inventory.json" \
  "contains: both name the alias" \
  "contains: 1 documentable unit: 1 component" \
  "not_contains: 2 components"

# --- a signature with no rung is not comparable ----------------------------------
#
# `rung` is optional on a stored reference, and the guard required it to be present AND
# different — so a signature with no rung went straight to the comparison and came out stale
# against a rung that may not have produced it, while the printed rule claimed comparison
# happened only at this read's rung. Two rungs sign one component differently by design.
C="$CASES/audit-signature-no-rung"; mkdir -p "$C"; audit_tiny_inventory "$C"
cat > "$C/guides.json" <<'EOF'
{
  "guidesVersion": 1,
  "guides": [
    {
      "page": "Notice Bar",
      "source": {
        "alias": "noticeBar",
        "kind": "element",
        "signature": "sha256:fromsomewhereelse"
      }
    }
  ]
}
EOF
expect "$C" \
  "exit: 0" \
  "args: audit --guides guides.json --inventory inventory.json" \
  "contains: stored at another rung, or at none this read can name" \
  "contains: Stale, whose stored signature no longer matches its source: 0" \
  "not_contains: noticeBar (Notice Bar)"

# --- a guide for schema that is real but not documentable ------------------------
#
# A settings model, a composition, a folder. Its subject exists, so it is not an orphan; it is
# not a documentable unit, so it closes no gap. It appears in no section and in no count but
# the guide-page total -- which was correct by inspection and asserted nowhere.
C="$CASES/audit-guide-for-non-unit"; mkdir -p "$C"
cat > "$C/guides.json" <<'EOF'
{
  "guidesVersion": 1,
  "guides": [
    {
      "page": "Spacing Properties",
      "source": {
        "alias": "spacingProperties",
        "kind": "element",
        "signature": "sha256:whatever",
        "rung": "deploy"
      }
    }
  ]
}
EOF
cat > "$C/inventory.json" <<'EOF'
{
  "inventoryVersion": 1,
  "rung": "deploy",
  "components": [],
  "pageTypesProposed": [],
  "unpalettedElementTypes": [
    {
      "alias": "spacingProperties",
      "name": "Spacing Properties"
    }
  ]
}
EOF
expect "$C" \
  "exit: 0" \
  "args: audit --guides guides.json --inventory inventory.json" \
  "contains: 1 guide page read" \
  "contains: Orphaned, claiming a source this project no longer holds: 0" \
  "contains: Undocumented, present in code with no guide page: 0" \
  "contains: Findings: none"

# Two guide pages claiming one source. NOT refused, and the contrast with the two cases above
# is the point: this one is answerable. The component is documented either way, so no count in
# the report moves — the note says so, and the audit still runs to completion at exit 0.
C="$CASES/audit-guides-duplicate-source"; mkdir -p "$C"; audit_tiny_inventory "$C"
cat > "$C/guides.json" <<'EOF'
{
  "guidesVersion": 1,
  "guides": [
    {
      "page": "Notice Bar",
      "source": { "alias": "noticeBar", "kind": "element", "signature": null, "rung": "deploy" }
    },
    {
      "page": "Notice Bar (old)",
      "source": { "alias": "noticebar", "kind": "element", "signature": null, "rung": "deploy" }
    }
  ]
}
EOF
expect "$C" \
  "exit: 0" \
  "args: audit --guides guides.json --inventory inventory.json" \
  "contains: 2 guide pages claim the source 'noticebar'" \
  "contains: Notice Bar (old)" \
  "contains: only one is the one to keep" \
  "contains: Undocumented, present in code with no guide page: 0" \
  "contains: Findings: none."


# --- completeness is relative to the rung, and thinness is said once -------------
#
# A project whose schema can only be read from generated model classes, with a guide for every
# one of its blocks. Nothing is undocumented, nothing is orphaned, nothing is stale — and the
# report still owes its reader one thing, because a guide generated from this rung shows no
# tabs, no required flags and no option lists. That is a limit of the source, so it is stated
# once for the whole report and never as a finding against a guide.
#
# **The inventory has to be supplied.** The determiner refuses at the models rung on purpose: a
# generated model carries no block-editor palette, so an empty component list there would read
# as "this project offers no blocks", which is true for some projects and false for others with
# nothing to tell them apart. `inventory-models-refused` asserts that refusal. So this case
# hands over a document through the same `--inventory` seam the spell uses for a live read —
# nothing restricts what rung that document may declare, which is what makes the seam worth
# having.
#
# Twelve blocks, the number the spec's scenario names. The report is compared whole because
# "once" and "never per guide" are both claims about the document rather than about a value in
# it: a per-guide incompleteness finding would satisfy every substring assertion here.
C="$CASES/audit-rung-statement"; mkdir -p "$C"
{
  printf '{\n  "inventoryVersion": 1,\n  "rung": "models",\n  "components": [\n'
  for i in $(seq 1 12); do
    two=$(printf '%02d' "$i")
    printf '    { "alias": "modelBlock%s", "name": "Model Block %s", "kind": "element" }' "$two" "$two"
    [ "$i" -lt 12 ] && printf ',\n' || printf '\n'
  done
  printf '  ],\n  "settingsModels": [],\n  "unpalettedElementTypes": [],\n  "pageTypesProposed": [],\n  "notProposed": []\n}\n'
} > "$C/inventory.json"
# One guide per block, each storing a reference at the rung the inventory was read at. No
# signature, because a fixture cannot state a hash — so all twelve land in the not-compared
# line, and the thinness statement is what this case is actually about.
{
  printf '{\n  "guidesVersion": 1,\n  "guides": [\n'
  for i in $(seq 1 12); do
    two=$(printf '%02d' "$i")
    printf '    {\n      "page": "Model Block %s",\n      "source": { "alias": "modelBlock%s", "kind": "element", "signature": null, "rung": "models" }\n    }' "$two" "$two"
    [ "$i" -lt 12 ] && printf ',\n' || printf '\n'
  done
  printf '  ]\n}\n'
} > "$C/guides.json"
# Hand-authored. The statement's per-field lines are the same text a dossier read at this rung
# carries in `structureGaps` — `models-only-rung`'s golden file states the JSON form of exactly
# these eight — so the two documents cannot disagree about what the rung cannot report.
cat > "$C/expected-report.txt" <<'EOF'
Guide audit, read at the models rung.
  12 documentable units: 12 components + 0 proposed page types.
  Counted from the project's own block-editor palettes and the page types it proposes,
  never from the element-type flag. Run inventory for that rule in full, with its own
  counts.
  12 guide pages read: 12 claim a source, 0 claim none.
  Not compared: 12 guides record no stored signature.

  Structure unavailable from this source: 8 dossier fields this rung cannot report in
  full, so completeness below is judged against what it can. Stated here once, and
  never against a guide: a guide is not incomplete for a field its source never
  recorded, and every line below is a limit of the read rather than work for anyone.
    description (component): not recorded. A generated model's class summary carries
      the display name and nothing else.
    description (property): recorded, but as ModelsBuilder escaped it: line breaks
      collapsed to spaces, and angle brackets rewritten as braces.
    editor: the generated C# property type, not the data type's editor alias.
    icon: not recorded. The backoffice icon is not generated into a model.
    mandatory: not recorded. Every property reads false; required flags
      are not generated.
    options: not recorded. Every option list reads empty; an option list lives on the
      data type, which this rung does not read.
    sortOrder: not recorded. Every property reads 0, and the unnamed bucket is in
      alias order.
    tabs: not recorded. A generated model carries no tab or group structure, so every
      property is in the one unnamed bucket.

Undocumented, present in code with no guide page: 0

Orphaned, claiming a source this project no longer holds: 0

Stale, whose stored signature no longer matches its source: 0

Findings: none. Every documentable unit has a guide page, and every stored source still
resolves and matches.
EOF
# The three `contains` lines are the manual claim in human terms: the statement names the
# missing *structure* — tabs, required flags, option lists — and not merely the rung. Short
# fragments, so they survive a rewording of the sentence they open.
# `not_contains: modelBlock` is how "no guide was reported as incomplete" is stated: every
# section names its items as `alias (Display Name)`, so an alias appearing anywhere in this
# report would mean some guide or unit was named as a finding.
expect "$C" \
  "exit: 0" \
  "args: audit --guides guides.json --inventory inventory.json" \
  "stdout_matches: expected-report.txt" \
  "contains: tabs: not recorded." \
  "contains: mandatory: not recorded." \
  "contains: options: not recorded." \
  "contains: Findings: none." \
  "not_contains: modelBlock"

# --- the exit code: a backlog by default, a gate only when asked for -------------
#
# Three cases over one pair of inputs, because the behavior under test is entirely the exit
# code and nothing else. Findings are a backlog: an audit that exited non-zero on them would
# fail a build by default in exactly the projects that wired it into CI early, which is how
# guides get cut from scope again, louder. So the default is 0 WITH findings, and `--strict`
# is the only path to a non-zero exit.
#
# The twin asserts `same_stdout_as` against the default case, which is the whole of "and
# nothing else changes with it": a flag that also reordered a section, or added a line naming
# itself, would pass an exit-code assertion and still have changed the report.
#
# One documentable unit and an empty guide set, so the finding is the smallest one that can
# exist. An empty `guides` array is a real shape -- the first run on an existing site -- and
# it is the one guide set that needs no invented page names.
audit_strict_inputs() {  # audit_strict_inputs <case-root>
  audit_tiny_inventory "$1"
  cat > "$1/guides.json" <<'EOF'
{
  "guidesVersion": 1,
  "guides": []
}
EOF
}

C="$CASES/audit-strict-exit"; mkdir -p "$C"; audit_strict_inputs "$C"
expect "$C" \
  "exit: 0" \
  "args: audit --guides guides.json --inventory inventory.json" \
  "contains: Undocumented, present in code with no guide page: 1" \
  "contains: noticeBar (Notice Bar)" \
  "contains: Findings: 1 undocumented, 0 orphaned, 0 stale."

# The same findings, gated. Non-zero, and specifically NOT 1: a read that could not be
# completed at all already exits 1, and a CI job that cannot tell "the audit found gaps" from
# "the audit broke" has no reason to have opted in.
C="$CASES/audit-strict-exit-gated"; mkdir -p "$C"; audit_strict_inputs "$C"
expect "$C" \
  "exit: 3" \
  "args: audit --guides guides.json --inventory inventory.json --strict" \
  "same_stdout_as: audit-strict-exit" \
  "contains: Findings: 1 undocumented, 0 orphaned, 0 stale."

# --strict on a healthy project. The permit side of the gate: a flag implemented as "exit
# non-zero" rather than "exit non-zero on findings" passes both cases above and fails every
# build that opted in, forever, with nothing to fix.
# --- a rung this script has no fidelity record for --------------------------------
#
# The registry answered `()` for an unlisted rung, which is the same answer it gives a source
# that reads everything — so a mistyped rung in a hand-built inventory, or a fourth adapter
# added without an entry, printed no caveat and read as full fidelity. That is the most
# over-confident sentence this report can produce, and it produced it silently.
#
# Three answers now: full, partial, and unknown. This case is the third, and it is the one no
# amount of comment could pin.
C="$CASES/audit-unknown-rung"; mkdir -p "$C"
cat > "$C/guides.json" <<'EOF'
{
  "guidesVersion": 1,
  "guides": []
}
EOF
cat > "$C/inventory.json" <<'EOF'
{
  "inventoryVersion": 1,
  "rung": "somethingElse",
  "components": [
    {
      "alias": "noticeBar",
      "name": "Notice Bar"
    }
  ],
  "pageTypesProposed": []
}
EOF
expect "$C" \
  "exit: 0" \
  "args: audit --guides guides.json --inventory inventory.json" \
  "contains: Structure completeness unknown" \
  "contains: somethingElse" \
  "contains: treat a clean result as unconfirmed" \
  "not_contains: Structure unavailable from this source"

# The same rung name a case-fold apart. `Models` is a typo, not a fourth rung, so it must
# resolve to the models rung's own gaps rather than falling through to unknown.
C="$CASES/audit-rung-folded"; mkdir -p "$C"
cat > "$C/guides.json" <<'EOF'
{
  "guidesVersion": 1,
  "guides": []
}
EOF
cat > "$C/inventory.json" <<'EOF'
{
  "inventoryVersion": 1,
  "rung": "Models",
  "components": [
    {
      "alias": "noticeBar",
      "name": "Notice Bar"
    }
  ],
  "pageTypesProposed": []
}
EOF
expect "$C" \
  "exit: 0" \
  "args: audit --guides guides.json --inventory inventory.json" \
  "contains: Structure unavailable from this source" \
  "not_contains: Structure completeness unknown"

C="$CASES/audit-strict-clean"; mkdir -p "$C"; audit_tiny_inventory "$C"
cat > "$C/guides.json" <<'EOF'
{
  "guidesVersion": 1,
  "guides": [
    {
      "page": "Notice Bar",
      "source": { "alias": "noticeBar", "kind": "element", "signature": null, "rung": "deploy" }
    }
  ]
}
EOF
expect "$C" \
  "exit: 0" \
  "args: audit --guides guides.json --inventory inventory.json --strict" \
  "contains: Findings: none."

echo "regenerated $(find "$CASES" -mindepth 1 -maxdepth 1 -type d | wc -l | tr -d ' ') fixtures"
