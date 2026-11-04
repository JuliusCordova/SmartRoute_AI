#!/usr/bin/env bash
# Owner-operated first deployment: PREPUBLISHED immutable gateway image only.
# No Docker commands; dry run by default.
set -euo pipefail

PROJECT="proyectopersonal-480420"
REGION="us-central1"
REGISTRY="smartroute-staging"
SERVICE="smartroute-gateway-staging"
BACKEND="smartroute-api-staging"
BACKEND_URL="https://smartroute-api-staging-913797829604.us-central1.run.app"
GATEWAY_SA="smartroute-gateway@$PROJECT.iam.gserviceaccount.com"
BACKEND_SA="smartroute-runtime@$PROJECT.iam.gserviceaccount.com"
# Verified GitHub Actions job 126353548154, workflow run 41762609116,
# success: docker push sha256 digest on commit 02bc8c145761cfa4a5e37243f238367f571c096e.
IMAGE="$REGION-docker.pkg.dev/$PROJECT/$REGISTRY/smartroute-gateway"
DIGEST="sha256:d5c6abe6d73fd8b1ee4b0a8364ad89fb10799c67cc063c1b8f72826397c8ab47"
IMAGE_URI="$IMAGE@$DIGEST"
fail(){ echo "ERROR: $*" >&2; exit 1; }

command -v gcloud >/dev/null || fail "gcloud required"
[[ "$(gcloud config get-value project 2>/dev/null)" == "$PROJECT" ]] || fail "unexpected active GCP project"
[[ "$(gcloud artifacts repositories describe "$REGISTRY" --project="$PROJECT" --location="$REGION" --format='value(format)')" == "DOCKER" ]] || fail "missing exclusive Docker repository"
[[ "$(gcloud iam service-accounts describe "$GATEWAY_SA" --project="$PROJECT" --format='value(email)')" == "$GATEWAY_SA" ]] || fail "missing dedicated gateway SA"
[[ "$(gcloud run services describe "$BACKEND" --project="$PROJECT" --region="$REGION" --format='value(spec.template.spec.serviceAccountName)')" == "$BACKEND_SA" ]] || fail "private backend runtime SA mismatch"
if gcloud run services describe "$SERVICE" --project="$PROJECT" --region="$REGION" >/dev/null 2>&1; then
  fail "gateway Cloud Run service already exists; refusing to replace or update it"
fi

POLICY="$(gcloud run services get-iam-policy "$BACKEND" --project="$PROJECT" --region="$REGION" --format=json)"
BACKEND_POLICY="$POLICY" GATEWAY_SA="$GATEWAY_SA" python3 - <<'PY'
import json, os, sys
p=json.loads(os.environ["BACKEND_POLICY"])
members=[m for b in p.get("bindings",[]) if b.get("role")=="roles/run.invoker" for m in b.get("members",[])]
if f"serviceAccount:{os.environ['GATEWAY_SA']}" not in members:
    sys.exit("ERROR: gateway has no service-scoped invoker grant on private backend")
if any(m in ("allUsers", "allAuthenticatedUsers") for b in p.get("bindings",[]) for m in b.get("members",[])):
    sys.exit("ERROR: backend service IAM contains public principals")
print("PASS: gateway-only invoker on private backend")
PY

# Check Artifact Registry server-side; no Docker network access needed.
gcloud artifacts docker images describe "$IMAGE_URI" --project="$PROJECT" --format="value(image_summary.digest)" > /dev/null \
  || fail "published immutable image not visible to gcloud artifacts"
echo "PASS: GitHub Actions published image is visible in Artifact Registry"
echo "Target new private service: $SERVICE in $PROJECT/$REGION"
echo "Pinned published image: $IMAGE_URI"
echo "Dedicated runtime: $GATEWAY_SA; backend: $BACKEND_URL"
echo "Cloud Run IAM private, ingress=all; min=0 max=1, 1 CPU, 512MiB, concurrency=10"
echo "No Docker build/push, no Firebase or Firestore changes, no CI/CD auto-enable."
echo "Cloud Run and Artifact Registry may incur costs. Max instances is not a budget cap."

if [[ "${CONFIRM_SMARTROUTE_PUBLISHED_GATEWAY_DEPLOY:-}" != "$PROJECT/$SERVICE" ]]; then
  echo "DRY RUN: no Cloud Run service created."
  echo "CONFIRM_SMARTROUTE_PUBLISHED_GATEWAY_DEPLOY=$PROJECT/$SERVICE bash scripts/gcp-deploy-published-gateway-private.sh"
  exit 0
fi

gcloud run deploy "$SERVICE" \
  --project="$PROJECT" --region="$REGION" \
  --image="$IMAGE_URI" \
  --service-account="$GATEWAY_SA" \
  --no-allow-unauthenticated --ingress=all \
  --min-instances=0 --max-instances=1 \
  --cpu=1 --memory=512Mi --concurrency=10 --timeout=30s \
  --set-env-vars="APP_ENV=staging,GOOGLE_CLOUD_PROJECT=$PROJECT,SMARTROUTE_BACKEND_URL=$BACKEND_URL,SMARTROUTE_GATEWAY_ENABLED=true" \
  --quiet

actual_sa="$(gcloud run services describe "$SERVICE" --project="$PROJECT" --region="$REGION" --format='value(spec.template.spec.serviceAccountName)')"
[[ "$actual_sa" == "$GATEWAY_SA" ]] || fail "Gateway runtime identity mismatch after deployment"
POLICY="$(gcloud run services get-iam-policy "$SERVICE" --project="$PROJECT" --region="$REGION" --format=json)"
GATEWAY_POLICY="$POLICY" python3 - <<'PY'
import json, os, sys
p=json.loads(os.environ["GATEWAY_POLICY"])
if any(m in ("allUsers","allAuthenticatedUsers") for b in p.get("bindings",[]) for m in b.get("members",[])):
    sys.exit("ERROR: gateway has public IAM principal; investigate immediately")
print("PASS: gateway private IAM; no public principals")
PY
echo "PASS: first private gateway Cloud Run deploy from GitHub-published immutable image."
echo "Next: authenticated health and Firebase negative tests before any public exposure."
