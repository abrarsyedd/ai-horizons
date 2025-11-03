#!/usr/bin/env bash
set -e

echo "=== Stopping AI Horizons service ==="
sudo systemctl stop ai_horizons.service || true
echo "Service stopped (if running)."
