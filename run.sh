#!/usr/bin/env bash
# ==========================================================
#  CargoOpt - one-click start for macOS / Linux
#  Run:  bash run.sh
#  The first run installs everything (needs internet).
# ==========================================================
set -e
cd "$(dirname "$0")"
echo
echo " CargoOpt - Truck Load Optimizer"
echo " ==============================="

# ---------- 1. find Python ----------
PY="$(command -v python3 || command -v python || true)"
if [ -z "$PY" ]; then
  echo " Python 3 is not installed. Install it from https://www.python.org/downloads/ and run this again."
  exit 1
fi
echo " Found $("$PY" --version 2>&1)"

# ---------- 2. private environment (.venv) ----------
if [ ! -x .venv/bin/python ]; then
  echo " [1/3] Creating a private Python environment in .venv ..."
  "$PY" -m venv .venv || { echo " Could not create .venv (on Ubuntu/Debian: sudo apt install python3-venv)"; exit 1; }
fi

# ---------- 3. install packages (only when requirements.txt changed) ----------
if ! cmp -s requirements.txt .venv/requirements.installed; then
  echo " [2/3] Installing packages - first time only, this can take a few minutes ..."
  .venv/bin/python -m pip install --upgrade pip --quiet
  .venv/bin/python -m pip install -r requirements.txt
  cp requirements.txt .venv/requirements.installed
fi

# ---------- 4. start the app and open the browser ----------
echo " [3/3] Starting CargoOpt at http://localhost:8501  (press Ctrl+C to stop)"
( sleep 5; (open http://localhost:8501 || xdg-open http://localhost:8501) >/dev/null 2>&1 ) &
exec .venv/bin/python -m streamlit run app.py --server.port 8501 --browser.gatherUsageStats false
