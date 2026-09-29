#!/bin/bash
# Orchestrator: runs every module in order. Stops cold on first failure.
set -euo pipefail
cd "$(dirname "$0")"

echo "=================================================="
echo " 1918: Ace of Aces — App Store Connect Autopilot"
echo "=================================================="

command -v python3 >/dev/null || { echo "ERROR: python3 not found. Install it first."; exit 1; }

if [ ! -f config.env ]; then
  echo "ERROR: config.env not found."
  echo "  cp config.env.example config.env"
  echo "then paste your Key ID, Issuer ID, and .p8 path into it."
  exit 1
fi

echo "--> setting up isolated python env (.venv)"
if [ ! -d .venv ]; then
  python3 -m venv .venv || { echo "ERROR: could not create venv. On Debian/Ubuntu: sudo apt install python3-venv"; exit 1; }
fi
.venv/bin/pip install -q -r requirements.txt
PY=.venv/bin/python

for mod in modules/01_register_bundle_id.py modules/02_enable_iap.py modules/03_create_app.py; do
  echo ""
  echo "--------------------------------------------------"
  echo " Running $mod"
  echo "--------------------------------------------------"
  $PY "$mod" || { echo ""; echo "AUTOPILOT STOPPED: $mod failed. Fix it and re-run ./run-all.sh"; exit 1; }
done

echo ""
echo "=================================================="
echo " ALL MODULES COMPLETE."
echo " Your bundle ID is registered, IAP is enabled, and"
echo " the app record exists in App Store Connect."
echo "=================================================="
