# Evidence · SmartRoute gateway first private deploy PASS

Cloud Shell owner ran `scripts/gcp-deploy-published-gateway-private.sh` after a successful dry-run. Command completed successfully with:
- GCP project `proyectopersonal-480420`, region `us-central1`.
- Cloud Run service `smartroute-gateway-staging`.
- Revision `smartroute-gateway-staging-00001-bq9`, serving 100% traffic.
- Cloud Run URL `https://smartroute-gateway-staging-913797829604.us-central1.run.app`.
- Dedicated service account `smartroute-gateway@proyectopersonal-480420.iam.gserviceaccount.com`.
- Private backend `smartroute-api-staging` with scoped `roles/run.invoker` for gateway service account.
- Published image exact digest `sha256:d5c6abe6d73fd8b1ee4b0a8364ad89fb10799c67cc063c1b8f72826397c8ab47`.
- `PASS: gateway private IAM; no public principals` and `PASS: first private gateway Cloud Run deploy from GitHub-published immutable image.`

This is **deployment evidence**, not an end-to-end functional validation. HTTP `/health`, direct unauthenticated rejection, Firebase verification, backend delegation and Firestore persistence are still pending. Direct service IAM checks do not automatically prove absence of project-level invoker grants or special Cloud Run org configurations. Keep `GCP_STAGING_ENABLED=false` and do not modify Firebase shared providers/users or Firestore `(default)`/`gestioncitas`.

## Safe next check (read-only)

```bash
PROJECT=proyectopersonal-480420
REGION=us-central1
SERVICE=smartroute-gateway-staging
URL=https://smartroute-gateway-staging-913797829604.us-central1.run.app

echo '=== Gateway runtime ==='
gcloud run services describe "$SERVICE" --project="$PROJECT" --region="$REGION" \
  --format='yaml(metadata.name,status.url,status.latestReadyRevisionName,spec.template.spec.serviceAccountName)'

echo '=== Direct Cloud Run IAM policy ==='
gcloud run services get-iam-policy "$SERVICE" --project="$PROJECT" --region="$REGION" \
  --format='json(bindings)'

echo '=== Unauthenticated /health must be denied ==='
STATUS="$(curl -sS -o /dev/null -w '%{http_code}' --max-time 15 "$URL/health")"
echo "Unauthenticated HTTP: $STATUS"
case "$STATUS" in
  401|403) echo 'PASS: unauthenticated Cloud Run request rejected' ;;
  *) echo "FAIL: unexpected HTTP $STATUS; stop before further exposure"; exit 1 ;;
esac

echo '=== Continuous deploy must remain disabled ==='
gh variable get GCP_STAGING_ENABLED --repo JuliusCordova/SmartRoute_AI
```

The `/health` endpoint does not require Firebase itself but Cloud Run IAM must protect it; a 401/403 unauthenticated response validates a useful rejection test, not the full policy / perimeter.

**Authenticated gateway health**: use a caller that already has service-specific `roles/run.invoker` on the gateway (do not assume the owner account has it). Before granting any access, inspect current roles and permissions; if needed request explicit owner approval for service-level `roles/run.invoker`, not project-wide roles. With an authorized identity, call `/health` via `gcloud run services proxy` or an audience-bound ID token. Next, test Firebase missing/invalid tokens through that authenticated Cloud Run channel, then a real OPERATOR account.

## Overall architecture invariants

Dedicated Firestore `smartroute` only, other apps untouched; backend remains private; gateway stays IAM-private and has no Firestore IAM roles; staging auto deploy disabled. Opening gateway to Android/web in later phase requires separate security and cost approval.
