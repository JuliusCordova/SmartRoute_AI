#!/usr/bin/env bash
# Run the complete FastAPI suite ONLY when the local Firestore emulator is available.
set -euo pipefail

: "${FIRESTORE_EMULATOR_HOST:?Firestore emulator required; refusing live Firestore}"
if [[ "$FIRESTORE_EMULATOR_HOST" != "127.0.0.1:8085" && "$FIRESTORE_EMULATOR_HOST" != "localhost:8085" ]]; then
  echo "Refusing unexpected Firestore emulator endpoint: $FIRESTORE_EMULATOR_HOST" >&2
  exit 2
fi
export GOOGLE_CLOUD_PROJECT=demo-smartroute
export FIREBASE_PROJECT_ID=demo-smartroute
export FIRESTORE_EMULATOR_REQUIRED=1
export FIRESTORE_DATABASE_ID="(default)"
unset GOOGLE_APPLICATION_CREDENTIALS CLOUDSDK_AUTH_CREDENTIAL_FILE_OVERRIDE

mkdir -p qa-results
python -m pytest -q tests --junitxml=qa-results/backend-junit.xml
