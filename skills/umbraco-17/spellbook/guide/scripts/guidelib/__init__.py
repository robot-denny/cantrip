"""Support modules for guide.py — one module per stage of the deterministic pipeline.

Nothing here is importable as an installed package: guide.py puts its own directory on
sys.path and imports `guidelib.<module>` from there. That is deliberate — a pack ships
files, not wheels, and a consuming project must be able to run the script straight out of
the skill directory.

The shared exception lives here because every stage raises the same one: a read that cannot
be completed is reported to the operator, never papered over with an empty result.
"""


class GuideError(Exception):
    """A read or a lookup could not be completed, with a message for the operator.

    Raised rather than returned so no caller can mistake a failed read for an empty
    component. guide.py catches it, prints it, and exits non-zero.
    """
