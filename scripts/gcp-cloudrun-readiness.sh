#!/usr/bin/env bash
# SmartRoute Cloud Run build/deploy readiness — READ ONLY.
# Prints narrowly scoped metadata only; never dumps shared project IAM policies.
set -euo pipefail
PROJECT="proyectopersonal-480420"
NUMBER="913797829604"
REGION="${SMARTROUTE_REGION:-us-central1}"
DEPLOYER="smartroute-deployer@$PROJECT.iam.gserviceaccount.com"
RUNTIME="smartroute-runtime@$PROJECT.iam.gserviceaccount.com"
SMOKE="smartroute-smoke@$PROJECT.iam.gserviceaccount.com"
echo "=== SmartRoute Cloud Run staging readiness (read-only) ==="
[[ "$(gcloud config get-value project 2>/dev/null)" == "$PROJECT" ]] || { echo "ERROR: wrong active GCP project" >&2; exit 1; }
echo "Project: $PROJECT ($NUMBER); proposed region: $REGION"
echo "--- Required APIs (names only) ---"
gcloud services list --project="$PROJECT" --enabled \
 --filter='config.name:(run.googleapis.com OR cloudbuild.googleapis.com OR artifactregistry.googleapis.com OR iamcredentials.googleapis.com OR sts.googleapis.com OR firestore.googleapis.com)' \
 --format='value(config.name)'
echo "--- Build identity resolved by Cloud Build ---"
if gcloud builds get-default-service-account --project="$PROJECT" --format='value(serviceAccountEmail)'; then
  echo "PASS: Cloud Build default identity queried"
else
  echo "WARNING: default build SA inspection unavailable; identify build identity in Console before deployment"
fi
echo "--- Compute build account (metadata only) ---"
gcloud iam service-accounts describe "$NUMBER-compute@developer.gserviceaccount.com" \
 --project="$PROJECT" --format='value(email,disabled)' || true
echo "--- SmartRoute dedicated identities ---"
for SA in "$DEPLOYER" "$RUNTIME" "$SMOKE"; do
  gcloud iam service-accounts describe "$SA" --project="$PROJECT" --format='value(email,disabled)'
done
echo "--- Existing service name collision ---"
gcloud run services list --project="$PROJECT" --region="$REGION" \
 --filter='metadata.name:smartroute-api-staging' --format='value(metadata.name)' || true
echo "--- Region and project constraints (no mutations) ---"
echo "Source deploy would require project-scoped run.sourceDeveloper and serviceusage.serviceUsageConsumer."
echo "ServiceAccountUser should bind only the dedicated runtime identity; build account needs run.builder."
echo "Cloud Run service must remain private and GCP_STAGING_ENABLED must stay false."
echo "No IAM policies changed; no GCP resource created."
