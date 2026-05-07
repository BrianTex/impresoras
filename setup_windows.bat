@echo off
echo ==========================================
echo Script de Configuracion para Windows
echo Proyecto: Impresoras Dashboard (FastAPI + React)
echo ==========================================
echo.
echo Iniciando proceso de configuracion en Windows...
timeout /t 2 /nobreak >nul

echo.
echo [1/2] Configurando el Backend (Python)...
cd backend
if not exist venv (
    echo Creando entorno virtual...
    python -m venv venv
)
echo Activando entorno virtual e instalando dependencias...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
deactivate
cd ..

echo.
echo [2/2] Configurando el Frontend (Node.js)...
cd frontend
echo Instalando modulos de Node.js...
call npm install
cd ..

echo.
echo ==========================================
echo Configuracion completada con exito!
echo ==========================================
echo Puedes iniciar la aplicacion ejecutando:
echo   start.bat
echo ==========================================
pause
