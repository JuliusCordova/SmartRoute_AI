#!/usr/bin/env bash
# Opt-in real Firestore test using service-account impersonation.
# Dry run default, no IAM changes, no writes to shared databases.
set -euo pipefail
PROJECT="proyectopersonal-480420"
DB="smartroute"
RUNTIME="smartroute-runtime@$PROJECT.iam.gserviceaccount.com"
[[ "$(gcloud config get-value project 2>/dev/null)" == "$PROJECT" ]] || { echo "ERROR: wrong active project" >&2; exit 1; }
[[ -f services/api/app/firestore_config.py ]] || { echo "ERROR: run from SmartRoute_AI root" >&2; exit 1; }
[[ -z "${FIRESTORE_EMULATOR_HOST:-}" ]] || { echo "ERROR: FIRESTORE_EMULATOR_HOST present" >&2; exit 1; }
command -v python3 >/dev/null || { echo "ERROR: python3 required" >&2; exit 1; }
gcloud iam service-accounts describe "$RUNTIME" --project="$PROJECT" --format='value(email)' >/dev/null
gcloud firestore databases describe --database="$DB" --project="$PROJECT" --format='value(name)' >/dev/null
echo "Real Firestore E2E target: projects/$PROJECT/databases/$DB"
echo "Identity: impersonated $RUNTIME (short-lived token, no keys)"
echo "Synthetic operations: create 1 driver + 1 order + 1 route; assign, read, delete exact IDs."
echo "No Firebase user authentication, app HTTP transport, other database, IAM or deployment writes."
if [[ "${CONFIRM_SMARTROUTE_FIRESTORE_TEST:-}" != "$PROJECT/$DB" ]]; then
  echo "DRY RUN: no synthetic data created."
  echo "CONFIRM_SMARTROUTE_FIRESTORE_TEST=$PROJECT/$DB bash scripts/gcp-firestore-runtime-e2e.sh"
  exit 0
fi
# Use isolated temporary Python virtual environment so API dependencies do not pollute Cloud Shell.
VENV="$(mktemp -d /tmp/smartroute-firestore-e2e.XXXXXXXX)"
cleanup(){ rm -rf "$VENV"; }
trap cleanup EXIT
python3 -m venv "$VENV"
"$VENV/bin/python" -m pip install --disable-pip-version-check -q \
  'google-cloud-firestore>=2.19,<3' 'google-auth>=2.0,<3' 'pydantic>=2.8,<3'
export GOOGLE_CLOUD_PROJECT="$PROJECT"
export FIRESTORE_DATABASE_ID="$DB"
export PYTHONPATH="services/api"
"$VENV/bin/python" scripts/gcp-firestore-runtime-e2e.py
