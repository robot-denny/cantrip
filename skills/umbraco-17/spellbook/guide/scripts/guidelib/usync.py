"""Rung 2 — uSync configuration (`*.config`, XML) read from the repository.

The same schema Deploy serializes, in a different shape: tabs, groups, sort order, mandatory
flags and compositions are all on disk, so this rung is as complete as rung 1. What differs is
where each value lives, and four of those differences are places an implementation goes wrong
quietly. All four come from `umbraco-17-feature-backfill`, which measured them on real
projects:

- **The alias is an attribute on the root `<ContentType>`, not an `<Info>` child.** A reader
  looking for `<Info><Alias>` finds nothing and reports every component as unnamed.
- **`<IsElement>` is always written**, so the kind is a boolean to read — the *opposite* of
  Deploy, where `Permissions.IsElementType` appears only when true. A reader that assumes the
  two formats are symmetric finds no element types on one of them.
- **A property's `Tab Alias` may be a `tab/group` path or a bare alias naming either level.**
  It is resolved against the `<Tabs>` list and that entry's `<Type>` decides the level. One
  project held 235 path-form references and 164 bare ones, of which 114 resolved to a *group*.
  So "no slash means tab" is not a shortcut that is usually right; it is wrong in the majority
  of the bare cases. See `_resolve_owner`.
- **Captions repeat and are never keys.** A "Content" tab routinely holds a "Content" group,
  so every lookup here is on the alias.

Two more things this adapter has to decide that the reference does not spell out.

**A missing data type is not fatal here, unlike under Deploy.** A uSync property names its
editor inline in `<Type>`, so the only thing the data type adds is the option list. A minimal
or partial export that serializes content types and not data types therefore still yields a
correct property table, and refusing it would refuse the common case. Deploy has to refuse the
same gap because there the editor itself is unreachable — the rule is the same ("never report a
field whose type is unknown"), and the two formats put different amounts behind the same
reference. A data type that is *present* but unreadable still raises.

**Files are found by directory name, not by extension.** `.config` is one of the most common
extensions in a .NET repository — `web.config`, `packages.config`, `app.config` — so the walk
looks only inside `ContentTypes/` and `DataTypes/` folders, and confirms each file by its root
element. uSync's filenames are the lowercased alias, so every lookup case-folds.
"""

import json
import os
import xml.etree.ElementTree as ElementTree

from guidelib import GuideError
from guidelib import dossier

RUNG = "usync"

CONFIG_EXTENSION = ".config"

# The two folders of a uSync export this rung reads, matched case-insensitively. uSync writes
# them capitalized; a case-insensitive filesystem or a hand-moved export may not.
CONTENT_TYPE_DIR = "contenttypes"
DATA_TYPE_DIR = "datatypes"

# The root element each file must carry to be the thing this adapter thinks it is. A folder is
# not proof: another tool's file sitting in the same directory is skipped rather than read as a
# content type with everything missing.
CONTENT_TYPE_ELEMENT = "ContentType"
DATA_TYPE_ELEMENT = "DataType"

# `<Tabs>` holds both levels, told apart only by this element.
LEVEL_TAB = "tab"
LEVEL_GROUP = "group"

# The separator in a `tabAlias/groupAlias` path alias.
PATH_SEPARATOR = "/"

# Build output and tooling directories can hold a copy of an export. Reading them would double
# every content type and let a stale copy claim an alias.
SKIP_DIRS = {"bin", "obj", "node_modules", "packages", "TestResults"}


class _Artifact:
    """One parsed file, kept with the path it came from so an error can name it."""

    __slots__ = ("path", "element")

    def __init__(self, path, element):
        self.path = path
        self.element = element


def present(project_root):
    """Whether this project carries a uSync export at all — the adapter's detect probe."""
    for _ in _config_files(project_root, CONTENT_TYPE_DIR):
        return True
    return False


def searched_locations(project_root):
    """The directories read, for an error message that names where it looked."""
    found = sorted({os.path.dirname(p)
                    for p in _config_files(project_root, CONTENT_TYPE_DIR)})
    return found or [os.path.abspath(project_root)]


def extract(project_root, alias, catalog=None):
    """Read one content type and everything it composes into a dossier.

    `catalog` is the same seam Deploy offers, for the same reason: a caller classifying every
    component in the project parses the corpus once instead of once per component. A lone
    `extract` passes nothing and reads only what it needs.
    """
    catalog = catalog or Catalog(project_root)
    artifact = catalog.document(alias)
    if artifact is None:
        raise GuideError(
            "no uSync content type declares the alias '%s' under %s"
            % (alias, ", ".join(searched_locations(project_root))))

    schema = dossier.Schema()
    compositions = []
    _collect(artifact, catalog, schema, compositions, set(), inherited_from=None)

    info = _info(artifact.element)
    return dossier.build(
        rung=RUNG,
        # The alias is the root element's attribute. `<Info>` has no Alias child.
        alias=artifact.element.get("Alias") or alias,
        name=_child(info, "Name"),
        # Always written, so this is a boolean read — not Deploy's truthiness test.
        kind=dossier.KIND_ELEMENT if _flag(_child(info, "IsElement")) else dossier.KIND_DOCUMENT,
        icon=_child(info, "Icon"),
        description=_child(info, "Description"),
        structure_available=True,
        compositions=sorted(set(compositions)),
        tabs=schema.tabs(),
    )


# ---------------------------------------------------------------------------
# Reading the export
# ---------------------------------------------------------------------------

def _config_files(project_root, dirname):
    """Every `*.config` inside a folder of this name, in a stable order.

    The location is searched for rather than configured, per the `paths.md → ## Umbraco`
    slot's fallback: a uSync export is identified by `uSync/*/ContentTypes/*.config`. The
    folder name is the filter because the extension alone would sweep up every `web.config`
    in the repository. A project may hold more than one export folder, so all of them are
    read — a lookup that silently picked the first would depend on directory order.
    """
    for dirpath, dirnames, filenames in os.walk(project_root):
        dirnames[:] = sorted(d for d in dirnames
                             if d not in SKIP_DIRS and not d.startswith("."))
        if os.path.basename(dirpath).lower() != dirname:
            continue
        for name in sorted(filenames):
            if name.lower().endswith(CONFIG_EXTENSION):
                yield os.path.join(dirpath, name)


def _parse(path):
    try:
        return ElementTree.parse(path).getroot()
    except (OSError, ElementTree.ParseError) as exc:
        # Loud, and named. A skipped file is how a component goes missing from a guide with
        # nothing in the output to say so.
        raise GuideError("cannot read uSync configuration %s: %s" % (path, exc))


def _normalize_key(key):
    """Fold a GUID to one spelling, so a dashed and an undashed reference match."""
    return (key or "").strip().strip("{}").replace("-", "").lower()


class Catalog:
    """Every content type and data type in the export, indexed the ways a read needs.

    By key, because that is how a composition names its base and how a property names its data
    type. By alias, because that is what an operator asks for — case-folded, since uSync writes
    filenames in lower case and an operator types the real casing.
    """

    def __init__(self, project_root):
        self.project_root = project_root
        self._documents = {}    # lowercased alias -> _Artifact
        self._by_key = {}       # normalized key -> _Artifact
        self._data_types = {}   # normalized key -> _Artifact
        self._options_cache = {}   # data-type key -> option list, parsed once
        self._loaded = False

    def _load_all(self):
        if self._loaded:
            return
        self._loaded = True
        for path in _config_files(self.project_root, CONTENT_TYPE_DIR):
            root = _parse(path)
            if root.tag != CONTENT_TYPE_ELEMENT:
                continue
            artifact = _Artifact(path, root)
            key = _normalize_key(root.get("Key"))
            if key:
                self._claim(self._by_key, key, artifact, "key")
            alias = root.get("Alias")
            if alias:
                self._claim(self._documents, alias.strip().lower(), artifact, "alias")
        for path in _config_files(self.project_root, DATA_TYPE_DIR):
            root = _parse(path)
            if root.tag != DATA_TYPE_ELEMENT:
                continue
            key = _normalize_key(root.get("Key"))
            if key:
                self._claim(self._data_types, key, _Artifact(path, root), "key")

    @staticmethod
    def _claim(index, key, artifact, what):
        """Index a file, refusing a second claim on the same key.

        Two files declaring one alias is not a preference to resolve — it is a question with no
        correct answer, and answering it by directory-walk order picks whichever sorts first.
        The same hazard Deploy's catalog refuses, reached two ways here: a second export folder
        beside a live one, and two files whose case-folded names collide on a case-sensitive
        filesystem (`AlertBanner.config` beside `alertbanner.config`). Both are legitimate
        input that happens to be ambiguous, which is why SKIP_DIRS is not enough on its own —
        that prunes build output, the one duplication worth pruning silently.
        """
        first = index.get(key)
        if first is None:
            index[key] = artifact
            return
        if first is artifact or first.path == artifact.path:
            return
        raise GuideError(
            "two uSync files declare the same %s '%s' — the export is ambiguous:\n"
            "  %s\n  %s\n"
            "Remove or exclude whichever is stale; reading either one silently would make "
            "the result depend on directory order."
            % (what, key, first.path, artifact.path))

    def document(self, alias):
        """The content type for an alias, matched case-insensitively."""
        self._load_all()
        return self._documents.get((alias or "").strip().lower())

    def by_key(self, key):
        self._load_all()
        return self._by_key.get(_normalize_key(key))

    def options(self, definition_key):
        """A property's option list, resolved through the data type it points at.

        An absent data type yields no options rather than an error, because a uSync property
        already names its editor inline: the option list is the only thing the reference adds,
        and `options: []` is the dossier's honest statement that none was recorded. A data type
        that is present but whose payload cannot be read does raise — a file that exists and
        cannot be understood is a different thing from a file that was never exported.

        Parsed once per data type, not once per property that points at one. Deploy gets this
        for free — its configuration is already a dict inside the artifact JSON — while here
        the payload is a JSON string embedded in XML, so every reference would otherwise
        re-parse it. Measured on a 170-type corpus with 1020 references across 40 data types,
        the redundant parsing was 9ms of a 60ms whole-project read; the fan-out grows with
        the corpus, and the inventory determiner reads every component.
        """
        self._load_all()
        key = _normalize_key(definition_key)
        if key in self._options_cache:
            return self._options_cache[key]
        options = self._read_options(key)
        self._options_cache[key] = options
        return options

    def _read_options(self, key):
        artifact = self._data_types.get(key)
        if artifact is None:
            return []
        payload = artifact.element.findtext("Config")
        if payload is None or not payload.strip():
            return []
        try:
            config = json.loads(payload)
        except ValueError as exc:
            raise GuideError(
                "the <Config> payload of the data type in %s is not readable JSON: %s"
                % (artifact.path, exc))
        return dossier.options_from_config(config)


# ---------------------------------------------------------------------------
# Walking a content type and its compositions
# ---------------------------------------------------------------------------

def _collect(artifact, catalog, schema, compositions, seen, inherited_from):
    """Add one content type's structure, then recurse into what it composes.

    Own structure first, so `Schema`'s first-wins declaration gives the nearest type's caption
    and sort order for a tab two types both name. `seen` guards the diamond: two compositions
    sharing a base would otherwise contribute its properties twice, and a duplicate property
    alias is a hard error one level down.
    """
    element = artifact.element
    key = _normalize_key(element.get("Key")) \
        or "alias:" + (element.get("Alias") or "").strip().lower()
    if key in seen:
        return
    seen.add(key)

    _collect_structure(artifact, catalog, schema, inherited_from)

    for composition in element.findall("Info/Compositions/Composition"):
        composed = catalog.by_key(composition.get("Key"))
        named = _text(composition.text)
        if composed is None and named:
            # uSync writes the alias as the element's text and the key as its attribute.
            # Either one identifies the base, so a key that resolves to nothing while the
            # alias resolves is read as a re-created type rather than as a missing one.
            composed = catalog.document(named)
        if composed is None:
            raise GuideError(
                "%s composes %s, which no uSync file under %s declares — the export is "
                "partial"
                % (element.get("Alias") or artifact.path,
                   named or composition.get("Key"),
                   ", ".join(searched_locations(catalog.project_root))))
        composed_alias = composed.element.get("Alias") or named
        compositions.append(composed_alias)
        _collect(composed, catalog, schema, compositions, seen,
                 inherited_from=composed_alias)


def _collect_structure(artifact, catalog, schema, inherited_from):
    """Declare an artifact's tabs and groups, then file its properties under them."""
    element = artifact.element
    entries = _tab_entries(element)

    for entry in entries:
        if entry["level"] == LEVEL_GROUP:
            # A group's alias is the `tabAlias/groupAlias` path. A bare one means a group with
            # no tab — the pre-tabs layout — which lands in the unnamed bucket.
            head, sep, _tail = entry["alias"].partition(PATH_SEPARATOR)
            schema.declare_group(entry["alias"], entry["caption"], entry["sortOrder"],
                                 head if sep else None)
        else:
            schema.declare_tab(entry["alias"], entry["caption"], entry["sortOrder"])

    for prop in element.findall("GenericProperties/GenericProperty"):
        owner = _resolve_owner(_owner_alias(prop), entries, artifact.path,
                               _text(prop.findtext("Alias")))
        schema.add_property(_property(prop, catalog, inherited_from), **owner)


def _tab_entries(element):
    """The `<Tabs>` list, in declared order, with each entry's level decided once."""
    entries = []
    for tab in element.findall("Tabs/Tab"):
        alias = _text(tab.findtext("Alias"))
        entries.append({
            "alias": alias,
            # The caption is display text and repeats freely — never a key.
            "caption": _text(tab.findtext("Caption")),
            "sortOrder": _int(tab.findtext("SortOrder")),
            "level": _level(_text(tab.findtext("Type")), alias),
        })
    return entries


def _level(declared, alias):
    """Tab or group, from the entry's own `<Type>`.

    The fallback on the alias shape is for an entry that declares no recognizable type at all.
    That is the inference the reference forbids for a *property's* reference — where the
    authoritative answer is one lookup away — used here only where nothing authoritative
    exists, and in preference to dropping the entry.
    """
    value = declared.strip().lower()
    if value == LEVEL_GROUP:
        return LEVEL_GROUP
    if value == LEVEL_TAB:
        return LEVEL_TAB
    return LEVEL_GROUP if PATH_SEPARATOR in alias else LEVEL_TAB


def _owner_alias(prop):
    """The `<Tab Alias="...">` a property names as its owner, or the empty string."""
    tab = prop.find("Tab")
    if tab is None:
        return ""
    return (tab.get("Alias") or "").strip()


def _resolve_owner(owner_alias, entries, path, property_alias):
    """Which tab or group a property's `Tab Alias` names — resolved, never inferred.

    The alias may be a `tab/group` path or a bare alias naming *either* level, so the level
    comes from the matched `<Tabs>` entry's own `<Type>`. An exact alias match wins; failing
    that, a bare alias matches an entry whose last path segment it is, which is how a bare
    `social` reaches the group declared as `seo/social`.

    Returns the keyword argument `Schema.add_property` files the property under.
    """
    if not owner_alias:
        # No owner at all: the property sits on the type with no tab and no group.
        return {}

    matches = [e for e in entries if e["alias"] == owner_alias]
    if not matches:
        matches = [e for e in entries
                   if e["alias"].rpartition(PATH_SEPARATOR)[2] == owner_alias]

    if len(matches) > 1:
        raise GuideError(
            "the property '%s' in %s names its owner as '%s', which matches %d entries in "
            "<Tabs> (%s) — the reference is ambiguous, and picking one would put the field "
            "under a heading nobody chose"
            % (property_alias, path, owner_alias, len(matches),
               ", ".join(e["alias"] for e in matches)))

    if not matches:
        # Named an owner no `<Tabs>` entry declares — a partial export, or a tab a composition
        # was expected to declare. Keep the property: `Schema` stands up a placeholder named
        # after the alias, so the gap is visible in the output rather than costing a field.
        if PATH_SEPARATOR in owner_alias:
            return {"group_alias": owner_alias}
        return {"tab_alias": owner_alias}

    entry = matches[0]
    if entry["level"] == LEVEL_GROUP:
        return {"group_alias": entry["alias"]}
    return {"tab_alias": entry["alias"]}


def _property(prop, catalog, inherited_from):
    return dossier.make_property(
        alias=_text(prop.findtext("Alias")),
        name=_text(prop.findtext("Name")),
        # Already the editor alias — no data type lookup needed to name the editor.
        editor=_text(prop.findtext("Type")),
        description=_text(prop.findtext("Description")),
        mandatory=_flag(_text(prop.findtext("Mandatory"))),
        sort_order=_int(prop.findtext("SortOrder")),
        options=catalog.options(prop.findtext("Definition")),
        inherited_from=inherited_from,
    )


# ---------------------------------------------------------------------------
# Reading values out of XML
# ---------------------------------------------------------------------------

def _info(element):
    """The `<Info>` block, or an empty stand-in so every read below is uniform."""
    info = element.find("Info")
    return info if info is not None else ElementTree.Element("Info")


def _child(element, name):
    return _text(element.findtext(name))


def _text(value):
    """One child's text, normalized — absent, empty and whitespace-only all become "".

    Surrounding whitespace is stripped because in XML it belongs to the serializer rather than
    to the project: a pretty-printed `<Name>\\n  Alert Banner\\n</Name>` says the same thing as
    the inline form, and the same thing as Deploy's JSON string. Keeping it would make the
    cross-format signature depend on how a file happened to be indented.
    """
    return dossier.text(value).strip()


def _flag(value):
    """A uSync boolean. Written as `true`/`false`; `1` accepted as the same claim."""
    return value.strip().lower() in ("true", "1")


def _int(value):
    try:
        return int(_text(value))
    except (TypeError, ValueError):
        return 0
