#!/usr/bin/env bash
# Owner-operated FIRST deploy of SmartRoute gateway as a PRIVATE Cloud Run service.
# Dry-run by default. No IAM grants/public access/Firestore changes.
set -euo pipefail

PROJECT="proyectopersonal-480420"
REGION="us-central1"
REPO="smartroute-staging"
GATEWAY="smartroute-gateway-staging"
BACKEND="smartroute-api-staging"
GATEWAY_SA="smartroute-gateway@$PROJECT.iam.gserviceaccount.com"
BACKEND_SA="smartroute-runtime@$PROJECT.iam.gserviceaccount.com"
BACKEND_URL="https://smartroute-api-staging-913797829604.us-central1.run.app"
IMAGE="$REGION-docker.pkg.dev/$PROJECT/$REPO/smartroute-gateway"
fail() { echo "ERROR: $*" >&2; exit 1; }

command -v gcloud >/dev/null || fail "gcloud required"
command -v docker >/dev/null || fail "docker required"
[[ -f services/gateway/Dockerfile ]] || fail "Run from SmartRoute_AI repository root"
[[ "$(gcloud config get-value project 2>/dev/null)" == "$PROJECT" ]] || fail "Unexpected active GCP project"
[[ "$(git branch --show-current)" == "main" ]] || fail "Run only on local main"
[[ -z "$(git status --porcelain)" ]] || fail "Working tree must be clean"
SHA="$(git rev-parse HEAD)"
[[ "$SHA" == "$(git rev-parse origin/main)" ]] || fail "Pull and sync to origin/main before deploying"
[[ "$(gcloud artifacts repositories describe "$REPO" --project="$PROJECT" --location="$REGION" --format='value(format)')" == "DOCKER" ]] || fail "Missing dedicated Docker repository"
[[ "$(gcloud iam service-accounts describe "$GATEWAY_SA" --project="$PROJECT" --format='value(email)')" == "$GATEWAY_SA" ]] || fail "Missing dedicated gateway SA"
actual_backend_sa="$(gcloud run services describe "$BACKEND" --project="$PROJECT" --region="$REGION" --format='value(spec.template.spec.serviceAccountName)')"
[[ "$actual_backend_sa" == "$BACKEND_SA" ]] || fail "Backend runtime identity mismatch"
if gcloud run services describe "$GATEWAY" --project="$PROJECT" --region="$REGION" >/dev/null 2>&1; then
  fail "Gateway service already exists: refusing overwrite; inspect it before another deployment"
fi

backend_policy="$(gcloud run services get-iam-policy "$BACKEND" --project="$PROJECT" --region="$REGION" --format=json)"
BACKEND_POLICY="$backend_policy" GATEWAY_SA="$GATEWAY_SA" python3 - <<'PY'
import json, os, sys
p=json.loads(os.environ["BACKEND_POLICY"])
members=[m for b in p.get("bindings",[]) if b.get("role")=="roles/run.invoker" for m in b.get("members",[])]
if f"serviceAccount:{os.environ['GATEWAY_SA']}" not in members:
    sys.exit("ERROR: gateway lacks backend-only roles/run.invoker")
if any(m in ("allUsers","allAuthenticatedUsers") for b in p.get("bindings",[]) for m in b.get("members",[])):
    sys.exit("ERROR: private backend has public IAM principal")
print("PASS: service-scoped backend IAM binding and private policy")
PY

echo "Target: projects/$PROJECT/locations/$REGION/services/$GATEWAY"
echo "Gateway runtime identity: $GATEWAY_SA (no Firestore grants)"
echo "Backend fixed: $BACKEND_URL"
echo "Image: $IMAGE:$SHA"
echo "Cloud Run ingress=all, IAM private (--no-allow-unauthenticated)"
echo "Scale 0..1, CPU 1, memory 512Mi, concurrency 10, timeout 30s"
echo "This creates a new Cloud Run revision and image, which may incur costs."
echo "No Firebase users, IAM role changes, public invoker, or auto-CI changes."
if [[ "${CONFIRM_SMARTROUTE_GATEWAY_DEPLOY:-}" != "$PROJECT/$GATEWAY" ]]; then
  echo "DRY RUN: no Docker push or service creation."
  echo "CONFIRM_SMARTROUTE_GATEWAY_DEPLOY=$PROJECT/$GATEWAY bash scripts/gcp-bootstrap-private-gateway.sh"
  exit 0
fi

gcloud auth configure-docker "$REGION-docker.pkg.dev" --quiet
TAG="$IMAGE:$SHA"
docker build --pull -t "$TAG" services/gateway
docker push "$TAG" | tee /tmp/smartroute-gateway-push.log
DIGEST="$(awk '/digest: sha256:/ {for (i=1;i<=NF;i++) if ($i=="digest:") print $(i+1)}' /tmp/smartroute-gateway-push.log | tail -n 1)"
[[ "$DIGEST" =~ ^sha256:[a-f0-9]{64}$ ]] || fail "Docker push did not yield immutable digest"
IMMUTABLE="$IMAGE@$DIGEST"

gcloud run deploy "$GATEWAY" \
  --project="$PROJECT" --region="$REGION" \
  --image="$IMMUTABLE" \
  --service-account="$GATEWAY_SA" \
  --no-allow-unauthenticated \
  --ingress=all \
  --min-instances=0 --max-instances=1 \
  --cpu=1 --memory=512Mi --concurrency=10 --timeout=30s \
  --set-env-vars="APP_ENV=staging,GOOGLE_CLOUD_PROJECT=$PROJECT,SMARTROUTE_BACKEND_URL=$BACKEND_URL,SMARTROUTE_GATEWAY_ENABLED=true" \
  --quiet

actual_gateway_sa="$(gcloud run services describe "$GATEWAY" --project="$PROJECT" --region="$REGION" --format='value(spec.template.spec.serviceAccountName)')"
[[ "$actual_gateway_sa" == "$GATEWAY_SA" ]] || fail "Gateway runtime SA mismatch after deploy"
gateway_policy="$(gcloud run services get-iam-policy "$GATEWAY" --project="$PROJECT" --region="$REGION" --format=json)"
GATEWAY_POLICY="$gateway_policy" python3 - <<'PY'
import json,os,sys
p=json.loads(os.environ["GATEWAY_POLICY"])
if any(m in ("allUsers","allAuthenticatedUsers") for b in p.get("bindings",[]) for m in b.get("members",[])):
    sys.exit("ERROR: gateway unexpectedly grants public invocation")
print("PASS: gateway Cloud Run IAM has no public principals")
PY

echo "PASS: private gateway deployed by immutable digest $DIGEST"
echo "Service health requires authorized IAM identity; no public gateway available."
echo "Next step: authenticated /health and negative unauthorized tests."
