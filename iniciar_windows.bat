@echo off
setlocal enabledelayedexpansion
title n8n Control Center Pro - Lanzador

cd /d "%~dp0"

echo ============================================================
echo        Iniciando n8n Control Center Pro...
echo ============================================================

:: 1. Si existe el ejecutable compilado en dist/, ejecutarlo directamente
if exist "dist\n8n-control-center.exe" (
    echo [OK] Ejecutable detectado en dist\n8n-control-center.exe
    start "" "dist\n8n-control-center.exe"
    exit /b 0
)

:: 2. Si existe el ejecutable compilado en la raiz, ejecutarlo
if exist "n8n-control-center.exe" (
    echo [OK] Ejecutable detectado en .\n8n-control-center.exe
    start "" "n8n-control-center.exe"
    exit /b 0
)

:: 3. Si no hay ejecutable, usar el entorno virtual Python
if exist ".venv\Scripts\python.exe" (
    echo [OK] Entorno virtual detectado (.venv)
    start "" ".venv\Scripts\python.exe" main.py
    exit /b 0
)

:: 4. Si no existe .venv, intentar crearlo con py o python
echo [INFO] Creando entorno virtual .venv por primera vez...
where py >nul 2>nul
if %errorlevel% equ 0 (
    py -m venv .venv
) else (
    where python >nul 2>nul
    if %errorlevel% equ 0 (
        python -m venv .venv
    ) else (
        echo [ERROR] No se encontro Python instalado en el sistema.
        echo Por favor instala Python 3.10 o superior desde https://www.python.org/
        pause
        exit /b 1
    )
)

echo [INFO] Instalando dependencias necesarias...
".venv\Scripts\pip.exe" install -r requirements.txt

echo [OK] Lanzando aplicacion...
start "" ".venv\Scripts\python.exe" main.py
exit /b 0
