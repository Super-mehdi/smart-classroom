import { useState, useEffect, useRef } from 'react';

export function useAttentionSocket(sessionId) {
    const [scores, setScores] = useState([]);
    const socketRef = useRef(null);

    useEffect(() => {
        if (!sessionId) {
            if (socketRef.current) {
                socketRef.current.close();
                socketRef.current = null;
            }
            setScores([]);
            return;
        }

        // Only create a new connection if none exists or it is closed
        if (!socketRef.current || socketRef.current.readyState === WebSocket.CLOSED) {
            console.log(`Establishing WebSocket for session: ${sessionId}`);
            const socket = new WebSocket(`ws://${window.location.hostname}:8000/ws/sessions/${sessionId}`);
            socketRef.current = socket;

            socket.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    setScores(data.students || []);
                } catch (err) {
                    console.error("Failed to parse socket data", err);
                }
            };

            socket.onclose = () => console.log('WebSocket connection closed');
            socket.onerror = (err) => console.error('WebSocket error', err);
        }

        return () => {
            if (socketRef.current) {
                socketRef.current.close();
                socketRef.current = null;
            }
        };
    }, [sessionId]);

    return scores;
}