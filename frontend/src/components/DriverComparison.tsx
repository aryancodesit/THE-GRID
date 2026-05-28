import React, { useState } from 'react';

const DRIVER_STATS: Record<string, any> = {
    "Lewis Hamilton": { no: 44, color: "#E10600", ch: 7, wins: 105, pod: 201, pole: 104, fl: 67, wr: 30.1 },
    "Max Verstappen": { no: 1, color: "#00327D", ch: 3, wins: 61, pod: 107, pole: 40, fl: 32, wr: 30.5 },
    "Charles Leclerc": { no: 16, color: "#E10600", ch: 0, wins: 6, pod: 36, pole: 25, fl: 9, wr: 4.5 },
    "Lando Norris": { no: 4, color: "#FF8700", ch: 0, wins: 1, pod: 21, pole: 3, fl: 1, wr: 0.9 },
    "Fernando Alonso": { no: 14, color: "#005AFF", ch: 2, wins: 32, pod: 106, pole: 22, fl: 24, wr: 8.2 },
    "George Russell": { no: 63, color: "#00A19B", ch: 0, wins: 2, pod: 13, pole: 2, fl: 6, wr: 1.5 },
    "Oscar Piastri": { no: 81, color: "#FF8700", ch: 0, wins: 0, pod: 4, pole: 0, fl: 2, wr: 0.0 },
    "Carlos Sainz": { no: 55, color: "#005AFF", ch: 0, wins: 3, pod: 22, pole: 5, fl: 3, wr: 1.5 },
    "Kimi Antonelli": { no: 12, color: "#00A19B", ch: 0, wins: 0, pod: 0, pole: 0, fl: 0, wr: 0.0 },
    "Oliver Bearman": { no: 87, color: "#B6BABD", ch: 0, wins: 0, pod: 0, pole: 0, fl: 0, wr: 0.0 },
};

export default function DriverComparison() {
    const [driverA, setDriverA] = useState('Lewis Hamilton');
    const [driverB, setDriverB] = useState('Max Verstappen');

    const aStats = DRIVER_STATS[driverA];
    const bStats = DRIVER_STATS[driverB];

    const calculateBar = (valA: number, valB: number) => {
        const max = Math.max(valA, valB) || 1; // prevent div by zero
        return {
            left: (valA / max) * 100,
            right: (valB / max) * 100,
            diff: valA - valB
        };
    };

    const metrics = [
        { name: 'CHAMPIONSHIPS', leftVal: aStats.ch, rightVal: bStats.ch, ...calculateBar(aStats.ch, bStats.ch) },
        { name: 'WINS', leftVal: aStats.wins, rightVal: bStats.wins, ...calculateBar(aStats.wins, bStats.wins) },
        { name: 'PODIUMS', leftVal: aStats.pod, rightVal: bStats.pod, ...calculateBar(aStats.pod, bStats.pod) },
        { name: 'POLES', leftVal: aStats.pole, rightVal: bStats.pole, ...calculateBar(aStats.pole, bStats.pole) },
        { name: 'FASTEST LAPS', leftVal: aStats.fl, rightVal: bStats.fl, ...calculateBar(aStats.fl, bStats.fl) },
        { name: 'WIN RATE (%)', leftVal: aStats.wr, rightVal: bStats.wr, ...calculateBar(aStats.wr, bStats.wr) },
    ];

    const scoreA = metrics.filter(m => m.diff > 0).length;
    const scoreB = metrics.filter(m => m.diff < 0).length;
    const draw = metrics.filter(m => m.diff === 0).length;

    return (
        <div className="bg-[#111] p-8 rounded border border-white/5 font-mono">
            {/* Header / Dropdowns */}
            <div className="flex justify-between items-start mb-12 relative">
                <div className="flex flex-col w-1/3">
                    <span className="text-gray-500 text-xs mb-2">§ A.LEFT - DRIVER A</span>
                    <select 
                        value={driverA} 
                        onChange={e => setDriverA(e.target.value)}
                        className="bg-black text-white text-xl font-black p-2 border border-white/10 outline-none w-full cursor-pointer"
                    >
                        {Object.keys(DRIVER_STATS).map(d => <option key={d} value={d}>{d.toUpperCase()}</option>)}
                    </select>
                    <div className="flex items-end gap-4 mt-4">
                        <span style={{backgroundColor: aStats.color}} className="text-white px-2 py-1 text-sm font-bold">{aStats.no}</span>
                    </div>
                </div>

                <div className="text-4xl font-black text-gray-700 absolute left-1/2 -translate-x-1/2 top-4">
                    VS
                </div>

                <div className="flex flex-col items-end w-1/3">
                    <span className="text-gray-500 text-xs mb-2">§ A.RIGHT - DRIVER B</span>
                    <select 
                        value={driverB} 
                        onChange={e => setDriverB(e.target.value)}
                        className="bg-black text-white text-xl font-black p-2 border border-white/10 outline-none w-full text-right cursor-pointer"
                    >
                        {Object.keys(DRIVER_STATS).map(d => <option key={d} value={d}>{d.toUpperCase()}</option>)}
                    </select>
                    <div className="flex items-end gap-4 mt-4 flex-row-reverse">
                        <span style={{backgroundColor: bStats.color}} className="text-white px-2 py-1 text-sm font-bold">{bStats.no}</span>
                    </div>
                </div>
            </div>

            {/* Metrics Breakdown */}
            <div>
                <span className="text-gray-500 text-xs mb-6 block">§ A.01 - LIFETIME CAREER METRICS</span>
                
                <div className="flex flex-col gap-4">
                    <div className="flex text-xs text-gray-500 pb-2 border-b border-gray-800">
                        <div className="w-48">METRIC</div>
                        <div className="flex-1 flex justify-between">
                            <span>L</span>
                            <span>LEFT</span>
                            <span>Δ</span>
                            <span>RIGHT</span>
                            <span>R</span>
                        </div>
                    </div>

                    {metrics.map((m, i) => (
                        <div key={i} className="flex items-center text-sm">
                            <div className="w-48 text-gray-400 font-bold">{m.name}</div>
                            <div className="flex-1 flex items-center gap-4">
                                <span className="w-8 text-right text-white">{m.leftVal}</span>
                                <div className="flex-1 bg-gray-900 h-2 rounded flex justify-end">
                                    <div className="h-full rounded" style={{ width: `${m.left}%`, backgroundColor: aStats.color }}></div>
                                </div>
                                <span className={`w-8 text-center text-[10px] font-bold ${m.diff > 0 ? 'text-white' : m.diff === 0 ? 'text-yellow-500' : 'text-gray-600'}`} style={{color: m.diff > 0 ? aStats.color : undefined}}>
                                    {m.diff > 0 ? `+${(m.diff).toFixed(1).replace('.0','')}` : m.diff === 0 ? '=' : (m.diff).toFixed(1).replace('.0','')}
                                </span>
                                <div className="flex-1 bg-gray-900 h-2 rounded">
                                    <div className="h-full rounded" style={{ width: `${m.right}%`, backgroundColor: bStats.color }}></div>
                                </div>
                                <span className="w-8 text-white">{m.rightVal}</span>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
            
            <div className="mt-8 pt-4 border-t border-gray-800 text-xs text-gray-400">
                HEAD-TO-HEAD DOMINANCE: {driverA.toUpperCase()} {scoreA} · <span className="text-yellow-500">DRAW {draw}</span> · {driverB.toUpperCase()} {scoreB}
            </div>
        </div>
    );
}
