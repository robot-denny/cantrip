"""Rung 4 — committed generated model classes (`*.generated.cs`, C#) read from the repository.

The lowest rung, and the only one some projects have. ModelsBuilder in `SourceCodeManual` mode
writes one C# class per content type into the repository, so a project that neither runs Deploy
nor commits its uSync export still carries a readable description of every component. Refusing
to read it would mean no guides at all for that project, which is the wrong answer to a source
that is thin rather than untrustworthy.

`umbraco-17-feature-backfill` is why this rung exists at all: it names the generated model as
the **primary** signal for what a property is, ahead of reverse-mapping a data-type identifier,
because a strongly-typed `IHtmlEncodedString` or `MediaWithCrops` says what an editor types into
a field more directly than a UDI does. What it cannot say is where the field sits or whether it
is required, and this module's job is to be exact about that difference.

## What this rung genuinely cannot report, and why the dossier says so out loud

A generated model carries properties and nothing about the screen they appear on. There are no
tabs, no groups, no sort order, no required flags, no option lists, no icon, and no component
description — the class summary carries the display name and stops. So the dossier says
`structureAvailable: false` and carries `structureGaps`, a per-field statement of what is
missing (see GAPS below).

**Stating it is not decoration.** `"options": []` is the same three characters whether the
component offers no options or the source could not report them, and a reader who cannot tell
those apart will eventually publish a guide claiming a dropdown has no choices. Absence cannot
carry that distinction; only a positive statement can.

Every property lands in the dossier's one unnamed bucket, which is exactly what that bucket is
for. It is not a fabricated tab: the tree is two levels deep by contract, so a property with no
known tab needs somewhere real to live, and a renderer that recognizes the empty alias presents
it without a heading.

## The thinness note and the gap list are different claims

guide.py notes a component that "declares no editable properties". That note does **not** fire
here merely because the rung is thin: the flattened properties are in the unnamed bucket, so
`dossier.count_properties` counts them and the note stays silent. It fires at this rung under
exactly the condition it fires at the others — a component that really has no fields, which is
a fact about the component. The gap list is a fact about the *source*. Neither restates the
other, and a component with five fields read from a model produces the gap list alone.

## The five things a parser gets wrong

Measured against Umbraco.ModelsBuilder.Embedded v17.5.3 output as committed in two real
projects (78 model files in one, 182 in the other, 342 model classes between them):

- **The alias is `[PublishedModel("...")]`, never the class or file name.** The generator
  mangles casing: an alias of `sEOControls` becomes a class `SEocontrols` in a file
  `SEocontrols.generated.cs`. A reader deriving the alias from either is wrong on every alias
  whose first two letters are capitals, and right often enough elsewhere to look correct.
- **The base class is the kind**, and the chain may be longer than one link. 125 of one
  project's classes derive from `PublishedElementModel` and 39 from `PublishedContentModel`,
  but 18 derive from *another model class* — a shared page base — so the kind is whatever the
  chain ends at. Those 18 also inherit their base's properties without re-declaring them, so
  the chain has to be walked for the properties too or the component under-reports by however
  many the base contributed.
- **A composition is an interface in the base list**, resolved through the mixin file that
  declares it. That file carries `// Mixin Content Type with alias "<alias>"` above the
  interface, which is a declaration rather than a naming convention. Across both projects,
  every interface named by every class resolved to one — so an interface that does *not* is a
  missing model file, and this adapter refuses rather than dropping the composition.
- **A property contributed by a mixin is re-declared in the composing class**, delegating to
  the mixin's static getter through its fully-qualified name. That delegation is the only
  `inheritedFrom` signal at this rung. The mixin's *own* copy of the property delegates to the
  same getter unqualified, so a reader that sees any `Get…` call as inheritance marks every
  composition's fields as inherited from itself.
- **Every property is followed by a `public static … GetX(…)` getter with its own doc
  summary.** Keying on the summary rather than on `[ImplementPropertyType]` reads each property
  twice, which the dossier's duplicate-alias refusal would then report as a contradiction in a
  file that has none.

## Two limits, recorded rather than papered over

**A property's name and description share one line, split on the first `": "`.** ModelsBuilder
writes `/// Post Notes: Optional notes displayed below the article content` and there is no
other separator to read. 439 summary blocks in one project and 972 in the other, none of them
wrapped across lines, so the split is safe in practice — but a display name that itself contains
`": "` would be read as a name and a description, and nothing in the file can tell the two
apart. A multi-line summary, if one ever appears, is joined with a space before the split.

**A description read here is ModelsBuilder's escaping of the real one, and that is lossy at the
source rather than here.** An XML doc comment cannot hold a `<`, so the generator rewrites angle
brackets as braces and collapses every line break to a space. Cross-checking every component
readable at two rungs on both projects — 68 against Deploy artifacts, 174 against a uSync export
— found the two rungs agreeing on the alias, the kind, the display names, the property alias
set, the compositions and the per-property `inheritedFrom` in every single case, and disagreeing
**only** on the descriptions of properties whose text contains markup: 32 and 41 fields
respectively, every one of which the escaping accounts for. **The comparison cannot say more than
that.** It compared dossiers, so a mis-parse here would present as a description difference too
and would have been counted among the escaping cases without being separable from them -- the
`Name: Description` split below is the specific way that could happen. What the sweep establishes
is that no difference appeared that escaping fails to explain, not that escaping is the only
cause. So a guide rendered from this rung shows a field's help text with its formatting
flattened. The gap list says so; recovering it is not possible from the model.

**Nothing here reads a serialization version, because a generated model declares none.** The
version stamped in the header comment is ModelsBuilder's own, not a schema format, and gating on
it would refuse a project for upgrading a package that changed nothing this parser reads. The
`ood.flag` file the generator leaves beside stale models is a *staleness* signal, not a version
one, and acting on it is a decision for whoever has a project where it matters.
"""

import os
import re

from guidelib import GuideError
from guidelib import dossier
from guidelib import missing_alias_error

RUNG = "models"

MODEL_SUFFIX = ".generated.cs"

# The two base classes that end a chain, and what each one means. Read from the class
# declaration, never from the file: nothing else in a generated model says which kind it is.
ELEMENT_BASE = "PublishedElementModel"
CONTENT_BASE = "PublishedContentModel"

# Build output, tooling directories, and Umbraco's own scratch folder.
#
# `TEMP` and `InMemoryAuto` are here for a reason the other adapters do not have: with
# ModelsBuilder in its in-memory mode, a running site writes `umbraco/Data/TEMP/InMemoryAuto/
# models.generated.cs` **and** `all.generated.cs`, each holding every model in the project. The
# demo project carries both, generated by an older ModelsBuilder than the committed models
# beside them. Reading them would claim every alias three times over and hand the duplicate
# refusal below a project that is perfectly well-formed — and if the refusal were ever relaxed,
# a stale runtime copy would win a lookup by directory order.
SKIP_DIRS = {"bin", "obj", "node_modules", "packages", "TestResults", "TEMP", "InMemoryAuto"}

# What the dossier's fields mean at this rung, stated in the dossier itself. Written per field
# rather than as one sentence about the rung, because a consumer rendering a property table
# needs to know which *column* it cannot fill; "the models rung is thin" does not tell it.
#
# ASCII only, and phrased as short declaratives: these strings are rendered into JSON with
# `ensure_ascii`, so a dash or a curly quote here would reach a reader as an escape sequence.
#
# `editor` is the one entry that is not an absence. The generated C# property type IS the
# rung's best answer to "what is this field", per `umbraco-17-feature-backfill` — but it is a
# different vocabulary from the editor alias the higher rungs put in the same field, so a
# consumer that pattern-matches on `Umbraco.*` has to be told rather than left to guess.
GAPS = (
    # Two entries, because the dossier has two `description` fields and this rung treats them
    # differently. One entry naming both read as "no descriptions anywhere" to anyone skimming
    # key-first, which is what the `field:` convention invites -- while property descriptions
    # sit populated in the same document.
    "description (component): not recorded. A generated model's class summary carries the "
    "display name and nothing else.",
    "description (property): recorded, but as ModelsBuilder escaped it: line breaks collapsed "
    "to spaces, and angle brackets rewritten as braces.",
    "editor: the generated C# property type, not the data type's editor alias.",
    "icon: not recorded. The backoffice icon is not generated into a model.",
    "mandatory: not recorded. Every property reads false; required flags are not generated.",
    "options: not recorded. Every option list reads empty; an option list lives on the data "
    "type, which this rung does not read.",
    "sortOrder: not recorded. Every property reads 0, and the unnamed bucket is in alias "
    "order.",
    "tabs: not recorded. A generated model carries no tab or group structure, so every "
    "property is in the one unnamed bucket.",
)

# --- the shapes ModelsBuilder writes -----------------------------------------
#
# Line-oriented rather than a C# parse, deliberately. Generated code is emitted by one
# templating pass with a fixed layout, so the lines below are the whole grammar this rung
# needs; a real parser would be more code defending against constructs the generator cannot
# produce. Anything unrecognized is skipped rather than guessed at, and a *reference* that
# cannot be resolved raises.
DECLARATION_RE = re.compile(
    r"^\s*public\s+partial\s+(class|interface)\s+(\w+)\s*(?::\s*(.+?))?\s*$")
PUBLISHED_MODEL_RE = re.compile(r'\[\s*PublishedModel\s*\(\s*"([^"]*)"')
MIXIN_ALIAS_RE = re.compile(r'^\s*//\s*Mixin Content Type with alias\s+"([^"]*)"')
IMPLEMENT_RE = re.compile(r'\[\s*ImplementPropertyType\s*\(\s*"([^"]*)"')
# `public virtual <type> <Name> => <expression>;` — the only property form the generator
# emits. `new` appears on the helper constants, not on properties, but it is allowed here so a
# future generator adding it does not silently drop every property.
PROPERTY_RE = re.compile(
    r"^\s*public\s+(?:new\s+)?virtual\s+(.+?)\s+(\w+)\s*=>\s*(.+?);\s*$")
DOC_ONE_LINE_RE = re.compile(r"^\s*///\s*<summary>(.*?)</summary>\s*$")
DOC_OPEN_RE = re.compile(r"^\s*///\s*<summary>\s*$")
DOC_CLOSE_RE = re.compile(r"^\s*///\s*</summary>\s*$")
DOC_BODY_RE = re.compile(r"^\s*///\s?(.*)$")

# The separator between a property's display name and its description, inside one doc line.
NAME_DESCRIPTION_SEPARATOR = ": "

# The prefix a delegating property carries when it points at another model's static getter.
GETTER_PREFIX = "Get"

# A dotted C# name inside a type expression, reduced to its last segment by `_short_type`.
QUALIFIED_NAME_RE = re.compile(r"[A-Za-z_][\w.]*")


class Model:
    """One content-type model class, as declared in one file."""

    __slots__ = ("path", "alias", "class_name", "name", "base", "interfaces", "properties")

    def __init__(self, path, alias, class_name, name, base, interfaces):
        self.path = path
        self.alias = alias
        self.class_name = class_name
        self.name = name
        self.base = base
        self.interfaces = list(interfaces)
        self.properties = []


def present(project_root):
    """Whether this project commits generated models at all — the adapter's detect probe."""
    for _ in _model_files(project_root):
        return True
    return False


def searched_locations(project_root):
    """The directories read, for an error message that names where it looked."""
    found = sorted({os.path.dirname(p) for p in _model_files(project_root)})
    return found or [os.path.abspath(project_root)]


# ---------------------------------------------------------------------------
# The whole-project accessors — and the one question this rung refuses
# ---------------------------------------------------------------------------

def palettes(catalog):
    """Refuse the inventory: a generated model carries no palette to read.

    **This is where the three adapters legitimately differ, and returning an empty list would
    be the wrong difference.** The higher two rungs read a project's block-editor data types,
    which state per entry which element type an editor can place. ModelsBuilder generates one
    class per content type and nothing about the data types at all, so there is no palette on
    disk at this rung — not an empty one, not a partial one, none.

    An empty list would render as "this project offers no blocks", which is indistinguishable
    from the truth on a project that genuinely offers none, and would hand an audit an empty
    backlog on a project full of them. That is precisely the silent-empty failure the whole
    ladder is built to refuse, so this refuses instead and names its own limit.

    The other half of the inventory is out of reach for the same reason: a generated model
    records no template assignment and no allowed-children structure, so every page-type signal
    but the alias itself is absent too. Both halves are named, because an operator told only
    about palettes would reasonably expect the page types to have come out.

    `catalog` is accepted and unused, so the three adapters present one signature.
    """
    raise GuideError(
        "the generated-models rung carries no block-editor palette, so the inventory cannot "
        "be determined from it — and an empty list would read as 'this project offers no "
        "blocks', which is the one answer no source should ever invent.\n"
        "  A generated model describes a content type's properties and nothing about the data "
        "types that offer it, its template, or the content tree, so neither the components nor "
        "the page types can be read here. `extract` and `signature` still work at this rung.\n"
        "  Read the inventory from a project that commits its Deploy artifacts or its uSync "
        "export, or have the spell read the running instance and supply the result.")


def components(catalog):
    """Refused, for the same reason `palettes` is.

    Present so the three adapters actually share an interface rather than sharing one by the
    order a caller happens to try them in. Without it, `determine()` survived only because it
    asks for palettes first — and a caller that asked the other way round, or a later step
    reaching for components alone, got an AttributeError instead of the refusal every other
    dead end in this codebase produces.
    """
    return palettes(catalog)


def extract(project_root, alias, catalog=None):
    """Read one content type's generated model, and its base chain, into a dossier.

    `catalog` is the same seam Deploy and uSync offer, for the same reason: a caller
    classifying every component in the project parses the corpus once instead of once per
    component. It matters more here than there — a model file is parsed line by line, and one
    project's 182 files hold 972 property declarations. A lone `extract` passes nothing.
    """
    catalog = catalog or Catalog(project_root)
    model = catalog.document(alias)
    if model is None:
        # The same refusal both other adapters raise, from the same place, so the one message
        # an operator is most likely to meet cannot drift between rungs. Its two
        # export-assuming clauses are replaced: a project on this rung has no export to
        # re-export, and an instruction naming an action nobody can take is worse than none.
        raise missing_alias_error(
            "generated model class", alias, searched_locations(project_root),
            catalog.document_count(),
            partial="the committed models are partial and this component's class was left "
                    "out of them",
            remedy="Regenerate the project's models, or point --project-root at the tree "
                   "that holds this one.")

    # The base chain is walked twice below -- once by `_collect` for properties, once by
    # `_kind` for the terminal base. Both are dict lookups against the parsed catalog, never a
    # re-read, and measured depth is at most 1 on both real projects (164 of 182 classes are
    # depth 0). Worth folding into one pass only if a project ever shows a deeper chain.
    schema = dossier.Schema()
    compositions = []
    _collect(model, catalog, schema, compositions, set(), own=True)

    return dossier.build(
        rung=RUNG,
        alias=model.alias,
        name=model.name,
        kind=_kind(model, catalog),
        # Neither is generated into a model. Stated as empty and named in the gap list, rather
        # than omitted, so the dossier's shape does not change between rungs.
        icon="",
        description="",
        structure_available=False,
        structure_gaps=GAPS,
        compositions=sorted(set(compositions)),
        tabs=schema.tabs(),
    )


# ---------------------------------------------------------------------------
# Walking a model class and its base chain
# ---------------------------------------------------------------------------

def _collect(model, catalog, schema, compositions, seen, own):
    """Add one class's properties and compositions, then recurse into its base class.

    `own` is False once the walk has left the requested class, which is what makes a base
    class's own properties come out marked as inherited from it — the same fact the higher
    rungs read from a composition reference.
    """
    if model.alias in seen:
        return
    seen.add(model.alias)

    for interface in model.interfaces:
        # Every interface named by a class in either measured project resolved to a mixin, so
        # one that does not is a model file the project did not commit — the same partial-read
        # condition a dangling composition reference is at the higher rungs. Dropping it
        # silently would under-report the component's inheritance with nothing in the output to
        # say so.
        composed = catalog.alias_for_interface(interface)
        if composed == model.alias:
            # A composition's own class implements its own mixin interface. Reading that as a
            # composition would make every element type used as a composition compose itself,
            # which the higher rungs never say.
            continue
        if composed is None:
            raise GuideError(
                "%s names the interface %s, which no generated model under %s declares as a "
                "composition — the committed models are partial.\n"
                "  A composition's model file carries `// Mixin Content Type with alias` above "
                "its interface; without it the fields it contributes cannot be attributed.\n"
                "  Regenerate the project's models, or point --project-root at the tree that "
                "holds all of them."
                % (model.class_name, interface,
                   ", ".join(searched_locations(catalog.project_root))))
        compositions.append(composed)

    for declared in model.properties:
        schema.add_property(_property(declared, model, catalog, own))

    base = catalog.model_for_class(model.base)
    if base is not None:
        # A model class deriving from another model class: the base's properties are inherited
        # in C# and so are absent from this class's file entirely. 18 of one project's 164
        # classes are shaped this way, and not walking the chain loses every field the base
        # contributes.
        compositions.append(base.alias)
        _collect(base, catalog, schema, compositions, seen, own=False)
        return
    if model.base not in (ELEMENT_BASE, CONTENT_BASE):
        raise GuideError(
            "the generated model %s derives from %s, which is neither %s, %s, nor another "
            "generated model under %s — so neither its kind nor the fields it inherits can be "
            "read.\n"
            "  Regenerate the project's models, or point --project-root at the tree that holds "
            "all of them."
            % (model.class_name, model.base or "nothing", ELEMENT_BASE, CONTENT_BASE,
               ", ".join(searched_locations(catalog.project_root))))


def _property(declared, model, catalog, own):
    """One property, with the only two facts this rung has about it beyond its alias."""
    name, description = _split_summary(declared["summary"])
    return dossier.make_property(
        alias=declared["alias"],
        name=name,
        # The generated C# type, short form. It is the rung's answer to "what is this field",
        # and `GAPS` says in the dossier that it is a C# type rather than an editor alias.
        editor=_short_type(declared["type"]),
        description=description,
        # Not generated. Explicit rather than omitted, per the dossier's absence-is-stated rule,
        # and named in the gap list so `false` is not read as "optional".
        mandatory=False,
        sort_order=0,
        options=(),
        inherited_from=_inherited_from(declared, model, catalog, own),
    )


def _inherited_from(declared, model, catalog, own):
    """Which type declared this property — read from what the property's body calls.

    A composing class re-declares a mixin's property and delegates to the mixin's static getter
    through its fully-qualified name. A mixin's *own* copy delegates to the same getter
    unqualified, so the qualifying class name is the whole signal, and a delegation naming the
    declaring class itself is not inheritance.
    """
    delegate = declared["delegate"]
    if delegate and delegate != model.class_name:
        composed = catalog.alias_for_class(delegate)
        if composed is None:
            raise GuideError(
                "%s.%s reads its value from %s, which no generated model under %s declares — "
                "the committed models are partial, so this field's owner cannot be named.\n"
                "  Regenerate the project's models, or point --project-root at the tree that "
                "holds all of them."
                % (model.class_name, declared["alias"], delegate,
                   ", ".join(searched_locations(catalog.project_root))))
        return composed
    # Declared here. Whether that counts as inherited depends on where the walk is: the
    # requested class owns its properties, a base class further up the chain does not.
    return None if own else model.alias


def _kind(model, catalog):
    """Element or document, from wherever the base chain ends."""
    current = model
    seen = set()
    while current.alias not in seen:
        seen.add(current.alias)
        if current.base == ELEMENT_BASE:
            return dossier.KIND_ELEMENT
        base = catalog.model_for_class(current.base)
        if base is None:
            # `_collect` has already refused anything that is neither a known base nor a model
            # in the catalog, so reaching here means CONTENT_BASE.
            return dossier.KIND_DOCUMENT
        current = base
    return dossier.KIND_DOCUMENT


def _split_summary(summary):
    """A property's display name and description, from the one doc line that holds both.

    Split on the FIRST `": "`, because a description routinely contains a colon of its own and
    a display name almost never does. The reverse split would truncate half the descriptions in
    the projects measured. See the module docstring for the case this cannot resolve.
    """
    name, separator, description = summary.partition(NAME_DESCRIPTION_SEPARATOR)
    if not separator:
        return summary.strip(), ""
    return name.strip(), description.strip()


def _short_type(declared):
    """A C# type as a reader wants it: no `global::`, no namespaces, generics kept.

    `global::System.Collections.Generic.IEnumerable<global::Umbraco.Cms.Core.Models.Link>`
    becomes `IEnumerable<Link>`. Generated models fully qualify everything, so the raw form
    would fill a guide's type column with framework namespaces and hide the one word that
    matters. Every dotted name is reduced to its last segment, which leaves the unqualified
    keywords (`string`, `bool`, `int`) untouched.
    """
    return QUALIFIED_NAME_RE.sub(
        lambda match: match.group(0).rsplit(".", 1)[-1],
        declared.replace("global::", ""))


# ---------------------------------------------------------------------------
# Reading the model files
# ---------------------------------------------------------------------------

def _model_files(project_root):
    """Every `*.generated.cs` under the project, in a stable order.

    The location is searched for rather than configured, per the `paths.md → ## Umbraco` slot's
    fallback. Every matching folder is read rather than the first one found, so the result does
    not depend on directory order.
    """
    for dirpath, dirnames, filenames in os.walk(project_root):
        dirnames[:] = sorted(d for d in dirnames
                             if d not in SKIP_DIRS and not d.startswith("."))
        for name in sorted(filenames):
            if name.endswith(MODEL_SUFFIX):
                yield os.path.join(dirpath, name)


def _read(path):
    try:
        with open(path, "r", encoding="utf-8-sig") as handle:
            return handle.read().split("\n")
    except OSError as exc:
        # Loud, and named. A skipped file is how a component goes missing from a guide with
        # nothing in the output to say so.
        raise GuideError("cannot read generated model %s: %s" % (path, exc))


def _split_bases(declared):
    """A declaration's base list: the base type first, then the interfaces it names."""
    parts = [part.strip() for part in (declared or "").split(",")]
    parts = [part for part in parts if part]
    if not parts:
        return "", []
    return parts[0], parts[1:]


def _delegated_class(expression):
    """The model class a property's body reads through, or None if it reads its own value.

    `global::…PublishedModels.BaseSettings.GetMetaDescription(this, fallback)` names
    `BaseSettings`. `GetMetaDescription(this, fallback)` and `this.Value<string>(…)` name
    nobody — the first is a mixin's own getter, the second a property with no getter at all.
    """
    head = expression.split("(", 1)[0].replace("global::", "").strip()
    parts = head.split(".")
    if len(parts) < 2 or not parts[-1].startswith(GETTER_PREFIX):
        return None
    return parts[-2]


def _parse(path):
    """Every content-type model declared in one file, in declaration order.

    One file per content type is what ModelsBuilder's manual mode writes, but its in-memory
    mode writes every model into one file — so a file holds any number of them, and the parser
    tracks which class it is inside rather than assuming.
    """
    models = []
    interface_aliases = {}   # interface name -> the mixin alias it declares
    pending_mixin = None     # a mixin alias awaiting the interface it describes
    summary = None           # the doc summary most recently read
    open_summary = None      # lines of a multi-line summary being read
    published_alias = None   # a pending [PublishedModel("…")]
    property_alias = None    # a pending [ImplementPropertyType("…")]
    current = None           # the model whose body we are inside

    for line in _read(path):
        stripped = line.strip()

        # --- doc comments: `/// <summary>x</summary>` or the three-line form ---
        if open_summary is not None:
            if DOC_CLOSE_RE.match(line):
                # Joined with a space: no summary in either project wrapped, and a wrapped one
                # is still one sentence rather than two facts.
                summary = " ".join(part for part in open_summary if part).strip()
                open_summary = None
            else:
                body = DOC_BODY_RE.match(line)
                open_summary.append(body.group(1).strip() if body else stripped)
            continue
        if DOC_OPEN_RE.match(line):
            open_summary = []
            continue
        one_line = DOC_ONE_LINE_RE.match(line)
        if one_line:
            summary = one_line.group(1).strip()
            continue
        if stripped.startswith("///"):
            continue

        # --- the mixin declaration, which sits above the interface it describes ---
        mixin = MIXIN_ALIAS_RE.match(line)
        if mixin:
            pending_mixin = mixin.group(1)
            continue

        # --- attributes: they sit between a summary and the thing it describes ---
        if stripped.startswith("["):
            model_attribute = PUBLISHED_MODEL_RE.search(line)
            if model_attribute:
                published_alias = model_attribute.group(1)
            implement = IMPLEMENT_RE.search(line)
            if implement:
                property_alias = implement.group(1)
            continue

        declaration = DECLARATION_RE.match(line)
        if declaration:
            keyword, class_name, bases = declaration.groups()
            base, interfaces = _split_bases(bases)
            if keyword == "interface":
                if pending_mixin is not None:
                    interface_aliases[class_name] = pending_mixin
                current = None
            elif published_alias is not None:
                current = Model(path, published_alias, class_name,
                                summary or class_name, base, interfaces)
                models.append(current)
            else:
                # A partial class the generator did not stamp — a hand-written half, or a
                # helper. It declares no content type, so it is not one.
                current = None
            summary = None
            published_alias = None
            property_alias = None
            pending_mixin = None
            continue

        prop = PROPERTY_RE.match(line)
        if prop and property_alias is not None and current is not None:
            declared_type, _member, expression = prop.groups()
            current.properties.append({
                "alias": property_alias,
                "summary": summary or "",
                "type": declared_type.strip(),
                "delegate": _delegated_class(expression),
            })

        if stripped and not stripped.startswith("//"):
            # A code line consumed whatever was pending. This is what keeps a static getter's
            # own doc summary from being attached to the next property.
            summary = None
            property_alias = None

    return models, interface_aliases


class Catalog:
    """Every generated model in the project, indexed the three ways a read needs.

    By alias, because that is what an operator asks for. By class name, because that is how a
    property names the type it reads through and how a class names its base. By interface name,
    because that is how a class names a composition.
    """

    def __init__(self, project_root):
        self.project_root = project_root
        self._documents = {}    # lowercased alias -> Model
        self._by_class = {}     # class name -> Model
        self._interfaces = {}   # interface name -> alias
        self._loaded = False

    def _load_all(self):
        if self._loaded:
            return
        self._loaded = True
        for path in _model_files(self.project_root):
            models, interfaces = _parse(path)
            for model in models:
                self._claim(self._documents, model.alias.lower(), model, "alias")
                self._claim(self._by_class, model.class_name, model, "class name")
            for name, alias in interfaces.items():
                self._interfaces.setdefault(name, alias)

    @staticmethod
    def _claim(index, key, model, what):
        """Index a model, refusing a second claim on the same key.

        The same hazard both other adapters refuse: two files declaring one alias is a question
        with no correct answer, and answering it by directory-walk order picks whichever sorts
        first. It is reachable here two ways — a second copy of the model tree, and a
        single-file dump of every model sitting beside the per-type files, which is exactly what
        Umbraco's in-memory mode leaves under `umbraco/Data/TEMP` (pruned by SKIP_DIRS, since
        that copy is build output rather than ambiguous input).
        """
        first = index.get(key)
        if first is None:
            index[key] = model
            return
        if first is model or first.path == model.path:
            return
        raise GuideError(
            "two generated models declare the same %s '%s' — the model tree is ambiguous:\n"
            "  %s\n  %s\n"
            "Remove or exclude whichever is stale; reading either one silently would make the "
            "result depend on directory order."
            % (what, key, first.path, model.path))

    def document(self, alias):
        """The model for an alias, matched case-insensitively.

        Case-folded because a generated file and class name mangle the alias's casing, so an
        operator reading the alias off a file name types something the project does not declare.
        """
        self._load_all()
        return self._documents.get((alias or "").lower())

    def document_count(self):
        """How many content types the committed models describe.

        Reported when a lookup misses: a tree that yielded models and one that yielded none call
        for different responses from the operator.
        """
        self._load_all()
        return len(self._documents)

    def model_for_class(self, class_name):
        self._load_all()
        return self._by_class.get(class_name)

    def alias_for_class(self, class_name):
        model = self.model_for_class(class_name)
        return None if model is None else model.alias

    def alias_for_interface(self, interface):
        self._load_all()
        return self._interfaces.get(interface)
