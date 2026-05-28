@echo off
:: THE GRID — one-command startup for Windows
:: Kills anything on port 8000 first (prevents WinError 10048),
:: then starts backend and frontend in separate windows.

echo.
echo  ========================================
echo   THE GRID  ^|  Starting up...
echo  ========================================
echo.

:: FIX 2 helper — free port 8000 before starting
echo [1/3] Freeing port 8000...
for /f "tokens=5" %%a in ('netstat -ano 2^>nul ^| findstr ":8000 " ^| findstr "LISTENING"') do (
    echo        Killing PID %%a
    taskkill /F /PID %%a >nul 2>&1
)

:: Set UTF-8 for this session (belt-and-suspenders for FIX 1)
chcp 65001 >nul
set PYTHONIOENCODING=utf-8

:: Start backend
echo [2/3] Starting FastAPI backend on :8000...
start "THE GRID — Backend" cmd /k "chcp 65001 && set PYTHONIOENCODING=utf-8 && python backend/main.py"

:: Wait for backend to be ready
timeout /t 3 /nobreak >nul

:: Start frontend
echo [3/3] Starting Next.js frontend on :3000...
start "THE GRID — Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo  Backend:   http://localhost:8000
echo  Frontend:  http://localhost:3000
echo  API docs:  http://localhost:8000/docs
echo.
echo  Press any key to stop both servers...
pause >nul

:: Cleanup on exit
echo Stopping servers...
taskkill /FI "WINDOWTITLE eq THE GRID*" /F >nul 2>&1
