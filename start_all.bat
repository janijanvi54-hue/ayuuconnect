@echo off
REM AYUConnect - start backend (Flask :5000) and frontend (Vite :5173)
REM Vite proxies /api to the Flask backend, so open http://localhost:5173 after start.

where python >nul 2>nul
if errorlevel 1 (
  echo python not found on PATH. Open it in the folder you normally use.
  pause
  exit /b 1
)

echo Starting AYUConnect API (http://localhost:5000) ...
start "AYUConnect API" cmd /k "cd /d "%~dp0backend" && python run.py"

echo Starting AYUConnect Web (http://localhost:5173) ...
start "AYUConnect Web" cmd /k "cd /d "%~dp0frontend" && npm.cmd run dev"

echo.
echo Both servers are starting in new windows.
echo Open http://localhost:5173 once the Vite window prints "Local:".
pause