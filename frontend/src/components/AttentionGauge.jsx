
import React from "react";

export function AttentionGauge({ scores }) {
    const averageScore = scores && scores.length > 0 
        ? scores.reduce((a, b) => a + (b.score || 0), 0) / scores.length 
        : 0;

    const getColor = (score) => {
        if (score >= 0.7) return "#34a853";
        if (score >= 0.4) return "#fbbc04";
        return "#ea4335";
    };

    const circumference = 251;
    const offset = circumference * (1 - averageScore);

    if (!scores || scores.length === 0) return null;

    return (
        <div className="flex flex-col items-center justify-center">
            <div className="relative w-40 h-40 flex items-center justify-center">
                <svg width="160" height="160" viewBox="0 0 160 160">
                    <circle cx="80" cy="80" r="60" fill="none" stroke="#f1f3f4" strokeWidth="12" />
                    <circle
                        cx="80" cy="80" r="60"
                        fill="none"
                        stroke={getColor(averageScore)}
                        strokeWidth="12"
                        strokeDasharray={circumference}
                        strokeDashoffset={offset}
                        strokeLinecap="round"
                        transform="rotate(-90 80 80)"
                        className="transition-all duration-500 ease-out"
                    />
                </svg>
                <div className="absolute text-3xl font-light text-gray-700">
                    {Math.round(averageScore * 100)}%
                </div>
            </div>
            <div className="text-xs text-gray-500 mt-2 font-medium uppercase tracking-wide">Class Average</div>
        </div>
    );
}