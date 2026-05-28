import React, { useState } from 'react';

const DRIVER_STATS: Record<string, any> = {
    "Lewis Hamilton": { no: 44, color: "#E10600", ch: 7, wins: 105, pod: 201, pole: 104, team: "Ferrari", desc: "Seven-time World Champion seeking his 8th title in red." },
    "Max Verstappen": { no: 1, color: "#00327D", ch: 3, wins: 61, pod: 107, pole: 40, team: "Red Bull Racing", desc: "The reigning dominant force in Formula 1." },
    "Charles Leclerc": { no: 16, color: "#E10600", ch: 0, wins: 6, pod: 36, pole: 25, team: "Ferrari", desc: "Il Predestinato, seeking championship glory with the Scuderia." },
    "Lando Norris": { no: 4, color: "#FF8700", ch: 0, wins: 1, pod: 21, pole: 3, team: "McLaren", desc: "McLaren's star driver pushing for his maiden championship." },
    "Fernando Alonso": { no: 14, color: "#005AFF", ch: 2, wins: 32, pod: 106, pole: 22, team: "Aston Martin", desc: "The legendary veteran still extracting maximum performance." },
    "Kimi Antonelli": { no: 12, color: "#00A19B", ch: 0, wins: 0, pod: 0, pole: 0, team: "Mercedes", desc: "The highly anticipated rookie prodigy debuting in Silver." },
};

export default function FavoriteDriver() {
    const [selected, setSelected] = useState('Lewis Hamilton');
    const stats = DRIVER_STATS[selected];

    return (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-12">
            <div className="bg-[#111] border border-white/5 p-8 rounded-xl flex flex-col justify-between">
                <div>
                    <h3 className="text-xs font-bold tracking-widest text-gray-500 mb-4 uppercase">Select Favorite Driver</h3>
                    <div className="grid grid-cols-2 gap-4 mb-8">
                        {Object.keys(DRIVER_STATS).map(d => (
                            <button 
                                key={d}
                                onClick={() => setSelected(d)}
                                className={`text-left p-3 rounded border text-sm font-bold transition-colors ${selected === d ? 'border-f1-red bg-f1-red/10 text-white' : 'border-white/5 bg-black/50 text-gray-400 hover:border-white/20 hover:text-white'}`}
                            >
                                {d}
                            </button>
                        ))}
                    </div>
                </div>
                
                <div className="border-t border-gray-800 pt-6">
                    <p className="text-sm text-gray-400 italic">"The THE GRID Favorite Driver module customizes your telemetry tracking and prediction alerts specifically for your chosen driver during live sessions."</p>
                </div>
            </div>

            <div className="bg-[#0a0a0a] border border-white/10 p-8 rounded-xl relative overflow-hidden flex flex-col justify-end min-h-[400px]">
                <div className="absolute top-0 right-0 w-64 h-64 rounded-full blur-3xl opacity-20" style={{backgroundColor: stats.color}}></div>
                <div className="absolute inset-0 bg-gradient-to-t from-black via-black/50 to-transparent z-10"></div>
                
                {/* Fake Driver Image Placeholder */}
                <div className="absolute top-12 left-1/2 -translate-x-1/2 w-64 h-64 border border-white/5 rounded-full flex items-center justify-center bg-[#111]">
                    <span className="text-9xl font-black opacity-10" style={{color: stats.color}}>{stats.no}</span>
                </div>

                <div className="relative z-20 mt-auto">
                    <div className="flex items-center gap-4 mb-2">
                        <span className="text-3xl font-black text-white">{selected.toUpperCase()}</span>
                        <span className="bg-white text-black px-2 py-0.5 rounded text-sm font-bold">{stats.no}</span>
                    </div>
                    <p className="text-f1-red font-bold tracking-widest text-xs uppercase mb-4">{stats.team}</p>
                    <p className="text-gray-400 text-sm max-w-sm mb-6">{stats.desc}</p>
                    
                    <div className="grid grid-cols-4 gap-4 border-t border-white/10 pt-6">
                        <div>
                            <p className="text-gray-500 text-xs font-mono">CHAMPS</p>
                            <p className="text-xl font-bold text-white">{stats.ch}</p>
                        </div>
                        <div>
                            <p className="text-gray-500 text-xs font-mono">WINS</p>
                            <p className="text-xl font-bold text-white">{stats.wins}</p>
                        </div>
                        <div>
                            <p className="text-gray-500 text-xs font-mono">PODIUMS</p>
                            <p className="text-xl font-bold text-white">{stats.pod}</p>
                        </div>
                        <div>
                            <p className="text-gray-500 text-xs font-mono">POLES</p>
                            <p className="text-xl font-bold text-white">{stats.pole}</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
