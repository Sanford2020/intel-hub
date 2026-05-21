#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VENDOR="$ROOT/.vendor"

echo "=== OPC Scaffold: Sync Integrations ==="

mkdir -p "$VENDOR"

# OPC Methodology
if [ ! -d "$VENDOR/opc-methodology" ]; then
  git clone --depth 1 https://github.com/easychen/opc-methodology.git "$VENDOR/opc-methodology"
else
  git -C "$VENDOR/opc-methodology" pull --ff-only
fi
mkdir -p "$ROOT/skills/opc"
cp -r "$VENDOR/opc-methodology/skills/"* "$ROOT/skills/opc/"
echo "OPC skills -> skills/opc/"

# Agency Agents
if [ ! -d "$VENDOR/agency-agents" ]; then
  git clone --depth 1 https://github.com/msitarzewski/agency-agents.git "$VENDOR/agency-agents"
else
  git -C "$VENDOR/agency-agents" pull --ff-only
fi
mkdir -p "$ROOT/agents/agency"
for div in engineering design product marketing project-management testing strategy support; do
  [ -d "$VENDOR/agency-agents/$div" ] && cp -r "$VENDOR/agency-agents/$div" "$ROOT/agents/agency/"
done
echo "Agency agents -> agents/agency/"
echo "=== Done ==="
