#!/usr/bin/env python3
"""Preview or write a metadata-only, incremental source index."""

from __future__ import annotations

import argparse
import hashlib
import os
import sys
from pathlib import Path

from vault_common import TABLES, next_id, read_csv, utc_now, write_csv


TYPE_BY_SUFFIX = {
    ".pdf": "pdf",
    ".docx": "docx",
    ".pptx": "pptx",
    ".xlsx": "xlsx",
    ".md": "markdown",
    ".csv": "csv",
    ".txt": "text",
}
SKIP_DIRS = {".git", ".svn", "node_modules", "__pycache__"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source_root")
    parser.add_argument("vault_root")
    parser.add_argument("--approved-paths", help="UTF-8 file listing content-approved paths, one per line")
    parser.add_argument("--include-other", action="store_true", help="index unsupported extensions as type other")
    parser.add_argument("--yes", action="store_true", help="write the displayed index plan")
    return parser.parse_args()


def load_approved(path: str | None, source_root: Path) -> set[Path]:
    if not path:
        return set()
    approved_file = Path(path).expanduser().resolve()
    approved: set[Path] = set()
    for line in approved_file.read_text(encoding="utf-8").splitlines():
        value = line.strip()
        if not value or value.startswith("#"):
            continue
        candidate = Path(value).expanduser()
        approved.add((candidate if candidate.is_absolute() else source_root / candidate).resolve())
    return approved


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def file_key(stat: os.stat_result) -> str:
    return f"{getattr(stat, 'st_dev', 0)}:{getattr(stat, 'st_ino', 0)}"


def iter_sources(root: Path, vault: Path, include_other: bool):
    for current, dirs, files in os.walk(root):
        current_path = Path(current).resolve()
        dirs[:] = [
            name for name in dirs
            if name not in SKIP_DIRS and not name.startswith(".")
            and (current_path / name).resolve() != vault
        ]
        for name in sorted(files):
            if name.startswith("."):
                continue
            path = (current_path / name).resolve()
            suffix = path.suffix.lower()
            if suffix not in TYPE_BY_SUFFIX and not include_other:
                continue
            yield path, TYPE_BY_SUFFIX.get(suffix, "other")


def append_change(change_rows: list[dict[str, str]], action: str, source_id: str, before: str, after: str) -> None:
    change_id = next_id("CHG", (row.get("change_id", "") for row in change_rows))
    change_rows.append({
        "change_id": change_id,
        "changed_at": utc_now(),
        "actor": "index_sources.py",
        "entity_type": "source",
        "entity_id": source_id,
        "action": action,
        "from_value": before,
        "to_value": after,
        "reason": "incremental source index",
        "snapshot_id": "",
    })


def main() -> int:
    args = parse_args()
    source_root = Path(args.source_root).expanduser().resolve()
    vault = Path(args.vault_root).expanduser().resolve()
    if not source_root.is_dir():
        print(f"error: source root not found: {source_root}", file=sys.stderr)
        return 1
    sources_path = vault / "sources.csv"
    changes_path = vault / "change-log.csv"
    if not sources_path.is_file() or not changes_path.is_file():
        print("error: target is not an initialized v0.2 vault", file=sys.stderr)
        return 1

    approved = load_approved(args.approved_paths, source_root)
    _, rows = read_csv(sources_path)
    _, change_rows = read_csv(changes_path)
    by_path = {Path(row["path"]).expanduser().resolve(): row for row in rows if row.get("path")}
    by_key = {row.get("file_key", ""): row for row in rows if row.get("file_key")}
    seen_ids: set[str] = set()
    added = moved = changed = unchanged = errored = hashed = 0

    for path, source_type in iter_sources(source_root, vault, args.include_other):
        try:
            stat = path.stat()
        except OSError:
            errored += 1
            continue
        key = file_key(stat)
        row = by_path.get(path) or by_key.get(key)
        old_path = row.get("path", "") if row else ""
        old_size = row.get("size_bytes", "") if row else ""
        old_modified = row.get("modified_at", "") if row else ""
        if row is None:
            source_id = next_id("SRC", (item.get("source_id", "") for item in rows))
            row = {field: "" for field in TABLES["sources.csv"]}
            row.update({
                "source_id": source_id,
                "sensitivity": "personal-sensitive",
                "model_access": "allowed" if path in approved else "pending",
                "publication_permission": "not-approved",
                "status": "active",
            })
            rows.append(row)
            added += 1
            append_change(change_rows, "source-added", source_id, "", str(path))
        elif old_path and Path(old_path).expanduser().resolve() != path:
            moved += 1
            append_change(change_rows, "source-moved", row["source_id"], old_path, str(path))

        modified_at = str(stat.st_mtime_ns)
        size = str(stat.st_size)
        if old_size and (old_size != size or old_modified != modified_at):
            changed += 1
            append_change(change_rows, "source-changed", row["source_id"], f"{old_size}:{old_modified}", f"{size}:{modified_at}")
        elif old_size:
            unchanged += 1

        row.update({
            "path": str(path),
            "source_type": source_type,
            "size_bytes": size,
            "modified_at": modified_at,
            "file_key": key,
            "status": "active",
            "last_indexed_at": utc_now(),
        })
        if path in approved:
            row["model_access"] = "allowed"
        if row.get("model_access") == "allowed":
            try:
                row["content_sha256"] = sha256(path)
                hashed += 1
            except OSError as exc:
                row["status"] = "error"
                row["notes"] = f"hash failed: {exc}"
                errored += 1
        elif row.get("model_access") == "do-not-model":
            row["content_sha256"] = ""
        seen_ids.add(row["source_id"])

    missing = 0
    for row in rows:
        path_text = row.get("path", "")
        if row.get("source_id") in seen_ids or not path_text:
            continue
        try:
            under_root = Path(path_text).expanduser().resolve().is_relative_to(source_root)
        except (OSError, ValueError):
            under_root = False
        if under_root and row.get("status") != "missing":
            row["status"] = "missing"
            missing += 1
            append_change(change_rows, "source-missing", row["source_id"], path_text, "missing")

    hashes: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        if row.get("content_sha256"):
            hashes.setdefault(row["content_sha256"], []).append(row)
    duplicates = 0
    for group in hashes.values():
        if len(group) > 1:
            duplicates += len(group)
            for row in group:
                row["status"] = "duplicate-candidate"

    print(f"SOURCE_ROOT {source_root}")
    print(f"VAULT_ROOT {vault}")
    print(f"PLAN added={added} moved={moved} changed={changed} unchanged={unchanged} missing={missing} duplicate_candidates={duplicates} hashed={hashed} errors={errored}")
    if not args.yes:
        print("DRY_RUN rerun with --yes to write sources.csv and change-log.csv")
        return 0
    write_csv(sources_path, TABLES["sources.csv"], rows)
    write_csv(changes_path, TABLES["change-log.csv"], change_rows)
    print(f"SOURCE_INDEX_UPDATED {len(rows)} records")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
