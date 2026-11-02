#!/usr/bin/env bash
# Read-only inspection before configuring SmartRoute IAM/WIF or enabling staging.
set -euo pipefail
PROJECT_ID="proyectopersonal-480420"
PROJECT_NUMBER="913797829604"
DATABASE="smartroute"

command -v gcloud >/dev/null || { echo "ERROR: Cloud Shell/gcloud required"; exit 2; }
echo "=== SmartRoute readonly IAM and Firestore preflight ==="
echo "Project: $PROJECT_ID ($PROJECT_NUMBER)"

echo "--- Dedicated Firestore database ---"
gcloud firestore databases describe --project="$PROJECT_ID" --database="$DATABASE" \
  --format="yaml(name,databaseEdition,locationId,type,deleteProtectionState,freeTier)" || {
  echo "ERROR: named smartroute Firestore database not accessible" >&2; exit 1;
}

echo "--- SmartRoute service accounts (names only) ---"
gcloud iam service-accounts list --project="$PROJECT_ID" \
  --filter='email~smartroute-' --format="value(email)"

echo "--- Workload Identity Pools (names only) ---"
gcloud iam workload-identity-pools list --project="$PROJECT_ID" \
  --location=global --format="value(name,state)"

echo "--- Potential existing SmartRoute staging service ---"
gcloud run services list --project="$PROJECT_ID" \
  --filter='metadata.name:smartroute' --format="table(metadata.name,status.url)"

echo "--- Cloud Build project identity ---"
gcloud projects describe "$PROJECT_ID" --format="value(projectNumber)"

echo "--- GitHub WIF provider collision check (no mutations) ---"
if gcloud iam workload-identity-pools describe smartroute-ci --project="$PROJECT_ID" \
  --location=global --format="value(name)" >/dev/null 2>&1; then
  echo "WARNING: smartroute-ci pool exists. Review its provider and bindings before any changes."
else
  echo "No confirmed smartroute-ci pool. If IAM permissions denied, inspect manually."
fi

echo "=== COMPLETE: no resources or IAM policies changed ==="
echo "Do not paste access tokens, Firebase user details, or complete IAM policy dumps into chat."
