"""The dossier — the one shape every adapter produces, and the signature over it.

A dossier is the format-blind description of a single component: the alias, the kind, and
the tab/group/property tree an editor sees in the backoffice. Adapters differ in what they
read; they do not differ in what they emit. Everything downstream — the signature, the
inventory, the audit, the change plan — consumes this and never the on-disk format, which is
what keeps a new rung from rippling through every stage.

Three rules the format exists to enforce:

- **Normalized on the alias.** Deploy names a reference with a UDI and uSync with a GUID or
  an alias. Both resolve to the alias here, at the point of reading, so nothing downstream
  has to know which format it came from.
- **Absence is stated, not implied.** An optional property says `"mandatory": false` rather
  than omitting the key, and an uninherited one says `"inheritedFrom": null`. A reader can
  then tell "optional" from "not recorded" — the distinction that matters at the lowest rung,
  where required flags genuinely are not available.
- **Order is derived, never incidental.** Tabs, groups and properties are sorted by the
  project's own sort order, so two adapters reading the same component in different file
  orders still agree, and the signature below is stable.

## The source signature

`sourceSignature` is a sha256 over the dossier minus the fields that describe *how* it was
read — `rung` and `dossierVersion` — and minus itself. Everything else is schema-bearing:
the alias, the kind, the names, the descriptions, the editors, the mandatory flags, the sort
orders, the option lists and their default markers, the compositions, and whether structure
was available at all. Two adapters reading the same component must therefore print the same
signature; anything format-specific leaking into the canonical form breaks that equality.

The value carries a `sha256:` prefix because it is stored in the CMS against a guide page and
compared on later runs. A stored value that names its own algorithm can be superseded without
a migration that cannot tell old from new.
"""

import hashlib
import json

from . import GuideError

# Bumped when the shape below changes in a way a stored dossier could not survive. It is
# excluded from the signature: a format revision is not a schema change in the project.
DOSSIER_VERSION = 1

# Fields excluded from the canonical subset the signature covers. `rung` and dossierVersion
# describe the read, not the component; sourceSignature cannot cover itself.
SIGNATURE_EXCLUDED = ("dossierVersion", "rung", "sourceSignature")

SIGNATURE_PREFIX = "sha256:"

# The unnamed bucket. Umbraco lets a property sit on a content type with no tab and no group
# (Deploy puts these in a root-level `PropertyTypes`), and lets a group sit outside any tab.
# The dossier's tree is exactly two levels deep, so those properties need somewhere real to
# live: a tab whose alias and name are empty, which a renderer can recognize and present
# without a heading. It is emitted only when something is actually in it.
UNGROUPED_TAB_ALIAS = ""
UNGROUPED_TAB_NAME = ""
UNGROUPED_TAB_SORT_ORDER = 0

# The keys a data type's configuration uses for its option list and its default marker.
# Both on-disk formats carry the *same* JSON payload here -- Deploy in an artifact's
# `Configuration` object, uSync in a `<Config>` CDATA block -- so the reading of it belongs
# in one place rather than once per adapter. Two adapters normalizing an option list
# separately is the most intricate thing they would each have to get right, and the
# signature's equality across formats is exactly what a divergence there would break.
#
# `default` is a BORROWED key: Umbraco's toggle configuration carries one, and the fixtures
# use it to state which option is the default. A stock dropdown export has not been confirmed
# to carry it -- of the demo project's data types, 11 carry `items[]` and none carries
# `default` -- so it is read as optional. Absent means no option is marked, never "the first".
CONFIG_ITEMS = "items"
CONFIG_DEFAULT = "default"

KIND_ELEMENT = "element"
KIND_DOCUMENT = "document"


def make_option(value, default=False):
    """One entry in a property's option list, with the default marked.

    The default marker is a separate boolean rather than an index or a bare value, because at
    some rungs the option list is readable and the default is not. `False` on every option
    then means "no default recorded", which is the honest reading of a data type whose
    configuration does not carry one.
    """
    return {"value": value, "default": bool(default)}


def make_property(alias, name, editor, description="", mandatory=False,
                  sort_order=0, options=None, inherited_from=None):
    """One editable field, as an editor meets it."""
    return {
        "alias": alias,
        "name": name,
        "description": description,
        "editor": editor,
        "mandatory": bool(mandatory),
        "sortOrder": int(sort_order),
        "options": list(options or []),
        "inheritedFrom": inherited_from,
    }


def text(value):
    """Normalize an absent or null field to the empty string.

    Both formats omit what has nothing to say -- Deploy leaves `Description` and `Icon` out
    of the JSON, uSync writes an empty element. A guide renderer wants one type back, not
    "string or missing"; the honest distinction the dossier does preserve is `mandatory`,
    where absence and false mean different things to a reader.

    **This does not strip whitespace, and the uSync adapter does.** That asymmetry is
    deliberate rather than an oversight: pretty-printed XML puts newlines and indentation
    inside every element, so an unstripped XML read would differ from its JSON twin on
    formatting alone and the two adapters would hash the same component differently. JSON
    strings carry no serializer-added whitespace, so stripping there would instead destroy a
    value someone typed. A future rung reading a third format has to make the same call: strip
    where the serializer adds whitespace, never where an author could have.
    """
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def options_from_config(config):
    """Option values in declared order, with the default marked if the config names one.

    Declared order is kept rather than sorted: an option list is a sequence an editor sees in
    the backoffice, and reordering it would misdescribe the field. Shared by every adapter,
    because the payload is the same JSON whatever envelope it arrived in.
    """
    if not isinstance(config, dict):
        return []
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
    marked = None if default is None else text(default)
    return [make_option(v, marked is not None and v == marked) for v in values if v != ""]


def _option_value(item):
    if isinstance(item, dict):
        for key in ("value", "Value", "name", "Name"):
            if key in item:
                return text(item[key])
        return ""
    return text(item)


def _key_order(key):
    try:
        return (0, int(key), "")
    except (TypeError, ValueError):
        return (1, 0, str(key))


def _sort_key(entry):
    """The project's own sort order, with the alias breaking ties.

    Sort order alone is not a total order — Umbraco happily gives two groups the same value —
    and an unstable order would change the signature between two reads of one project.
    """
    return (entry["sortOrder"], entry["alias"])


class Schema:
    """Tabs, groups and properties collected from a content type and its compositions.

    Adapters hand this whatever they find, in whatever order the files happen to be read.
    It owns the two things every adapter would otherwise reimplement: merging a composition's
    structure into the composed type's, and putting the result in a stable order.

    Declarations are first-wins, so an adapter that adds the requested type before recursing
    into its compositions gets the nearest declaration's caption and sort order — which is
    what the backoffice shows when a type and a composition name the same tab.
    """

    def __init__(self):
        self._tabs = {}          # tab alias -> tab dict
        self._group_tabs = {}    # group alias -> owning tab alias
        self._groups = {}        # group alias -> group dict
        self._property_paths = {}  # property alias -> the path it was first filed under

    # --- declarations ---------------------------------------------------------

    def declare_tab(self, alias, name, sort_order):
        if alias not in self._tabs:
            self._tabs[alias] = {
                "alias": alias,
                "name": name,
                "sortOrder": int(sort_order),
                "properties": [],
                "groups": [],
            }
        return alias

    def declare_group(self, alias, name, sort_order, tab_alias=None):
        """Declare a group, optionally inside a tab.

        `tab_alias` of None means the group sits outside any tab — the pre-tabs layout, still
        present in real projects — and it lands in the unnamed bucket rather than being
        promoted to a tab it was never given.
        """
        if alias not in self._groups:
            self._groups[alias] = {
                "alias": alias,
                "name": name,
                "sortOrder": int(sort_order),
                "properties": [],
            }
            self._group_tabs[alias] = tab_alias
        return alias

    # --- properties -----------------------------------------------------------

    def add_property(self, prop, tab_alias=None, group_alias=None):
        """File one property under a group, a tab, or the unnamed bucket.

        A group alias wins over a tab alias when both are given, because the group is the
        narrower statement of where the property sits.

        A property alias may appear once. The backoffice will not let a type declare an alias
        one of its compositions already declares, so a second one is not a shape to merge --
        it is a contradiction, and the two entries would sit side by side in the tables as
        though an editor filled in both. It is also the one input that could make the
        signature depend on the order compositions happened to be read: two entries with one
        alias and one sort order have no canonical order between them.
        """
        alias = prop.get("alias")
        where = group_alias or tab_alias or ""
        if alias in self._property_paths:
            raise GuideError(
                "the property alias '%s' is declared twice in this component's schema, "
                "under '%s' and '%s' — one of the two declarations has to go, and choosing "
                "for you would put the same field in the tables twice"
                % (alias, self._property_paths[alias], where))
        self._property_paths[alias] = where
        if group_alias is not None:
            if group_alias not in self._groups:
                # A property naming a group nobody declared. Keep the property rather than
                # dropping it: an under-described component is recoverable, a silently
                # missing field is not.
                self.declare_group(group_alias, group_alias, 0,
                                   self._tab_of_path(group_alias))
            self._groups[group_alias]["properties"].append(prop)
            return
        self._tab(tab_alias)["properties"].append(prop)

    # --- assembly -------------------------------------------------------------

    def tabs(self):
        """The assembled two-level tree, in sort order, ready to serialize."""
        for tab in self._tabs.values():
            tab["groups"] = []
        for alias, group in self._groups.items():
            owner = self._tab(self._group_tabs.get(alias))
            owner["groups"].append(group)

        assembled = []
        for tab in sorted(self._tabs.values(), key=_sort_key):
            # An empty tab is real structure: the backoffice shows it, and a composition may
            # fill it. Only the unnamed bucket is suppressed when empty, since it is a
            # rendering device rather than something the project declared.
            if tab["alias"] == UNGROUPED_TAB_ALIAS and not (tab["properties"] or tab["groups"]):
                continue
            tab["properties"] = sorted(tab["properties"], key=_sort_key)
            tab["groups"] = [
                dict(g, properties=sorted(g["properties"], key=_sort_key))
                for g in sorted(tab["groups"], key=_sort_key)
            ]
            assembled.append(tab)
        return assembled

    # --- internals ------------------------------------------------------------

    @staticmethod
    def _tab_of_path(group_alias):
        """The tab half of a `tab/group` path alias, or None for a bare one."""
        head, sep, _ = group_alias.partition("/")
        return head if sep else None

    def _tab(self, alias):
        """The tab with this alias, creating the unnamed bucket or a placeholder as needed."""
        if alias is None:
            alias = UNGROUPED_TAB_ALIAS
            if alias not in self._tabs:
                self.declare_tab(alias, UNGROUPED_TAB_NAME, UNGROUPED_TAB_SORT_ORDER)
            return self._tabs[alias]
        if alias not in self._tabs:
            # A group's path named a tab no artifact declared — a partial export, or a tab
            # declared by a composition that was not exported. Stand one up so the group is
            # still reported, named after the alias so the gap is visible.
            self.declare_tab(alias, alias, 0)
        return self._tabs[alias]


def count_properties(entry):
    """How many editable fields a dossier describes, across both levels of the tree.

    Zero is a real answer, not a failure. Two shapes with no fields were found among the demo
    project's 68 document types -- a taxonomy-style node carrying only a name, and a type
    declaring one empty tab for a composition to fill -- so a rule that read an empty property
    list as a broken export would refuse real components. What that rule wants is
    resolvability, not thinness, and every detectable partial export already raises before a
    dossier is built. guide.py carries the full reasoning and reports the count.
    """
    total = 0
    for tab in entry.get("tabs") or []:
        total += len(tab.get("properties") or [])
        for group in tab.get("groups") or []:
            total += len(group.get("properties") or [])
    return total


def canonical(entry):
    """The schema-bearing subset the signature covers."""
    return {k: v for k, v in entry.items() if k not in SIGNATURE_EXCLUDED}


def signature(entry):
    """A stable hash over the canonical subset.

    `sort_keys` makes the hash independent of the field order this module happens to emit, so
    reordering the serialization for readability does not invalidate every stored signature.
    """
    payload = json.dumps(canonical(entry), sort_keys=True,
                         separators=(",", ":"), ensure_ascii=False)
    return SIGNATURE_PREFIX + hashlib.sha256(payload.encode("utf-8")).hexdigest()


def build(rung, alias, name, kind, icon, description,
          structure_available, compositions, tabs):
    """Assemble a dossier and sign it. Key order here is the serialized key order."""
    entry = {
        "dossierVersion": DOSSIER_VERSION,
        "rung": rung,
        "alias": alias,
        "name": name,
        "kind": kind,
        "icon": icon,
        "description": description,
        "structureAvailable": bool(structure_available),
        "compositions": list(compositions),
        "tabs": list(tabs),
    }
    entry["sourceSignature"] = signature(entry)
    return entry


def render(entry):
    """Serialize for stdout: two-space indent, a space after each colon, no trailing newline.

    `ensure_ascii` is left at its default so the output is pure ASCII. A real project's
    descriptions carry curly quotes and accented characters, and a consumer's stdout encoding
    is not something a shipped script gets to assume.
    """
    return json.dumps(entry, indent=2)
