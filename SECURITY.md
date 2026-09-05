# Security and privacy

## Supported status

Career Proof is currently `v0.2 beta`. Schema and migration behavior may change before a stable release.

## Data boundary

The public repository contains only generic instructions, fictional templates, tests, and deterministic validation tools. Keep real resumes, project evidence, contact details, interview records, credentials, customer data, and employer-confidential information in a separate private vault.

`do-not-model` means the agent must not open, hash, extract, upload, quote, or summarize the source content. A user may provide a separately written redacted summary.

The source index stores private absolute paths inside the private vault. Scoped exports omit those paths.

## Reporting

Use a private GitHub security advisory when available. Never paste a real secret or private career document into a public issue. Rotate exposed credentials even after removing them from Git history.

## Preflight limitation

`preflight_public_repo.py` checks tracked files and Git history for common leaks. It cannot prove that a repository is safe. Manual review remains required.
