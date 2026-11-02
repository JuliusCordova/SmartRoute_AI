#!/usr/bin/env bash
# Recover from a transient Docker push failure AFTER build succeeded.
# Reuses the existing local image, retries upload, then creates only SmartRoute Cloud Run staging.
set -euo pipefail
PROJECT="proyectopersonal-480420"
REGION="us-central1"
REPO="smartroute-staging"
SERVICE="smartroute-api-staging"
RUNTIME="smartroute-runtime@$PROJECT.iam.gserviceaccount.com"
SHA="${SMARTROUTE_IMAGE_SHA:-}"
[[ "$SHA" =~ ^[a-f0-9]{40}$ ]] || { echo "ERROR: SMARTROUTE_IMAGE_SHA must be the full commit SHA of the already-built image" >&2; exit 2; }
IMAGE="$REGION-docker.pkg.dev/$PROJECT/$REPO/smartroute-api:$SHA"
[[ "$(gcloud config get-value project 2>/dev/null)" == "$PROJECT" ]] || { echo "ERROR: wrong active project" >&2; exit 1; }
gcloud artifacts repositories describe "$REPO" --project="$PROJECT" --location="$REGION" --format='value(name)' >/dev/null || exit 1
gcloud iam service-accounts describe "$RUNTIME" --project="$PROJECT" --format='value(email)' >/dev/null || exit 1
if gcloud run services describe "$SERVICE" --project="$PROJECT" --region="$REGION" --format='value(metadata.name)' >/dev/null 2>&1; then
  echo "ERROR: staging Cloud Run service already exists; inspect before changing it" >&2
  exit 1
fi
if ! docker image inspect "$IMAGE" >/dev/null 2>&1; then
  echo "ERROR: built image not present in this Cloud Shell Docker context: $IMAGE" >&2
  echo "Return to original Cloud Shell session; rebuilding should be a separate decision."
  exit 1
fi
echo "Recovery target: $IMAGE"
echo "Uses existing local Docker image; no re-build, no Firestore/IAM changes."
echo "Retries registry push up to four times; then deploys private Cloud Run 0-2 instances."
if [[ "${CONFIRM_SMARTROUTE_RECOVERY:-}" != "$PROJECT/$SERVICE" ]]; then
  echo "DRY RUN: no upload or deployment performed."
  echo "CONFIRM_SMARTROUTE_RECOVERY=$PROJECT/$SERVICE SMARTROUTE_IMAGE_SHA=$SHA bash scripts/gcp-recover-staging-push.sh"
  exit 0
fi
gcloud auth configure-docker "$REGION-docker.pkg.dev" --quiet
pushed=0
for attempt in 1 2 3 4; do
  echo "Push attempt $attempt/4"
  if docker push "$IMAGE"; then
    pushed=1
    break
  fi
  if (( attempt < 4 )); then sleep $((attempt * 8)); fi
done
if [[ "$pushed" != 1 ]]; then
  echo "ERROR: registry push still failing. Do NOT deploy; inspect Cloud Shell network status." >&2
  exit 1
fi
echo "Docker push successful; creating only the authorized private Cloud Run service."
gcloud run deploy "$SERVICE" --project="$PROJECT" --region="$REGION" \
  --image="$IMAGE" --service-account="$RUNTIME" \
  --no-allow-unauthenticated --ingress=all \
  --min-instances=0 --max-instances=2 \
  --cpu=1 --memory=512Mi --concurrency=10 --timeout=30s \
  --set-env-vars="APP_ENV=staging,FIREBASE_PROJECT_ID=$PROJECT,GOOGLE_CLOUD_PROJECT=$PROJECT,FIRESTORE_DATABASE_ID=smartroute" \
  --quiet
gcloud run services describe "$SERVICE" --project="$PROJECT" --region="$REGION" \
  --format="yaml(metadata.name,status.url,status.conditions,spec.template.spec.serviceAccountName)"
echo "Recovery deployment complete. GitHub staging remains disabled."
