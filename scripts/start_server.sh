#!/usr/bin/env bash
set -e

echo "=== Starting AI Horizons service ==="
sudo systemctl restart ai_horizons.service
sudo systemctl enable ai_horizons.service
echo "Service started successfully."
