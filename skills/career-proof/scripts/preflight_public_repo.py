#!/usr/bin/env python3
"""Conservative publication preflight for tracked files and Git history."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path


TEXT_SUFFIXES = {".md", ".txt", ".csv", ".json", ".yaml", ".yml", ".py", ".js", ".ts", ".html", ".css", ".toml", ".gitignore"}
TEXT_FILENAMES = {"LICENSE", "VERSION", ".gitignore"}
ALLOWED_BINARY_SUFFIXES: set[str] = set()
PATTERNS = {
    "absolute POSIX user path": re.compile(r"/(?:Users|home)/[^/\s]+/"),
    "absolute Windows user path": re.compile(r"[A-Za-z]:[\\/]Users[\\/][^\\/\s]+[\\/]", re.I),
    "email address": re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I),
    "China mobile number": re.compile(r"(?<!\d)1[3-9]\d{9}(?!\d)"),
    "GitHub token": re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]{20,})\b"),
    "AWS access key": re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b"),
    "private key": re.compile(r"BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY"),
    "secret assignment": re.compile(r"[\"']?(?:api[_-]?key|access[_-]?token|secret|password)[\"']?\s*[:=]\s*[\"'][^\"']{8,}[\"']", re.I),
}


def run_git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", "-C", str(root), *args], text=True, capture_output=True, check=False)


def scan_text(label: str, text: str, findings: list[str]) -> None:
    for number, line in enumerate(text.splitlines(), 1):
        for pattern_label, pattern in PATTERNS.items():
            if pattern.search(line):
                findings.append(f"{label}:{number}: {pattern_label}")


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: preflight_public_repo.py REPOSITORY_PATH", file=sys.stderr)
        return 2
    root = Path(sys.argv[1]).resolve()
    if not root.is_dir():
        print(f"PUBLIC_PREFLIGHT_FAILED\n- directory not found: {root}")
        return 1
    if run_git(root, "rev-parse", "--is-inside-work-tree").stdout.strip() != "true":
        print("PUBLIC_PREFLIGHT_FAILED\n- target is not a Git worktree")
        return 1

    findings: list[str] = []
    tracked_result = run_git(root, "ls-files", "-z")
    untracked_result = run_git(root, "ls-files", "--others", "--exclude-standard", "-z")
    tracked = [item for item in tracked_result.stdout.split("\0") if item]
    untracked = [item for item in untracked_result.stdout.split("\0") if item]
    working_files = list(dict.fromkeys([*tracked, *untracked]))
    for relative_text in working_files:
        path = root / relative_text
        if not path.is_file():
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES and path.name not in TEXT_FILENAMES:
            if path.suffix.lower() not in ALLOWED_BINARY_SUFFIXES:
                findings.append(f"{relative_text}: tracked binary or unreviewed file type")
            continue
        try:
            scan_text(relative_text, path.read_text(encoding="utf-8"), findings)
        except UnicodeDecodeError:
            findings.append(f"{relative_text}: tracked file is not valid UTF-8")

    commits = [item for item in run_git(root, "rev-list", "--all").stdout.splitlines() if item]
    for commit in commits:
        tree = run_git(root, "ls-tree", "-r", "--name-only", commit)
        for relative_text in tree.stdout.splitlines():
            path = Path(relative_text)
            if path.suffix.lower() not in TEXT_SUFFIXES and path.name not in TEXT_FILENAMES:
                continue
            blob = run_git(root, "show", f"{commit}:{relative_text}")
            if blob.returncode == 0:
                scan_text(f"history {commit[:12]} {relative_text}", blob.stdout, findings)

    unique = list(dict.fromkeys(findings))
    if unique:
        print("PUBLIC_PREFLIGHT_FAILED")
        for finding in unique:
            print(f"- {finding}")
        print("If any finding was a real secret, rotate it even after removing it from Git history.")
        return 1
    print(f"PUBLIC_PREFLIGHT_OK {len(tracked)} tracked files {len(untracked)} untracked files {len(commits)} commits")
    print("NOTE regex preflight cannot guarantee that a repository contains no private information")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
