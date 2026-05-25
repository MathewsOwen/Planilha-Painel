@echo off
setlocal enableextensions

cd /d "%~dp0"

set "PY_CMD="

where py >nul 2>&1 && set "PY_CMD=py -3"
if "%PY_CMD%"=="" (
    where python >nul 2>&1 && set "PY_CMD=python"
)
if "%PY_CMD%"=="" (
    if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" set "PY_CMD=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
)
if "%PY_CMD%"=="" (
    if exist "%LOCALAPPDATA%\Programs\Python\Python313\python.exe" set "PY_CMD=%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
)
if "%PY_CMD%"=="" (
    if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" set "PY_CMD=%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
)

if "%PY_CMD%"=="" (
    echo.
    echo ============================================================
    echo  ERRO: Python nao foi encontrado neste computador.
    echo ============================================================
    echo  1. Baixe Python 3.10+ em https://www.python.org/downloads/
    echo  2. No instalador, MARQUE a opcao "Add Python to PATH"
    echo  3. Feche e abra esta janela novamente
    echo ============================================================
    echo.
    pause
    exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
    echo.
    echo [Planilha Painel] Primeira execucao - criando ambiente virtual...
    echo.
    %PY_CMD% -m venv .venv
    if errorlevel 1 (
        echo ERRO ao criar ambiente virtual.
        pause
        exit /b 1
    )
)

call ".venv\Scripts\activate.bat"

".venv\Scripts\python.exe" -c "import streamlit" >nul 2>&1
if errorlevel 1 (
    echo.
    echo [Planilha Painel] Instalando dependencias (primeira vez, ~2 min)...
    echo.
    ".venv\Scripts\python.exe" -m pip install --upgrade pip
    ".venv\Scripts\python.exe" -m pip install -r requirements.txt
    if errorlevel 1 (
        echo ERRO ao instalar dependencias.
        pause
        exit /b 1
    )
)

echo.
echo ============================================================
echo  Planilha Painel - Dashboard Streamlit
echo ============================================================
echo  Navegador: http://localhost:8501
echo  Planilha: data\planilha.csv (ou planilha.exemplo.csv)
echo ============================================================
echo.

".venv\Scripts\streamlit.exe" run app.py
pause
