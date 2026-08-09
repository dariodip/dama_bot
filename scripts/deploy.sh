#!/usr/bin/env bash

set -euo pipefail

# ==============================
# Configuration
# ==============================

REMOTE_USER=$1
REMOTE_HOST=$2
REMOTE_DIR="/home/${REMOTE_USER}/dama_bot"

SERVICE_NAME="dama-bot"

# ==============================
# Helpers
# ==============================

log() {
    echo
    echo "==> $1"
}

# ==============================
# Deploy
# ==============================

log "Syncing project to Raspberry Pi"

rsync -avz --delete \
    --exclude '.git/' \
    --exclude '.venv/' \
    --exclude '__pycache__/' \
    --exclude '*.pyc' \
    --exclude '.DS_Store' \
    ./ "${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_DIR}/"

log "Installing dependencies"

ssh "${REMOTE_USER}@${REMOTE_HOST}" << EOF
set -e

cd "${REMOTE_DIR}"

uv sync
EOF

log "Installing systemd service"

ssh "${REMOTE_USER}@${REMOTE_HOST}" "sudo tee /etc/systemd/system/${SERVICE_NAME}.service > /dev/null" << EOF
[Unit]
Description=Dama Telegram Bot
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=${REMOTE_USER}
WorkingDirectory=${REMOTE_DIR}

ExecStart=${REMOTE_DIR}/.venv/bin/dama-bot

Restart=always
RestartSec=5

Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOF

log "Reloading systemd"

ssh "${REMOTE_USER}@${REMOTE_HOST}" << EOF
set -e

sudo systemctl daemon-reload
sudo systemctl enable "${SERVICE_NAME}"
sudo systemctl restart "${SERVICE_NAME}"

echo
echo "Service status:"
sudo systemctl --no-pager --full status "${SERVICE_NAME}"
EOF

log "Deploy completed"