"""Fingerprints, and the record of which text on a guide page a model wrote.

A guide page carries prose a model drafted: the purpose sentence, the when-to-use section, and
the information note on each property row. Some of it an editor will rewrite in their own words,
and some of it nobody will touch. The two must be told apart before anything is regenerated,
because rewriting text somebody chose is the one mistake this tooling exists not to make, and
leaving stale text nobody chose is the mistake that makes guides drift out of date.

They are told apart by a **record**, stored on the page itself in a machine-owned field
(`guideGenerated` by default; the `## Editor guides` slot can rename it). It holds, for each
model-authored field and each row note the tooling wrote, a fingerprint of the value the CMS
stored at the time:

    {"recordVersion": 1,
     "fields": {"guidePurpose": "sha256:…", "guideWhenToUse": "sha256:…"},
     "rows":   {"<property alias>": "sha256:…"}}

Read later, a field whose current value still has its recorded fingerprint is exactly what was
generated, so nobody has edited it and it may be rewritten. A field whose value differs was
edited, and is kept. A field with no entry has no record, and is kept too: the absence of a
record is never read as permission.

The record lives on the page rather than in a store beside the tooling so it travels with the
page through Deploy, and so the spell and any dashboard read one record rather than two that
can disagree.

## What is fingerprinted

**The value the CMS stored, not the value that was sent.** The spell reads every field back
after writing it, and the record is computed from those read-back values. A rich-text editor
that reformats markup on save would otherwise make freshly written text read as "edited" on
the very next run, and the first refresh would keep everything.

**The exact value, with no normalization.** No trimming, no case folding, no markup
canonicalization. A normalization rule is a second definition of "the same text" that a port
of this tooling would have to reproduce exactly, and the cost of not normalizing is only that a
whitespace-only change counts as an edit -- which errs toward keeping somebody's text. So a
fingerprint is `sha256:` plus the lowercase hex SHA-256 of the value's UTF-8 bytes, and that
sentence is the whole specification.

## What this module does not know

Nothing here knows the page file's shape, the register's field names, or where rows live on a
page. Those belong to `guidelib/changeplan.py`, which reads the page file and hands this module
plain values. That split is what lets the change plan import this module to read a record
without the two importing each other.
"""

import hashlib

from guidelib import GuideError

# The prefix names the algorithm, so a record written by a later algorithm is distinguishable
# from this one by reading it rather than by guessing from a hash's length.
FINGERPRINT_PREFIX = "sha256:"

# The record shapes this module writes and has been written against. Absence of a version is
# not accepted here, unlike a page file's: the record is a value this tooling alone writes, and
# every record it has ever written carries one, so a record without one was written by
# something else and its entries cannot be trusted to mean what ours mean.
RECORD_VERSION = 1
ACCEPTED_RECORD_VERSIONS = (1,)


def fingerprint(value, name=None):
    """`sha256:` plus the hex SHA-256 of `value`'s exact UTF-8 bytes.

    Refuses anything that is not text rather than hashing a rendering of it: a value that is
    not a string was not stored by a text field, and a fingerprint of `str(value)` would be a
    fingerprint of something the CMS never held.
    """
    what = "'%s'" % name if name else "a value"
    if not isinstance(value, str):
        raise GuideError("cannot fingerprint %s, which is %s; only a field's stored text is "
                         "fingerprinted." % (what, type(value).__name__))
    try:
        encoded = value.encode("utf-8")
    except UnicodeEncodeError:
        # A lone surrogate survives a JSON read and cannot be encoded. Refused rather than
        # hashed some other way: a fingerprint of a repaired value is a fingerprint of text
        # the CMS never held.
        raise GuideError("cannot fingerprint %s: its text is not valid Unicode (it holds a lone "
                         "surrogate), so it is not text the CMS stores as written." % what)
    return FINGERPRINT_PREFIX + hashlib.sha256(encoded).hexdigest()


def fold(alias):
    """A row alias as every reader and writer of the record compares it: stripped, lower-cased.

    One rule in one place. `plan` matching an entry the merge then drops, or the reverse, is
    two answers to one question about the same row.
    """
    return alias.strip().lower()


def stored_record(where, label, raw):
    """A page's record of generated text, validated, or None where the page holds none.

    `raw` is the value as the page file carries it: `None` means the page holds no record,
    which is answerable and common -- every page generated before the record existed, and
    every page written by hand. Anything else must be a record this module recognizes.

    Returns `{"recordVersion", "fields", "rows"}` with both maps copied, so a caller merging
    into the result never edits the page it was read from. A record missing `fields` or `rows`
    is read as holding no entries there: the record is one stored value, so a missing map
    cannot be a map somebody failed to read, and "no entry" already means "kept".

    Fingerprints are compared as opaque strings and never parsed, for the reason a stored
    signature is not: a format check in a reader is a second rule that could disagree with the
    writer. A value that is not a fingerprint simply never matches, so the field it guards is
    kept -- the safe direction.
    """
    if raw is None:
        return None
    if not isinstance(raw, dict):
        raise GuideError("%s ('%s') has a 'generated' record that is %s, not an object or null."
                         % (where, label, type(raw).__name__))
    version = raw.get("recordVersion")
    # A boolean is refused by type: `True in (1,)` holds in Python, and `true` is not a version.
    if isinstance(version, bool) or version not in ACCEPTED_RECORD_VERSIONS:
        raise GuideError(
            "%s ('%s') holds a 'generated' record with recordVersion %r, which this script has "
            "not been written against.\n"
            "  Known versions: %s. The record decides which text on the page may be rewritten, "
            "so one read under the wrong rules could mark somebody's writing as replaceable."
            % (where, label, version,
               ", ".join(str(v) for v in ACCEPTED_RECORD_VERSIONS)))
    return {
        "recordVersion": version,
        "fields": _entries(where, label, raw, "fields"),
        "rows": _entries(where, label, raw, "rows"),
    }


def _entries(where, label, raw, key):
    """One of the record's two maps, name to fingerprint, as a fresh dict."""
    entries = raw.get(key)
    if entries is None:
        return {}
    if not isinstance(entries, dict):
        raise GuideError("%s ('%s') has a 'generated' record whose '%s' is %s, not an object."
                         % (where, label, key, type(entries).__name__))
    for name, value in entries.items():
        if not name.strip():
            raise GuideError("%s ('%s') has a 'generated' record with an empty name in '%s'."
                             % (where, label, key))
        if not isinstance(value, str):
            raise GuideError("%s ('%s') has a 'generated' record whose '%s' entry '%s' is %s, "
                             "not a fingerprint." % (where, label, key, name,
                                                     type(value).__name__))
    return dict(entries)


def build_record(existing, field_values, row_values, held_rows=None):
    """The record after a write: fresh fingerprints for what was written, merged over `existing`.

    `existing` is the page's record as `stored_record` returned it, or None. `field_values`
    maps each model-authored field the spell just wrote to its read-back value; `row_values`
    maps each property alias whose note it just wrote to that note's read-back value.

    **An entry for anything not written this time is kept exactly as it was.** It is the
    fingerprint of what was generated *then*, and recomputing it from today's value would
    record an editor's change as the tooling's own text -- the next run would then rewrite it.

    Row entries are keyed by the alias, and an existing entry whose alias differs from a
    written one only in case or surrounding space is replaced rather than kept beside it: rows
    are matched on the folded alias everywhere else (see `fold`), so two entries for one row
    would be two answers to one question.

    **A row entry for a row the page no longer holds is dropped.** `held_rows` is the set of
    folded aliases the page's row list holds, or None where the page holds no row list to judge
    by -- then every entry is kept, the safe direction. A row removed from the table took
    its note with it, so its entry protects nothing, and a record still naming it would read as
    a note somebody could find.

    Keys are sorted within each map so the same record prints the same way every time, which is
    what lets a stored record be compared to a freshly built one as text.
    """
    fields = dict(existing["fields"]) if existing else {}
    rows = dict(existing["rows"]) if existing else {}
    if held_rows is not None:
        rows = {key: value for key, value in rows.items() if fold(key) in held_rows}
    for name, value in field_values.items():
        fields[name] = fingerprint(value, name)
    for alias, value in row_values.items():
        folded = fold(alias)
        for old in [key for key in rows if fold(key) == folded]:
            del rows[old]
        rows[alias] = fingerprint(value, alias)
    return {
        "recordVersion": RECORD_VERSION,
        "fields": {key: fields[key] for key in sorted(fields)},
        "rows": {key: rows[key] for key in sorted(rows)},
    }
