#!/usr/bin/env python3
"""Preview and initialize an empty private Career Proof v0.2 vault."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

from vault_common import DIRECTORIES


FILES = {
    "profile.template.md": "profile.md",
    "career-timeline.template.md": "career-timeline.md",
    "sources.template.csv": "sources.csv",
    "canonical-claims.template.csv": "canonical-claims.csv",
    "capability-map.template.csv": "capability-map.csv",
    "review-queue.template.csv": "review-queue.csv",
    "change-log.template.csv": "change-log.csv",
    "project-card.template.md": "projects/PROJECT-CARD.template.md",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", help="absolute path for the private vault")
    parser.add_argument("--allow-git", action="store_true", help="allow a target inside a Git worktree")
    parser.add_argument("--preview", action="store_true", help="print the exact plan and exit without writing")
    parser.add_argument("--yes", action="store_true", help="confirm the displayed creation plan")
    return parser.parse_args()


def existing_parent(path: Path) -> Path:
    current = path
    while not current.exists() and current.parent != current:
        current = current.parent
    return current


def git_root(path: Path) -> Path | None:
    probe = existing_parent(path)
    for candidate in (probe, *probe.parents):
        if (candidate / ".git").exists():
            return candidate.resolve()
    try:
        result = subprocess.run(
            ["git", "-C", str(probe), "rev-parse", "--show-toplevel"],
            text=True,
            capture_output=True,
            check=False,
        )
    except FileNotFoundError:
        return None
    return Path(result.stdout.strip()).resolve() if result.returncode == 0 else None


def merge_gitignore(target: Path, template: Path) -> int:
    destination = target / ".gitignore"
    required = [line for line in template.read_text(encoding="utf-8").splitlines() if line]
    existing_text = destination.read_text(encoding="utf-8") if destination.exists() else ""
    existing = set(existing_text.splitlines())
    missing = [line for line in required if line not in existing]
    if not missing:
        return 0
    prefix = "" if not existing_text or existing_text.endswith("\n") else "\n"
    with destination.open("a", encoding="utf-8") as handle:
        handle.write(prefix)
        if "# Career Proof private workspace" not in existing:
            handle.write("# Career Proof private workspace\n")
        handle.write("\n".join(missing) + "\n")
    return len(missing)


def main() -> int:
    args = parse_args()
    raw_target = Path(args.target).expanduser()
    if not raw_target.is_absolute():
        print("error: target path must be absolute", file=sys.stderr)
        return 2
    target = raw_target.resolve()
    skill_root = Path(__file__).resolve().parent.parent
    if target == skill_root or skill_root in target.parents:
        print("error: refusing to initialize inside the installed skill", file=sys.stderr)
        return 1
    repository = git_root(target)
    if repository and not args.allow_git:
        print(f"error: target is inside Git worktree {repository}", file=sys.stderr)
        print("Choose a non-Git directory or approve --allow-git explicitly.", file=sys.stderr)
        return 1

    print(f"TARGET {target}")
    print("PLAN")
    for directory in DIRECTORIES:
        print(f"- directory if absent: {directory}/")
    for destination in FILES.values():
        print(f"- file if absent: {destination}")
    print("- merge private-workspace patterns into .gitignore")
    if repository:
        print(f"WARNING_GIT_WORKTREE {repository}")
    if args.preview:
        print("DRY_RUN no files were created; obtain path-specific approval before rerunning with --yes")
        return 0
    if not args.yes:
        try:
            answer = input("Create this private vault? [y/N] ").strip().lower()
        except EOFError:
            answer = ""
        if answer not in {"y", "yes"}:
            print("CANCELLED")
            return 1

    assets = skill_root / "assets"
    target.mkdir(parents=True, exist_ok=True)
    if os.name == "posix":
        target.chmod(0o700)
    for directory in DIRECTORIES:
        child = target / directory
        child.mkdir(exist_ok=True)
        if os.name == "posix":
            child.chmod(0o700)

    created: list[str] = []
    skipped: list[str] = []
    for source_name, destination_name in FILES.items():
        source = assets / source_name
        destination = target / destination_name
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists():
            skipped.append(destination_name)
            continue
        shutil.copyfile(source, destination)
        if os.name == "posix":
            destination.chmod(0o600)
        created.append(destination_name)

    patterns_added = merge_gitignore(target, assets / "vault.gitignore")
    print(f"VAULT_READY {target}")
    print(f"CREATED {len(created)}: {', '.join(created) if created else '-'}")
    print(f"SKIPPED {len(skipped)}: {', '.join(skipped) if skipped else '-'}")
    print(f"GITIGNORE_PATTERNS_ADDED {patterns_added}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
