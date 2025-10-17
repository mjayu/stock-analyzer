#!/usr/bin/env bash
set -euo pipefail

# setup_env.sh
# Usage: ./scripts/setup_env.sh [--no-system-deps]
# Installs system deps (optional), creates .venv, installs python deps and
# creates a .env template if missing.

NO_SYSTEM_DEPS=0
if [[ "${1-}" == "--no-system-deps" ]]; then
  NO_SYSTEM_DEPS=1
fi

echo "Running setup script (no-system-deps=$NO_SYSTEM_DEPS)"

if [[ "$NO_SYSTEM_DEPS" -eq 0 ]]; then
  echo "Installing system packages (requires sudo)"
  sudo apt-get update
  sudo apt-get install -y libjpeg-dev zlib1g-dev libpng-dev build-essential python3-dev
else
  echo "Skipping system packages installation"
fi

# create venv
if [[ ! -d ".venv" ]]; then
  echo "Creating virtualenv at .venv"
  python -m venv .venv
else
  echo ".venv already exists, skipping creation"
fi

# upgrade pip and install requirements
echo "Upgrading pip and installing Python dependencies into .venv"
.venv/bin/pip install --upgrade pip setuptools wheel
.venv/bin/pip install -r requirements.txt

# create .env template if not exists
if [[ ! -f ".env" ]]; then
  echo "Creating .env template"
  cat > .env <<EOF
# Put API keys and environment variables here
# Example:
# ALPHA_VANTAGE_KEY=your_key_here
EOF
else
  echo ".env already exists, skipping template creation"
fi

echo "Setup complete. Activate the venv with: source .venv/bin/activate"
echo "Run the app: .venv/bin/streamlit run app.py"
