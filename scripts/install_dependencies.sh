#!/usr/bin/env bash
set -euo pipefail

echo "=== [INSTALL_DEPENDENCIES] Starting installation ==="

APP_DIR="/home/ubuntu/ai_horizons"
VENV_DIR="$APP_DIR/venv"

# Ensure correct ownership
sudo chown -R ubuntu:ubuntu "$APP_DIR"

# Create virtual environment if not exists
if [ ! -d "$VENV_DIR" ]; then
  echo "Creating Python virtual environment..."
  python3 -m venv "$VENV_DIR"
fi

# Activate the virtual environment
source "$VENV_DIR/bin/activate"

# Upgrade pip and install dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
if [ -f "$APP_DIR/requirements.txt" ]; then
  pip install -r "$APP_DIR/requirements.txt"
fi

# Ensure Gunicorn is installed
pip install gunicorn

# Copy systemd and nginx configs if exist
if [ -f "$APP_DIR/deploy/ai_horizons.service" ]; then
  echo "Copying systemd service file..."
  sudo cp -f "$APP_DIR/deploy/ai_horizons.service" /etc/systemd/system/ai_horizons.service
fi

if [ -f "$APP_DIR/deploy/nginx-ai_horizons.conf" ]; then
  echo "Copying Nginx config..."
  sudo cp -f "$APP_DIR/deploy/nginx-ai_horizons.conf" /etc/nginx/conf.d/ai_horizons.conf
  sudo nginx -t && sudo systemctl restart nginx
fi

# Reload systemd daemon
sudo systemctl daemon-reload
sudo systemctl enable ai_horizons.service

echo "=== [INSTALL_DEPENDENCIES] Completed successfully ==="
