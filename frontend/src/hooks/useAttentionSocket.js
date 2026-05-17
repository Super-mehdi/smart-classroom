import { useState, useEffect } from 'react';

export function useAttentionSocket(sessionId) {
    const  [scores, setScores] = useState([]);
    useEffect(() => {
        if (!sessionId) return;
        const socket = new WebSocket(`ws://localhost:8000/ws/sessions/${sessionId}`);
        socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            setScores(data.students);
        }
        return () => {socket.close();
        }
    }, [sessionId]);

    return scores;
}