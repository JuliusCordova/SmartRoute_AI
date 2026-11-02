# SmartRoute API — US-003/US-004 initial code slice

**Status: implemented source + locally tested; not yet Firestore-emulator integrated or cloud deployed.** See [project SDD](../../../specs/SPEC.md) and [Firestore ADR](../../../docs/FIRESTORE_STANDARD_MVP.md).

## Endpoints
- `GET /health`: process health, unauthenticated.
- `GET /ready`: process-only readiness (does not verify Firestore).
- `POST /api/v1/orders`: OPERATOR only, validated synthetic order `{address_label, geo:{latitude,longitude},due_at?}`; returns 201.
- `GET /api/v1/orders?limit=20&cursor=<doc-id>`: OPERATOR only; returns `{items,next_cursor}`, max 50; 422 invalid cursor.

**Authentication:** Firebase ID token in `Authorization: Bearer <token>`. The backend verifies the token, loads `users/{uid}` from Firestore and only allows active OPERATOR accounts. Headers and request payload cannot grant roles. Server SDK uses the runtime service-account IAM and bypasses Firestore Security Rules: restrict permissions and enable deny-all direct-client rules. The app fails closed when identity configuration is unavailable.

## Local unit tests (no cloud usage)
```bash
cd services/api
python -m pip install -r requirements.txt
python -m pytest -q
docker build -t smartroute-api:dev .
```
Test suite exercises create/list, geo validation, no-token rejection, DRIVER forbidden and invalid cursor/limit. Tests replace the API's role dependency and repository with explicit synthetic fakes; this is not proof that Firebase verification or Firestore persistence works in GCP.

## Next integration gate (not yet executed)
1. Install and start Firestore emulator, setting `FIRESTORE_EMULATOR_HOST` and `GOOGLE_CLOUD_PROJECT` to an emulator-only project.
2. Add integration suite covering document creation/read, sorting, paging, database auth/permission boundaries and errors.
3. Configure Firebase Authentication, runtime identity, `users/{uid}` provisioned by owner. Avoid deploying clients until auth tested.
4. Verify API matches `specs/openapi.yaml` (including fields and status codes), add `GET /orders?status=` only as a separately specified feature if required.
5. Deploy staging Cloud Run only with human approval and verify smoke. Record commit, test output, cost and rollback.

## Cost discipline
Reads limited to 51 documents per page, cursor lookup adds one read; no polling/listeners, Firestore only, Gemini and Google Maps not called. All newly created orders are labeled `synthetic` to prevent misrepresentation as field-observed deliveries.
