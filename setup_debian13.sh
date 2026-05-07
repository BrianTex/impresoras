#!/bin/bash
set -e

# ==========================================
# Script de Migración para Debian 13 (Trixie)
# Proyecto: Impresoras Dashboard (FastAPI + React)
# ==========================================

echo "Iniciando proceso de migración y configuración en Debian 13..."
sleep 2

# 1. Actualizar repositorios e instalar herramientas básicas
echo ">> Actualizando repositorios del sistema..."
sudo apt-get update && sudo apt-get upgrade -y
sudo apt-get install -y curl wget git build-essential

# 2. Instalar Python 3 y entorno virtual
echo ">> Instalando Python 3 y dependencias..."
sudo apt-get install -y python3 python3-pip python3-venv sqlite3 libsnmp-dev snmp

# 3. Instalar Node.js (v20 o superior recomendado para React/Vite)
echo ">> Instalando Node.js y npm..."
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

# 4. Configurar el Backend (FastAPI)
echo ">> Configurando el Backend..."
cd backend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
deactivate
cd ..

# 5. Configurar el Frontend (React)
echo ">> Configurando el Frontend..."
cd frontend
npm install
# Opcional: Crear el build de producción
# npm run build
cd ..

# 6. Crear script de inicio para Linux (start.sh)
echo ">> Creando script de inicio (start.sh)..."
cat << 'EOF' > start.sh
#!/bin/bash
echo "Iniciando Impresoras Dashboard..."

# Obtener IP local (útil para saber a dónde conectarse)
IP=$(hostname -I | awk '{print $1}')

# Iniciar Backend en segundo plano
echo "Iniciando Backend en el puerto 8000..."
cd backend
source venv/bin/activate
nohup python3 main.py > backend.log 2>&1 &
BACKEND_PID=$!
cd ..

# Iniciar Frontend en segundo plano
echo "Iniciando Frontend..."
cd frontend
nohup npm run dev -- --host 0.0.0.0 > frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

echo "===================================================="
echo " Sistema Iniciado Correctamente"
echo " Backend: http://$IP:8000"
echo " Frontend: http://$IP:5173"
echo "===================================================="
echo "Para detener el sistema, ejecuta: kill $BACKEND_PID $FRONTEND_PID"
EOF

# Dar permisos de ejecución al script de inicio
chmod +x start.sh

echo "=========================================="
echo "¡Migración completada con éxito!"
echo "=========================================="
echo "Puedes iniciar la aplicación ejecutando:"
echo "  ./start.sh"
echo "=========================================="
