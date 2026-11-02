#!/usr/bin/env bash
set -euo pipefail
: "${GCP_PROJECT:?Set GCP_PROJECT}"
: "${GCP_REGION:?Set GCP_REGION}"
: "${GCP_SERVICE_ACCOUNT:?Set dedicated GCP_SERVICE_ACCOUNT email}"
: "${DEPLOY_APPROVED:?Set DEPLOY_APPROVED=yes only after human review}"
test "$DEPLOY_APPROVED" = "yes" || { echo "Deployment requires explicit human approval"; exit 1; }
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
gcloud config set project "$GCP_PROJECT"
gcloud run deploy smartroute-api \
  --source "$ROOT/services/api" \
  --region "$GCP_REGION" \
  --service-account "$GCP_SERVICE_ACCOUNT" \
  --no-allow-unauthenticated \
  --set-env-vars APP_ENV=staging
echo "Deploy requested; verify revision, URL and smoke result before marking gate PASS."
