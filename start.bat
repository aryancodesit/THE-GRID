@echo off
:: THE GRID v2.0 Startup Script
echo Starting THE GRID v2.0...

:: 1. Start Backend
echo Starting FastAPI Backend on port 8000...
start "THE GRID - Backend" cmd /k "cd backend && if not exist venv (python -m venv venv) && call venv\Scripts\activate && pip install -r requirements.txt -q && uvicorn main:app --reload --host 0.0.0.0 --port 8000"

:: Wait for backend
timeout /t 5 /nobreak >nul

:: 2. Start Frontend
echo Starting Next.js Frontend on port 3000...
start "THE GRID - Frontend" cmd /k "cd frontend && npm install && npm run dev"

echo THE GRID v2.0 is live!
