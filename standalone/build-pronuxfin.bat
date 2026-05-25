@echo off
cd /d "%~dp0"
set PLANILHA_BRAND=pronuxfin
python build.py --brand pronuxfin
pause
