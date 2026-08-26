"""Rung 1 — Umbraco Deploy artifacts (`*.uda`, JSON) read from the repository.

The highest-fidelity rung available without a running instance: Deploy serializes the whole
content type, so tabs, groups, sort order, mandatory flags, compositions and data-type
configuration are all on disk.

The mapping comes from `umbraco-17-feature-backfill`, which was verified against real Deploy
projects. Three of its rules are the ones an implementation gets wrong:

- **The kind is a truthiness test, not a field.** `Permissions.IsElementType` is emitted only
  when true, so a reader that treats it as a boolean it can read and trust finds no element
  types at all on a project full of blocks.
- **`"Type": 1` marks a tab.** A group without `Type` is a group, and its `Alias` is the
  `tabAlias/groupAlias` path naming its owner.
- **Compositions carry properties.** `CompositionContentTypes` holds UDIs, resolved
  recursively, and every property they contribute is marked with the alias of the type that
  declared it — so a guide can say which fields are inherited rather than presenting a
  composed type's fields as its own.

Two more things this adapter has to do that the reference does not spell out. There is no
`element-type__*.uda`, so aliases are found by reading artifacts rather than by filename. And
a property's editor is reachable only by resolving its `DataType` UDI to the data-type
artifact, which is also where an option list and its default marker live.
"""

import json
import os

from guidelib import GuideError
from guidelib import dossier

RUNG = "deploy"

ARTIFACT_EXTENSION = ".uda"

# `__type` is the reliable discriminator: the filename prefix set is open, and packages
# contribute their own prefixes. Matched as a substring of the fully-qualified type name.
TYPE_DOCUMENT = "DocumentTypeArtifact"
TYPE_DATA = "DataTypeArtifact"

# Build output and tooling directories can hold copies of a revision folder. Reading them
# would double every artifact and let a stale copy win a lookup.
SKIP_DIRS = {"bin", "obj", "node_modules", "packages", "TestResults"}

# The key a data type's configuration uses for its option list. Both the flexible dropdown
# and the list editors use it.
CONFIG_ITEMS = "items"

# `Configuration.default` is a BORROWED key: Umbraco's toggle configuration carries one, and
# the fixtures use it to state which option is the default. A stock dropdown export has not
# been confirmed to carry it, so it is read as optional — absent means no option is marked,
# never "the first one".
CONFIG_DEFAULT = "default"


def present(project_root):
    """Whether this project carries Deploy artifacts at all — the adapter's detect probe."""
    for _ in _artifact_files(project_root):
        return True
    return False


def searched_locations(project_root):
    """The directories artifacts were found in, for an error message that names where it looked."""
    found = sorted({os.path.dirname(p) for p in _artifact_files(project_root)})
    return found or [os.path.abspath(project_root)]


def extract(project_root, alias, catalog=None):
    """Read one content type and everything it composes into a dossier.

    `catalog` lets a caller reading several components share one parsed corpus. A Catalog
    parses the project once per instance, so building a fresh one per component re-walks and
    re-parses everything unchanged: measured at 3.03s across one project's 68 content types
    against 0.045s sharing a single instance. The inventory determiner classifies every
    component in the project, so it is the caller that needs this; a lone `extract` passes
    nothing and behaves exactly as before.
    """
    catalog = catalog or Catalog(project_root)
    artifact = catalog.document(alias)
    if artifact is None:
        raise GuideError(
            "no Deploy artifact declares the alias '%s' under %s"
            % (alias, ", ".join(searched_locations(project_root))))

    schema = dossier.Schema()
    compositions = []
    _collect(artifact, catalog, schema, compositions, set(), inherited_from=None)

    permissions = artifact.get("Permissions") or {}
    return dossier.build(
        rung=RUNG,
        alias=artifact.get("Alias") or alias,
        name=_text(artifact.get("Name")),
        # Emitted only when true, so truthiness is the whole test.
        kind=dossier.KIND_ELEMENT if permissions.get("IsElementType") else dossier.KIND_DOCUMENT,
        icon=_text(artifact.get("Icon")),
        description=_text(artifact.get("Description")),
        structure_available=True,
        compositions=sorted(set(compositions)),
        tabs=schema.tabs(),
    )


# ---------------------------------------------------------------------------
# Reading the revision directory
# ---------------------------------------------------------------------------

def _artifact_files(project_root):
    """Every `*.uda` under the project, in a stable order.

    The location is searched for rather than configured, per the `paths.md → ## Umbraco`
    slot's fallback: the Deploy revision directory is identified by its `*.uda` files. A
    project may hold more than one revision folder, so all of them are read — a lookup that
    silently picked the first would depend on directory order.
    """
    for dirpath, dirnames, filenames in os.walk(project_root):
        dirnames[:] = sorted(d for d in dirnames
                             if d not in SKIP_DIRS and not d.startswith("."))
        for name in sorted(filenames):
            if name.endswith(ARTIFACT_EXTENSION):
                yield os.path.join(dirpath, name)


def _load(path):
    try:
        with open(path, "r", encoding="utf-8-sig") as handle:
            return json.load(handle)
    except (OSError, ValueError) as exc:
        # Loud, and named. A skipped artifact is how a component goes missing from a guide
        # with nothing in the output to say so.
        raise GuideError("cannot read Deploy artifact %s: %s" % (path, exc))


def _normalize_udi(udi):
    """Fold the two spellings of the same reference.

    Deploy writes `umb://document-type/<guid-with-dashes-stripped>`; other sources write the
    canonical dashed form. Only the identifier is folded — the entity-type half of the UDI
    contains a dash of its own.
    """
    text = (udi or "").strip().lower()
    head, sep, tail = text.rpartition("/")
    if not sep:
        return text
    return head + "/" + tail.replace("-", "")


class Catalog:
    """Every artifact in the project, indexed the two ways a read needs.

    By UDI, because that is how a content type names a composition and how a property names
    its data type. By alias, because that is what an operator asks for. Both indexes cover
    every artifact regardless of `__type`, since a reference may point at a type this adapter
    does not otherwise care about.
    """

    def __init__(self, project_root):
        self.project_root = project_root
        self._by_udi = {}
        self._documents = {}      # lowercased alias -> artifact
        self._loaded = False

    def _load_all(self):
        if self._loaded:
            return
        self._loaded = True
        for path in _artifact_files(self.project_root):
            artifact = _load(path)
            if not isinstance(artifact, dict):
                raise GuideError("Deploy artifact %s is not a JSON object" % path)
            artifact["__path"] = path
            udi = _normalize_udi(artifact.get("Udi"))
            if udi:
                self._claim(self._by_udi, udi, artifact, "UDI")
            alias = artifact.get("Alias")
            if alias and TYPE_DOCUMENT in (artifact.get("__type") or ""):
                self._claim(self._documents, alias.lower(), artifact, "alias")

    @staticmethod
    def _claim(index, key, artifact, what):
        """Index an artifact, refusing a second claim on the same key.

        Two artifacts declaring one alias is not a preference to resolve — it is a question
        with no correct answer, and answering it by directory-walk order picks whichever
        sorts first. That reliably produced the emptier of the two in testing: a stale
        revision folder holding a property-less copy silently won over the real schema, and
        the dossier came out with no tabs, `structureAvailable` true, and exit 0. The
        silent-empty read is what this whole ladder's fail-loudly rule exists to prevent, so
        it fails here instead, naming both files so a human can delete the right one.

        This is why SKIP_DIRS is not enough on its own. It prunes build output, which is the
        common duplication and the one worth pruning silently; a second revision folder is
        legitimate input that happens to be ambiguous.
        """
        first = index.get(key)
        if first is None:
            index[key] = artifact
            return
        if first is artifact or first.get("__path") == artifact.get("__path"):
            return
        raise GuideError(
            "two Deploy artifacts declare the same %s '%s' — the export is ambiguous:\n"
            "  %s\n  %s\n"
            "Remove or exclude whichever is stale; reading either one silently would make "
            "the result depend on directory order."
            % (what, key, first.get("__path"), artifact.get("__path")))

    def document(self, alias):
        """The document-type artifact for an alias, matched case-insensitively."""
        self._load_all()
        return self._documents.get((alias or "").lower())

    def by_udi(self, udi):
        self._load_all()
        return self._by_udi.get(_normalize_udi(udi))

    def editor_and_options(self, udi):
        """A property's editor alias and option list, resolved through its data type."""
        self._load_all()
        artifact = self.by_udi(udi)
        if artifact is None or TYPE_DATA not in (artifact.get("__type") or ""):
            # A partial export, and the same condition a dangling composition raises on.
            # An earlier version degraded here instead, returning an empty editor — but that
            # leaves `structureAvailable` claiming true while a field's type is unknown, and
            # a guide's property table exists to say what an editor types into a field. The
            # two readings of "partial export" have to agree, or the fail-loudly rule holds
            # only wherever it was remembered.
            raise GuideError(
                "the data type %s, used by a property, is not among the exported artifacts "
                "under %s — the export is partial"
                % (udi, ", ".join(searched_locations(self.project_root))))
        config = artifact.get("Configuration")
        if not isinstance(config, dict):
            config = {}
        return _text(artifact.get("EditorAlias")), _options(config)


def _options(config):
    """Option values in declared order, with the default marked if the config names one.

    Declared order is kept rather than sorted: an option list is a sequence an editor sees in
    the backoffice, and reordering it would misdescribe the field.
    """
    items = config.get(CONFIG_ITEMS)
    values = []
    if isinstance(items, list):
        for item in items:
            values.append(_option_value(item))
    elif isinstance(items, dict):
        # The older keyed shape, `{"0": {...}, "1": {...}}`. Sorted numerically where the
        # keys are numbers, so `"10"` does not sort before `"2"`.
        for key in sorted(items, key=_key_order):
            values.append(_option_value(items[key]))
    else:
        return []

    default = config.get(CONFIG_DEFAULT)
    marked = None if default is None else _text(default)
    return [dossier.make_option(v, marked is not None and v == marked) for v in values
            if v != ""]


def _option_value(item):
    if isinstance(item, dict):
        for key in ("value", "Value", "name", "Name"):
            if key in item:
                return _text(item[key])
        return ""
    return _text(item)


def _key_order(key):
    try:
        return (0, int(key), "")
    except (TypeError, ValueError):
        return (1, 0, str(key))


def _text(value):
    """Normalize an absent or null field to the empty string.

    Deploy omits `Description` and `Icon` when they have nothing to say. A guide renderer
    wants one type back, not "string or missing"; the honest distinction the dossier does
    preserve is `mandatory`, where absence and false mean different things to a reader.
    """
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


# ---------------------------------------------------------------------------
# Walking a content type and its compositions
# ---------------------------------------------------------------------------

def _collect(artifact, catalog, schema, compositions, seen, inherited_from):
    """Add one content type's structure, then recurse into what it composes.

    Own structure first, so the first-wins declaration in `Schema` gives the nearest type's
    caption and sort order for a tab two types both name. `seen` guards the diamond: two
    compositions sharing a base would otherwise contribute its properties twice.
    """
    # Identity for the diamond guard. Deploy always writes `Udi`, but falling back to the
    # alias keeps a missing one from making every subsequent artifact look already-visited.
    key = _normalize_udi(artifact.get("Udi")) or "alias:" + _text(artifact.get("Alias"))
    if key in seen:
        return
    seen.add(key)

    _collect_groups(artifact, catalog, schema, inherited_from)

    for composition_udi in artifact.get("CompositionContentTypes") or []:
        composed = catalog.by_udi(composition_udi)
        if composed is None:
            raise GuideError(
                "%s composes %s, which no artifact under %s declares — the export is partial"
                % (artifact.get("Alias") or artifact.get("__path"), composition_udi,
                   ", ".join(searched_locations(catalog.project_root))))
        composed_alias = composed.get("Alias") or ""
        compositions.append(composed_alias)
        _collect(composed, catalog, schema, compositions, seen,
                 inherited_from=composed_alias)


def _collect_groups(artifact, catalog, schema, inherited_from):
    """Declare an artifact's tabs and groups, and file its properties under them."""
    for group in artifact.get("PropertyGroups") or []:
        alias = _text(group.get("Alias"))
        name = _text(group.get("Name"))
        sort_order = _int(group.get("SortOrder"))

        if group.get("Type") == 1:
            schema.declare_tab(alias, name, sort_order)
            owner = {"tab_alias": alias}
        else:
            # A group's alias is the `tabAlias/groupAlias` path. A bare alias means a group
            # with no tab — the pre-tabs layout — which lands in the unnamed bucket.
            head, sep, _tail = alias.partition("/")
            schema.declare_group(alias, name, sort_order, head if sep else None)
            owner = {"group_alias": alias}

        for property_type in group.get("PropertyTypes") or []:
            schema.add_property(_property(property_type, catalog, inherited_from), **owner)

    # Root-level `PropertyTypes` — a property on the content type belonging to no group at
    # all. Empty on all 68 artifacts of the demo project, but the key is real, so it is read
    # and merged as the unnamed bucket rather than assumed away.
    for property_type in artifact.get("PropertyTypes") or []:
        schema.add_property(_property(property_type, catalog, inherited_from))


def _property(property_type, catalog, inherited_from):
    editor, options = catalog.editor_and_options(property_type.get("DataType"))
    return dossier.make_property(
        alias=_text(property_type.get("Alias")),
        name=_text(property_type.get("Name")),
        editor=editor,
        description=_text(property_type.get("Description")),
        # Emitted only when it has something to say, so absence normalizes to an explicit
        # false — the dossier states "optional" rather than "not recorded".
        mandatory=bool(property_type.get("Mandatory")),
        sort_order=_int(property_type.get("SortOrder")),
        options=options,
        inherited_from=inherited_from,
    )


def _int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0
