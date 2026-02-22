#!/usr/bin/env python3
import re
import sys
from pathlib import Path

PATTERN = re.compile(r"第\d+話")


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: detect_metanarrative.py <draft_path>", file=sys.stderr)
        return 2

    path = Path(sys.argv[1])
    if not path.exists():
        print(f"error: file not found: {path}", file=sys.stderr)
        return 1

    lines = path.read_text(encoding="utf-8").splitlines()
    matches = []
    for idx, line in enumerate(lines, start=1):
        if idx == 1:
            continue
        if PATTERN.search(line):
            snippet = line.strip()
            if len(snippet) > 120:
                snippet = snippet[:117] + "..."
            matches.append((idx, snippet))

    if not matches:
        print("NO_MATCH")
        return 0

    for line_no, text in matches:
        print(f"MATCH line={line_no} text={text}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
