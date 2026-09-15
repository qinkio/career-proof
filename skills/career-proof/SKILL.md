---
name: career-proof
description: "Build and maintain a private, evidence-backed career asset and project vault from resumes, project files, reviews, presentations, spreadsheets, and notes. Use for 职业资产库、项目库、经历证据、项目证据卡、Claim核验、指标口径、个人贡献归因、技能映射、资料索引、资产迁移、隐私审计, or when another career Skill needs current project facts directly from the vault. Do not use for full interview preparation, resume writing, job discovery, career-pivot recommendations, auto-application, or document layout."
---

# Career Proof

## Current local vault workflow

Use the current career vault directly for local resume and interview tasks. Read [references/direct-vault-reading.md](references/direct-vault-reading.md) for the reading and update contract. A separate maintained evidence package is not required; exports are optional one-time transfer outputs. This direct-read mode supersedes export preferences elsewhere for local work.


Maintain a durable evidence layer:

`source -> complete career/project record -> atomic facts and review -> capability map -> direct downstream reading`

Treat the private vault as the source of truth. Treat reports, resumes, interview packs, and Notion pages as downstream expressions.

## Enforce the boundary

Perform only vault work: initialize, index, capture, review, audit, migrate, inspect status, and export approved evidence.

- Route complete interview preparation to `prepare-interview-pack`; let it read the current relevant project cards and canonical claims directly. Use a scoped export only when a real transfer requires it.
- Route resume writing, job discovery, career-pivot planning, application tracking, and offer work to their dedicated workflows.
- Never silently perform an external upload, Notion write, Git commit, or application action.

## Read the required references

1. Read `references/vault-schema.md` before initialization, capture, migration, or schema edits.
2. Read `references/privacy-and-claims.md` before opening sources, drafting claims, changing permissions, or exporting.
3. Read `references/operations.md` for indexing, review, snapshots, migration, status, and failure handling.
4. Read `references/direct-vault-reading.md` for local downstream skills; read `references/export-contract.md` only for a requested transfer, export, or Notion publication.

## Locate and gate the vault

Locate the private vault from the user's workspace. Never assume a global data path. Keep it outside the public Skill repository and, by default, outside any Git worktree.

Before initialization, migration, overwrite, bulk status promotion, restore, or external publication:

1. Resolve exact source and target paths.
2. Show the planned files and effects.
3. Confirm that existing user authorization covers the resolved paths and effects. Ask once only when it does not; ordinary requested updates and reversible organization within the authorized vault do not require repeated confirmation. New destructive replacement and external publication require their own authorization.
4. Preserve originals and prior versions.

One vault represents one person. For another person, create another vault.

## Choose an operation

- **Initialize:** run `scripts/init_vault.py ABSOLUTE_TARGET --preview` and report the plan. Run with `--yes` when existing or new authorization covers the exact target and effects.
- **Index:** index metadata first with `scripts/index_sources.py SOURCE_ROOT VAULT_ROOT`; rerun with `--yes` when the indexing write is covered by existing or new approval. Do not parse file content during indexing.
- **Capture:** read only approved sources. Integrate facts explicitly confirmed by the user into the relevant project and canonical claims, recording the confirmation in the review history. Put newly extracted unconfirmed facts and substantive unresolved decisions in `review-queue.csv`. Keep confirmed values visible; missing optional details remain refinements.
- **Review:** present one coherent project or evidence chain at a time. Promote only user-approved items.
- **Audit:** run structural validators and duplicate/conflict candidate detection, then check completeness and actual usability using references/operations.md. Propose substantive merges; apply a merge only within explicit user authorization, preserving old IDs and aliases.
- **Status:** report source counts, unresolved review items, claim status, capability coverage, conflicts, withdrawn claims, and stale exports.
- **Read downstream:** local skills read the relevant complete project records and current canonical claims directly.
- **Export:** optionally create a minimal purpose-bound JSON with `scripts/export_evidence.py` when a requested transfer requires it; do not maintain it as a second source.
- **Migrate:** create a new v0.2 vault with `scripts/migrate_v01_to_v02.py`; never migrate in place.

## Capture evidence safely

Preserve source files. Index path, size, modification time, file identity, and access settings. Hash content only after that source is explicitly marked `allowed`; never hash or open `do-not-model` content.

Define a project around one business objective, time boundary, and result chain. Use a parent project with child projects when stages have materially different objectives, ownership, or metrics. Ask the user to decide when boundaries remain ambiguous.

Create one atomic claim per responsibility, decision, action, metric, scale fact, recognition, or learning. Keep formal title, actual responsibility, personal action, project result, and team result distinct. Link claims to stable source and project IDs.

## Review before promotion

Put unconfirmed proposed claims, project-boundary decisions, permission changes, duplicate candidates, and conflicts in `review-queue.csv`. Existing explicit user confirmation satisfies confirmation for the same fact and limits; record it rather than asking again. The user owns unresolved substantive decisions.

- Preserve explicitly user-confirmed metric values even when optional measurement details are absent. Record missing details as refinements; unresolved meaning or attribution needs qualified wording or pending/conflict status for the affected statement. Never invent baselines, denominators or ownership.
- Do not promote ownership language beyond the evidence.
- Do not resolve conflicting sources by choosing the newest, largest, or most favorable value.
- Similar wording alone does not authorize a merge. Approved consolidation preserves all distinct facts, old IDs and an alias to the current fact.
- Keep withdrawn and prohibited claim IDs reserved; exclude them from future exports.

Append material state changes to `change-log.csv`. Before a bulk change, run `scripts/snapshot_vault.py VAULT_ROOT --yes`.

## Map capabilities separately

Claims are facts; capabilities are interpretations. Store capability mappings in `capability-map.csv` with supporting claim IDs.

Use three layers:

1. A concise standard capability.
2. A domain or industry capability.
3. The candidate's original evidence-grounded expression.

Mark new mappings `proposed` until reviewed. Preserve aliases when standardizing terms.

## Validate and deliver

After changes, resolve logical paths through the current layout (see references/vault-schema.md), then run:

```bash
python3 scripts/validate_vault.py /absolute/private/vault
python3 scripts/detect_claim_candidates.py /absolute/resolved/current-facts.csv
```

Before an external career output, audit using its actual purpose (`resume`, `interview`, or `portfolio`); for example:

```bash
python3 scripts/audit_claims.py /absolute/private/vault --purpose resume
```

Only for an explicitly requested transfer, resolve the optional output directory and generate a scoped package:

```bash
python3 scripts/export_evidence.py /absolute/private/vault /absolute/private/vault/exports/interview.json \
  --purpose interview --project-ids PRJ-001 --yes
```

`VAULT_SCHEMA_OK` means structural consistency only. It does not prove truth, confidentiality clearance, or publication approval.

## Publish to Notion only when asked

When the user explicitly requests Notion, use the available Notion knowledge-capture workflow. Export or write only a purpose-approved, redacted view. Search and fetch before writing, preserve unrelated content, avoid raw source paths and internal notes, fetch again to verify, and return the page link. Do not implement implicit or bidirectional synchronization.

## Deliver the result

Lead with what changed, what remains pending, and what downstream use is now safe. Distinguish structural validation from completeness, usability and human confirmation. Do not report organization complete until the physical folder view, current links, project/result coverage and downstream reading have been checked. Point to the current vault records and remaining refinements; report an export only if one was requested.
