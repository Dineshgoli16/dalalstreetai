@echo off
echo =======================================================
echo    LAUNCHING DALAL STREET AI TRADING TERMINAL
echo =======================================================
echo.
echo [1/2] Starting Python FastAPI Backend on port 8000 (0.0.0.0 for LAN)...
start "Dalal Street AI - Backend" cmd /k "cd /d %~dp0 && python -m uvicorn server:app --host 0.0.0.0 --port 8000"

timeout /t 3 /nobreak >nul

echo [2/2] Starting Node.js Frontend Dashboard on port 3000...
start "Dalal Street AI - Dashboard" cmd /k "cd /d %~dp0frontend && node server.js"

timeout /t 2 /nobreak >nul

echo.
echo =======================================================
echo  Terminal Ready!
echo  PC Dashboard:    http://localhost:3000
echo  Mobile/LAN:      http://192.168.29.102:3000
echo  Android APK:     %~dp0dalal-street-ai.apk
echo =======================================================
start http://localhost:3000
