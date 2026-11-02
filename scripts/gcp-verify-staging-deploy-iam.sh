#!/usr/bin/env bash
# Read-only, minimum-output check of resource-scoped SmartRoute CI IAM grants.
set -euo pipefail
PROJECT=proyectopersonal-480420
REGION=us-central1
REPO=smartroute-staging
SERVICE=smartroute-api-staging
DEPLOYER="serviceAccount:smartroute-deployer@$PROJECT.iam.gserviceaccount.com"
SMOKE="serviceAccount:smartroute-smoke@$PROJECT.iam.gserviceaccount.com"
[[ "$(gcloud config get-value project 2>/dev/null)" == "$PROJECT" ]] || { echo "FAIL: unexpected project" >&2; exit 1; }
validate_policy() {
 local label="$1" role="$2" member="$3" policy="$4"
 IAM_POLICY="$policy" ROLE="$role" MEMBER="$member" LABEL="$label" python3 - <<'PY'
import json,os,sys
policy=json.loads(os.environ["IAM_POLICY"])
role=os.environ["ROLE"]
member=os.environ["MEMBER"]
label=os.environ["LABEL"]
match=[b for b in policy.get("bindings",[]) if b.get("role")==role and member in b.get("members",[])]
if len(match)!=1 or "condition" in match[0]:
    sys.exit("FAIL: "+label)
print("PASS: "+label)
PY
}
echo "Checking SmartRoute IAM stage 2 (read-only, scoped resources)..."
policy="$(gcloud artifacts repositories get-iam-policy "$REPO" --project="$PROJECT" --location="$REGION" --format=json)"
validate_policy "deployer can push to SmartRoute Docker repo" "roles/artifactregistry.writer" "$DEPLOYER" "$policy"
policy="$(gcloud run services get-iam-policy "$SERVICE" --project="$PROJECT" --region="$REGION" --format=json)"
validate_policy "deployer can update SmartRoute Cloud Run" "roles/run.developer" "$DEPLOYER" "$policy"
validate_policy "smoke can invoke SmartRoute Cloud Run" "roles/run.invoker" "$SMOKE" "$policy"
SERVICE_POLICY_JSON="$policy" python3 - <<'PY'
import json,os,sys
p=json.loads(os.environ["SERVICE_POLICY_JSON"])
assert not any(any(m in ("allUsers","allAuthenticatedUsers") for m in b.get("members",[])) for b in p.get("bindings",[])), "FAIL: public Cloud Run IAM principal"
print("PASS: no public principal in service IAM policy")
PY
policy="$(gcloud iam service-accounts get-iam-policy "smartroute-runtime@$PROJECT.iam.gserviceaccount.com" --project="$PROJECT" --format=json)"
validate_policy "deployer can act as SmartRoute runtime only" "roles/iam.serviceAccountUser" "$DEPLOYER" "$policy"
policy="$(gcloud iam service-accounts get-iam-policy "smartroute-smoke@$PROJECT.iam.gserviceaccount.com" --project="$PROJECT" --format=json)"
validate_policy "smoke can mint ID tokens for own service account" "roles/iam.serviceAccountTokenCreator" "$SMOKE" "$policy"
echo "PASS: five direct Stage 2 IAM bindings validated; no changes applied."
echo "NOTE: this does not prove effective permissions, inherited grants or GitHub OIDC smoke."
