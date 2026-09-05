#!/usr/bin/env python3
"""Audit claim eligibility for one declared downstream purpose."""

from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path

from validate_claims import validate
from vault_common import read_csv, split_ids


PURPOSES = {"interview", "resume", "portfolio", "private-analysis"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("vault_root")
    parser.add_argument("--purpose", choices=sorted(PURPOSES), required=True)
    return parser.parse_args()


def eligibility(row: dict[str, str], sources: dict[str, dict[str, str]], purpose: str) -> list[str]:
    reasons: list[str] = []
    if row.get("status") not in {"verified", "user-confirmed"}:
        reasons.append("ineligible-status")
    if row.get("ownership") == "unknown":
        reasons.append("unknown-ownership")
    if row.get("withdrawn_at") or row.get("status") == "withdrawn":
        reasons.append("withdrawn")
    if row.get("valid_to"):
        reasons.append("superseded-or-expired")
    permission = row.get("publication_permission")
    if purpose in {"interview", "resume"} and permission not in {"application-only", "public-approved"}:
        reasons.append("purpose-not-approved")
    if purpose == "portfolio" and permission != "public-approved":
        reasons.append("public-not-approved")
    if purpose == "private-analysis" and permission == "not-approved":
        reasons.append("analysis-not-approved")
    if row.get("sensitivity") == "restricted":
        reasons.append("restricted")
    if purpose == "portfolio" and row.get("sensitivity") != "public":
        reasons.append("not-public-sensitivity")

    source_ids = split_ids(row.get("source_ids", ""))
    if row.get("status") == "verified" and not source_ids:
        reasons.append("verified-without-source")
    for source_id in source_ids:
        source = sources.get(source_id)
        if not source:
            reasons.append("unknown-source")
            continue
        if source.get("status") not in {"active", "moved", "duplicate-candidate"}:
            reasons.append("unavailable-source")
        if source.get("model_access") in {"pending", "do-not-model"}:
            reasons.append("source-not-readable")
        source_permission = source.get("publication_permission")
        if purpose in {"interview", "resume"} and source_permission not in {"application-only", "public-approved"}:
            reasons.append("source-purpose-not-approved")
        if purpose == "portfolio" and source_permission != "public-approved":
            reasons.append("source-public-not-approved")
    return list(dict.fromkeys(reasons))


def main() -> int:
    args = parse_args()
    vault = Path(args.vault_root).expanduser().resolve()
    claims_path = vault / "canonical-claims.csv"
    sources_path = vault / "sources.csv"
    errors, warnings, _ = validate(claims_path, sources_path)
    if errors:
        print("CLAIMS_AUDIT_FAILED")
        for error in errors:
            print(f"- structural: {error}")
        return 1
    _, claim_rows = read_csv(claims_path)
    _, source_rows = read_csv(sources_path)
    sources = {row["source_id"]: row for row in source_rows}
    rejected: dict[str, list[str]] = {}
    eligible: list[str] = []
    counts: Counter[str] = Counter()
    for row in claim_rows:
        reasons = eligibility(row, sources, args.purpose)
        if reasons:
            rejected[row.get("claim_id", "unknown")] = reasons
            counts.update(reasons)
        else:
            eligible.append(row["claim_id"])
    print(f"CLAIMS_AUDIT purpose={args.purpose} eligible={len(eligible)} excluded={len(rejected)}")
    if eligible:
        print(f"ELIGIBLE_IDS {'|'.join(eligible)}")
    for reason, count in sorted(counts.items()):
        print(f"EXCLUDED {reason}={count}")
    for warning in warnings:
        print(f"! {warning}")
    print("NOTE the user remains responsible for final truthfulness, confidentiality, and destination approval")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
