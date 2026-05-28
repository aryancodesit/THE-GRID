"use client";
import React, { useState } from 'react';
import TUIDashboard from '@/components/TUIDashboard';
import PredictionPanel from '@/components/PredictionPanel';
import VisualReplay from '@/components/VisualReplay';
import DriverComparison from '@/components/DriverComparison';
import FavoriteDriver from '@/components/FavoriteDriver';

export default function Home() {
  const [year, setYear] = useState(2026);
  const [round, setRound] = useState(1);
  const [activeTab, setActiveTab] = useState('LEADERBOARD');

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white font-sans selection:bg-f1-red selection:text-white">
      {/* Top Navigation */}
      <nav className="flex items-center justify-between px-8 py-4 border-b border-white/5 bg-[#0a0a0a] sticky top-0 z-50">
        <div className="flex items-center gap-12">
          <h1 className="text-2xl font-black italic tracking-tighter">THE GRID <span className="text-f1-red">+</span></h1>
          <div className="hidden md:flex items-center gap-6 text-xs font-bold tracking-widest text-gray-400">
            <span onClick={() => setActiveTab('LEADERBOARD')} className={`cursor-pointer transition-colors ${activeTab === 'LEADERBOARD' ? 'text-white border-b-2 border-white pb-1' : 'hover:text-white'}`}>LEADERBOARD</span>
            <span onClick={() => setActiveTab('TELEMETRY')} className={`cursor-pointer transition-colors ${activeTab === 'TELEMETRY' ? 'text-white border-b-2 border-white pb-1' : 'hover:text-white'}`}>LIVE TELEMETRY</span>
            <span onClick={() => setActiveTab('COMPARISON')} className={`cursor-pointer transition-colors ${activeTab === 'COMPARISON' ? 'text-f1-red border-b-2 border-f1-red pb-1' : 'hover:text-white'}`}>COMPARISON (f1-versus)</span>
            <span onClick={() => setActiveTab('FAVORITE')} className={`cursor-pointer transition-colors ${activeTab === 'FAVORITE' ? 'text-white border-b-2 border-white pb-1' : 'hover:text-white'}`}>FAVORITE DRIVER</span>
          </div>
        </div>
      </nav>

      <main className="max-w-[1400px] mx-auto px-8 py-12">
        {/* Hero Section */}
        <div className="mb-12">
          <p className="text-xs font-bold tracking-widest text-gray-500 mb-2 uppercase">Race Weekend</p>
          <h2 className="text-5xl font-black mb-4 tracking-tight">{activeTab === 'COMPARISON' ? 'DRIVER COMPARISON' : 'RACE INTEL'}</h2>
          <p className="text-gray-400 text-sm max-w-xl leading-relaxed">
            {activeTab === 'COMPARISON' ? 'Head-to-head metric breakdown using era-normalized statistics.' : 'Session results, race outcomes, and performance analysis across every Formula 1 Grand Prix weekend.'}
          </p>
        </div>

        {activeTab === 'COMPARISON' ? (
            <DriverComparison />
        ) : activeTab === 'FAVORITE' ? (
            <FavoriteDriver />
        ) : (
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-12">
            {/* Left Column: Official Results or Telemetry */}
            <div className="lg:col-span-8">
                {activeTab === 'TELEMETRY' ? (
                    <VisualReplay year={year} round={round} />
                ) : (
                    <TUIDashboard year={year} round={round} />
                )}
            </div>

            {/* Right Column: Selectors & Info */}
            <div className="lg:col-span-4 flex flex-col gap-6">
                {/* Year Tabs */}
                <div className="flex gap-2 text-sm">
                <button onClick={() => setYear(2026)} className={`px-4 py-1.5 font-bold rounded ${year === 2026 ? 'bg-f1-red text-white' : 'bg-[#1a1a1a] text-gray-400 hover:text-white'}`}>2026</button>
                <button onClick={() => setYear(2025)} className={`px-4 py-1.5 font-bold rounded ${year === 2025 ? 'bg-f1-red text-white' : 'bg-[#1a1a1a] text-gray-400 hover:text-white'}`}>2025</button>
                <button onClick={() => setYear(2024)} className={`px-4 py-1.5 font-bold rounded ${year === 2024 ? 'bg-f1-red text-white' : 'bg-[#1a1a1a] text-gray-400 hover:text-white'}`}>2024</button>
                <button onClick={() => setYear(2023)} className={`px-4 py-1.5 font-bold rounded ${year === 2023 ? 'bg-f1-red text-white' : 'bg-[#1a1a1a] text-gray-400 hover:text-white'}`}>2023</button>
                </div>

                {/* Race Dropdown */}
                <div>
                <label className="text-xs font-bold tracking-widest text-gray-500 block mb-2">RACE</label>
                <select 
                    value={round}
                    onChange={(e) => setRound(Number(e.target.value))}
                    className="w-full bg-[#1a1a1a] text-white text-sm p-3 rounded border border-white/5 outline-none focus:border-f1-red transition-colors appearance-none cursor-pointer"
                >
                    <option value={1}>BH Formula 1 Gulf Air Bahrain Grand Prix {year}</option>
                    <option value={2}>SA Formula 1 STC Saudi Arabian Grand Prix {year}</option>
                    <option value={3}>AU Formula 1 Rolex Australian Grand Prix {year}</option>
                    <option value={4}>JP Formula 1 MSC Cruises Japanese Grand Prix {year}</option>
                    <option value={5}>CN Formula 1 Lenovo Chinese Grand Prix {year}</option>
                    <option value={6}>US Formula 1 Crypto.com Miami Grand Prix {year}</option>
                    <option value={7}>IT Formula 1 MSC Cruises Gran Premio del Made in Italy {year}</option>
                    <option value={8}>MC Formula 1 Grand Prix de Monaco {year}</option>
                    <option value={9}>CA Formula 1 AWS Grand Prix du Canada {year}</option>
                </select>
                </div>

                {/* Info Cards & Prediction */}
                <div className="bg-[#111] border border-white/5 rounded-xl p-6 flex flex-col gap-6">
                <h3 className="text-xs font-bold tracking-widest text-gray-500 mb-2">WHAT YOU GET</h3>
                
                <div className="flex gap-4">
                    <div className="mt-1"><div className="w-6 h-6 rounded-full bg-white/5 border border-white/10 flex items-center justify-center text-[10px]">⏱</div></div>
                    <div>
                    <h4 className="font-bold text-sm mb-1">SESSION RESULTS</h4>
                    <p className="text-xs text-gray-500 leading-relaxed">Qualifying, sprint, and race outcomes with detailed timing, fastest laps, and driver standings.</p>
                    </div>
                </div>

                <div className="flex gap-4">
                    <div className="mt-1"><div className="w-6 h-6 rounded-full bg-white/5 border border-white/10 flex items-center justify-center text-[10px]">↻</div></div>
                    <div>
                    <h4 className="font-bold text-sm mb-1 flex items-center gap-2">F1DB HISTORIC ARCHIVE 🔒</h4>
                    <p className="text-xs text-gray-500 leading-relaxed">Every season from 1950 to today — all 77 seasons of Formula 1 history at your fingertips.</p>
                    </div>
                </div>
                </div>

                <div className="mt-4">
                    <PredictionPanel year={year} round={round} />
                </div>
            </div>
            </div>
        )}
      </main>
    </div>
  );
}
