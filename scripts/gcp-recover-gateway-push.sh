#!/usr/bin/env bash
# Recovery ONLY for gateway Docker push failed on transient Artifact Registry network error.
# Reuses the EXACT image that was built from commit 78c1104; no rebuild or broad IAM.
set -euo pipefail
PROJECT=proyectopersonal-480420
REGION=us-central1
REPO=smartroute-staging
SERVICE=smartroute-gateway-staging
GATEWAY_SA="smartroute-gateway@$PROJECT.iam.gserviceaccount.com"
BACKEND=smartroute-api-staging
BACKEND_SA="smartroute-runtime@$PROJECT.iam.gserviceaccount.com"
BACKEND_URL="https://smartroute-api-staging-913797829604.us-central1.run.app"
SOURCE_SHA=78c1104a5eb901f1225e3651be71f3c944593f88
IMAGE="$REGION-docker.pkg.dev/$PROJECT/$REPO/smartroute-gateway"
TAG="$IMAGE:$SOURCE_SHA"
fail(){ echo "ERROR: $*" >&2; exit 1; }
[[ "$(gcloud config get-value project 2>/dev/null)" == "$PROJECT" ]] || fail "wrong active project"
[[ -f services/gateway/Dockerfile ]] || fail "run from SmartRoute_AI root"
[[ "$(gcloud artifacts repositories describe "$REPO" --project="$PROJECT" --location="$REGION" --format='value(format)')" == "DOCKER" ]] || fail "dedicated Docker repository absent/mismatch"
[[ "$(gcloud iam service-accounts describe "$GATEWAY_SA" --project="$PROJECT" --format='value(email)')" == "$GATEWAY_SA" ]] || fail "gateway SA absent"
[[ "$(gcloud run services describe "$BACKEND" --project="$PROJECT" --region="$REGION" --format='value(spec.template.spec.serviceAccountName)')" == "$BACKEND_SA" ]] || fail "backend runtime SA mismatch"
if gcloud run services describe "$SERVICE" --project="$PROJECT" --region="$REGION" >/dev/null 2>&1; then
  fail "gateway service already exists; refuse to overwrite without inspection"
fi
p="$(gcloud run services get-iam-policy "$BACKEND" --project="$PROJECT" --region="$REGION" --format=json)"
BACKEND_POLICY="$p" GATEWAY_SA="$GATEWAY_SA" python3 - <<'PY'
import json, os, sys
policy=json.loads(os.environ["BACKEND_POLICY"])
members=[m for b in policy.get("bindings",[]) if b.get("role")=="roles/run.invoker" for m in b.get("members",[])]
if f"serviceAccount:{os.environ['GATEWAY_SA']}" not in members:
    sys.exit("ERROR: missing gateway-only backend invoker")
if any(m in ("allUsers","allAuthenticatedUsers") for b in policy.get("bindings",[]) for m in b.get("members",[])):
    sys.exit("ERROR: backend has public principal")
print("PASS: scoped backend invoke IAM, no public principals")
PY
command -v docker >/dev/null || fail "docker is required"
docker image inspect "$TAG" >/dev/null || fail "original Docker image not found locally: $TAG. Do not rebuild or retag silently."
echo "Recovery target: $TAG"
echo "This script reuses the original image built from commit $SOURCE_SHA."
echo "Retries ONLY docker push (up to 4 attempts); new Cloud Run service stays private."
echo "Cloud Run max instances 1, min 0, runtime $GATEWAY_SA"
echo "New image storage / Cloud Run may incur costs; no IAM or Firebase changes."
if [[ "${CONFIRM_SMARTROUTE_GATEWAY_RECOVERY:-}" != "$PROJECT/$SERVICE" ]]; then
  echo "DRY RUN: no Docker push or Cloud Run deployment."
  echo "CONFIRM_SMARTROUTE_GATEWAY_RECOVERY=$PROJECT/$SERVICE bash scripts/gcp-recover-gateway-push.sh"
  exit 0
fi

gcloud auth configure-docker "$REGION-docker.pkg.dev" --quiet
LOG="$(mktemp /tmp/smartroute-gateway-push.XXXXXXXX)"
trap 'rm -f "$LOG"' EXIT
OK=false
for attempt in 1 2 3 4; do
  echo "Docker push attempt $attempt/4"
  if docker push "$TAG" 2>&1 | tee "$LOG"; then
    OK=true
    break
  fi
  if [[ "$attempt" -lt 4 ]]; then sleep 5; fi
done
[[ "$OK" == true ]] || fail "Registry push still failing; no Cloud Run deployment attempted"
DIGEST="$(awk '/digest: sha256:/ {for (i=1;i<=NF;i++) if ($i=="digest:") print $(i+1)}' "$LOG" | tail -n 1)"
[[ "$DIGEST" =~ ^sha256:[a-f0-9]{64}$ ]] || fail "Push lacked validated immutable digest; no deployment"
echo "PASS: immutable image push: $IMAGE@$DIGEST"
# Recheck absence after push, so recovery cannot overwrite a concurrent deployment.
if gcloud run services describe "$SERVICE" --project="$PROJECT" --region="$REGION" >/dev/null 2>&1; then
  fail "gateway appeared during push; inspect it before deploying"
fi

gcloud run deploy "$SERVICE" \
  --project="$PROJECT" --region="$REGION" \
  --image="$IMAGE@$DIGEST" \
  --service-account="$GATEWAY_SA" \
  --no-allow-unauthenticated --ingress=all \
  --min-instances=0 --max-instances=1 \
  --cpu=1 --memory=512Mi --concurrency=10 --timeout=30s \
  --set-env-vars="APP_ENV=staging,GOOGLE_CLOUD_PROJECT=$PROJECT,SMARTROUTE_BACKEND_URL=$BACKEND_URL,SMARTROUTE_GATEWAY_ENABLED=true" \
  --quiet
[[ "$(gcloud run services describe "$SERVICE" --project="$PROJECT" --region="$REGION" --format='value(spec.template.spec.serviceAccountName)')" == "$GATEWAY_SA" ]] || fail "runtime identity mismatch"
policy="$(gcloud run services get-iam-policy "$SERVICE" --project="$PROJECT" --region="$REGION" --format=json)"
GATEWAY_POLICY="$policy" python3 - <<'PY'
import json, os, sys
p=json.loads(os.environ["GATEWAY_POLICY"])
if any(m in ("allUsers","allAuthenticatedUsers") for b in p.get("bindings",[]) for m in b.get("members",[])):
    sys.exit("ERROR: gateway has public Cloud Run IAM principal")
print("PASS: private gateway IAM has no public principals")
PY
echo "PASS: gateway deployed privately from original immutable Docker image."
echo "Next: authenticated health and Firebase negative-case smoke; continuous staging still disabled."
