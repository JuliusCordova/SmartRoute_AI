# Copilot coding agent instructions — SmartRoute AI

Follow [AGENTS.md](../AGENTS.md), [SPEC](../specs/SPEC.md), [Fast Lane](../docs/SDLC_FAST_LANE.md), [Firestore ADR](../docs/FIRESTORE_STANDARD_MVP.md) and the latest [development plan](../docs/PLAN_DESARROLLO_7_SEMANAS.md). This is a 7-week academic **software deliverable**, not just a report.

## Work per issue
1. Identify `US-###`, `RF-###`, `AC-###`, `NEC-###`, `OE#`; present implementation approach concisely.
2. Prefer vertical feature slices in FastAPI; Firestore Standard Native mode is the only operational datastore. Do NOT create Cloud SQL, BigQuery, GKE, Redis or persistent agent runtime.
3. Add tests first or alongside code. Run unit tests, emulator integration tests if relevant, syntax checks and Docker build; report exact commands and outcomes in PR.
4. No Firebase Admin credentials in client. API verifies Firebase token, checks role/ownership from Firestore. Firestore rules deny direct client access; server SDK IAM is separate enforcement.
5. Keep fixtures synthetic; label `data_origin`, do not invent real route outcomes. Never log GPS, ID tokens, passwords or personal data.
6. Map optimization is deterministic OR-Tools. Google Maps Routes API should be mocked for CI. Gemini is optional P1 read-only with golden evaluations and no writes.
7. Branch/PR only; do not bypass CI, self-approve, change production IAM, enable public endpoints or create billable cloud resources.
8. If scope is unclear, make smallest testable implementation and describe assumptions. If tests fail, keep PR open and provide failure evidence.

## Definition of Done
A PR is ready only with traceability, source code, deterministic tests, integration tests where applicable, no secrets, updated documentation, and CI passing. Deploying a staging service additionally needs configured WIF, successful deploy and authenticated smoke evidence. No false success claims.

## Development acceleration
Issues assigned to a coding agent should result in a PR. GitHub CI then validates the PR. Only approved low-risk changes may use GitHub auto-merge under required checks. Production and resource-budget changes require human authorization.
