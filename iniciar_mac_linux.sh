#!/usr/bin/env bash
set -e

# Cambiar al directorio del script
cd "$(dirname "$0")"

echo "============================================================"
echo "       Iniciando n8n Control Center Pro..."
echo "============================================================"

# 1. Si existe ejecutable compilado en dist/, ejecutarlo directamente
if [ -f "dist/n8n-control-center" ]; then
    echo "[OK] Ejecutable detectado en dist/n8n-control-center"
    chmod +x "dist/n8n-control-center"
    exec "./dist/n8n-control-center"
fi

if [ -f "n8n-control-center" ]; then
    echo "[OK] Ejecutable detectado en ./n8n-control-center"
    chmod +x "n8n-control-center"
    exec "./n8n-control-center"
fi

# 2. Si no hay binario, preparar entorno virtual Python
if [ ! -d ".venv" ]; then
    echo "[INFO] Creando entorno virtual .venv..."
    if command -v python3 &>/dev/null; then
        python3 -m venv .venv
    elif command -v python &>/dev/null; then
        python -m venv .venv
    else
        echo "[ERROR] Python 3 no está instalado. Por favor instálalo (ej: sudo apt install python3 python3-venv python3-tk)"
        exit 1
    fi
fi

# Activar venv
source .venv/bin/activate

# Verificar librerías mínimas
if ! python -c "import customtkinter" &>/dev/null; then
    echo "[INFO] Instalando dependencias de requirements.txt..."
    pip install -r requirements.txt
fi

echo "[OK] Lanzando interfaz gráfica..."
python main.py
