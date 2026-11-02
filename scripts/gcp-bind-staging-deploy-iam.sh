#!/usr/bin/env bash
# Least-privilege IAM grants only on approved SmartRoute resources. Dry run by default.
set -euo pipefail
PROJECT=proyectopersonal-480420
REGION=us-central1
REPO=smartroute-staging
SERVICE=smartroute-api-staging
DEPLOYER="smartroute-deployer@$PROJECT.iam.gserviceaccount.com"
RUNTIME="smartroute-runtime@$PROJECT.iam.gserviceaccount.com"
SMOKE="smartroute-smoke@$PROJECT.iam.gserviceaccount.com"

fail(){ echo "ERROR: $*" >&2; exit 1; }
[[ "$(gcloud config get-value project 2>/dev/null)" == "$PROJECT" ]] || fail "Unexpected active project"
for sa in "$DEPLOYER" "$RUNTIME" "$SMOKE"; do
  gcloud iam service-accounts describe "$sa" --project="$PROJECT" --format='value(email)' >/dev/null || fail "Missing service account $sa"
done
gcloud artifacts repositories describe "$REPO" --project="$PROJECT" --location="$REGION" --format='value(name)' >/dev/null || fail "Missing dedicated Artifact Registry repository"
gcloud run services describe "$SERVICE" --project="$PROJECT" --region="$REGION" --format='value(metadata.name)' >/dev/null || fail "Missing dedicated Cloud Run service"
actual_sa="$(gcloud run services describe "$SERVICE" --project="$PROJECT" --region="$REGION" --format='value(spec.template.spec.serviceAccountName)')"
[[ "$actual_sa" == "$RUNTIME" ]] || fail "Unexpected Cloud Run runtime identity"
# Fail closed if public invoker bindings exist at the service level.
service_policy="$(gcloud run services get-iam-policy "$SERVICE" --project="$PROJECT" --region="$REGION" --format=json)"
SERVICE_POLICY_JSON="$service_policy" python3 - <<'PY'
import json, os, sys
p=json.loads(os.environ["SERVICE_POLICY_JSON"])
if any(x in b.get("members",[]) for b in p.get("bindings",[]) for x in ("allUsers","allAuthenticatedUsers")):
    sys.exit("ERROR: Cloud Run service has a public/blanket principal in its IAM policy")
print("PASS: Cloud Run service policy has no public IAM principal")
PY

echo "IAM stage 2 plan (resource scoped):"
echo "  deployer: artifactregistry.writer on repository $REPO only"
echo "  deployer: run.developer on Cloud Run service $SERVICE only"
echo "  deployer: iam.serviceAccountUser on runtime $RUNTIME only"
echo "  smoke: run.invoker on service $SERVICE only"
echo "  smoke: iam.serviceAccountTokenCreator on itself only for GitHub Actions ID-token generation"
echo "No project-level IAM roles or existing non-SmartRoute resources are modified."
if [[ "${CONFIRM_SMARTROUTE_DEPLOY_GRANTS:-}" != "$PROJECT/$SERVICE" ]]; then
  echo "DRY RUN: no IAM changes applied."
  echo "CONFIRM_SMARTROUTE_DEPLOY_GRANTS=$PROJECT/$SERVICE bash scripts/gcp-bind-staging-deploy-iam.sh"
  exit 0
fi

gcloud artifacts repositories add-iam-policy-binding "$REPO" \
  --project="$PROJECT" --location="$REGION" \
  --member="serviceAccount:$DEPLOYER" --role=roles/artifactregistry.writer --quiet \
  --format=json >/dev/null
gcloud run services add-iam-policy-binding "$SERVICE" \
  --project="$PROJECT" --region="$REGION" \
  --member="serviceAccount:$DEPLOYER" --role=roles/run.developer --quiet \
  --format=json >/dev/null
gcloud iam service-accounts add-iam-policy-binding "$RUNTIME" \
  --project="$PROJECT" --member="serviceAccount:$DEPLOYER" \
  --role=roles/iam.serviceAccountUser --quiet --format=json >/dev/null
gcloud run services add-iam-policy-binding "$SERVICE" \
  --project="$PROJECT" --region="$REGION" \
  --member="serviceAccount:$SMOKE" --role=roles/run.invoker --quiet \
  --format=json >/dev/null
gcloud iam service-accounts add-iam-policy-binding "$SMOKE" \
  --project="$PROJECT" --member="serviceAccount:$SMOKE" \
  --role=roles/iam.serviceAccountTokenCreator --quiet --format=json >/dev/null
echo "IAM STAGE 2 COMPLETE; GitHub GCP_STAGING_ENABLED still remains disabled."
