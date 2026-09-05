#!/usr/bin/env python3
"""Migrate a Career Proof v0.1 vault into a separate v0.2 vault."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

from vault_common import TABLES, next_id, read_csv, utc_now, write_csv


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source_vault")
    parser.add_argument("target_vault")
    parser.add_argument("--yes", action="store_true", help="confirm creation of the migration copy")
    return parser.parse_args()


def source_type(path: Path) -> str:
    return {
        ".pdf": "pdf", ".docx": "docx", ".pptx": "pptx", ".xlsx": "xlsx",
        ".md": "markdown", ".csv": "csv", ".txt": "text",
    }.get(path.suffix.lower(), "other")


def privacy_axes(old: str) -> tuple[str, str]:
    mapping = {
        "public": ("public", "not-approved"),
        "external-approved": ("personal-sensitive", "application-only"),
        "personal-sensitive": ("personal-sensitive", "not-approved"),
        "local-sensitive": ("personal-sensitive", "not-approved"),
        "company-confidential": ("company-sensitive", "not-approved"),
        "do-not-upload": ("restricted", "not-approved"),
        "do-not-model": ("restricted", "not-approved"),
    }
    return mapping.get(old, ("personal-sensitive", "not-approved"))


def locate_claims(source: Path) -> Path | None:
    for name in ("canonical_claims.csv", "canonical-claims.csv"):
        path = source / name
        if path.is_file():
            return path
    return None


def locate_project(source: Path, project_id: str) -> Path | None:
    for directory in (source / "projects", source / "项目证据卡"):
        if not directory.is_dir():
            continue
        matches = sorted(directory.glob(f"{project_id}*.md"))
        if matches:
            return matches[0]
    return None


def placeholder_project(project_id: str) -> str:
    return f"""# 项目证据卡 / Project Card: {project_id}

## 项目边界

- 项目名称：迁移项目，待确认
- 父项目ID：
- 开始与结束：
- 核心业务目标：
- 为什么这些资料属于同一项目：由v0.1 Claim引用迁移，需人工复核
- 状态：proposed

## 背景与对象

- 业务背景：
- 用户：
- 关键协作方：
- 正式职称：
- 实际职责：

## 问题与基线

## 关键判断、决策与行动

## 结果与口径

- Claim IDs：

## 所有权边界

## 证据

## 可证明能力

## 待审核问题

- 确认项目边界和名称。
"""


def main() -> int:
    args = parse_args()
    source = Path(args.source_vault).expanduser().resolve()
    target = Path(args.target_vault).expanduser().resolve()
    if not source.is_dir():
        print(f"error: source vault not found: {source}", file=sys.stderr)
        return 1
    if target.exists():
        print(f"error: refusing to overwrite existing target: {target}", file=sys.stderr)
        return 1
    claims_path = locate_claims(source)
    if not claims_path:
        print("error: v0.1 canonical claims CSV not found", file=sys.stderr)
        return 1
    try:
        _, old_claims = read_csv(claims_path)
    except (OSError, UnicodeError) as exc:
        print(f"error: cannot read legacy claims: {exc}", file=sys.stderr)
        return 1

    print(f"SOURCE {source}")
    print(f"TARGET {target}")
    print(f"PLAN create a v0.2 copy for {len(old_claims)} claims; preserve the source; queue ambiguous permissions and metrics")
    if not args.yes:
        print("DRY_RUN rerun with --yes to create the migration copy")
        return 0

    init_script = Path(__file__).resolve().with_name("init_vault.py")
    result = subprocess.run(
        [sys.executable, str(init_script), str(target), "--yes"],
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        print(result.stdout, end="")
        print(result.stderr, end="", file=sys.stderr)
        return result.returncode

    for old_name, new_name in (("00-profile.md", "profile.md"), ("01-career-timeline.md", "career-timeline.md")):
        old_path = source / old_name
        if old_path.is_file():
            shutil.copyfile(old_path, target / new_name)

    source_rows: list[dict[str, str]] = []
    source_id_by_path: dict[str, str] = {}
    claim_rows: list[dict[str, str]] = []
    review_rows: list[dict[str, str]] = []
    project_ids: set[str] = set()
    now = utc_now()

    for old in old_claims:
        raw_project = (old.get("project_id") or "").strip() or "MIGRATED"
        project_id = raw_project if raw_project.startswith("PRJ-") else f"PRJ-{raw_project}"
        project_ids.add(project_id)
        old_privacy = (old.get("privacy") or "").strip()
        sensitivity, permission = privacy_axes(old_privacy)
        raw_path = (old.get("source_path") or "").strip()
        source_ids = ""
        if raw_path:
            resolved = Path(raw_path).expanduser()
            resolved = resolved.resolve() if resolved.is_absolute() else (source / resolved).resolve()
            key = str(resolved)
            if key not in source_id_by_path:
                source_id = next_id("SRC", source_id_by_path.values())
                source_id_by_path[key] = source_id
                try:
                    stat = resolved.stat()
                    size, modified, fkey, status = str(stat.st_size), str(stat.st_mtime_ns), f"{stat.st_dev}:{stat.st_ino}", "active"
                except OSError:
                    size = modified = fkey = ""
                    status = "missing"
                source_rows.append({
                    "source_id": source_id,
                    "path": key,
                    "source_type": source_type(resolved),
                    "size_bytes": size,
                    "modified_at": modified,
                    "file_key": fkey,
                    "content_sha256": "",
                    "sensitivity": sensitivity,
                    "model_access": "do-not-model" if old_privacy in {"do-not-upload", "do-not-model"} else "pending",
                    "publication_permission": permission,
                    "status": status,
                    "last_indexed_at": now,
                    "notes": "Migrated metadata only; content access requires review.",
                })
            source_ids = source_id_by_path[key]

        status = (old.get("status") or "pending").strip()
        claim_type = (old.get("claim_type") or "action").strip()
        metric_definition = (old.get("metric_definition") or "").strip()
        needs_metric_review = claim_type in {"metric", "scale"}
        if needs_metric_review:
            status = "pending"
        elif status == "verified" and not source_ids:
            status = "pending"
        claim_id = (old.get("claim_id") or "").strip() or next_id("CLM", (row["claim_id"] for row in claim_rows))
        claim_rows.append({
            "claim_id": claim_id,
            "project_id": project_id,
            "claim_text": (old.get("claim_text") or "").strip(),
            "claim_type": claim_type,
            "ownership": (old.get("ownership") or "unknown").strip(),
            "source_ids": source_ids,
            "source_locators": (old.get("source_locator") or "").strip(),
            "metric_name": "",
            "metric_baseline": "",
            "metric_result": "",
            "metric_unit": "",
            "metric_time_window": "",
            "metric_population": "",
            "metric_calculation": metric_definition,
            "status": status,
            "sensitivity": sensitivity,
            "publication_permission": permission,
            "valid_from": "",
            "valid_to": "",
            "supersedes_claim_id": "",
            "withdrawn_at": "",
            "notes": (old.get("notes") or "").strip(),
        })
        if old_privacy in {"public", "", "personal-sensitive", "local-sensitive", "company-confidential"}:
            review_rows.append({
                "review_id": next_id("REV", (row["review_id"] for row in review_rows)),
                "item_type": "permission",
                "item_id": claim_id,
                "project_id": project_id,
                "question": "Confirm sensitivity and purpose-specific publication permission after migration.",
                "proposed_value": f"{sensitivity}|{permission}",
                "current_value": old_privacy,
                "evidence_ids": source_ids,
                "risk": "high" if sensitivity == "company-sensitive" else "medium",
                "decision": "",
                "status": "pending",
                "created_at": now,
                "resolved_at": "",
                "notes": "Legacy privacy vocabulary does not map one-to-one to v0.2 axes.",
            })
        if needs_metric_review:
            review_rows.append({
                "review_id": next_id("REV", (row["review_id"] for row in review_rows)),
                "item_type": "metric",
                "item_id": claim_id,
                "project_id": project_id,
                "question": "Split the legacy metric into name, baseline, result, unit, period, population, calculation, and attribution.",
                "proposed_value": metric_definition,
                "current_value": "",
                "evidence_ids": source_ids,
                "risk": "high",
                "decision": "",
                "status": "pending",
                "created_at": now,
                "resolved_at": "",
                "notes": "Migrated metric remains pending until structured review.",
            })

    for project_id in sorted(project_ids):
        destination = target / "projects" / f"{project_id}.md"
        original = locate_project(source, project_id)
        if original:
            shutil.copyfile(original, destination)
        else:
            destination.write_text(placeholder_project(project_id), encoding="utf-8")

    write_csv(target / "sources.csv", TABLES["sources.csv"], source_rows)
    write_csv(target / "canonical-claims.csv", TABLES["canonical-claims.csv"], claim_rows)
    write_csv(target / "review-queue.csv", TABLES["review-queue.csv"], review_rows)
    write_csv(target / "change-log.csv", TABLES["change-log.csv"], [{
        "change_id": "CHG-0001",
        "changed_at": now,
        "actor": "migrate_v01_to_v02.py",
        "entity_type": "vault",
        "entity_id": "VAULT",
        "action": "migration-copy-created",
        "from_value": str(source),
        "to_value": str(target),
        "reason": "Career Proof v0.1 to v0.2 migration",
        "snapshot_id": "",
    }])
    if os.name == "posix":
        for path in target.glob("*.csv"):
            path.chmod(0o600)
    print(f"MIGRATION_COPY_READY claims={len(claim_rows)} sources={len(source_rows)} projects={len(project_ids)} review_items={len(review_rows)} target={target}")
    print("REVIEW_REQUIRED migrated permissions, metrics, ownership, and project boundaries remain subject to human approval")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
