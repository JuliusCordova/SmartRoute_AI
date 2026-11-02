#!/usr/bin/env bash
# Private Cloud Run smoke. Requires an audience-bound Google ID token for the URL.
set -euo pipefail
: "${SERVICE_URL:?Set SERVICE_URL from deployed Cloud Run URL}"
: "${ACCESS_TOKEN:?Set ACCESS_TOKEN to a short-lived Google ID token; never log it}"
case "$SERVICE_URL" in
  https://*) ;;
  *) echo "ERROR: Cloud Run smoke requires HTTPS URL" >&2; exit 2 ;;
esac

for endpoint in health ready; do
  # curl failure, invalid JSON or unexpected readiness status fail the CI job.
  response="$(curl --fail --silent --show-error --max-time 20 --retry 2 \
    --header "Authorization: Bearer ${ACCESS_TOKEN}" \
    "${SERVICE_URL%/}/${endpoint}")"
  if [ "$endpoint" = "health" ]; then
    printf '%s' "$response" | python3 -c '
import json,sys
r=json.load(sys.stdin)
assert r.get("status") == "ok" and r.get("service") == "smartroute-api"
'
  else
    printf '%s' "$response" | python3 -c '
import json,sys
r=json.load(sys.stdin)
assert r.get("status") == "ready" and r.get("scope") == "process-only"
'
  fi
  echo "Smoke PASS: /${endpoint}"
done
# NOTE: process-level only, NOT a Firebase-authenticated Firestore persistence test.
