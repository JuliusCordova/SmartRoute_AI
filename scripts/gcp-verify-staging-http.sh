#!/usr/bin/env bash
# Read-only HTTP health verification of private SmartRoute staging through gcloud proxy.
set -euo pipefail
PROJECT="proyectopersonal-480420"
REGION="us-central1"
SERVICE="smartroute-api-staging"
PORT=18088
[[ "$(gcloud config get-value project 2>/dev/null)" == "$PROJECT" ]] || { echo "ERROR: select the approved GCP project" >&2; exit 1; }
gcloud run services describe "$SERVICE" --project="$PROJECT" --region="$REGION" --format='value(metadata.name)' >/dev/null
echo "Starting temporary authenticated localhost proxy; no resources modified."
gcloud run services proxy "$SERVICE" --project="$PROJECT" --region="$REGION" --port="$PORT" >/tmp/smartroute-proxy-output.log 2>&1 &
PID=$!
cleanup(){ kill "$PID" 2>/dev/null || true; wait "$PID" 2>/dev/null || true; }
trap cleanup EXIT
READY=0
for i in {1..15}; do
  if ! kill -0 "$PID" 2>/dev/null; then
    echo "ERROR: gcloud proxy terminated; see /tmp/smartroute-proxy-output.log" >&2
    exit 1
  fi
  if curl --silent --max-time 2 --output /dev/null "http://127.0.0.1:$PORT/health"; then READY=1; break; fi
  sleep 2
done
[[ "$READY" == 1 ]] || { echo "ERROR: localhost proxy not ready; inspect /tmp/smartroute-proxy-output.log" >&2; exit 1; }
for endpoint in health ready; do
  curl --fail --silent --show-error --max-time 20 "http://127.0.0.1:$PORT/$endpoint" | \
    ENDPOINT="$endpoint" python3 -c 'import json,os,sys
r=json.load(sys.stdin)
if os.environ["ENDPOINT"]=="health":
    assert r.get("status")=="ok" and r.get("service")=="smartroute-api"
else:
    assert r.get("status")=="ready" and r.get("scope")=="process-only"
'
  echo "PASS: /$endpoint"
done
echo "Read-only HTTP smoke PASS. Firestore business access and Firebase sign-in are NOT tested."
