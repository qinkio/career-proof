# Career Proof v0.2 vault schema

## Workspace

Logical names such as `canonical-claims.csv` identify roles, not mandatory root-level filenames. Prefer a readable layout for a human-maintained vault; preserve an established layout unless organization is requested.

```text
职业资产库/
├── 00-职业资产库首页.md
├── 01-个人经历/
├── 02-项目库/项目详情/
├── 03-求职记录/
├── 04-证据与来源/
├── 05-事实与维护/
└── 06-历史归档/
```

`scripts/vault_common.py:vault_path` resolves supported Chinese paths and legacy flat paths. An optional `.vault-layout.json` object can map logical names to relative paths; mappings must stay inside the vault. For custom layouts, use this map rather than creating another data copy or hidden compatibility links. The initializer retains the legacy layout for migration compatibility; organize it into the chosen human layout before declaring setup complete. Project IDs remain stable regardless of display folders. Update links and internal source paths after moves. Archive templates, old entry pages and former exports separately from current facts.

Keep the vault outside the public Skill repository. One vault represents one person. Preserve source files in place unless the user explicitly requests a managed copy in `evidence/`.

## Stable identifiers

- Source: `SRC-...`
- Project: `PRJ-...`
- Claim: `CLM-...`
- Capability: `CAP-...`
- Review item: `REV-...`
- Change: `CHG-...`
- Snapshot: `SNP-...`
- Export: `EXP-...`

Never reuse an identifier after rejection, withdrawal, supersession, or archival.

## Sources

`sources.csv` records metadata and permissions, not extracted content.

- `source_id`
- `path`
- `source_type`: `pdf`, `docx`, `pptx`, `xlsx`, `markdown`, `csv`, `text`, or `other`
- `size_bytes`
- `modified_at`
- `file_key`: filesystem identity used to recognize moves where supported
- `content_sha256`: blank unless content access is explicitly allowed
- `sensitivity`: `public`, `personal-sensitive`, `company-sensitive`, or `restricted`
- `model_access`: `pending`, `allowed`, `summary-only`, or `do-not-model`
- `publication_permission`: `not-approved`, `application-only`, or `public-approved`
- `status`: `active`, `moved`, `missing`, `duplicate-candidate`, or `error`
- `last_indexed_at`
- `notes`

## Projects

Keep one Markdown card per project. Record project ID, optional parent project ID, objective, time boundary, business context, users, stakeholders, formal title, actual responsibility, baseline, decisions, actions, results, claim IDs, source IDs, ownership boundary, unresolved questions, and archival status.

Use a parent and child projects when stages differ materially in objective, ownership, or metric definition. A file is evidence, not automatically a project.

## Canonical claims

`canonical-claims.csv` contains one atomic statement per row.

- Identity: `claim_id`, `project_id`, `claim_text`, `claim_type`
- Attribution: `ownership`
- Evidence: `source_ids`, `source_locators`
- Metric: `metric_name`, `metric_baseline`, `metric_result`, `metric_unit`, `metric_time_window`, `metric_population`, `metric_calculation`
- Governance: `status`, `sensitivity`, `publication_permission`
- History: `valid_from`, `valid_to`, `supersedes_claim_id`, `withdrawn_at`, `notes`

Allowed claim types: `responsibility`, `decision`, `action`, `metric`, `scale`, `recognition`, `learning`.

Allowed ownership: `owned`, `co-owned`, `participated`, `supported`, `team-result`, `unknown`.

Allowed status: `verified`, `user-confirmed`, `pending`, `conflict`, `inferred`, `prohibited`, `withdrawn`.

Use `|` between multiple IDs or locators. Do not store source paths directly in claims.

## Capability map

`capability-map.csv` stores interpretations separately from facts:

- `capability_id`
- `standard_skill`
- `industry_skill`
- `original_expression`
- `category`
- `claim_ids`
- `project_ids`
- `confidence`: `low`, `medium`, or `high`
- `status`: `proposed`, `approved`, `rejected`, or `deprecated`
- `notes`

An approved capability requires at least one eligible supporting claim.

## Review queue

`review-queue.csv` stores proposed claims and decisions before promotion:

- `review_id`, `item_type`, `item_id`, `project_id`
- `question`, `proposed_value`, `current_value`
- `evidence_ids`, `risk`, `decision`, `status`
- `created_at`, `resolved_at`, `notes`

Allowed statuses: `pending`, `approved`, `rejected`, `deferred`.

## Change log

`change-log.csv` is append-only:

- `change_id`, `changed_at`, `actor`
- `entity_type`, `entity_id`, `action`
- `from_value`, `to_value`, `reason`, `snapshot_id`

Do not rewrite history to match the current state.
