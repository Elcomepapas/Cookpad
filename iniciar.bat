@echo off
setlocal
title Cookpad - Lanzador
cd /d "%~dp0"

REM ================= BACKEND (FastAPI) =================
where py >nul 2>nul && (set "PY=py") || (set "PY=python")

if not exist "backend\venv\Scripts\python.exe" (
    echo [backend] Creando entorno virtual...
    %PY% -m venv backend\venv || (echo ERROR: no se encontro Python. Instalalo desde python.org & pause & exit /b 1)
    echo [backend] Instalando dependencias...
    backend\venv\Scripts\python.exe -m pip install -r backend\requirements.txt
)

if not exist "backend\.env" (
    echo [backend] Creando backend\.env desde .env.example - editalo con tu DATABASE_URL
    copy "backend\.env.example" "backend\.env" >nul
)

start "Cookpad Backend" cmd /k "cd /d "%~dp0backend" && venv\Scripts\python.exe -m uvicorn src.app:app --reload --port 8000"

REM ================= FRONTEND (Vite) =================
where bun >nul 2>nul && (set "PM=bun") || (set "PM=npm")
where %PM% >nul 2>nul || (echo ERROR: no se encontro Node.js/npm. Instalalo desde nodejs.org & pause & exit /b 1)

if not exist "frontend\node_modules" (
    echo [frontend] Instalando dependencias con %PM%...
    pushd frontend
    call %PM% install
    popd
)

start "Cookpad Frontend" cmd /k "cd /d "%~dp0frontend" && set "VITE_API_URL=http://localhost:8000" &&%PM% run dev"

REM ================= ABRIR NAVEGADOR =================
echo Esperando que levanten los servidores...
timeout /t 8 /nobreak >nul
start "" http://localhost:8080
start "" http://localhost:8000/docs

echo Listo. Cerra las ventanas "Cookpad Backend" y "Cookpad Frontend" para detenerlos.
timeout /t 5 >nul
