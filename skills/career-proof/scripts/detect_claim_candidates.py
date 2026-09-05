#!/usr/bin/env python3
"""Detect possible duplicate or conflict claim pairs without modifying data."""

from __future__ import annotations

import argparse
import json
import re
from difflib import SequenceMatcher
from itertools import combinations
from pathlib import Path

from vault_common import read_csv


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("claims_csv")
    parser.add_argument("--threshold", type=float, default=0.86)
    return parser.parse_args()


def normalize(text: str) -> str:
    return re.sub(r"[^\w\u4e00-\u9fff]+", "", text.casefold())


def main() -> int:
    args = parse_args()
    if not 0.5 <= args.threshold <= 1:
        print("error: threshold must be between 0.5 and 1")
        return 2
    path = Path(args.claims_csv)
    if not path.is_file():
        print(f"error: file not found: {path}")
        return 1
    _, rows = read_csv(path)
    candidates: list[dict[str, object]] = []
    for left, right in combinations(rows, 2):
        left_text = normalize(left.get("claim_text", ""))
        right_text = normalize(right.get("claim_text", ""))
        if not left_text or not right_text:
            continue
        score = SequenceMatcher(None, left_text, right_text).ratio()
        kind = ""
        reason = ""
        if left_text == right_text:
            kind, reason = "duplicate", "normalized text is identical"
        elif (
            left.get("project_id") == right.get("project_id")
            and left.get("claim_type") in {"metric", "scale"}
            and right.get("claim_type") in {"metric", "scale"}
            and left.get("metric_name")
            and left.get("metric_name") == right.get("metric_name")
            and left.get("metric_result") != right.get("metric_result")
        ):
            kind, reason = "conflict", "same project and metric name have different results"
        elif score >= args.threshold:
            kind, reason = "duplicate", "claim text is highly similar"
        if kind:
            candidates.append({
                "kind": kind,
                "left_claim_id": left.get("claim_id"),
                "right_claim_id": right.get("claim_id"),
                "similarity": round(score, 3),
                "reason": reason,
            })
    print(f"CLAIM_CANDIDATES {len(candidates)}")
    for candidate in candidates:
        print(json.dumps(candidate, ensure_ascii=False, sort_keys=True))
    print("NOTE candidates require human review; this tool never merges or resolves claims")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
