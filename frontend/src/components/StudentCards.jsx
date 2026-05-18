import React from "react";

export function StudentCards({ scores }) {
    if (!scores || !Array.isArray(scores) || scores.length === 0) {
        return <div className="text-gray-400 text-sm italic p-4">No student data available</div>;
    }

    const getStatusColor = (score) => {
        if (score >= 0.7) return "bg-blue-600";
        if (score >= 0.4) return "bg-amber-400";
        return "bg-red-500";
    };

    return (
        <div className="grid grid-cols-2 gap-3 max-h-80 overflow-y-auto">
            {scores.map((student) => (
                <div key={student.student_id} className="bg-white border border-gray-100 rounded-xl p-3 flex items-center gap-3 hover:shadow-md transition-all duration-200">
                    <div className={`w-10 h-10 rounded-full flex items-center justify-center text-white text-sm font-medium ${getStatusColor(student.score || 0)}`}>
                        {student.student_id?.slice(0, 2).toUpperCase() || "??"}
                    </div>
                    <div className="flex-1 min-w-0">
                        <div className="text-sm font-medium text-gray-800 truncate">{student.student_id}</div>
                        <div className="text-xs text-gray-500">{(student.score * 100).toFixed(0)}%</div>
                    </div>
                    <div className={`w-2 h-2 rounded-full ${getStatusColor(student.score || 0)}`} />
                </div>
            ))}
        </div>
    );
}