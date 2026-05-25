@echo off
cd /d "%~dp0"
set PLANILHA_BRAND=grafyco
python build.py --brand grafyco
pause
