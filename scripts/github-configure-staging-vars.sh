#!/usr/bin/env bash
# One-time GitHub Actions configuration for SmartRoute, staging OFF by design.
set -euo pipefail
REPO="JuliusCordova/SmartRoute_AI"
command -v gh >/dev/null || { echo "ERROR: GitHub CLI gh is required" >&2; exit 2; }
gh auth status >/dev/null || { echo "ERROR: gh login required" >&2; exit 2; }
echo "Target GitHub repo: $REPO"
echo "Setting seven non-secret repo variables for SmartRoute only."
echo "GCP_STAGING_ENABLED will be explicitly FALSE."
if [[ "${CONFIRM_SMARTROUTE_GH_VARS:-}" != "$REPO" ]]; then
  echo "DRY RUN: no GitHub settings modified."
  echo "CONFIRM_SMARTROUTE_GH_VARS=$REPO bash scripts/github-configure-staging-vars.sh"
  exit 0
fi
gh variable set GCP_STAGING_ENABLED --repo "$REPO" --body false
gh variable set GCP_PROJECT_ID --repo "$REPO" --body proyectopersonal-480420
gh variable set GCP_REGION --repo "$REPO" --body us-central1
gh variable set GCP_FIRESTORE_DATABASE_ID --repo "$REPO" --body smartroute
gh variable set GCP_WIF_PROVIDER --repo "$REPO" --body projects/913797829604/locations/global/workloadIdentityPools/smartroute-ci/providers/smartroute-main
gh variable set GCP_DEPLOYER_SERVICE_ACCOUNT --repo "$REPO" --body smartroute-deployer@proyectopersonal-480420.iam.gserviceaccount.com
gh variable set GCP_RUNTIME_SERVICE_ACCOUNT --repo "$REPO" --body smartroute-runtime@proyectopersonal-480420.iam.gserviceaccount.com
gh variable set GCP_SMOKE_SERVICE_ACCOUNT --repo "$REPO" --body smartroute-smoke@proyectopersonal-480420.iam.gserviceaccount.com
actual="$(gh variable get GCP_STAGING_ENABLED --repo "$REPO")"
[[ "$actual" == "false" ]] || { echo "ERROR: staging safety flag is not false" >&2; exit 1; }
echo "PASS: GitHub repository variables configured; GCP_STAGING_ENABLED=false."
echo "No GitHub Actions environment created; no deployment triggered."
