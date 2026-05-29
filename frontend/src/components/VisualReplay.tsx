"use client";
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Activity, Loader2 } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';

export default function VisualReplay({ year = 2024, round = 1 }: { year?: number, round?: number }) {
    const [payload, setPayload] = useState<any>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        setLoading(true);
        axios.get(`${process.env.NEXT_PUBLIC_API_URL}/api/telemetry/${year}/${round}?driver1=VER&driver2=PER`)
            .then(res => {
                setPayload(res.data);
                setLoading(false);
            })
            .catch(err => {
                console.error("Failed to fetch telemetry:", err);
                setLoading(false);
            });
    }, [year, round]);

    if (loading || !payload) {
        return (
            <div className="glass-panel p-6 rounded-xl flex items-center justify-center h-full">
                <Loader2 className="animate-spin text-f1-red mb-4" size={48} />
                <span className="text-gray-400 font-mono ml-4">DOWNLOADING FASTF1 TELEMETRY CACHE...</span>
            </div>
        );
    }

    const { driver1, driver2, data } = payload;

    return (
        <div className="bg-[#111] p-6 rounded-xl flex flex-col gap-4 relative border border-white/5">
            <div className="flex justify-between items-center">
                <h2 className="text-xl font-bold flex items-center gap-2 text-white">
                    <Activity size={24} className="text-f1-red" /> Telemetry & Track Replay
                </h2>
                <div className="text-xs font-mono text-gray-500 border border-gray-700 px-2 py-1 rounded">
                    FASTF1 CACHE: LOADED
                </div>
            </div>

            {/* Simulated Track Map Area */}
            <div className="w-full h-48 bg-black/50 border border-white/5 rounded-lg relative overflow-hidden flex items-center justify-center">
                <div className="absolute inset-0 opacity-20 bg-[url('https://www.formula1.com/content/dam/fom-website/2018-redesign-assets/Track%20icons%204x3/Monaco.png.transform/2col/image.png')] bg-contain bg-center bg-no-repeat filter invert"></div>
                <div className="z-10 flex gap-4 text-xs font-mono text-gray-400">
                    <span className="flex items-center gap-1"><div className="w-2 h-2 rounded-full" style={{backgroundColor: driver1?.color}}></div> {driver1?.code} TRACK POS</span>
                    <span className="flex items-center gap-1"><div className="w-2 h-2 rounded-full" style={{backgroundColor: driver2?.color}}></div> {driver2?.code} TRACK POS</span>
                </div>
            </div>
            
            <div className="flex-1 bg-black/50 rounded-lg p-4 border border-white/5 relative overflow-hidden min-h-[250px]">
                <div className="absolute top-2 right-4 text-xs font-mono text-gray-500">SPEED (KM/H) VS DISTANCE (M)</div>
                <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={data} margin={{ top: 20, right: 10, left: -20, bottom: 0 }}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#333" vertical={false} />
                        <XAxis dataKey="distance" stroke="#555" tick={{fill: '#888', fontSize: 12}} />
                        <YAxis stroke="#555" tick={{fill: '#888', fontSize: 12}} domain={[0, 350]} />
                        <Tooltip 
                            contentStyle={{backgroundColor: '#000', border: '1px solid #333', borderRadius: '8px'}}
                            itemStyle={{color: '#fff'}}
                        />
                        <Line type="monotone" dataKey="speed1" name={driver1?.code} stroke={driver1?.color} strokeWidth={3} dot={false} activeDot={{r: 6}} />
                        <Line type="monotone" dataKey="speed2" name={driver2?.code} stroke={driver2?.color} strokeWidth={3} dot={false} />
                    </LineChart>
                </ResponsiveContainer>
            </div>
            
            <div className="grid grid-cols-2 gap-4 mt-2">
                <button className="bg-f1-red/20 hover:bg-f1-red/40 border border-f1-red text-f1-red font-bold py-2 px-4 rounded transition-all">
                    REWIND REPLAY
                </button>
                <button className="bg-neon-blue/20 hover:bg-neon-blue/40 border border-neon-blue text-neon-blue font-bold py-2 px-4 rounded transition-all">
                    LIVE STREAM
                </button>
            </div>
        </div>
    );
}
