#!/usr/bin/env bash
# Register OpenFGA tuples for Ratio industry endpoints (products GET/POST).
# Prerequisites: OpenFGA on :8083; FGA_STORE_ID from l2/docker-compose.yml.
set -euo pipefail

FGA_URL="${RATIO_ODS_FGA_URL:-http://localhost:8083}"
STORE_ID="${RATIO_ODS_FGA_STORE_ID:?set RATIO_ODS_FGA_STORE_ID from l2/docker-compose.yml FGA_STORE_ID}"
OPERATOR_ID="${RATIO_ODS_OPERATOR_ID:-}"

write_tuples() {
  local body="$1"
  local label="$2"
  local code
  code=$(curl -s -o /tmp/ratio-fga-write.json -w '%{http_code}' -X POST \
    "${FGA_URL}/stores/${STORE_ID}/write" \
    -H "Content-Type: application/json" \
    -d "${body}")
  if [[ "$code" == "200" ]]; then
    echo "OK: ${label}"
    return 0
  fi
  # Idempotent: already-exists is fine
  if [[ "$code" == "400" ]] && grep -q 'already exists' /tmp/ratio-fga-write.json 2>/dev/null; then
    echo "OK: ${label} (already present)"
    return 0
  fi
  echo "FAIL: ${label} HTTP ${code}" >&2
  python3 -c 'import json;print(json.load(open("/tmp/ratio-fga-write.json")))' >&2 || cat /tmp/ratio-fga-write.json >&2
  return 1
}

write_tuples '{
  "writes": {
    "tuple_keys": [
      { "user": "group:endpoint-products-get#member",  "relation": "can_access", "object": "endpoint:products.get" },
      { "user": "group:endpoint-products-post#member", "relation": "can_access", "object": "endpoint:products.post" }
    ]
  }
}' "endpoint tuples for products.get / products.post"

if [[ -n "${OPERATOR_ID}" ]]; then
  MODEL_ID="${RATIO_ODS_FGA_MODEL_ID:?set RATIO_ODS_FGA_MODEL_ID when granting operator}"
  write_tuples "{
      \"authorization_model_id\": \"${MODEL_ID}\",
      \"writes\": {
        \"tuple_keys\": [
          { \"user\": \"user:${OPERATOR_ID}\", \"relation\": \"member\", \"object\": \"group:endpoint-products-get\" },
          { \"user\": \"user:${OPERATOR_ID}\", \"relation\": \"member\", \"object\": \"group:endpoint-products-post\" }
        ]
      }
    }" "operator ${OPERATOR_ID} → products get/post groups"
else
  echo "NOTE: set RATIO_ODS_OPERATOR_ID (+ RATIO_ODS_FGA_MODEL_ID) to grant a business operator"
fi
