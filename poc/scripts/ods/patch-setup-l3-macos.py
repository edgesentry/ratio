#!/usr/bin/env python3
"""Patch SDK setup_l3.sh for macOS (no GNU grep -P / gawk)."""
from __future__ import annotations

import re
from pathlib import Path

p = Path("/Users/yoheionishi/work/open-dataspaces/SDK-docker-compose/setup/setup_l3.sh")
bak = Path(str(p) + ".bak-macos")
# Always restore from bak if present so patch is idempotent
if bak.exists():
    src = bak.read_text(encoding="utf-8")
else:
    src = p.read_text(encoding="utf-8")
    bak.write_text(src, encoding="utf-8")

lines = src.splitlines(keepends=True)
out: list[str] = []
i = 0
py_extract = (
    '  | python3 -c "import sys,re; '
    "m=re.search(r'\\\"id\\\":\\\"([^\\\"]+)\\\"', sys.stdin.read()); "
    "print(m.group(1) if m else '')\"\n"
)
replaced_grep = 0
while i < len(lines):
    line = lines[i]
    if "grep -Po" in line and "id" in line:
        out.append(py_extract)
        replaced_grep += 1
        i += 1
        if i < len(lines) and "head -1" in lines[i]:
            i += 1
        continue
    out.append(line)
    i += 1

text = "".join(out)

new_port_fn = '''get_compose_host_port() {
  local service="$1"
  local container_port="$2"
  # Prefer live published port (works on macOS without GNU awk)
  local cid
  cid=$(docker compose -f "$DOCKER_COMPOSE_FILE" ps -q "$service" 2>/dev/null | head -1)
  if [ -n "$cid" ]; then
    docker port "$cid" "${container_port}/tcp" 2>/dev/null | sed -n 's/.*:\\([0-9]*\\)$/\\1/p' | head -1
    return 0
  fi
  python3 - "$DOCKER_COMPOSE_FILE" "$service" "$container_port" <<'PY'
import re, sys
path, service, cport = sys.argv[1], sys.argv[2], sys.argv[3]
in_service = in_ports = False
for line in open(path, encoding="utf-8"):
    if re.match(rf"^  {re.escape(service)}:", line):
        in_service, in_ports = True, False
        continue
    if in_service and re.match(r"^  [^\\s].*:$", line) and not line.startswith("    "):
        in_service = in_ports = False
    if in_service and re.match(r"^    ports:\\s*$", line):
        in_ports = True
        continue
    if in_service and in_ports and not line.startswith("      "):
        in_ports = False
    if in_service and in_ports:
        m = re.match(r'^\\s*-\\s*"?([0-9]+):([0-9]+)"?', line)
        if m and m.group(2) == cport:
            print(m.group(1))
            break
PY
}
'''

text, nport = re.subn(
    r"get_compose_host_port\(\) \{.*?\n\}",
    lambda _m: new_port_fn,
    text,
    count=1,
    flags=re.S,
)
print(f"host_port replacements={nport}, grep replacements={replaced_grep}")

text = text.replace('sed -i "', 'sed -i.bak "')

if "grep -P" in text:
    raise SystemExit("grep -P still present after patch")

p.write_text(text, encoding="utf-8")
print(f"wrote {p}")
