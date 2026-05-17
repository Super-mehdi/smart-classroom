

export function AttentionGauge({ scores }) {
    const averageScore = scores.reduce((a, b) => a + b.score, 0) / scores.length;
    if (Object.values(scores).length === 0) return null;
    const circumference = 251;
    const offset = circumference * (1 - averageScore);

    return (        <div className="attention-gauge">
            <h2>Attention Gauge</h2>
            <p>Average Score: {averageScore.toFixed(2)}</p>
            <svg width="120" height="120" viewBox="0 0 120 120">
            <circle
                cx="60" cy="60" r="40"
                fill="none"
                stroke="#eee"
                strokeWidth="10"
            />
            <circle
                cx="60" cy="60" r="40"
                fill="none"
                stroke="green"
                strokeWidth="10"
                strokeDasharray={circumference}
                strokeDashoffset={offset}
                transform="rotate(-90 60 60)"
            />
            </svg>
            </div>
    );
}