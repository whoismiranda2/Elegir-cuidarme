#!/bin/bash
# Actualizar la app con los últimos cambios del repo
# Uso:  bash /opt/elegir-cuidarme/deploy/update.sh

set -e
APP_DIR="/opt/elegir-cuidarme"
SERVICE_NAME="elegir-cuidarme"

echo "Descargando cambios..."
cd "$APP_DIR"
git pull origin main

echo "Actualizando dependencias..."
source venv/bin/activate
pip install -q -r requirements.txt

echo "Reiniciando servicio..."
sudo systemctl restart "$SERVICE_NAME"

echo "✅ Actualización completa. Estado del servicio:"
sudo systemctl status "$SERVICE_NAME" --no-pager -l
