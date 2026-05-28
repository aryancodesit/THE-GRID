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
echo [1/4] Freeing port 8000...
for /f "tokens=5" %%a in ('netstat -ano 2^>nul ^| findstr ":8000 " ^| findstr "LISTENING"') do (
    echo        Killing PID %%a
    taskkill /F /PID %%a >nul 2>&1
)

echo [2/4] Checking dependencies...
echo        Installing backend requirements...
python -m pip install -r backend/requirements.txt -q
echo        Installing frontend requirements...
cd frontend && call npm install --no-fund --no-audit --silent && cd ..

:: Start backend
echo [3/4] Starting FastAPI backend on :8000...
start "THE GRID — Backend" cmd /k "chcp 65001 && set PYTHONIOENCODING=utf-8 && python backend/main.py"

:: Wait for backend to be ready
timeout /t 3 /nobreak >nul

:: Start frontend
echo [4/4] Starting Next.js frontend on :3000...
start "THE GRID — Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo  Backend:   http://localhost:8000
echo  Frontend:  http://localhost:3000
echo  API docs:  http://localhost:8000/docs
echo.
echo  [ WARNING ] 
echo  Pressing ANY key in this window will IMMEDIATELY STOP the servers!
echo  To open the links, copy them using your mouse (Right-Click) or type them in your browser.
echo.
echo  Press any key ONLY when you are ready to stop both servers...
echo.
echo  Press any key to stop both servers...
pause >nul

:: Cleanup on exit
echo Stopping servers...
taskkill /FI "WINDOWTITLE eq THE GRID*" /F >nul 2>&1
