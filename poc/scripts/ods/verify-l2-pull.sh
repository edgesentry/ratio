#!/usr/bin/env bash
# Low-level curl smoke for L2 Pull. Asserted consumer: uv run ratio-poc-pull --via l2
# Consumer-side Pull check: L2 → Ratio industry (products only; never raw).
set -euo pipefail

L2_URL="${RATIO_ODS_L2_URL:-http://localhost:8090}"
API_KEY="${RATIO_ODS_L2_API_KEY:-${RATIO_ODS_API_KEY:-2dfd3409-ce01-4451-96fa-7e10c9681422y}}"
STEM="${1:-}"
TOKEN="${RATIO_ODS_BEARER:-}"

if [[ -z "$TOKEN" ]]; then
  echo "Fetching L3 token…" >&2
  TOKEN="$(dirname "$0")/fetch-l3-token.sh"
  TOKEN="$("$TOKEN")"
fi

if [[ -z "$STEM" ]]; then
  echo "GET ${L2_URL}/products (catalog via industry)" >&2
  curl -sf "${L2_URL}/products" \
    -H "API-Key: ${API_KEY}" \
    -H "Authorization: Bearer ${TOKEN}" \
    -H "X-TrackingId: $(uuidgen | tr '[:upper:]' '[:lower:]')" \
    -H "X-ODS-UserId: ${RATIO_ODS_USER_ID:-ratio-poc}"
  echo
else
  echo "GET ${L2_URL}/products/${STEM}" >&2
  curl -sf "${L2_URL}/products/${STEM}" \
    -H "API-Key: ${API_KEY}" \
    -H "Authorization: Bearer ${TOKEN}" \
    -H "X-TrackingId: $(uuidgen | tr '[:upper:]' '[:lower:]')" \
    -H "X-ODS-UserId: ${RATIO_ODS_USER_ID:-ratio-poc}" \
    -H "Accept: application/ld+json"
  echo
fi

code=$(curl -s -o /dev/null -w '%{http_code}' "${L2_URL}/raw/" \
  -H "API-Key: ${API_KEY}" \
  -H "Authorization: Bearer ${TOKEN}" || true)
echo "raw path via L2 HTTP ${code} (expect 404)" >&2
