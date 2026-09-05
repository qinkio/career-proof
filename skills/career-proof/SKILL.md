---
name: career-proof
description: "Build and maintain a private, evidence-backed career asset and project vault from resumes, project files, reviews, presentations, spreadsheets, and notes. Use for 职业资产库、项目库、经历证据、项目证据卡、Claim核验、指标口径、个人贡献归因、技能映射、资料索引、资产迁移、隐私审计, or when another career Skill needs a minimal approved evidence bundle. Do not use for full interview preparation, resume writing, job discovery, career-pivot recommendations, auto-application, or document layout."
---

# Career Proof

Maintain a durable evidence layer:

`source -> project boundary -> atomic claim -> review -> capability map -> scoped export`

Treat the private vault as the source of truth. Treat reports, resumes, interview packs, and Notion pages as downstream expressions.

## Enforce the boundary

Perform only vault work: initialize, index, capture, review, audit, migrate, inspect status, and export approved evidence.

- Route complete interview preparation to `prepare-interview-pack` and provide it a scoped JSON export rather than the full vault.
- Route resume writing, job discovery, career-pivot planning, application tracking, and offer work to their dedicated workflows.
- Never silently perform an external upload, Notion write, Git commit, or application action.

## Read the required references

1. Read `references/vault-schema.md` before initialization, capture, migration, or schema edits.
2. Read `references/privacy-and-claims.md` before opening sources, drafting claims, changing permissions, or exporting.
3. Read `references/operations.md` for indexing, review, snapshots, migration, status, and failure handling.
4. Read `references/export-contract.md` before producing data for another Skill or Notion.

## Locate and gate the vault

Locate the private vault from the user's workspace. Never assume a global data path. Keep it outside the public Skill repository and, by default, outside any Git worktree.

Before initialization, migration, overwrite, bulk status promotion, restore, or external publication:

1. Resolve exact source and target paths.
2. Show the planned files and effects.
3. Obtain explicit approval for the displayed absolute paths and effects. Do not treat a generic request such as “建立资产库” as approval of a later path-specific plan.
4. Preserve originals and prior versions.

One vault represents one person. For another person, create another vault.

## Choose an operation

- **Initialize:** run `scripts/init_vault.py ABSOLUTE_TARGET --preview`, report the plan, and stop. Only after a new explicit confirmation run it again with `--yes`.
- **Index:** index metadata first with `scripts/index_sources.py SOURCE_ROOT VAULT_ROOT`; rerun with `--yes` after approval. Do not parse file content during indexing.
- **Capture:** read only approved sources, propose project boundaries, and place proposed facts or decisions in `review-queue.csv`. Do not write unapproved facts into `canonical-claims.csv`.
- **Review:** present one coherent project or evidence chain at a time. Promote only user-approved items.
- **Audit:** run the structural validators and duplicate/conflict candidate detector; never auto-merge.
- **Status:** report source counts, unresolved review items, claim status, capability coverage, conflicts, withdrawn claims, and stale exports.
- **Export:** create a minimal purpose-bound JSON package with `scripts/export_evidence.py`; do not give downstream Skills unrestricted vault access.
- **Migrate:** create a new v0.2 vault with `scripts/migrate_v01_to_v02.py`; never migrate in place.

## Capture evidence safely

Preserve source files. Index path, size, modification time, file identity, and access settings. Hash content only after that source is explicitly marked `allowed`; never hash or open `do-not-model` content.

Define a project around one business objective, time boundary, and result chain. Use a parent project with child projects when stages have materially different objectives, ownership, or metrics. Ask the user to decide when boundaries remain ambiguous.

Create one atomic claim per responsibility, decision, action, metric, scale fact, recognition, or learning. Keep formal title, actual responsibility, personal action, project result, and team result distinct. Link claims to stable source and project IDs.

## Review before promotion

Put proposed claims, project-boundary decisions, permission changes, duplicate candidates, and conflicts in `review-queue.csv`. The user owns the final decision.

- Do not promote a metric without definition, baseline/result when applicable, time window, population, calculation, and attribution.
- Do not promote ownership language beyond the evidence.
- Do not resolve conflicting sources by choosing the newest, largest, or most favorable value.
- Do not auto-merge similar claims.
- Keep withdrawn and prohibited claim IDs reserved; exclude them from future exports.

Append material state changes to `change-log.csv`. Before a bulk change, run `scripts/snapshot_vault.py VAULT_ROOT --yes`.

## Map capabilities separately

Claims are facts; capabilities are interpretations. Store capability mappings in `capability-map.csv` with supporting claim IDs.

Use three layers:

1. A concise standard capability.
2. A domain or industry capability.
3. The candidate's original evidence-grounded expression.

Mark new mappings `proposed` until reviewed. Preserve aliases when standardizing terms.

## Validate and export

After changes, run:

```bash
python3 scripts/validate_vault.py /absolute/private/vault
python3 scripts/detect_claim_candidates.py /absolute/private/vault/canonical-claims.csv
```

Before an external career output, also run:

```bash
python3 scripts/audit_claims.py /absolute/private/vault --purpose interview
```

Generate a scoped package only after approval:

```bash
python3 scripts/export_evidence.py /absolute/private/vault /absolute/private/vault/exports/interview.json \
  --purpose interview --project-ids PRJ-001 --yes
```

`VAULT_SCHEMA_OK` means structural consistency only. It does not prove truth, confidentiality clearance, or publication approval.

## Publish to Notion only when asked

When the user explicitly requests Notion, use the available Notion knowledge-capture workflow. Export or write only a purpose-approved, redacted view. Search and fetch before writing, preserve unrelated content, avoid raw source paths and internal notes, fetch again to verify, and return the page link. Do not implement implicit or bidirectional synchronization.

## Deliver the result

Lead with what changed, what remains pending, and what downstream use is now safe. Distinguish structural validation from human approval. End with the next review batch or the exact export that is ready.
