"use client";
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Trophy, Clock, Target, AlertTriangle } from 'lucide-react';

interface Prediction {
    year: number;
    round: number;
    predicted_winner_code: string;
    predicted_time_seconds: number;
    mae_error: number;
    confidence: number;
}

export default function PredictionPanel({ year = 2024, round = 1 }: { year?: number, round?: number }) {
    const [prediction, setPrediction] = useState<Prediction | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        setLoading(true);
        axios.get(`${process.env.NEXT_PUBLIC_API_URL}/api/predict/${year}/${round}`)
            .then(res => {
                setPrediction(res.data);
                setLoading(false);
            })
            .catch(err => {
                console.error(err);
                setLoading(false);
            });
    }, [year, round]);

    if (loading) return <div className="bg-[#111] border border-white/5 p-6 animate-pulse h-64 rounded-xl"></div>;

    return (
        <div className="bg-[#111] border border-white/5 p-6 rounded-xl flex flex-col gap-4 relative overflow-hidden">
            <div className="absolute top-0 right-0 w-32 h-32 bg-f1-red/10 rounded-full blur-3xl"></div>
            
            <h2 className="text-xl font-bold flex items-center gap-2 text-f1-red uppercase tracking-widest">
                <Target size={24} /> ML Predictions Engine
            </h2>
            
            {prediction ? (
                <div className="flex flex-col gap-4 mt-2">
                    <div className="bg-black/40 border border-f1-red/30 p-4 rounded-lg">
                        <div className="text-sm text-gray-400 font-mono mb-1">PREDICTED WINNER</div>
                        <div className="text-4xl font-black text-f1-red tracking-tighter flex items-center gap-3">
                            <Trophy size={32} />
                            {prediction.predicted_winner_code}
                        </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                        <div className="bg-black/30 p-3 rounded-lg border border-white/5">
                            <div className="text-xs text-gray-500 mb-1 flex items-center gap-1"><Clock size={12}/> EST TIME</div>
                            <div className="text-lg font-mono text-neon-green">
                                {(prediction.predicted_time_seconds / 60).toFixed(2)} mins
                            </div>
                        </div>
                        <div className="bg-black/30 p-3 rounded-lg border border-white/5">
                            <div className="text-xs text-gray-500 mb-1 flex items-center gap-1"><AlertTriangle size={12}/> MAE ERROR</div>
                            <div className="text-lg font-mono text-f1-light">
                                ±{prediction.mae_error.toFixed(2)}s
                            </div>
                        </div>
                    </div>
                    
                    <div className="mt-2">
                        <div className="flex justify-between text-xs mb-1">
                            <span>Confidence</span>
                            <span className="text-neon-blue">{prediction.confidence}%</span>
                        </div>
                        <div className="h-1.5 bg-gray-800 rounded-full overflow-hidden">
                            <div className="h-full bg-neon-blue transition-all duration-1000" style={{width: `${prediction.confidence}%`}}></div>
                        </div>
                    </div>
                </div>
            ) : (
                <div className="text-gray-400">Model offline.</div>
            )}
        </div>
    );
}
