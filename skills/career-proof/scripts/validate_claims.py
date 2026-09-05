#!/usr/bin/env python3
"""Validate Career Proof v0.2 claim-table structure; do not infer truth."""

from __future__ import annotations

import argparse
from pathlib import Path

from vault_common import ID_PATTERNS, TABLES, read_csv, split_ids


ENUMS = {
    "claim_type": {"responsibility", "decision", "action", "metric", "scale", "recognition", "learning"},
    "ownership": {"owned", "co-owned", "participated", "supported", "team-result", "unknown"},
    "status": {"verified", "user-confirmed", "pending", "conflict", "inferred", "prohibited", "withdrawn"},
    "sensitivity": {"public", "personal-sensitive", "company-sensitive", "restricted"},
    "publication_permission": {"not-approved", "application-only", "public-approved"},
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("claims_csv")
    parser.add_argument("--sources", help="optional sources.csv for cross-reference checks")
    return parser.parse_args()


def validate(path: Path, sources_path: Path | None = None) -> tuple[list[str], list[str], int]:
    errors: list[str] = []
    warnings: list[str] = []
    try:
        fields, rows = read_csv(path)
    except (OSError, UnicodeError) as exc:
        return [f"cannot open UTF-8 CSV: {exc}"], warnings, 0
    missing = [field for field in TABLES["canonical-claims.csv"] if field not in fields]
    if missing:
        errors.append(f"missing columns: {missing}")

    source_ids: set[str] | None = None
    if sources_path:
        try:
            _, source_rows = read_csv(sources_path)
            source_ids = {(row.get("source_id") or "").strip() for row in source_rows}
        except (OSError, UnicodeError) as exc:
            errors.append(f"cannot read sources CSV: {exc}")

    seen: set[str] = set()
    for line, row in enumerate(rows, 2):
        claim_id = (row.get("claim_id") or "").strip()
        project_id = (row.get("project_id") or "").strip()
        if not ID_PATTERNS["claim_id"].fullmatch(claim_id):
            errors.append(f"line {line}: invalid claim_id {claim_id!r}")
        elif claim_id in seen:
            errors.append(f"line {line}: duplicate claim_id {claim_id}")
        seen.add(claim_id)
        if not ID_PATTERNS["project_id"].fullmatch(project_id):
            errors.append(f"line {line}: invalid project_id {project_id!r}")
        if not (row.get("claim_text") or "").strip():
            errors.append(f"line {line}: empty claim_text")
        for field, allowed in ENUMS.items():
            value = (row.get(field) or "").strip()
            if value not in allowed:
                errors.append(f"line {line}: invalid {field} {value!r}")

        status = (row.get("status") or "").strip()
        withdrawn_at = (row.get("withdrawn_at") or "").strip()
        if status == "withdrawn" and not withdrawn_at:
            errors.append(f"line {line}: withdrawn claim requires withdrawn_at")
        if status != "withdrawn" and withdrawn_at:
            warnings.append(f"line {line}: withdrawn_at is set but status is {status}")
        if status in {"verified", "user-confirmed"} and (row.get("ownership") or "").strip() == "unknown":
            errors.append(f"line {line}: eligible claim cannot have unknown ownership")

        if (row.get("claim_type") or "").strip() in {"metric", "scale"}:
            required_metric = ["metric_name", "metric_unit", "metric_time_window", "metric_population", "metric_calculation"]
            absent = [field for field in required_metric if not (row.get(field) or "").strip()]
            message = f"line {line}: metric fields missing {absent}"
            if absent and status in {"verified", "user-confirmed"}:
                errors.append(message)
            elif absent:
                warnings.append(message)

        if source_ids is not None:
            for source_id in split_ids(row.get("source_ids") or ""):
                if source_id not in source_ids:
                    errors.append(f"line {line}: unknown source_id {source_id}")
    return errors, warnings, len(rows)


def main() -> int:
    args = parse_args()
    path = Path(args.claims_csv)
    if not path.is_file():
        print(f"CLAIMS_SCHEMA_INVALID\n- file not found: {path}")
        return 1
    sources = Path(args.sources) if args.sources else None
    errors, warnings, rows = validate(path, sources)
    if errors:
        print("CLAIMS_SCHEMA_INVALID")
        for error in errors:
            print(f"- {error}")
        for warning in warnings:
            print(f"! {warning}")
        return 1
    print(f"CLAIMS_SCHEMA_OK {rows} claims")
    print("NOTE structural validity does not grant truth or publication eligibility")
    for warning in warnings:
        print(f"! {warning}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
