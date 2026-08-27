"""What two report renderers must not say differently.

`inventory` and `audit` both count things and name them, and they are read side by side by the
same person in the same terminal. Three pieces were duplicated verbatim between them, which is
exactly the shape that drifts: a plural rule fixed in one renderer and not the other, or one
naming an item `alias (Name)` while the other switches to `Name (alias)`. There is nothing to
decide here — only one place to decide it.
"""

# The width every hand-wrapped rule in both renderers sits inside.
WRAP_WIDTH = 88


def plural(count, one, many):
    """The singular form for exactly one. A report that says "1 content types read" reads as a
    bug in the tool, which is the last thing a report whose job is to be believed can afford."""
    return one if count == 1 else many


def item(item):
    """`alias (Display Name)` — the one way this toolkit names a component to a person."""
    name = item.get("name") or ""
    return "%s (%s)" % (item["alias"], name) if name else item["alias"]
