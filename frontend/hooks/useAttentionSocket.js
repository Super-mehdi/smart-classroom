import { useState, useEffect } from 'react';

export function useAttentionSocket(sessionId) {
    const  [scores, setScores] = useState([]);
    useEffect(() => {
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