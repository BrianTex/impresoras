@echo off
echo Iniciando Backend...
start cmd /k "cd backend && pip install -r requirements.txt && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000"

echo Iniciando Frontend...
start cmd /k "cd frontend && npm install && npm run dev"

echo.
echo Panel de Impresoras iniciado.
echo Accede a la interfaz desde tu navegador: http://localhost:5173
echo.
pause
