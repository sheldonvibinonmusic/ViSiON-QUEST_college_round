@echo off
title Second Opinion Launcher
echo ========================================================
echo Starting Second Opinion: Evidence-Grounded AI Auditor
echo ========================================================

cd /d "%~dp0"

echo Starting Backend Server on port 8000...
start "Second Opinion Backend" cmd /k "call .\.venv\Scripts\activate.bat && python -m uvicorn backend.app.main:app --port 8000"

timeout /t 2 /nobreak >nul

echo Starting Frontend Server on port 5173...
cd frontend
set "PATH=C:\Program Files\nodejs;%PATH%"
start "Second Opinion Frontend" cmd /k "npm run dev"

echo.
echo ========================================================
echo Both servers are launching in separate windows!
echo - Frontend UI:  http://localhost:5173
echo - Backend Docs: http://localhost:8000/docs
echo ========================================================
pause
