@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>&1 && set PY=py -3 || set PY=python
%PY% run_eval_agent.py
if errorlevel 1 pause
