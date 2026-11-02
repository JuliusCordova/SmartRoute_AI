#!/usr/bin/env bash
# One-time, explicitly gated GCP identity bootstrap for SmartRoute AI.
# Creates only dedicated service accounts and a dedicated GitHub WIF pool/provider.
# DOES NOT grant project-wide deploy roles, Firestore access, or enable GitHub staging.
set -euo pipefail
PROJECT="proyectopersonal-480420"
NUMBER="913797829604"
POOL="smartroute-ci"
PROVIDER="smartroute-main"
REPO="JuliusCordova/SmartRoute_AI"

if [[ "${CONFIRM_SMARTROUTE_IDENTITY_SETUP:-}" != "$PROJECT/$POOL" ]]; then
  echo "DRY RUN: no changes applied."
  echo "Creates service accounts: smartroute-deployer, smartroute-runtime, smartroute-smoke"
  echo "Creates WIF pool: $POOL and GitHub OIDC provider: $PROVIDER for $REPO main only"
  echo "Does not grant Firestore, Cloud Run or deploy IAM permissions."
  echo "To execute the approved identity-only bootstrap:"
  echo "CONFIRM_SMARTROUTE_IDENTITY_SETUP=$PROJECT/$POOL bash scripts/gcp-bootstrap-smartroute-identities.sh"
  exit 0
fi

ACTIVE_PROJECT="$(gcloud config get-value project 2>/dev/null)"
if [[ "$ACTIVE_PROJECT" != "$PROJECT" ]]; then
  echo "ERROR: active Cloud Shell project must be $PROJECT" >&2
  exit 1
fi

# Require the named database to exist with deletion protection before creating identities.
db="$(gcloud firestore databases describe --project="$PROJECT" --database=smartroute --format='value(name)')"
[[ "$db" == "projects/$PROJECT/databases/smartroute" ]] || { echo "ERROR: expected named database missing"; exit 1; }

for name in smartroute-deployer smartroute-runtime smartroute-smoke; do
  email="$name@$PROJECT.iam.gserviceaccount.com"
  if gcloud iam service-accounts describe "$email" --project="$PROJECT" >/dev/null 2>&1; then
    echo "Service account exists: $email"
  else
    gcloud iam service-accounts create "$name" --project="$PROJECT" --display-name="SmartRoute $name"
  fi
done

pool_name="projects/$NUMBER/locations/global/workloadIdentityPools/$POOL"
if gcloud iam workload-identity-pools describe "$POOL" --project="$PROJECT" --location=global >/dev/null 2>&1; then
  echo "Pool already exists; STOP to review manually to prevent modifying an unrelated trust configuration."
  exit 1
fi

gcloud iam workload-identity-pools create "$POOL" \
  --project="$PROJECT" --location=global \
  --display-name="SmartRoute CI isolated"
gcloud iam workload-identity-pools providers create-oidc "$PROVIDER" \
  --project="$PROJECT" --location=global \
  --workload-identity-pool="$POOL" \
  --display-name="SmartRoute main only" \
  --issuer-uri="https://token.actions.githubusercontent.com" \
  --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository,attribute.ref=assertion.ref" \
  --attribute-condition="assertion.repository=='$REPO' && assertion.ref=='refs/heads/main'"

echo "Created WIF provider: $pool_name/providers/$PROVIDER"
echo "Identities created, but NO WIF service-account trust granted yet."
echo "Runbook: docs/GCP_IDENTITY_BOOTSTRAP.md"
