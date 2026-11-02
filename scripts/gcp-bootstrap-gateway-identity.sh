#!/usr/bin/env bash
# SmartRoute gateway identity bootstrap. Dry run by default.
# Creates ONE gateway SA and grants ONE service-scoped Cloud Run invoker.
set -euo pipefail

PROJECT="proyectopersonal-480420"
REGION="us-central1"
BACKEND="smartroute-api-staging"
GATEWAY_SERVICE="smartroute-gateway-staging"
GATEWAY_SA="smartroute-gateway@$PROJECT.iam.gserviceaccount.com"
BACKEND_SA="smartroute-runtime@$PROJECT.iam.gserviceaccount.com"

fail(){ echo "ERROR: $*" >&2; exit 1; }
command -v gcloud >/dev/null || fail "gcloud is required"
[[ "$(gcloud config get-value project 2>/dev/null)" == "$PROJECT" ]] || fail "Unexpected active project"
[[ -f services/gateway/Dockerfile ]] || fail "Run from SmartRoute_AI root"

gcloud iam service-accounts describe "$BACKEND_SA" --project="$PROJECT" --format='value(email)' >/dev/null || fail "Existing backend identity missing"
actual_backend_sa="$(gcloud run services describe "$BACKEND" --project="$PROJECT" --region="$REGION" --format='value(spec.template.spec.serviceAccountName)')"
[[ "$actual_backend_sa" == "$BACKEND_SA" ]] || fail "Existing private backend runtime SA mismatch"
existing_policy="$(gcloud run services get-iam-policy "$BACKEND" --project="$PROJECT" --region="$REGION" --format=json)"
BACKEND_POLICY_JSON="$existing_policy" python3 - <<'PY'
import json,os,sys
policy=json.loads(os.environ["BACKEND_POLICY_JSON"])
if any(m in ("allUsers","allAuthenticatedUsers") for b in policy.get("bindings",[]) for m in b.get("members",[])):
    sys.exit("ERROR: backend has public Cloud Run IAM principal")
print("PASS: backend service IAM policy has no broad public principal")
PY

if gcloud run services describe "$GATEWAY_SERVICE" --project="$PROJECT" --region="$REGION" >/dev/null 2>&1; then
  fail "Gateway service already exists; stop and review before changing IAM"
fi
if gcloud iam service-accounts describe "$GATEWAY_SA" --project="$PROJECT" >/dev/null 2>&1; then
  fail "Gateway SA already exists; stop and review rather than reusing or changing it"
fi

echo "Approved target project: $PROJECT"
echo "New dedicated service account: $GATEWAY_SA"
echo "New binding: roles/run.invoker on $BACKEND ONLY to serviceAccount:$GATEWAY_SA"
echo "No project-level roles, no Firestore grants, no SA Token Creator, no service deployment."
echo "No public Cloud Run access; GCP_STAGING_ENABLED is not modified."
if [[ "${CONFIRM_SMARTROUTE_GATEWAY_IDENTITY:-}" != "$PROJECT/$BACKEND" ]]; then
  echo "DRY RUN: no resources changed."
  echo "CONFIRM_SMARTROUTE_GATEWAY_IDENTITY=$PROJECT/$BACKEND bash scripts/gcp-bootstrap-gateway-identity.sh"
  exit 0
fi

gcloud iam service-accounts create smartroute-gateway \
  --project="$PROJECT" \
  --display-name="SmartRoute AI staging gateway runtime" \
  --description="Dedicated Cloud Run gateway identity; invokes only SmartRoute staging API"
gcloud run services add-iam-policy-binding "$BACKEND" \
  --project="$PROJECT" --region="$REGION" \
  --member="serviceAccount:$GATEWAY_SA" --role="roles/run.invoker" \
  --quiet --format=json >/dev/null

echo "--- Verify new SA ---"
gcloud iam service-accounts describe "$GATEWAY_SA" --project="$PROJECT" \
  --format="value(email)"
echo "--- Verify service-specific gateway invoker grant ---"
gcloud run services get-iam-policy "$BACKEND" --project="$PROJECT" --region="$REGION" \
  --format=json | GATEWAY_PRINCIPAL="serviceAccount:$GATEWAY_SA" python3 -c '
import json,sys,os
policy=json.load(sys.stdin)
members=[m for b in policy.get("bindings",[]) if b.get("role")=="roles/run.invoker" for m in b.get("members",[])]
if os.environ["GATEWAY_PRINCIPAL"] not in members:
    sys.exit("ERROR: gateway grant not found")
if "allUsers" in members or "allAuthenticatedUsers" in members:
    sys.exit("ERROR: backend publicly invokable")
print("PASS: gateway can invoke ONLY via binding on SmartRoute backend; backend remains private")
'
echo "PASS: gateway identity ready; no deployment and no auto-CI change."
