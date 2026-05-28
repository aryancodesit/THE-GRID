# THE GRID 🏁

![THE GRID Logo](frontend/public/grid_logo.png)

**Advanced F1 Race Replay & Telemetry Analysis Tool**

[![Next.js](https://img.shields.io/badge/Next.js-14-black?style=for-the-badge&logo=next.js)](https://nextjs.org/)
[![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.68+-green?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![FastF1](https://img.shields.io/badge/FastF1-3.0+-orange?style=for-the-badge)](https://github.com/theOehrly/Fast-F1)

THE GRID is a professional-grade Formula 1 race replay and analysis platform. It visualizes high-frequency telemetry data to recreate races with precision, offering a "Pro-Level" leaderboard, realistic tyre strategies, and deep insights into driver performance.

## 🌟 Key Features

*   **🏎️ Real-Time Race Replay**: Watch any race from the 2023-2025 seasons with synchronized driver positions on a 2D track map.
*   **📊 Pro-Level Leaderboard**: Dynamic leaderboard sorted by "Total Race Distance" for accurate race order, even during pit stops.
*   **🛞 Realistic Tyre Data**: Visualizes actual tyre compounds (Soft, Medium, Hard, Inter, Wet) used by drivers.
*   **📈 Live Telemetry**: View real-time Speed, Gear, DRS, and Throttle/Brake data for any selected driver.
*   **🆚 Head-to-Head Mode**: Compare two drivers simultaneously with synchronized gap delta charts and side-by-side strategy tracking.
*   **⏱️ Race Events Timeline**: Interactive scrubber timeline showing Safety Cars (SC), Virtual Safety Cars (VSC), Red/Yellow Flags, and DRS activations.
*   **🔗 Deep Linking URLs**: Share a specific race instantly with a direct link (e.g., `/race/2025/Monaco/R`).
*   **⚡ 2025 Season Ready**: Full backend support for the 2025 season schedule, including Sprint (S) and Sprint Qualifying (SQ) data ingestion.
*   **💾 Auto-Updating Cache**: Intelligent backend scheduler automatically processes and stores new race data the moment it becomes available.

## 🛠️ Tech Stack

*   **Frontend**: Next.js (App Router), React, TypeScript, Tailwind CSS, Recharts, HTML5 Canvas
*   **Backend**: Python, FastAPI, Pandas, NumPy, Pydantic
*   **Data Source**: FastF1 (OpenF1 API integration)

## 🚀 Getting Started

### Prerequisites

*   Node.js (v18+)
*   Python (v3.10+)

### One-Command Startup (Windows)

The absolute easiest way to run the project is using the included `start.bat` file, which automatically handles port cleanup and boots both the frontend and backend simultaneously.

```bash
# Just double-click start.bat or run:
start.bat
```

### Manual Installation

If you prefer to start them manually:

1.  **Clone the repository**
    ```bash
    git clone https://github.com/aryancodesit/THE-GRID.git
    cd THE-GRID
    ```

2.  **Backend Setup**
    ```bash
    cd backend
    # Install dependencies from requirements
    pip install -r requirements.txt
    
    # Run the backend server
    python main.py
    ```
    *The backend runs on `http://localhost:8000`*

3.  **Frontend Setup**
    ```bash
    cd frontend
    # Install Node dependencies
    npm install
    
    # Run the development server
    npm run dev
    ```
    *The frontend runs on `http://localhost:3000`*

## 🚀 Scope of Improvements

There is significant potential to expand THE GRID into a comprehensive F1 analytics suite:

*   **📱 Cross-Platform Application**: Wrap the application using **Electron** for a native desktop experience (Windows/macOS/Linux) and port the frontend to **React Native** for iOS and Android mobile apps.
*   **🏎️ 3D Race Visualization**: Upgrade the 2D track map to a fully immersive 3D environment using **Three.js** or **React Three Fiber**, allowing for realistic elevation changes and camera angles.
*   **🧠 AI-Powered Strategy Analysis**: Implement machine learning models to predict tyre degradation, pit stop windows, and undercut/overcut probabilities in real-time.
*   **📜 Historical Archive**: Expand the database to include full race replays and telemetry for all seasons supported by FastF1 (back to 2018) and potentially older historical data.
*   **📊 Advanced Telemetry**: Add detailed throttle/brake traces, steering angle visualization, and G-force heatmaps for deeper technical analysis.
*   **👥 Multiplayer Sync**: Allow multiple users to watch a race replay together in perfect sync, enabling remote watch parties and collaborative analysis.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License.
