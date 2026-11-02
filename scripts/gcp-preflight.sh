#!/usr/bin/env bash
# Read-only inventory. No APIs enabled, IAM modified, databases created or services deployed.
set -euo pipefail
PROJECT_ID="proyectopersonal-480420"
echo "SmartRoute GCP PRE-FLIGHT (read only)"
echo "Project: ${PROJECT_ID}"
if ! command -v gcloud >/dev/null 2>&1; then
  echo "ERROR: install gcloud CLI or run in Cloud Shell" >&2
  exit 2
fi
gcloud auth list --filter=status:ACTIVE --format="value(account)" | head -n 1
echo "----- Project metadata -----"
gcloud projects describe "$PROJECT_ID" --format="table(projectId,projectNumber,lifecycleState)"
echo "----- Firestore databases (READ ONLY) -----"
gcloud firestore databases list --project="$PROJECT_ID" --format="table(name,locationId,type,edition)" || {
  echo "NOTE: Firestore database inventory unavailable; verify API access/roles without enabling APIs blindly."
}
echo "----- Cloud Run services (READ ONLY) -----"
gcloud run services list --project="$PROJECT_ID" --format="table(metadata.name,metadata.namespace,status.url)" || {
  echo "NOTE: Run inventory unavailable; verify access manually."
}
echo "----- Service accounts with SmartRoute name (READ ONLY) -----"
gcloud iam service-accounts list --project="$PROJECT_ID" --filter="email~smartroute" --format="table(email,displayName)" || true
echo "----- Existing Workload Identity Pools (READ ONLY) -----"
gcloud iam workload-identity-pools list --project="$PROJECT_ID" --location=global --format="table(name,state)" || true
echo "----- Relevant services enabled (READ ONLY) -----"
gcloud services list --enabled --project="$PROJECT_ID" --filter="NAME:(firestore.googleapis.com run.googleapis.com cloudbuild.googleapis.com iamcredentials.googleapis.com sts.googleapis.com artifactregistry.googleapis.com)" --format="value(config.name)" || true
echo ""
echo "PRE-FLIGHT COMPLETE. This command DID NOT authorize a deploy or configure billing."
echo "STOP if Firestore (default) already holds unrelated data. Review docs/GCP_EXISTING_PROJECT_RUNBOOK.md."
