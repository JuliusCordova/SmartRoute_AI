#!/usr/bin/env bash
# Read-only IAM stage 1 verification. Prints only PASS/FAIL, never full policies.
set -euo pipefail
PROJECT="proyectopersonal-480420"
NUMBER="913797829604"
RUNTIME="smartroute-runtime@$PROJECT.iam.gserviceaccount.com"
PRINCIPAL="principalSet://iam.googleapis.com/projects/$NUMBER/locations/global/workloadIdentityPools/smartroute-ci/attribute.repository/JuliusCordova/SmartRoute_AI"
CONDITION="resource.name=='projects/$PROJECT/databases/smartroute'"

command -v gcloud >/dev/null || { echo "ERROR: gcloud required" >&2; exit 2; }
echo "Checking SmartRoute IAM stage 1 (read only)..."

# Secrets / unrelated project IAM are not echoed. Process JSON in memory.
for name in smartroute-deployer smartroute-smoke; do
  sa="$name@$PROJECT.iam.gserviceaccount.com"
  policy="$(gcloud iam service-accounts get-iam-policy "$sa" --project="$PROJECT" --format=json)" || exit 1
  IAM_POLICY_JSON="$policy" REQUIRED_PRINCIPAL="$PRINCIPAL" python3 - <<'PY'
import json, os, sys
policy=json.loads(os.environ["IAM_POLICY_JSON"])
expected=os.environ["REQUIRED_PRINCIPAL"]
matches=[b for b in policy.get("bindings", []) if b.get("role")=="roles/iam.workloadIdentityUser" and expected in b.get("members", [])]
if not matches:
    sys.exit("FAIL: workload identity binding missing")
print("PASS: repo-scoped WIF binding present")
PY
done

project_policy="$(gcloud projects get-iam-policy "$PROJECT" --format=json)" || exit 1
IAM_POLICY_JSON="$project_policy" RUNTIME="$RUNTIME" CONDITION="$CONDITION" python3 - <<'PY'
import json, os, sys
policy=json.loads(os.environ["IAM_POLICY_JSON"])
member="serviceAccount:"+os.environ["RUNTIME"]
expected=os.environ["CONDITION"]
matches=[b for b in policy.get("bindings", []) if b.get("role")=="roles/datastore.user" and member in b.get("members", [])]
if not matches:
    sys.exit("FAIL: runtime datastore.user binding missing")
if any(b.get("condition", {}).get("expression", "").replace(" ", "") != expected.replace(" ", "") for b in matches):
    sys.exit("FAIL: runtime has datastore.user binding without exact database constraint")
print("PASS: runtime datastore.user is constrained to smartroute database")
PY
echo "PASS: IAM stage 1 bindings are present. No IAM changes applied."
echo "Note: verifies these bindings only, not other inherited permissions or live data-plane access."
