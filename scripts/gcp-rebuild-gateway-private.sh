#!/usr/bin/env bash
# Cloud Shell recovery when original Docker image is no longer cached.
# Rebuilds gateway from a vetted, unchanged source tree and deploys privately.
set -euo pipefail
PROJECT=proyectopersonal-480420
REGION=us-central1
REPO=smartroute-staging
SERVICE=smartroute-gateway-staging
GATEWAY_SA="smartroute-gateway@$PROJECT.iam.gserviceaccount.com"
BACKEND=smartroute-api-staging
BACKEND_SA="smartroute-runtime@$PROJECT.iam.gserviceaccount.com"
BACKEND_URL="https://smartroute-api-staging-913797829604.us-central1.run.app"
BASE_SHA=78c1104a5eb901f1225e3651be71f3c944593f88
IMAGE="$REGION-docker.pkg.dev/$PROJECT/$REPO/smartroute-gateway"
TAG="$IMAGE:$SOURCE_SHA"
fail(){ echo "ERROR: $*" >&2; exit 1; }
[[ "$(git branch --show-current)" == "main" ]] || fail "must run on main"
[[ -z "$(git status --porcelain)" ]] || fail "working tree must be clean; inspect untracked files, no global clean"
SOURCE_SHA="$(git rev-parse HEAD)"
[[ "$SOURCE_SHA" == "$(git rev-parse origin/main)" ]] || fail "local main not synchronized with origin/main"
git cat-file -e "$BASE_SHA^{commit}" || fail "original vetted commit unavailable; fetch main history"
git diff --quiet "$BASE_SHA" HEAD -- services/gateway || fail "gateway source has changed since vetted version; review before rebuilding"
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
echo "PASS: gateway sources match original vetted commit $BASE_SHA"
echo "Recovery target: $TAG"
echo "Rebuilds gateway from current clean main SHA $SOURCE_SHA (gateway source unchanged since $BASE_SHA)."
echo "Builds once locally, then retries docker push up to 4 times; new Cloud Run service stays private."
echo "Cloud Run max instances 1, min 0, runtime $GATEWAY_SA"
echo "New image storage / Cloud Run may incur costs; no IAM or Firebase changes."
if [[ "${CONFIRM_SMARTROUTE_GATEWAY_REBUILD:-}" != "$PROJECT/$SERVICE" ]]; then
  echo "DRY RUN: no Docker build, push or Cloud Run deployment."
  echo "CONFIRM_SMARTROUTE_GATEWAY_RECOVERY=$PROJECT/$SERVICE bash scripts/gcp-rebuild-gateway-private.sh"
  exit 0
fi

gcloud auth configure-docker "$REGION-docker.pkg.dev" --quiet
echo "Building gateway once from vetted source..."
docker build --pull -t "$TAG" services/gateway
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
echo "PASS: gateway rebuilt from vetted gateway source and deployed privately by digest."
echo "Next: authenticated health and Firebase negative-case smoke; continuous staging still disabled."
