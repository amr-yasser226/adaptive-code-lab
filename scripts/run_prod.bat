@echo off
REM Windows wrapper for starting the server
cd /d "%~dp0\.."
set PYTHON_EXEC=python
if exist .venv\Scripts\python.exe set PYTHON_EXEC=.venv\Scripts\python.exe
if exist venv\Scripts\python.exe set PYTHON_EXEC=venv\Scripts\python.exe
%PYTHON_EXEC% scripts/run_prod.py
pause
