# Optional scoped export contract

For ordinary local resume and interview tasks, use direct-vault-reading.md and read the current vault directly. This contract applies only when a transfer or explicit export is needed; no separate maintained package is required.

## Principle

Export the minimum evidence needed for one declared purpose. Never expose the whole vault by default.

## Purposes

- `interview`: evidence for an interview-preparation Skill.
- `resume`: evidence for a resume-tailoring workflow.
- `portfolio`: facts approved for public portfolio use.
- `private-analysis`: approved facts for a local career analysis.

`interview` and `resume` require `application-only` or `public-approved`. `portfolio` requires `public-approved`. `private-analysis` may include only claim IDs explicitly approved for that export.

## Package shape

```json
{
  "schema_version": "0.2.0",
  "export_id": "EXP-...",
  "generated_at": "ISO-8601 UTC",
  "purpose": "interview",
  "scope": {"project_ids": [], "claim_ids": []},
  "profile": {},
  "projects": [],
  "claims": [],
  "capabilities": [],
  "exclusions": {"counts_by_reason": {}},
  "warnings": []
}
```

Include claim ID, project ID, statement, type, ownership, structured metric fields, status, sensitivity, publication permission, and source evidence level. Include source IDs and locators only when necessary for the downstream task. Never include private absolute paths, raw evidence, contact details, hidden notes, or unrelated claims.

## Downstream contract

The consumer must:

1. Treat the package as purpose-bound and time-bound.
2. Use only included eligible claims.
3. Preserve ownership and metric limitations.
4. Avoid presenting IDs or evidence notes in external prose.
5. Stop using a package after the vault marks it stale or a claim is withdrawn.

If an export for `prepare-interview-pack` is actually required, export only the target role's relevant projects and approved claims. Keep pending, conflicting, inferred, prohibited, withdrawn, and unrelated claims out of the package.

## Notion publication

Notion is a redacted presentation layer, not the canonical vault. Publish only after an explicit request. Strip absolute paths, internal notes, unresolved review content, and company-sensitive detail unless the user separately approves the exact field and destination.
