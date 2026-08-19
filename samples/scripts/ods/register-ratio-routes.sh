#!/usr/bin/env bash
# Register L2 gateway routes that forward /products** to Ratio industry stub.
# Prerequisites: SDK-docker-compose gateway on :8090; ratio-poc-serve on host :8787.
set -euo pipefail

L2_URL="${RATIO_ODS_L2_URL:-http://localhost:8090}"
MGMT_KEY="${RATIO_ODS_L2_MGMT_KEY:-your-secret-management-api-key}"
# From inside Docker, host industry is typically host.docker.internal (Mac/Windows).
INDUSTRY_URI="${RATIO_ODS_INDUSTRY_URI:-http://host.docker.internal:8787}"

register_route() {
  local id="$1"
  local method="$2"
  local endpoint_id="$3"
  local body
  body=$(cat <<EOF
{
  "id": "${id}",
  "uri": "${INDUSTRY_URI}",
  "predicates": [
    { "name": "Path", "args": { "_genkey_0": "/products/**" } },
    { "name": "Method", "args": { "_genkey_0": "${method}" } }
  ],
  "metadata": { "endpointId": "${endpoint_id}" }
}
EOF
)
  curl -sf -X POST \
    -H "Content-Type: application/json" \
    -H "X-API-KEY: ${MGMT_KEY}" \
    -d "${body}" \
    "${L2_URL}/actuator/gateway/routes/${id}"
  echo "registered ${id} ${method} → ${INDUSTRY_URI} (endpointId=${endpoint_id})"
}

register_route "ratio-products-get" "GET" "products.get"
register_route "ratio-products-post" "POST" "products.post"

curl -sf -X POST \
  -H "X-API-KEY: ${MGMT_KEY}" \
  "${L2_URL}/actuator/gateway/refresh" >/dev/null 2>&1 || true
echo "OK: L2 Ratio product routes registered"
