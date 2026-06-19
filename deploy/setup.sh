#!/bin/bash
# =============================================================
#  Elegir Cuidarme — Setup inicial en Oracle Cloud Free Tier
#  Ejecutar UNA SOLA VEZ como usuario ubuntu:
#    bash setup.sh
# =============================================================
# Pasos previos en la consola de Oracle Cloud:
#  1. Crear instancia Ubuntu 22.04 (Always Free: AMD o ARM)
#  2. Descargar la llave SSH que Oracle genera al crearla
#  3. Conectarse:  ssh -i <llave.key> ubuntu@<IP-publica>
#  4. Copiar este archivo y ejecutarlo:
#       scp -i <llave.key> deploy/setup.sh ubuntu@<IP>:~/
#       ssh -i <llave.key> ubuntu@<IP> "bash setup.sh"
#  5. En Oracle Cloud Console → VCN → Security List:
#       Agregar Ingress Rule: TCP puerto 80 desde 0.0.0.0/0
# =============================================================

set -e  # detener si algo falla

APP_DIR="/opt/elegir-cuidarme"
APP_USER="ubuntu"
REPO_URL="https://github.com/whoismiranda2/Elegir-cuidarme.git"
SERVICE_NAME="elegir-cuidarme"

echo ""
echo "┌─────────────────────────────────────────┐"
echo "│  Elegir Cuidarme — Instalación inicial  │"
echo "└─────────────────────────────────────────┘"
echo ""

# ── 1. Sistema ────────────────────────────────────────────────
echo "[1/7] Actualizando paquetes..."
sudo apt-get update -q && sudo apt-get upgrade -y -q

echo "[2/7] Instalando Python, nginx, git..."
sudo apt-get install -y -q python3 python3-pip python3-venv nginx git iptables-persistent

# ── 2. Código ─────────────────────────────────────────────────
echo "[3/7] Clonando repositorio..."
if [ -d "$APP_DIR" ]; then
  sudo rm -rf "$APP_DIR"
fi
sudo git clone "$REPO_URL" "$APP_DIR"
sudo chown -R "$APP_USER":"$APP_USER" "$APP_DIR"

# ── 3. Entorno virtual Python ─────────────────────────────────
echo "[4/7] Creando entorno virtual e instalando dependencias..."
cd "$APP_DIR"
python3 -m venv venv
source venv/bin/activate
pip install -q --upgrade pip
pip install -q -r requirements.txt

# ── 4. Servicio systemd ───────────────────────────────────────
echo "[5/7] Configurando servicio systemd..."
sudo cp "$APP_DIR/deploy/$SERVICE_NAME.service" /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable "$SERVICE_NAME"
sudo systemctl start "$SERVICE_NAME"

# ── 5. Nginx ─────────────────────────────────────────────────
echo "[6/7] Configurando nginx..."
sudo cp "$APP_DIR/deploy/nginx.conf" /etc/nginx/sites-available/"$SERVICE_NAME"
sudo ln -sf /etc/nginx/sites-available/"$SERVICE_NAME" /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
sudo systemctl enable nginx

# ── 6. Firewall (iptables) ────────────────────────────────────
# Oracle Cloud bloquea puertos a nivel de OS además de Security Lists
echo "[7/7] Abriendo puerto 80 en iptables..."
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 80 -j ACCEPT
sudo netfilter-persistent save

# ── Listo ─────────────────────────────────────────────────────
PUBLIC_IP=$(curl -s --max-time 5 ifconfig.me 2>/dev/null || echo "<IP-publica>")
echo ""
echo "✅ ¡Instalación completa!"
echo ""
echo "   App corriendo en:  http://$PUBLIC_IP"
echo ""
echo "   Comandos útiles:"
echo "   - Ver logs:     sudo journalctl -u $SERVICE_NAME -f"
echo "   - Estado:       sudo systemctl status $SERVICE_NAME"
echo "   - Actualizar:   bash $APP_DIR/deploy/update.sh"
echo ""
