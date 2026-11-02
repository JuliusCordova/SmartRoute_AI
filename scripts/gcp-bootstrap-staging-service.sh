#!/usr/bin/env bash
# Explicitly authorized bootstrap: dedicated Artifact Registry + private Cloud Run staging.
# Run manually in Cloud Shell after reviewing scope and costs.
set -euo pipefail
PROJECT="proyectopersonal-480420"
REGION="us-central1"
REPOSITORY="smartroute-staging"
SERVICE="smartroute-api-staging"
RUNTIME="smartroute-runtime@$PROJECT.iam.gserviceaccount.com"
IMAGE="$REGION-docker.pkg.dev/$PROJECT/$REPOSITORY/smartroute-api"
SHA="$(git rev-parse --verify HEAD)"
TAG="$IMAGE:$SHA"

command -v gcloud >/dev/null || { echo "ERROR: gcloud required" >&2; exit 2; }
command -v docker >/dev/null || { echo "ERROR: docker required; use Cloud Shell" >&2; exit 2; }
[[ "$(gcloud config get-value project 2>/dev/null)" == "$PROJECT" ]] || { echo "ERROR: unexpected active project" >&2; exit 1; }
[[ -f services/api/Dockerfile ]] || { echo "ERROR: execute from SmartRoute_AI repository root" >&2; exit 1; }
[[ "$(gcloud firestore databases describe --project="$PROJECT" --database=smartroute --format='value(name)')" == "projects/$PROJECT/databases/smartroute" ]] || { echo "ERROR: dedicated Firestore database missing" >&2; exit 1; }
gcloud iam service-accounts describe "$RUNTIME" --project="$PROJECT" --format='value(email)' >/dev/null
echo "Project: $PROJECT / Region: $REGION"
echo "Artifact Registry Docker repository: $REPOSITORY"
echo "Cloud Run service (private): $SERVICE / runtime identity: $RUNTIME"
echo "Image: $TAG"
echo "Scaling: 0 to 2 instances; 1 CPU; 512Mi RAM; concurrency 10"
echo "This may incur Artifact Registry, Cloud Run, network and logging costs."
echo "NO budget cap is created by this script. GitHub staging remains disabled."
if [[ "${CONFIRM_SMARTROUTE_STAGING_BOOTSTRAP:-}" != "$PROJECT/$SERVICE" ]]; then
  echo "DRY RUN: nothing created or modified."
  echo "After owner approval, execute:"
  echo "CONFIRM_SMARTROUTE_STAGING_BOOTSTRAP=$PROJECT/$SERVICE bash scripts/gcp-bootstrap-staging-service.sh"
  exit 0
fi

# Fail closed if a service with this name already exists. Never alter an unrelated service.
if gcloud run services describe "$SERVICE" --project="$PROJECT" --region="$REGION" --format='value(metadata.name)' >/dev/null 2>&1; then
  echo "ERROR: $SERVICE already exists. Inspect it manually; no deployment attempted." >&2
  exit 1
fi

if gcloud artifacts repositories describe "$REPOSITORY" --project="$PROJECT" --location="$REGION" --format='value(name)' >/dev/null 2>&1; then
  FORMAT="$(gcloud artifacts repositories describe "$REPOSITORY" --project="$PROJECT" --location="$REGION" --format='value(format)')"
  [[ "$FORMAT" == "DOCKER" ]] || { echo "ERROR: existing repo is not Docker" >&2; exit 1; }
  echo "Using preexisting SmartRoute-only Docker repo (name and format checked); inspect ownership if unexpected."
else
  gcloud artifacts repositories create "$REPOSITORY" --project="$PROJECT" \
    --location="$REGION" --repository-format=docker \
    --description="Isolated SmartRoute AI staging images"
fi

gcloud auth configure-docker "$REGION-docker.pkg.dev" --quiet
docker build --pull -t "$TAG" services/api
docker push "$TAG"

# Owner executes initial deploy. This action creates only the dedicated service.
gcloud run deploy "$SERVICE" \
  --project="$PROJECT" --region="$REGION" \
  --image="$TAG" \
  --service-account="$RUNTIME" \
  --no-allow-unauthenticated \
  --ingress=all \
  --min-instances=0 --max-instances=2 \
  --cpu=1 --memory=512Mi --concurrency=10 \
  --timeout=30s \
  --set-env-vars="APP_ENV=staging,FIREBASE_PROJECT_ID=$PROJECT,GOOGLE_CLOUD_PROJECT=$PROJECT,FIRESTORE_DATABASE_ID=smartroute" \
  --quiet

echo "--- Verified dedicated staging service ---"
gcloud run services describe "$SERVICE" --project="$PROJECT" --region="$REGION" \
  --format="yaml(metadata.name,status.url,spec.template.spec.serviceAccountName,spec.template.spec.containerConcurrency,spec.template.metadata.annotations)"
echo "Bootstrap complete. No GitHub deployment permissions granted; GCP_STAGING_ENABLED remains false."
