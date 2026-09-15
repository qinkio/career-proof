#!/usr/bin/env python3
"""Shared constants and helpers for Career Proof v0.2 scripts."""

from __future__ import annotations

import csv
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


SCHEMA_VERSION = "0.2.0"
TABLES = {
    "sources.csv": [
        "source_id", "path", "source_type", "size_bytes", "modified_at", "file_key",
        "content_sha256", "sensitivity", "model_access", "publication_permission",
        "status", "last_indexed_at", "notes",
    ],
    "canonical-claims.csv": [
        "claim_id", "project_id", "claim_text", "claim_type", "ownership", "source_ids",
        "source_locators", "metric_name", "metric_baseline", "metric_result", "metric_unit",
        "metric_time_window", "metric_population", "metric_calculation", "status",
        "sensitivity", "publication_permission", "valid_from", "valid_to",
        "supersedes_claim_id", "withdrawn_at", "notes",
    ],
    "capability-map.csv": [
        "capability_id", "standard_skill", "industry_skill", "original_expression", "category",
        "claim_ids", "project_ids", "confidence", "status", "notes",
    ],
    "review-queue.csv": [
        "review_id", "item_type", "item_id", "project_id", "question", "proposed_value",
        "current_value", "evidence_ids", "risk", "decision", "status", "created_at",
        "resolved_at", "notes",
    ],
    "change-log.csv": [
        "change_id", "changed_at", "actor", "entity_type", "entity_id", "action",
        "from_value", "to_value", "reason", "snapshot_id",
    ],
}
DIRECTORIES = ("projects", "evidence", "exports", "archive")
ID_PATTERNS = {
    "source_id": re.compile(r"^SRC-[A-Z0-9][A-Z0-9-]*$"),
    "project_id": re.compile(r"^PRJ-[A-Z0-9][A-Z0-9-]*$"),
    "claim_id": re.compile(r"^CLM-[A-Z0-9][A-Z0-9-]*$"),
    "capability_id": re.compile(r"^CAP-[A-Z0-9][A-Z0-9-]*$"),
    "review_id": re.compile(r"^REV-[A-Z0-9][A-Z0-9-]*$"),
    "change_id": re.compile(r"^CHG-[A-Z0-9][A-Z0-9-]*$"),
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), [dict(row) for row in reader]


def write_csv(path: Path, fields: list[str], rows: Iterable[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def split_ids(value: str) -> list[str]:
    return [item.strip() for item in value.split("|") if item.strip()]


def next_id(prefix: str, existing: Iterable[str]) -> str:
    highest = 0
    pattern = re.compile(rf"^{re.escape(prefix)}-(\d+)$")
    for value in existing:
        match = pattern.fullmatch(value)
        if match:
            highest = max(highest, int(match.group(1)))
    return f"{prefix}-{highest + 1:04d}"


def project_ids(project_dir: Path) -> set[str]:
    return {path.stem for path in project_dir.glob("PRJ-*.md")}


HUMAN_PATHS = {
    "profile.md": "01-个人经历/个人背景.md",
    "career-timeline.md": "01-个人经历/职业时间线.md",
    "sources.csv": "04-证据与来源/来源登记.csv",
    "canonical-claims.csv": "05-事实与维护/已记录事实.csv",
    "capability-map.csv": "05-事实与维护/能力映射.csv",
    "review-queue.csv": "05-事实与维护/待补充与审核.csv",
    "change-log.csv": "05-事实与维护/修改记录.csv",
    "claim-aliases.csv": "05-事实与维护/事实合并索引.csv",
    "projects": "02-项目库/项目详情",
    "evidence": "04-证据与来源/证据资料",
    "exports": "03-求职记录/临时输出",
    "archive": "06-历史归档",
}


def vault_path(vault: Path, name: str) -> Path:
    """Resolve a logical role without requiring root compatibility copies."""
    layout = vault / ".vault-layout.json"
    mappings = json.loads(layout.read_text(encoding="utf-8")) if layout.is_file() else {}
    if not isinstance(mappings, dict):
        raise ValueError("vault layout must be an object")
    if name in mappings:
        relative = mappings[name]
        if not isinstance(relative, str) or Path(relative).is_absolute():
            raise ValueError(f"invalid relative layout path: {name}")
        target = vault / relative
        if not target.resolve().is_relative_to(vault.resolve()):
            raise ValueError(f"layout path escapes vault: {name}")
        return target
    human = vault / HUMAN_PATHS[name] if name in HUMAN_PATHS else None
    return human if human is not None and human.exists() else vault / name
