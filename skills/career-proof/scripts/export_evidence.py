#!/usr/bin/env python3
"""Create a minimal, purpose-bound Career Proof JSON evidence package."""

from __future__ import annotations

import argparse
import json
import sys
import uuid
from collections import Counter
from pathlib import Path

from audit_claims import PURPOSES, eligibility
from vault_common import SCHEMA_VERSION, read_csv, split_ids, utc_now


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("vault_root")
    parser.add_argument("output_json")
    parser.add_argument("--purpose", choices=sorted(PURPOSES), required=True)
    parser.add_argument("--project-ids", default="", help="pipe- or comma-separated project IDs")
    parser.add_argument("--claim-ids", default="", help="pipe- or comma-separated claim IDs")
    parser.add_argument("--yes", action="store_true", help="confirm the displayed export plan")
    return parser.parse_args()


def parse_scope(value: str) -> set[str]:
    return {item.strip() for item in value.replace(",", "|").split("|") if item.strip()}


def parse_project(path: Path) -> dict[str, str]:
    result = {"project_id": path.stem, "title": path.stem}
    prefixes = {
        "- 项目名称：": "title",
        "- 父项目ID：": "parent_project_id",
        "- 开始与结束：": "date_range",
        "- 核心业务目标：": "objective",
        "- 正式职称：": "formal_title",
        "- 实际职责：": "actual_responsibility",
    }
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError):
        return result
    for line in lines:
        for prefix, field in prefixes.items():
            if line.startswith(prefix):
                result[field] = line[len(prefix):].strip()
    return result


def public_claim(row: dict[str, str], sources: dict[str, dict[str, str]]) -> dict[str, object]:
    source_evidence = []
    for source_id in split_ids(row.get("source_ids", "")):
        source = sources.get(source_id, {})
        source_evidence.append({
            "source_id": source_id,
            "source_type": source.get("source_type", ""),
            "model_access": source.get("model_access", ""),
            "status": source.get("status", ""),
        })
    return {
        "claim_id": row.get("claim_id"),
        "project_id": row.get("project_id"),
        "claim_text": row.get("claim_text"),
        "claim_type": row.get("claim_type"),
        "ownership": row.get("ownership"),
        "metric": {
            "name": row.get("metric_name"),
            "baseline": row.get("metric_baseline"),
            "result": row.get("metric_result"),
            "unit": row.get("metric_unit"),
            "time_window": row.get("metric_time_window"),
            "population": row.get("metric_population"),
            "calculation": row.get("metric_calculation"),
        },
        "status": row.get("status"),
        "sensitivity": row.get("sensitivity"),
        "publication_permission": row.get("publication_permission"),
        "source_evidence": source_evidence,
    }


def main() -> int:
    args = parse_args()
    vault = Path(args.vault_root).expanduser().resolve()
    output = Path(args.output_json).expanduser().resolve()
    project_scope = parse_scope(args.project_ids)
    claim_scope = parse_scope(args.claim_ids)
    if not project_scope and not claim_scope:
        print("error: a minimal export requires --project-ids or --claim-ids", file=sys.stderr)
        return 2
    if output.exists():
        print(f"error: refusing to overwrite existing export: {output}", file=sys.stderr)
        return 1
    try:
        _, claim_rows = read_csv(vault / "canonical-claims.csv")
        _, source_rows = read_csv(vault / "sources.csv")
        _, capability_rows = read_csv(vault / "capability-map.csv")
    except (OSError, UnicodeError) as exc:
        print(f"error: cannot read vault tables: {exc}", file=sys.stderr)
        return 1
    sources = {row["source_id"]: row for row in source_rows}

    selected = [
        row for row in claim_rows
        if (row.get("claim_id") in claim_scope) or (row.get("project_id") in project_scope)
    ]
    if not selected:
        print("error: export scope matched no claims", file=sys.stderr)
        return 1
    included: list[dict[str, object]] = []
    exclusions: Counter[str] = Counter()
    included_ids: set[str] = set()
    for row in selected:
        reasons = eligibility(row, sources, args.purpose)
        if reasons:
            exclusions.update(reasons)
            continue
        included.append(public_claim(row, sources))
        included_ids.add(row["claim_id"])
    included_projects = {str(row["project_id"]) for row in included}
    projects = []
    for project_id in sorted(included_projects):
        path = vault / "projects" / f"{project_id}.md"
        projects.append(parse_project(path) if path.is_file() else {"project_id": project_id})

    capabilities = []
    for row in capability_rows:
        support = set(split_ids(row.get("claim_ids", "")))
        if row.get("status") == "approved" and support.intersection(included_ids):
            capabilities.append({
                "capability_id": row.get("capability_id"),
                "standard_skill": row.get("standard_skill"),
                "industry_skill": row.get("industry_skill"),
                "original_expression": row.get("original_expression"),
                "category": row.get("category"),
                "supporting_claim_ids": sorted(support.intersection(included_ids)),
                "confidence": row.get("confidence"),
            })

    export_id = f"EXP-{uuid.uuid4().hex[:12].upper()}"
    package = {
        "schema_version": SCHEMA_VERSION,
        "export_id": export_id,
        "generated_at": utc_now(),
        "purpose": args.purpose,
        "scope": {"project_ids": sorted(project_scope), "claim_ids": sorted(claim_scope)},
        "profile": {},
        "projects": projects,
        "claims": included,
        "capabilities": capabilities,
        "exclusions": {"counts_by_reason": dict(sorted(exclusions.items()))},
        "warnings": ["Profile omitted by the deterministic exporter; add only approved task-specific context."],
    }
    print(f"EXPORT_PLAN id={export_id} purpose={args.purpose} selected={len(selected)} included={len(included)} excluded={len(selected) - len(included)} output={output}")
    if not included:
        print("error: no eligible claims remain after purpose and permission checks", file=sys.stderr)
        return 1
    if not args.yes:
        print("DRY_RUN rerun with --yes to create the JSON package")
        return 0
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(package, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"EVIDENCE_EXPORT_READY {export_id} {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
