#!/usr/bin/env python3
import json
import re
import statistics
import sys
from pathlib import Path

STAR = re.compile(r"★\s*([0-5](?:\.\d+)?)")


def extract_score(path: Path) -> float:
    text = path.read_text(encoding="utf-8")
    m = STAR.search(text)
    if not m:
        raise ValueError(f"score not found in {path}")
    return float(m.group(1))


def main() -> int:
    if len(sys.argv) != 4:
        print(
            "usage: aggregate_reader_scores.py <reader_ym.md> <reader_af.md> <reader_vet.md>",
            file=sys.stderr,
        )
        return 2

    files = [Path(p) for p in sys.argv[1:4]]
    for path in files:
        if not path.exists():
            print(f"error: file not found: {path}", file=sys.stderr)
            return 1

    try:
        scores = [extract_score(p) for p in files]
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    result = {
        "scores": scores,
        "average": round(sum(scores) / len(scores), 3),
        "median": float(statistics.median(scores)),
    }
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
