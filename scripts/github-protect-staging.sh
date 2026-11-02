#!/usr/bin/env bash
# GitHub repository branch + environment protection. Dry-run unless explicit opt-in.
set -euo pipefail
REPO="JuliusCordova/SmartRoute_AI"
command -v gh >/dev/null || { echo "ERROR: GitHub CLI required" >&2; exit 2; }
gh auth status >/dev/null || { echo "ERROR: gh login required" >&2; exit 2; }
visibility="$(gh api "repos/$REPO" --jq '.private')"
[[ "$visibility" == "false" ]] || { echo "ERROR: this protection plan assumes a public repo; inspect plan and settings" >&2; exit 1; }
enabled="$(gh variable get GCP_STAGING_ENABLED --repo "$REPO")"
[[ "$enabled" == "false" ]] || { echo "ERROR: GCP_STAGING_ENABLED must be false" >&2; exit 1; }
echo "GitHub repo: $REPO (public). GCP_STAGING_ENABLED=false."
echo "Plan: protect main with required api-tests + firestore-emulator checks;"
echo "      block force pushes/deletion; do not require another PR reviewer."
echo "Plan: create staging environment restricted to protected branches only."
echo "      No deployment approvals enforced; no CI/CD activation."
if [[ "${CONFIRM_SMARTROUTE_GH_PROTECTION:-}" != "$REPO" ]]; then
  echo "DRY RUN: no GitHub settings changed."
  echo "CONFIRM_SMARTROUTE_GH_PROTECTION=$REPO bash scripts/github-protect-staging.sh"
  exit 0
fi
# Never overwrite existing protections without a separate review.
if gh api "repos/$REPO/branches/main/protection" >/dev/null 2>&1; then
  echo "ERROR: main branch protection already exists; inspect it; refusing overwrite" >&2
  exit 1
fi
if gh api "repos/$REPO/environments/staging" >/dev/null 2>&1; then
  echo "ERROR: staging environment already exists; inspect it; refusing overwrite" >&2
  exit 1
fi

# Safe ordered mutations: branch protection first, environment second.
gh api --method PUT "repos/$REPO/branches/main/protection" \
  -H "Accept: application/vnd.github+json" --input - >/dev/null <<'JSON'
{
 "required_status_checks":{"strict":true,"contexts":["api-tests","firestore-emulator"]},
 "enforce_admins":false,
 "required_pull_request_reviews":null,
 "restrictions":null,
 "required_linear_history":true,
 "allow_force_pushes":false,
 "allow_deletions":false,
 "required_conversation_resolution":true,
 "lock_branch":false
}
JSON
echo "PASS: main branch protection created; validating..."
gh api "repos/$REPO/branches/main/protection" \
  --jq '{required_checks:.required_status_checks.contexts,strict:.required_status_checks.strict,force_pushes:.allow_force_pushes.enabled,deletions:.allow_deletions.enabled,admin_enforcement:.enforce_admins.enabled}'

gh api --method PUT "repos/$REPO/environments/staging" \
  -H "Accept: application/vnd.github+json" --input - >/dev/null <<'JSON'
{"deployment_branch_policy":{"protected_branches":true,"custom_branch_policies":false}}
JSON
echo "PASS: staging environment created; validating..."
gh api "repos/$REPO/environments/staging" \
  --jq '{name,protected_branches:.deployment_branch_policy.protected_branches,custom_branch_policies:.deployment_branch_policy.custom_branch_policies}'
[[ "$(gh variable get GCP_STAGING_ENABLED --repo "$REPO")" == "false" ]] || { echo "ERROR: staging flag changed unexpectedly" >&2; exit 1; }
echo "PASS: GitHub branch and environment guardrails configured. Staging automation remains disabled."
