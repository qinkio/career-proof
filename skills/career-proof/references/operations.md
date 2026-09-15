# Operations

## Initialize

Run the initializer with `--preview` and show the exact absolute target. Use `--yes` only when authorization covers the displayed target and creation effects; reuse existing path-specific approval rather than requesting it again. The initializer refuses an installed Skill directory and a Git worktree by default. It creates files only when absent and never overwrites a vault.

## Index

1. Index metadata for the user-approved root.
2. Default new sources to `model_access=pending`, `publication_permission=not-approved`, and conservative sensitivity.
3. Do not parse document text during indexing.
4. Hash content only for an existing source marked `allowed`.
5. Use file identity to recognize moves where supported.
6. Mark missing files; never silently delete their records.
7. Report unsupported or unreadable files as errors without constructing claims.

## Capture

Read only sources marked `allowed`. For `summary-only`, use only the manually supplied redacted summary. Never open `do-not-model` sources.

Group evidence around a business objective and result chain. Propose parent/child boundaries when a long program contains distinct stages. Put uncertain boundaries in the review queue.

Draft newly extracted unconfirmed claims into review items. Explicit user confirmation may resolve the corresponding review item and update the project and canonical facts in the same operation. Missing optional refinements do not erase confirmed values. Appearance in a resume or presentation alone is not explicit confirmation.

## Review

Review one coherent project or evidence chain at a time in this order:

1. Project boundary.
2. Formal title and actual responsibility.
3. Personal decisions and actions.
4. Metrics and result definitions.
5. Ownership and team-result boundaries.
6. Sensitivity and publication permission.
7. Capability mapping.

Record the user's decision and timestamp. Append material promotions, withdrawals, permission changes, merges, and conflict resolutions to `change-log.csv`.

## Snapshot

Before migration, bulk promotion, bulk permission change, or restore, create a metadata snapshot with `snapshot_vault.py`. Snapshots include canonical tables and project cards, not external source documents or managed evidence binaries.

Use restore preview before any recovery. The v0.2 tool reports differences; it does not overwrite the active vault automatically.

## Audit

Run structural validation after changes. Run duplicate/conflict candidate detection before a review batch. Treat candidates as prompts for human review, not automatic corrections.

When a file cannot be read, preserve successful work, record the failure, and create no claim from that file. Never infer content from a filename, folder name, or neighboring document.

## Migration

Migrate to a separate target. Preserve the source vault. Map old privacy values conservatively and place ambiguous permission decisions in the review queue. Do not claim that a structurally successful migration preserves every semantic detail; review migrated metrics and ownership.

## Status

Report:

- source totals by access and status;
- projects with unresolved boundaries;
- claims by status and permission;
- unresolved review items by risk;
- capabilities without eligible evidence;
- duplicate and conflict candidates;
- latest snapshot; stale exports only when exports actually exist.

## Preserve completeness during consolidation

Before bulk organization, inventory current and confirmed historical projects, career facts and distinct results. Record each item's target: retained in the current record, merged with a named current fact, pending refinement, or explicitly archived/withdrawn for a stated reason. A short summary is not a replacement for the full project account. Merge confirmed historical narrative into the relevant project; retain source originals in evidence/archive instead of maintaining a separate excerpt page as another current account.

Keep background, problem/judgment, personal responsibility, decisions/actions, difficulties, results, learning and refinements available. Use these sections where useful, without inventing missing content. Preserve all distinct confirmed improvement figures in results, with limits and team attribution. Do not create a project for every source file. Synchronize changed narrative, canonical facts, resolved review items and aliases in the same operation. Preserve stable IDs and log the changes.

## Completion checks

For content consolidation, compare the before/after inventory and explain any unaccounted item. For folder organization, inspect the real visible root and chosen categories; an index page alone is insufficient. Check active links and source relocations. For layout/tool changes, verify validation and snapshot collection on a vault without compatibility links. For downstream usability, read relevant full projects and current facts as a resume/interview task would; ensure confirmed results and refinements are distinguishable. Report actual scope and remaining issues; schema success alone does not establish completeness.
