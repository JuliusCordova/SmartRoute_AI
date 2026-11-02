# Minimum SDD release gate — SmartRoute AI

**Current status:** code for orders and transactional route assignment merged to main, with GitHub CI passing in prior runs; no GCP staging deployment verified.

| Gate | Required proof | Current |
|---|---|---|
| G0 | Capstone requirement and owner | Design |
| G1 | SPEC, architecture, contracts, BDD, human review | Design |
| G2 | Feature code + unit and negative-path tests | Orders and route assignment implemented; emulator CI green; remaining product flows pending |
| G3 | CI green, security/secret review, AI evals if used | CI verified for API/emulator/Docker in prior runs; security review and other gates pending |
| G4 | Cloud Run staging URL, image digest, dedicated service account, smoke, rollback | Not verified |
| G5 | Monitoring, business metrics, pilot, costs and incident owner | Not verified |

## Commands (staging only)
1. `cd services/api && python -m pip install -r requirements.txt && python -m pytest -q`
2. `docker build -t smartroute-api:local services/api`
3. Configure GCP_PROJECT, GCP_REGION, dedicated GCP_SERVICE_ACCOUNT and service permissions; use GitHub WIF instead of static service keys in future CI/CD.
4. **Only after human approval:** `DEPLOY_APPROVED=yes bash scripts/deploy-gcp.sh`
5. Automated staging job (when explicitly enabled) uses a dedicated `GCP_SMOKE_SERVICE_ACCOUNT` with `roles/run.invoker`, gets an audience-bound short-lived ID token and runs `scripts/smoke-test.sh`. Manual smoke must use an ID token minted with correct Cloud Run audience and invoker grants.
6. Record commit, revision/digest, URL, test output, cost settings and rollback revision in evidence log. `/health` and `/ready` are process-only checks and are **not** evidence that Firestore or Firebase authentication work in GCP.

## Blockers for complete MVP
- Implement auth, order CRUD, Firestore Standard database, IAM, emulator transactions and conflict tests, idempotent events, Flutter, React, Maps and OR-Tools adapters.
- Add database integration tests, contract validation, feature acceptance runner, IAM least privilege and CI security scan.
- Deploy separately governed runtime Gemini/ADK only after A1 contract, guardrails and golden evals.
- Configure budget/quota alerting and retention policy before real GPS.
