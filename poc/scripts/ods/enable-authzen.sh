#!/usr/bin/env bash
# Enable AuthZEN on the official L2 gateway (SDK-docker-compose) and re-register Ratio routes.
# Requires RATIO_ODS_SDK_DIR (default ~/work/open-dataspaces/SDK-docker-compose).
set -euo pipefail

SDK_DIR="${RATIO_ODS_SDK_DIR:-$HOME/work/open-dataspaces/SDK-docker-compose}"
COMPOSE="$SDK_DIR/l2/docker-compose.yml"
ENABLE="${1:-true}"

if [[ ! -f "$COMPOSE" ]]; then
  echo "FAIL: missing $COMPOSE (set RATIO_ODS_SDK_DIR)" >&2
  exit 1
fi

if [[ "$ENABLE" != "true" && "$ENABLE" != "false" ]]; then
  echo "Usage: $0 [true|false]" >&2
  exit 2
fi

python3 - "$COMPOSE" "$ENABLE" <<'PY'
from pathlib import Path
import sys
path, enable = Path(sys.argv[1]), sys.argv[2]
text = path.read_text(encoding="utf-8")
old_t = "AUTHZEN_AUTHORIZATION_ENABLED=true"
old_f = "AUTHZEN_AUTHORIZATION_ENABLED=false"
new = f"AUTHZEN_AUTHORIZATION_ENABLED={enable}"
if old_t in text:
    text = text.replace(old_t, new)
elif old_f in text:
    text = text.replace(old_f, new)
else:
    raise SystemExit("AUTHZEN_AUTHORIZATION_ENABLED not found in compose")
path.write_text(text, encoding="utf-8")
print(f"set {new}")
PY

cd "$SDK_DIR"
docker compose up -d gateway
echo "Waiting for gateway…" >&2
sleep 4

ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
bash "$ROOT/poc/scripts/ods/register-ratio-routes.sh"
echo "OK: AuthZEN=${ENABLE}; Ratio /products/** routes re-registered" >&2
echo "Verify: source poc/scripts/ods/.local/operator.env && bash poc/scripts/ods/verify-l2-pull.sh k1-<stem>" >&2
