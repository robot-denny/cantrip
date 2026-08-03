#!/usr/bin/env python3
"""Verify load-bearing content survived an extraction.

The side-by-side diff half of a checkpoint (docs/contract.md) needs to confirm that
de-projecting a source file didn't quietly drop something that mattered. Plain grep is
the wrong tool: extracted files are hard-wrapped, so any probe phrase that lands across
a line break reports as missing when it is present. That produced three false "LOST"
flags during increment 2.2 before the method was fixed.

This normalizes whitespace on both sides before matching, and ignores markdown emphasis
markers so a probe written as plain prose still matches bolded output.

Usage:
    scripts/check-preserved.py <file> <probe> [<probe> ...]
    scripts/check-preserved.py <file> --from-file <probes.txt>

Exit: 0 if every probe is present, 1 otherwise.
"""

import re
import sys
from pathlib import Path


def normalize(text: str) -> str:
    """Collapse whitespace and strip markdown emphasis, so wrapping and bolding don't matter."""
    text = re.sub(r"[*_`]", "", text)
    return re.sub(r"\s+", " ", text).strip().lower()


def main(argv: list[str]) -> int:
    if len(argv) < 3:
        print(__doc__)
        return 2

    target = Path(argv[1])
    if not target.is_file():
        print(f"error: no such file: {target}", file=sys.stderr)
        return 2

    if argv[2] == "--from-file":
        probe_file = Path(argv[3])
        probes = [ln.strip() for ln in probe_file.read_text().splitlines()
                  if ln.strip() and not ln.startswith("#")]
    else:
        probes = argv[2:]

    haystack = normalize(target.read_text())

    missing = []
    for probe in probes:
        if normalize(probe) in haystack:
            print(f"  ok    {probe}")
        else:
            print(f"  LOST  {probe}")
            missing.append(probe)

    print()
    if missing:
        print(f"{len(missing)} of {len(probes)} probes missing from {target}")
        return 1
    print(f"all {len(probes)} probes present in {target}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
