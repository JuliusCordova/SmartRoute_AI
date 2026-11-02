#!/usr/bin/env bash
set -euo pipefail
: "${SERVICE_URL:?Set SERVICE_URL}"
: "${ACCESS_TOKEN:?Set authorized identity token (do not log)}"
curl --fail --silent --show-error -H "Authorization: Bearer $ACCESS_TOKEN" "${SERVICE_URL%/}/health" | python3 -c 'import json,sys; d=json.load(sys.stdin); assert d["status"]=="ok", d; print("Smoke PASS: /health")'
