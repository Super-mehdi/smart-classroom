import { createContext, useContext, useState, useEffect } from "react";
import { apiFetch } from "../api/client";

export const SessionContext = createContext();

export function SessionProvider({ children, token }) {
    const [sessionId, setSessionId] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (!token) {
            setSessionId(null);
            setLoading(false);
            return;
        }

        apiFetch("/api/sessions", {}, token).then(sessions => {
            const active = sessions.find(s => !s.ended_at);
            setSessionId(active ? active.session_id : null);
            setLoading(false);
        }).catch(() => {
            setLoading(false);
        });
    }, [token]);

    return (
        <SessionContext.Provider value={{ sessionId, setSessionId, loading }}>
            {children}
        </SessionContext.Provider>
    );
}

export const useSession = () => useContext(SessionContext);
