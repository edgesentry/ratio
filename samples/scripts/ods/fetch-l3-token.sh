#!/usr/bin/env bash
# Fetch L3 access token via client credentials (operator or system client).
# Prints token to stdout; other messages on stderr.
# See L3 tutorial 2-2-1 / auth/token/client.
set -euo pipefail

L3_URL="${RATIO_ODS_L3_URL:-http://localhost:8080}"
API_KEY="${RATIO_ODS_API_KEY:-API-Key-Sample}"
CLIENT_ID="${RATIO_ODS_CLIENT_ID:?set RATIO_ODS_CLIENT_ID}"
CLIENT_SECRET="${RATIO_ODS_CLIENT_SECRET:?set RATIO_ODS_CLIENT_SECRET}"

resp=$(curl -sf -X POST "${L3_URL}/auth/token/client" \
  -H "Content-Type: application/json" \
  -H "API-Key: ${API_KEY}" \
  -d "{\"client_id\": \"${CLIENT_ID}\", \"client_secret\": \"${CLIENT_SECRET}\"}")

token=$(printf '%s' "$resp" | python3 -c 'import sys,json; d=json.load(sys.stdin); print((d.get("data") or d).get("access_token") or "")')
if [[ -z "$token" || "$token" == "None" ]]; then
  echo "FAIL: no access_token in response: $resp" >&2
  exit 1
fi
echo "$token"
