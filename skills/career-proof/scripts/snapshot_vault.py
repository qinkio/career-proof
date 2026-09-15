#!/usr/bin/env python3
"""Create a metadata snapshot or preview restoration differences."""

from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from vault_common import vault_path


ROOT_FILES = (
    "profile.md", "career-timeline.md", "sources.csv", "canonical-claims.csv",
    "capability-map.csv", "review-queue.csv", "change-log.csv",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("vault_root")
    parser.add_argument("--preview-restore", help="snapshot ZIP to compare against the active vault")
    parser.add_argument("--yes", action="store_true", help="confirm snapshot creation")
    return parser.parse_args()


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def collect(vault: Path) -> dict[str, bytes]:
    files: dict[str, bytes] = {}
    for name in ROOT_FILES:
        path = vault_path(vault, name)
        if path.is_file():
            files[path.relative_to(vault).as_posix()] = path.read_bytes()
    for path in sorted((vault_path(vault, "projects")).glob("*.md")):
        files[path.relative_to(vault).as_posix()] = path.read_bytes()
    for path in vault.rglob("*.md"):
        if path.is_symlink() or any(part in {"archive", "06-历史归档", "exports", "临时输出"} for part in path.relative_to(vault).parts):
            continue
        files[path.relative_to(vault).as_posix()] = path.read_bytes()
    for name in ("claim-aliases.csv", ".vault-layout.json"):
        path = vault_path(vault, name)
        if path.is_file():
            files[path.relative_to(vault).as_posix()] = path.read_bytes()
    return files


def preview_restore(vault: Path, snapshot: Path) -> int:
    if not snapshot.is_file():
        print(f"error: snapshot not found: {snapshot}")
        return 1
    current = {name: digest(data) for name, data in collect(vault).items()}
    with zipfile.ZipFile(snapshot) as archive:
        manifest = json.loads(archive.read("manifest.json").decode("utf-8"))
    previous = manifest.get("files", {})
    added = sorted(set(current) - set(previous))
    missing = sorted(set(previous) - set(current))
    changed = sorted(name for name in set(current).intersection(previous) if current[name] != previous[name])
    print(f"RESTORE_PREVIEW snapshot={snapshot} added_now={len(added)} missing_now={len(missing)} changed={len(changed)}")
    for label, names in (("ADDED_NOW", added), ("MISSING_NOW", missing), ("CHANGED", changed)):
        for name in names:
            print(f"{label} {name}")
    print("NOTE preview only; this tool does not overwrite the active vault")
    return 0


def main() -> int:
    args = parse_args()
    vault = Path(args.vault_root).expanduser().resolve()
    if not vault.is_dir():
        print(f"error: vault not found: {vault}")
        return 1
    if args.preview_restore:
        return preview_restore(vault, Path(args.preview_restore).expanduser().resolve())

    files = collect(vault)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    snapshot_id = f"SNP-{stamp}"
    output = vault_path(vault, "archive") / f"{snapshot_id}.zip"
    print(f"SNAPSHOT_PLAN id={snapshot_id} files={len(files)} output={output}")
    print("EXCLUDES external source documents, evidence binaries, exports, and prior archives")
    if not args.yes:
        print("DRY_RUN rerun with --yes to create the snapshot")
        return 0
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        print(f"error: refusing to overwrite snapshot: {output}")
        return 1
    manifest = {
        "snapshot_id": snapshot_id,
        "created_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "files": {name: digest(data) for name, data in files.items()},
    }
    with zipfile.ZipFile(output, "x", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, data in files.items():
            archive.writestr(name, data)
        archive.writestr("manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    print(f"SNAPSHOT_READY {snapshot_id} {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
