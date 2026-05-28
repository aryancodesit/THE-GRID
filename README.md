# THE GRID 🏎️

The ultimate hybrid Formula 1 telemetry, live timing, and prediction platform. 
Built to flawlessly handle dynamic updates for the 2026 season (including Audi and Cadillac integration) without relying on hardcoded caches.

## Features
- **TUI Dashboard:** High-density, monospace live timing feed featuring S1/S2/S3 sector times (inspired by `undercut-f1`).
- **Visual Replay:** Dynamic 2D track map and speed vs. distance telemetry charts utilizing real-time FastF1 parsed data (inspired by `f1-race-replay`).
- **ML Predictions Engine:** Uses `scikit-learn` Gradient Boosting to predict race outcomes based on a robust local SQLite historical database (inspired by `2025_f1_predictions`).
- **Jolpica DB Architecture:** Efficient, normalized database schema replacing sluggish JSON caches.
- **Glassmorphism UI:** Built with Next.js and Tailwind CSS for a premium, high-aesthetic experience (inspired by `gridvex.app`).

## Tech Stack
- **Frontend**: Next.js 16 (App Router), Tailwind CSS, Recharts, Server-Sent Events (SSE)
- **Backend**: FastAPI, Python 3, SQLAlchemy (SQLite), FastF1, Pandas, Scikit-learn

## Deployment Architecture
1. **Frontend (Next.js)** is optimized to be deployed directly to **Vercel** for ultra-fast edge delivery.
2. **Backend (FastAPI)** is designed to run on a dedicated VPS/Server (e.g., Render, DigitalOcean) due to the heavy memory and computational requirements of parsing FastF1 caches and training ML models.

## Local Setup
Ensure you have Python and Node.js installed, then run the bootstrapper:
```bash
./start.bat
```
*Note: `start.bat` will automatically initialize a Python virtual environment and install all necessary backend dependencies before booting the frontend.*
