import React, { useState } from 'react';

export default function DriverComparison() {
    // Mocking the data from f1-versus.com layout
    const [driverA, setDriverA] = useState('LEWIS HAMILTON');
    const [driverB, setDriverB] = useState('MICHAEL SCHUMACHER');

    const metrics = [
        { name: 'CHAMPIONSHIPS', left: 100, right: 100, leftVal: '7', rightVal: '7', diff: '=' },
        { name: 'WINS', left: 100, right: 87, leftVal: '103', rightVal: '91', diff: '+12' },
        { name: 'PODIUMS', left: 100, right: 76, leftVal: '197', rightVal: '155', diff: '+42' },
        { name: 'POLES', left: 100, right: 66, leftVal: '104', rightVal: '68', diff: '+36' },
        { name: 'FASTEST LAPS', left: 88, right: 100, leftVal: '65', rightVal: '77', diff: '-12' },
        { name: 'WIN RATE', left: 66, right: 71, leftVal: '30.1%', rightVal: '29.6%', diff: '+0.5%' },
    ];

    return (
        <div className="bg-[#111] p-8 rounded border border-white/5 font-mono">
            {/* Header / Scores */}
            <div className="flex justify-between items-center mb-12 relative">
                <div className="flex flex-col">
                    <span className="text-gray-500 text-xs mb-2">§ A.LEFT - DRIVER A</span>
                    <h2 className="text-3xl font-black text-white">{driverA}</h2>
                    <div className="flex items-end gap-4 mt-2">
                        <span className="bg-[#8A2BE2] text-white px-2 py-1 text-sm font-bold">44</span>
                        <span className="text-5xl font-black text-[#8A2BE2]">86.1</span>
                    </div>
                </div>

                <div className="text-4xl font-black text-[#8A2BE2] absolute left-1/2 -translate-x-1/2 top-1/2 -translate-y-1/2">
                    VS
                </div>

                <div className="flex flex-col items-end">
                    <span className="text-gray-500 text-xs mb-2">§ A.RIGHT - DRIVER B</span>
                    <h2 className="text-3xl font-black text-white">{driverB}</h2>
                    <div className="flex items-end gap-4 mt-2 flex-row-reverse">
                        <span className="bg-white text-black px-2 py-1 text-sm font-bold">1</span>
                        <span className="text-5xl font-black text-gray-400">81.1</span>
                    </div>
                </div>
            </div>

            {/* Metrics Breakdown */}
            <div>
                <span className="text-gray-500 text-xs mb-6 block">§ A.01 - METRIC BREAKDOWN</span>
                
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
                                <span className="w-8 text-right text-white">{m.left}</span>
                                <div className="flex-1 bg-gray-900 h-2 rounded flex justify-end">
                                    <div className="h-full bg-[#8A2BE2] rounded" style={{ width: `${m.left}%` }}></div>
                                </div>
                                <span className={`w-8 text-center text-[10px] ${m.diff.startsWith('+') ? 'text-[#8A2BE2]' : m.diff === '=' ? 'text-yellow-500' : 'text-gray-500'}`}>
                                    {m.diff}
                                </span>
                                <div className="flex-1 bg-gray-900 h-2 rounded">
                                    <div className="h-full bg-gray-500 rounded" style={{ width: `${m.right}%` }}></div>
                                </div>
                                <span className="w-8 text-white">{m.right}</span>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
            
            <div className="mt-8 pt-4 border-t border-gray-800 text-xs text-gray-400">
                RESULT = {driverA} 4 · <span className="text-yellow-500">DRAW 1</span> · {driverB} 4
            </div>
        </div>
    );
}
