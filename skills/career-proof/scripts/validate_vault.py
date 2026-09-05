#!/usr/bin/env python3
"""Validate a complete Career Proof v0.2 vault and its references."""

from __future__ import annotations

import argparse
from pathlib import Path

from validate_claims import validate as validate_claims
from vault_common import DIRECTORIES, ID_PATTERNS, TABLES, project_ids, read_csv, split_ids


SOURCE_ENUMS = {
    "source_type": {"pdf", "docx", "pptx", "xlsx", "markdown", "csv", "text", "other"},
    "sensitivity": {"public", "personal-sensitive", "company-sensitive", "restricted"},
    "model_access": {"pending", "allowed", "summary-only", "do-not-model"},
    "publication_permission": {"not-approved", "application-only", "public-approved"},
    "status": {"active", "moved", "missing", "duplicate-candidate", "error"},
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("vault_root")
    return parser.parse_args()


def check_table(path: Path, expected: list[str], errors: list[str]) -> list[dict[str, str]]:
    if not path.is_file():
        errors.append(f"missing file: {path.name}")
        return []
    try:
        fields, rows = read_csv(path)
    except (OSError, UnicodeError) as exc:
        errors.append(f"cannot read {path.name}: {exc}")
        return []
    missing = [field for field in expected if field not in fields]
    if missing:
        errors.append(f"{path.name}: missing columns {missing}")
    return rows


def validate(vault: Path) -> tuple[list[str], list[str], dict[str, int]]:
    errors: list[str] = []
    warnings: list[str] = []
    counts: dict[str, int] = {}
    for required in ("profile.md", "career-timeline.md"):
        if not (vault / required).is_file():
            errors.append(f"missing file: {required}")
    for directory in DIRECTORIES:
        if not (vault / directory).is_dir():
            errors.append(f"missing directory: {directory}/")

    sources = check_table(vault / "sources.csv", TABLES["sources.csv"], errors)
    claims = check_table(vault / "canonical-claims.csv", TABLES["canonical-claims.csv"], errors)
    capabilities = check_table(vault / "capability-map.csv", TABLES["capability-map.csv"], errors)
    reviews = check_table(vault / "review-queue.csv", TABLES["review-queue.csv"], errors)
    changes = check_table(vault / "change-log.csv", TABLES["change-log.csv"], errors)
    counts.update(sources=len(sources), claims=len(claims), capabilities=len(capabilities), reviews=len(reviews), changes=len(changes))

    source_ids: set[str] = set()
    for line, row in enumerate(sources, 2):
        source_id = (row.get("source_id") or "").strip()
        if not ID_PATTERNS["source_id"].fullmatch(source_id):
            errors.append(f"sources.csv line {line}: invalid source_id {source_id!r}")
        elif source_id in source_ids:
            errors.append(f"sources.csv line {line}: duplicate source_id {source_id}")
        source_ids.add(source_id)
        for field, allowed in SOURCE_ENUMS.items():
            value = (row.get(field) or "").strip()
            if value not in allowed:
                errors.append(f"sources.csv line {line}: invalid {field} {value!r}")
        if row.get("model_access") == "do-not-model" and row.get("content_sha256"):
            errors.append(f"sources.csv line {line}: do-not-model source must not retain content_sha256")

    claim_errors, claim_warnings, _ = validate_claims(vault / "canonical-claims.csv", vault / "sources.csv")
    errors.extend(claim_errors)
    warnings.extend(claim_warnings)
    claim_by_id = {(row.get("claim_id") or "").strip(): row for row in claims}
    projects = project_ids(vault / "projects")
    counts["projects"] = len(projects)
    for line, row in enumerate(claims, 2):
        project_id = (row.get("project_id") or "").strip()
        if project_id not in projects:
            errors.append(f"canonical-claims.csv line {line}: missing project card {project_id}.md")

    capability_ids: set[str] = set()
    for line, row in enumerate(capabilities, 2):
        capability_id = (row.get("capability_id") or "").strip()
        if not ID_PATTERNS["capability_id"].fullmatch(capability_id):
            errors.append(f"capability-map.csv line {line}: invalid capability_id {capability_id!r}")
        elif capability_id in capability_ids:
            errors.append(f"capability-map.csv line {line}: duplicate capability_id {capability_id}")
        capability_ids.add(capability_id)
        if (row.get("confidence") or "").strip() not in {"low", "medium", "high"}:
            errors.append(f"capability-map.csv line {line}: invalid confidence")
        status = (row.get("status") or "").strip()
        if status not in {"proposed", "approved", "rejected", "deprecated"}:
            errors.append(f"capability-map.csv line {line}: invalid status {status!r}")
        support = split_ids(row.get("claim_ids") or "")
        if status == "approved" and not support:
            errors.append(f"capability-map.csv line {line}: approved capability has no claims")
        for claim_id in support:
            claim = claim_by_id.get(claim_id)
            if not claim:
                errors.append(f"capability-map.csv line {line}: unknown claim_id {claim_id}")
            elif status == "approved" and claim.get("status") not in {"verified", "user-confirmed"}:
                errors.append(f"capability-map.csv line {line}: approved capability uses ineligible claim {claim_id}")

    review_ids: set[str] = set()
    for line, row in enumerate(reviews, 2):
        review_id = (row.get("review_id") or "").strip()
        if not ID_PATTERNS["review_id"].fullmatch(review_id):
            errors.append(f"review-queue.csv line {line}: invalid review_id {review_id!r}")
        elif review_id in review_ids:
            errors.append(f"review-queue.csv line {line}: duplicate review_id {review_id}")
        review_ids.add(review_id)
        status = (row.get("status") or "").strip()
        if status not in {"pending", "approved", "rejected", "deferred"}:
            errors.append(f"review-queue.csv line {line}: invalid status {status!r}")
        if status in {"approved", "rejected"} and not (row.get("resolved_at") or "").strip():
            errors.append(f"review-queue.csv line {line}: resolved item requires resolved_at")

    change_ids: set[str] = set()
    for line, row in enumerate(changes, 2):
        change_id = (row.get("change_id") or "").strip()
        if not ID_PATTERNS["change_id"].fullmatch(change_id):
            errors.append(f"change-log.csv line {line}: invalid change_id {change_id!r}")
        elif change_id in change_ids:
            errors.append(f"change-log.csv line {line}: duplicate change_id {change_id}")
        change_ids.add(change_id)
    return errors, warnings, counts


def main() -> int:
    args = parse_args()
    vault = Path(args.vault_root).expanduser().resolve()
    if not vault.is_dir():
        print(f"VAULT_SCHEMA_INVALID\n- directory not found: {vault}")
        return 1
    errors, warnings, counts = validate(vault)
    if errors:
        print("VAULT_SCHEMA_INVALID")
        for error in errors:
            print(f"- {error}")
        for warning in warnings:
            print(f"! {warning}")
        return 1
    summary = " ".join(f"{key}={value}" for key, value in sorted(counts.items()))
    print(f"VAULT_SCHEMA_OK {summary}")
    print("NOTE structural validity does not grant truth or publication eligibility")
    for warning in warnings:
        print(f"! {warning}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
