#!/usr/bin/env bash
# Safe opt-in IAM stage 1 for existing SmartRoute resources.
# Dedicated project/repo/Firestore DB. NO broad Cloud Run deploy roles granted.
set -euo pipefail
PROJECT="proyectopersonal-480420"
NUMBER="913797829604"
POOL="smartroute-ci"
PROVIDER="smartroute-main"
REPO="JuliusCordova/SmartRoute_AI"
DB="smartroute"
WIF="projects/$NUMBER/locations/global/workloadIdentityPools/$POOL"
PRINCIPAL="principalSet://iam.googleapis.com/$WIF/attribute.repository/$REPO"
DEPLOYER="smartroute-deployer@$PROJECT.iam.gserviceaccount.com"
RUNTIME="smartroute-runtime@$PROJECT.iam.gserviceaccount.com"
SMOKE="smartroute-smoke@$PROJECT.iam.gserviceaccount.com"

die() { echo "ERROR: $*" >&2; exit 1; }
command -v gcloud >/dev/null || die "gcloud required"
[[ "$(gcloud config get-value project 2>/dev/null)" == "$PROJECT" ]] || die "unexpected active GCP project"
for sa in "$DEPLOYER" "$RUNTIME" "$SMOKE"; do
  gcloud iam service-accounts describe "$sa" --project="$PROJECT" --format='value(email)' >/dev/null || die "missing $sa"
done

db_path="$(gcloud firestore databases describe --project="$PROJECT" --database="$DB" --format='value(name)')" || die "cannot inspect Firestore"
[[ "$db_path" == "projects/$PROJECT/databases/$DB" ]] || die "unexpected Firestore database"

# Exact provider settings are checked via structured JSON to fail closed.
provider_json="$(gcloud iam workload-identity-pools providers describe "$PROVIDER" --project="$PROJECT" --location=global --workload-identity-pool="$POOL" --format=json)" || die "missing provider"
export PROVIDER_JSON="$provider_json"
python3 - <<'PY'
import json, os, sys
p = json.loads(os.environ["PROVIDER_JSON"])
cond = p.get("attributeCondition", "")
expected = ("assertion.repository=='JuliusCordova/SmartRoute_AI'", "assertion.ref=='refs/heads/main'")
checks = [
    p.get("state") == "ACTIVE",
    p.get("oidc", {}).get("issuerUri") == "https://token.actions.githubusercontent.com",
    all(x in cond for x in expected),
    p.get("attributeMapping", {}).get("attribute.repository") == "assertion.repository",
    p.get("attributeMapping", {}).get("google.subject") == "assertion.sub",
]
if not all(checks):
    sys.exit("ERROR: OIDC provider is not the expected repo/main-scoped provider")
PY
unset PROVIDER_JSON

echo "Verified approved repo/main OIDC provider, service accounts and named Firestore DB."
echo "Plan: grant roles/iam.workloadIdentityUser for repo-scoped principal on DEPLOYER and SMOKE accounts only."
echo "Plan: grant runtime roles/datastore.user with resource.name condition on ONLY projects/$PROJECT/databases/$DB."
echo "NO Cloud Run deploy, build, Firebase, serviceAccountUser, service invocation or billing roles."
if [[ "${CONFIRM_SMARTROUTE_IAM_BINDINGS:-}" != "$PROJECT/$DB" ]]; then
  echo "DRY RUN: no IAM policy changed."
  echo "Execute only after reviewing the plan:"
  echo "CONFIRM_SMARTROUTE_IAM_BINDINGS=$PROJECT/$DB bash scripts/gcp-bind-smartroute-iam.sh"
  exit 0
fi

# IAM trust binds only to dedicated service accounts (not project-level).
for sa in "$DEPLOYER" "$SMOKE"; do
  gcloud iam service-accounts add-iam-policy-binding "$sa" \
    --project="$PROJECT" \
    --member="$PRINCIPAL" \
    --role="roles/iam.workloadIdentityUser" --quiet
done

# The predefined Firestore role is project-bindable; use an exact resource.name IAM Condition.
# This cannot grant access to Atlas (default) or gestioncitas through this binding.
gcloud projects add-iam-policy-binding "$PROJECT" \
  --member="serviceAccount:$RUNTIME" \
  --role="roles/datastore.user" \
  --condition="expression=resource.name=='projects/$PROJECT/databases/$DB',title=SmartRouteDbOnly,description=SmartRoute named Firestore database only" \
  --quiet

echo "IAM STAGE 1 COMPLETE. Do not enable GCP_STAGING_ENABLED yet."
echo "Verify service account IAM bindings and runtime conditional role in Google Cloud Console."
