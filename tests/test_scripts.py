from __future__ import annotations

import csv
import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "career-proof" / "scripts"


def run(script: str, *args: object, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPTS / script), *map(str, args)],
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
    )


def read_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def write_rows(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def add_project(vault: Path, project_id: str = "PRJ-001") -> None:
    (vault / "projects" / f"{project_id}.md").write_text(
        f"# 项目证据卡 / Project Card: {project_id}\n\n"
        "- 项目名称：虚构流程项目\n"
        "- 父项目ID：\n"
        "- 开始与结束：2025-01 至 2025-03\n"
        "- 核心业务目标：缩短虚构审批流程\n"
        "- 正式职称：虚构运营\n"
        "- 实际职责：流程梳理与上线协作\n",
        encoding="utf-8",
    )


def append_source(vault: Path, source_id: str = "SRC-0001") -> Path:
    evidence = vault / "evidence" / "fictional.md"
    evidence.write_text("Fictional evidence only.\n", encoding="utf-8")
    fields, rows = read_rows(vault / "sources.csv")
    stat = evidence.stat()
    rows.append({
        "source_id": source_id,
        "path": str(evidence),
        "source_type": "markdown",
        "size_bytes": str(stat.st_size),
        "modified_at": str(stat.st_mtime_ns),
        "file_key": f"{stat.st_dev}:{stat.st_ino}",
        "content_sha256": "fictional-hash",
        "sensitivity": "public",
        "model_access": "allowed",
        "publication_permission": "public-approved",
        "status": "active",
        "last_indexed_at": "2026-01-01T00:00:00Z",
        "notes": "fictional fixture",
    })
    write_rows(vault / "sources.csv", fields, rows)
    return evidence


def append_claim(
    vault: Path,
    claim_id: str = "CLM-0001",
    text: str = "Redesigned a fictional approval workflow",
    result: str = "",
) -> None:
    fields, rows = read_rows(vault / "canonical-claims.csv")
    rows.append({
        "claim_id": claim_id,
        "project_id": "PRJ-001",
        "claim_text": text,
        "claim_type": "metric" if result else "action",
        "ownership": "owned",
        "source_ids": "SRC-0001",
        "source_locators": "section 1",
        "metric_name": "cycle time" if result else "",
        "metric_baseline": "10" if result else "",
        "metric_result": result,
        "metric_unit": "days" if result else "",
        "metric_time_window": "2025-Q1" if result else "",
        "metric_population": "fictional workflow cases" if result else "",
        "metric_calculation": "median completion days" if result else "",
        "status": "verified",
        "sensitivity": "public",
        "publication_permission": "public-approved",
        "valid_from": "2026-01-01",
        "valid_to": "",
        "supersedes_claim_id": "",
        "withdrawn_at": "",
        "notes": "fictional fixture",
    })
    write_rows(vault / "canonical-claims.csv", fields, rows)


class CareerProofScriptTests(unittest.TestCase):
    def init_vault(self, root: Path) -> Path:
        vault = root / "vault"
        result = run("init_vault.py", vault, "--yes")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return vault

    def test_initializer_and_empty_vault_validate(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            vault = root / "vault"
            preview = run("init_vault.py", vault, "--preview")
            self.assertEqual(preview.returncode, 0, preview.stdout + preview.stderr)
            self.assertIn("DRY_RUN", preview.stdout)
            self.assertFalse(vault.exists())
            vault = self.init_vault(root)
            second = run("init_vault.py", vault, "--yes")
            self.assertEqual(second.returncode, 0, second.stdout + second.stderr)
            self.assertIn("CREATED 0", second.stdout)
            result = run("validate_vault.py", vault)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("VAULT_SCHEMA_OK", result.stdout)

    def test_initializer_refuses_git_worktree_without_override(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            result = run("init_vault.py", root / "vault", "--yes")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Git worktree", result.stderr)

    def test_index_is_dry_run_then_incremental_and_permission_aware(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            vault = self.init_vault(root)
            source_root = root / "sources"
            source_root.mkdir()
            document = source_root / "fictional.md"
            document.write_text("fictional content\n", encoding="utf-8")

            dry = run("index_sources.py", source_root, vault)
            self.assertEqual(dry.returncode, 0, dry.stdout + dry.stderr)
            self.assertIn("DRY_RUN", dry.stdout)
            self.assertEqual(read_rows(vault / "sources.csv")[1], [])

            written = run("index_sources.py", source_root, vault, "--yes")
            self.assertEqual(written.returncode, 0, written.stdout + written.stderr)
            fields, rows = read_rows(vault / "sources.csv")
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["model_access"], "pending")
            self.assertEqual(rows[0]["content_sha256"], "")

            rows[0]["model_access"] = "allowed"
            write_rows(vault / "sources.csv", fields, rows)
            hashed = run("index_sources.py", source_root, vault, "--yes")
            self.assertEqual(hashed.returncode, 0, hashed.stdout + hashed.stderr)
            rows = read_rows(vault / "sources.csv")[1]
            self.assertTrue(rows[0]["content_sha256"])
            source_id = rows[0]["source_id"]

            moved = source_root / "renamed.md"
            document.rename(moved)
            moved_result = run("index_sources.py", source_root, vault, "--yes")
            self.assertEqual(moved_result.returncode, 0, moved_result.stdout + moved_result.stderr)
            rows = read_rows(vault / "sources.csv")[1]
            self.assertEqual(rows[0]["source_id"], source_id)
            self.assertEqual(Path(rows[0]["path"]), moved.resolve())

    def test_do_not_model_source_cannot_keep_hash(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            vault = self.init_vault(Path(directory))
            append_source(vault)
            fields, rows = read_rows(vault / "sources.csv")
            rows[0]["model_access"] = "do-not-model"
            write_rows(vault / "sources.csv", fields, rows)
            result = run("validate_vault.py", vault)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("must not retain content_sha256", result.stdout)

    def test_claim_validation_and_candidate_detection(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            vault = self.init_vault(Path(directory))
            add_project(vault)
            append_source(vault)
            append_claim(vault)
            append_claim(vault, "CLM-0002", "Redesigned the fictional approval workflow")
            valid = run("validate_vault.py", vault)
            self.assertEqual(valid.returncode, 0, valid.stdout + valid.stderr)
            candidates = run("detect_claim_candidates.py", vault / "canonical-claims.csv")
            self.assertEqual(candidates.returncode, 0, candidates.stdout + candidates.stderr)
            self.assertIn('"kind": "duplicate"', candidates.stdout)

    def test_metric_conflict_candidate(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            vault = self.init_vault(Path(directory))
            add_project(vault)
            append_source(vault)
            append_claim(vault, "CLM-0001", "Reduced fictional cycle time to six days", "6")
            append_claim(vault, "CLM-0002", "A separate statement about cycle time", "7")
            result = run("detect_claim_candidates.py", vault / "canonical-claims.csv")
            self.assertIn('"kind": "conflict"', result.stdout)

    def test_scoped_export_omits_paths_and_requires_scope(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            vault = self.init_vault(Path(directory))
            add_project(vault)
            evidence = append_source(vault)
            append_claim(vault)
            output = vault / "exports" / "interview.json"
            no_scope = run("export_evidence.py", vault, output, "--purpose", "interview", "--yes")
            self.assertNotEqual(no_scope.returncode, 0)
            result = run(
                "export_evidence.py", vault, output, "--purpose", "interview",
                "--project-ids", "PRJ-001", "--yes",
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            package = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(package["schema_version"], "0.2.0")
            self.assertEqual(len(package["claims"]), 1)
            self.assertNotIn(str(evidence), output.read_text(encoding="utf-8"))

    def test_snapshot_and_restore_preview(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            vault = self.init_vault(Path(directory))
            result = run("snapshot_vault.py", vault, "--yes")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            snapshots = list((vault / "archive").glob("SNP-*.zip"))
            self.assertEqual(len(snapshots), 1)
            with zipfile.ZipFile(snapshots[0]) as archive:
                self.assertIn("manifest.json", archive.namelist())
            (vault / "profile.md").write_text("changed\n", encoding="utf-8")
            preview = run("snapshot_vault.py", vault, "--preview-restore", snapshots[0])
            self.assertEqual(preview.returncode, 0, preview.stdout + preview.stderr)
            self.assertIn("CHANGED profile.md", preview.stdout)

    def test_v01_migration_creates_copy_and_review_queue(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            old = root / "old"
            old.mkdir()
            claims = old / "canonical_claims.csv"
            fields = [
                "claim_id", "project_id", "claim_text", "claim_type", "ownership",
                "source_type", "source_path", "source_locator", "metric_definition",
                "status", "privacy", "notes",
            ]
            write_rows(claims, fields, [{
                "claim_id": "CLM-001",
                "project_id": "DEMO",
                "claim_text": "Improved a fictional metric",
                "claim_type": "metric",
                "ownership": "owned",
                "source_type": "user-confirmed",
                "source_path": "",
                "source_locator": "confirmed fixture",
                "metric_definition": "fictional definition",
                "status": "user-confirmed",
                "privacy": "public",
                "notes": "fictional",
            }])
            before = claims.read_bytes()
            target = root / "new"
            result = run("migrate_v01_to_v02.py", old, target, "--yes")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(claims.read_bytes(), before)
            migrated = read_rows(target / "canonical-claims.csv")[1]
            self.assertEqual(migrated[0]["project_id"], "PRJ-DEMO")
            self.assertEqual(migrated[0]["status"], "pending")
            reviews = read_rows(target / "review-queue.csv")[1]
            self.assertGreaterEqual(len(reviews), 2)
            self.assertTrue((target / "projects" / "PRJ-DEMO.md").is_file())
            overwrite = run("migrate_v01_to_v02.py", old, target, "--yes")
            self.assertNotEqual(overwrite.returncode, 0)

    def test_preflight_detects_secret_in_history(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            subprocess.run(["git", "-C", str(root), "config", "user.name", "Test"], check=True)
            noreply = "test" + "@users.noreply.github.com"
            subprocess.run(["git", "-C", str(root), "config", "user.email", noreply], check=True)
            leak = root / "leak.txt"
            leak.write_text('api_key="ghp_' + ("1" * 36) + '"\n', encoding="utf-8")
            subprocess.run(["git", "-C", str(root), "add", "leak.txt"], check=True)
            subprocess.run(["git", "-C", str(root), "commit", "-qm", "fixture"], check=True)
            leak.unlink()
            subprocess.run(["git", "-C", str(root), "add", "-u"], check=True)
            subprocess.run(["git", "-C", str(root), "commit", "-qm", "remove fixture"], check=True)
            result = run("preflight_public_repo.py", root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("GitHub token", result.stdout)

    def test_public_fictional_example_is_valid_and_private_path_free(self) -> None:
        example = ROOT / "examples" / "fictional-career-vault"
        validated = run("validate_vault.py", example)
        self.assertEqual(validated.returncode, 0, validated.stdout + validated.stderr)

        audited = run("audit_claims.py", example, "--purpose", "interview")
        self.assertEqual(audited.returncode, 0, audited.stdout + audited.stderr)
        self.assertIn("eligible=2", audited.stdout)

        exported = json.loads(
            (example / "exports" / "interview-evidence.json").read_text(encoding="utf-8")
        )
        serialized = json.dumps(exported, ensure_ascii=False)
        self.assertEqual(exported["schema_version"], "0.2.0")
        self.assertEqual(len(exported["claims"]), 2)
        self.assertNotIn("/Users/", serialized)


if __name__ == "__main__":
    unittest.main()
