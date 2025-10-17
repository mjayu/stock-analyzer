#!/usr/bin/env bash
set -euo pipefail

# scripts/run_app.sh
# Simple helper to run the Streamlit app from the project's .venv.
# Usage: ./scripts/run_app.sh [--port PORT] [--foreground] [--no-headless]
# Options:
#   --port PORT       : port to run (default 8501)
#   --foreground      : run in foreground (default is background)
#   --no-headless     : allow Streamlit to open a browser (not recommended in CI)

PORT=8501
FOREGROUND=0
HEADLESS=1

while [[ $# -gt 0 ]]; do
  case "$1" in
    --port)
      PORT="$2"
      shift 2
      ;;
    --foreground)
      FOREGROUND=1
      shift
      ;;
    --no-headless)
      HEADLESS=0
      shift
      ;;
    -h|--help)
      sed -n '1,120p' "$0"
      exit 0
      ;;
    *)
      echo "Unknown arg: $1" >&2
      exit 2
      ;;
  esac
done

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

if [[ -f ".env" ]]; then
  # Export variables from .env (simple, best-effort)
  set -o allexport
  # shellcheck disable=SC1091
  source .env
  set +o allexport
fi

if [[ -x ".venv/bin/streamlit" ]]; then
  STREAMLIT_BIN=".venv/bin/streamlit"
else
  echo ".venv not found or streamlit not installed. Run: ./scripts/setup_env.sh" >&2
  exit 1
fi

CMD=("$STREAMLIT_BIN" run app.py "--server.port" "$PORT")
if [[ "$HEADLESS" -eq 1 ]]; then
  CMD+=("--server.headless" "true")
fi

mkdir -p .venv/logs

if [[ "$FOREGROUND" -eq 1 ]]; then
  echo "Starting Streamlit in foreground on port $PORT"
  exec "${CMD[@]}"
else
  echo "Starting Streamlit in background on port $PORT"
  nohup "${CMD[@]}" > .venv/logs/streamlit.log 2>&1 &
  PID=$!
  echo $PID > .venv/streamlit.pid
  echo "Streamlit started (pid=$PID). Logs: .venv/logs/streamlit.log"
  echo "You can bring it foreground with: kill -SIGINT $PID"
fi
