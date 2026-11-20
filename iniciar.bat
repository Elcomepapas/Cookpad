@echo off
setlocal EnableExtensions
title Cookpad - Lanzador
cd /d "%~dp0"
set "ROOT=%CD%"

if not exist "backend\requirements.txt" goto :err_estructura
if not exist "front\package.json" goto :err_estructura

REM ================= BACKEND (FastAPI) =================
REM Si el venv existe pero esta roto (Python desinstalado/movido), se recrea.
if exist "backend\venv\Scripts\python.exe" "backend\venv\Scripts\python.exe" --version >nul 2>nul || rmdir /s /q "backend\venv"
if exist "backend\venv\Scripts\python.exe" goto :pip

call :detectar_python
if not defined PY goto :err_python
echo [backend] Creando entorno virtual con %PY%...
%PY% -m venv "backend\venv"
if errorlevel 1 goto :err_venv

:pip
echo [backend] Sincronizando dependencias...
"backend\venv\Scripts\python.exe" -m pip install -q --disable-pip-version-check -r "backend\requirements.txt"
if errorlevel 1 goto :err_pip

if exist "backend\.env" goto :backend_run
echo [backend] Creando backend\.env desde .env.example
copy "backend\.env.example" "backend\.env" >nul
echo.
echo   ATENCION: edita backend\.env y pone tu DATABASE_URL real,
echo   si no el backend no va a poder conectarse a la base de datos.
echo.

:backend_run
start "Cookpad Backend" /D "%ROOT%\backend" cmd /k venv\Scripts\python.exe -m uvicorn src.app:app --reload --port 8000

REM ================= FRONTEND (Vite) =================
set "PM="
where bun >nul 2>nul && set "PM=bun"
if defined PM goto :front_env
where node >nul 2>nul || goto :err_node
where npm >nul 2>nul || goto :err_node
set "PM=npm"

:front_env
if not exist "front\.env.local" if exist "front\.env.example" (
    echo [front] Creando front\.env.local desde .env.example
    copy "front\.env.example" "front\.env.local" >nul
)

if exist "front\node_modules" goto :front_run
echo [front] Instalando dependencias con %PM% - la primera vez tarda unos minutos...
pushd "front"
call %PM% install
set "RC=%errorlevel%"
popd
if not "%RC%"=="0" goto :err_install

:front_run
set "VITE_API_URL=http://localhost:8000"
start "Cookpad Frontend" /D "%ROOT%\front" cmd /k %PM% run dev

REM ================= ABRIR NAVEGADOR =================
echo Esperando que levanten los servidores...
timeout /t 8 /nobreak >nul
start "" http://localhost:8080
start "" http://localhost:8000/docs

echo Listo. Cerra las ventanas "Cookpad Backend" y "Cookpad Frontend" para detenerlos.
timeout /t 5 >nul
exit /b 0

REM ================= SUBRUTINAS =================
:detectar_python
set "PY="
py -3 --version >nul 2>nul && (set "PY=py -3" & exit /b 0)
python --version >nul 2>nul && (set "PY=python" & exit /b 0)
exit /b 1

REM ================= ERRORES =================
:err_estructura
echo ERROR: no se encontraron las carpetas backend y front junto a este .bat.
echo Ejecuta iniciar.bat desde la raiz del repo Cookpad.
goto :fin_error

:err_python
echo ERROR: no se encontro Python 3. Instalalo desde https://www.python.org/downloads/
echo y marca la opcion "Add python.exe to PATH" durante la instalacion.
goto :fin_error

:err_venv
echo ERROR: no se pudo crear el entorno virtual en backend\venv.
goto :fin_error

:err_pip
echo ERROR: fallo la instalacion de backend\requirements.txt. Revisa el mensaje de arriba.
goto :fin_error

:err_node
echo ERROR: no se encontro Node.js/npm. Instalalo desde https://nodejs.org/ y reinicia la terminal.
goto :fin_error

:err_install
echo ERROR: fallo "%PM% install" en front. Borrando front\node_modules incompleto...
if exist "front\node_modules" rmdir /s /q "front\node_modules"
echo Revisa el mensaje de arriba y volve a ejecutar iniciar.bat.
goto :fin_error

:fin_error
echo.
pause
exit /b 1
