# Privacy and claim policy

## Three independent permission axes

### Sensitivity

- `public`: inherently safe public information.
- `personal-sensitive`: private career, identity, contact, or application information.
- `company-sensitive`: internal metrics, customers, processes, strategy, or non-public operating information.
- `restricted`: credentials, contracts, account data, personal identifiers, or material the user marks highly restricted.

### Model access

- `pending`: metadata indexed; content access not decided.
- `allowed`: the user approves content access for the current source and task.
- `summary-only`: do not open the source; use only a user-provided redacted summary.
- `do-not-model`: do not open, hash, extract, upload, quote, or summarize the content.

### Publication permission

- `not-approved`: not approved for downstream or external use.
- `application-only`: approved for scoped job-search material after review, not for a public portfolio.
- `public-approved`: approved for public portfolio or publication after review.

Truth status never grants publication permission. Publication permission never proves truth.

## Claim status

- `verified`: primary evidence exists; locator, meaning, and ownership are clear; user approved the review batch.
- `user-confirmed`: the user confirms the fact and its limits; primary evidence may be absent.
- `pending`: plausible but evidence, definition, attribution, or approval is incomplete.
- `conflict`: sources disagree or use incompatible definitions.
- `inferred`: agent analysis, never an external fact.
- `prohibited`: misleading, contradicted, unsafe, or disallowed.
- `withdrawn`: previously retained but explicitly revoked from future use.

Only `verified` and `user-confirmed` claims are candidates for export. They must also pass ownership, metric, sensitivity, purpose, and publication checks.

## Ownership

| Evidence | Safe wording |
|---|---|
| The candidate held the decision and execution responsibility | owned, led, designed, delivered |
| Decision rights were shared | co-owned, jointly defined, partnered on |
| The candidate contributed to a larger effort | participated, contributed, supported |
| The outcome belongs to the team or organization | team result; use supported or contributed to |
| Attribution is unclear | keep `unknown`; do not publish personal impact |

Never convert discovery participation, PRD input, testing, launch support, adoption work, or a team metric into end-to-end ownership without evidence.

## Metric gate

Record, where applicable:

1. Metric name and unit.
2. Numerator and denominator.
3. Baseline and result.
4. Time window and population.
5. Calculation method.
6. Percentage points versus relative percent.
7. Candidate action and attribution.
8. Other material contributors.
9. Source and known limitation.

If a missing field could materially change the statement, keep the claim `pending`.

## Conflict, duplicate, and withdrawal rules

- Preserve all conflicting source statements and create a review item.
- Never choose the newest, largest, or most favorable value automatically.
- Suggest duplicate candidates; never merge them automatically.
- Preserve withdrawn IDs and history. Exclude withdrawn and superseded claims from new exports.
- Mark existing exports stale when a source permission or included claim is withdrawn.

## Public examples

Use fully fictional people, employers, projects, dates, and metrics. Removing a name is not sufficient when the remaining combination can identify a real person or employer.
