"use client";
import React, { useState, useEffect } from 'react';
import { Terminal, Clock } from 'lucide-react';

export default function TUIDashboard({ year = 2026, round = 1 }: { year?: number, round?: number }) {
    const [currentTime, setCurrentTime] = useState(new Date());
    
    const [drivers, setDrivers] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const timer = setInterval(() => setCurrentTime(new Date()), 1000);
        return () => clearInterval(timer);
    }, []);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/timing/${year}/${round}`);
                const data = await res.json();
                setDrivers(data);
                setLoading(false);
            } catch (err) {
                console.error(err);
            }
        };
        fetchData();
        const interval = setInterval(fetchData, 15000);
        return () => clearInterval(interval);
    }, [year, round]);

    return (
        <div className="bg-[#111] rounded-xl overflow-hidden border border-white/5 h-full">
            <div className="flex border-b border-gray-800">
                <div className="px-6 py-4 font-black tracking-widest text-sm text-white flex-1">OFFICIAL RESULTS <span className="text-gray-500 font-normal">Race</span></div>
                <div className="flex text-[10px] font-bold tracking-widest text-gray-500 mt-4 mr-4 gap-4">
                    <span className="text-white bg-f1-red px-2 py-1 rounded h-fit">RACE</span>
                    <span className="hover:text-white cursor-pointer h-fit py-1">QUALI</span>
                    <span className="hover:text-white cursor-pointer h-fit py-1">SPRINT</span>
                    <span className="hover:text-white cursor-pointer h-fit py-1">SQ</span>
                    <span className="hover:text-white cursor-pointer h-fit py-1">FP1</span>
                </div>
            </div>

            <div className="overflow-x-auto">
                <table className="w-full text-sm text-left">
                    <thead className="text-[10px] font-bold tracking-widest text-gray-500 border-b border-gray-800">
                        <tr>
                            <th className="px-6 py-4">POS</th>
                            <th className="py-4">DRIVER</th>
                            <th className="py-4 text-center">GRID</th>
                            <th className="py-4 text-right">TIME/GAP</th>
                            <th className="px-6 py-4 text-right">PTS</th>
                        </tr>
                    </thead>
                    <tbody>
                        {loading && drivers.length === 0 ? (
                            <tr><td colSpan={5} className="px-6 py-12 text-center text-gray-500 font-mono text-xs animate-pulse">CONNECTING TO FASTF1 TIMING STREAM...</td></tr>
                        ) : drivers.map((d, index) => (
                            <tr key={d.code} className="hover:bg-white/5 transition-colors border-b border-gray-900/50 group">
                                <td className={`px-6 py-4 font-black ${d.pos === 1 ? 'text-yellow-500' : 'text-gray-400'}`}>{d.pos}</td>
                                <td className="py-4">
                                    <div className="flex items-center gap-3">
                                        <div className="w-6 h-6 rounded-full bg-gray-800 flex items-center justify-center text-[10px] font-bold text-gray-400 overflow-hidden">
                                            {/* Fake headshot placeholder */}
                                            <span className="opacity-50">{d.code}</span>
                                        </div>
                                        <div>
                                            <div className="font-bold text-white group-hover:text-f1-red transition-colors flex items-center gap-2">
                                                {d.no} {d.code} 
                                                {d.pos === 1 && <span className="bg-yellow-500 text-black text-[8px] px-1 rounded">WTN</span>}
                                            </div>
                                            <div className="text-[10px] text-gray-500 font-bold uppercase">{d.tyre} Compound</div>
                                        </div>
                                    </div>
                                </td>
                                <td className="py-4 text-center text-gray-400 font-mono text-xs">{d.pos + (index % 3)}</td>
                                <td className="py-4 text-right text-gray-400 font-mono text-xs">{d.gap}</td>
                                <td className="px-6 py-4 text-right text-white font-black">{Math.max(25 - (d.pos * 2), 0)}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
            
        </div>
    );
}
