#!/usr/bin/env bash
# One-time explicitly authorized Firestore database creation for SmartRoute AI.
# Run manually in Cloud Shell. Does not change existing databases, IAM or billing.
set -euo pipefail

PROJECT="proyectopersonal-480420"
DATABASE="smartroute"
LOCATION="nam5"

command -v gcloud >/dev/null || { echo "ERROR: gcloud CLI required" >&2; exit 2; }
echo "Target: project=$PROJECT, database=$DATABASE, location=$LOCATION"
echo "Expected: Standard edition / Firestore Native / deletion protection enabled"

# Any API lookup error is fatal; do not mistake permission/transport failures for absence.
if gcloud firestore databases describe --project="$PROJECT" --database="$DATABASE" --format="value(name)" >/dev/null 2>&1; then
  echo "Database already exists. No changes applied."
  gcloud firestore databases describe --project="$PROJECT" --database="$DATABASE" --format="yaml(name,locationId,type,edition,deleteProtectionState)"
  exit 0
fi
echo "Checking existing database inventory before potential creation..."
gcloud firestore databases list --project="$PROJECT" --format="value(name)" >/dev/null
# Must still inspect billing setup yourself before executing. Named databases have no free tier.
echo "WARNING: this named Firestore database is usage-billed and has no free tier."
echo "This script does not configure a spending cap or budget alert."
if [[ "${CONFIRM_CREATE_SMARTROUTE_DB:-}" != "$PROJECT/$DATABASE" ]]; then
  echo "No changes applied. To authorize this exact operation, run:"
  echo "CONFIRM_CREATE_SMARTROUTE_DB=$PROJECT/$DATABASE bash scripts/gcp-create-smartroute-db.sh"
  exit 2
fi

gcloud firestore databases create \
  --project="$PROJECT" \
  --database="$DATABASE" \
  --location="$LOCATION" \
  --edition=standard \
  --type=firestore-native \
  --delete-protection

gcloud firestore databases describe --project="$PROJECT" --database="$DATABASE" \
  --format="yaml(name,locationId,type,edition,deleteProtectionState)"
echo "Created database. Do NOT enable staging until IAM/WIF, app access and costs are verified."
