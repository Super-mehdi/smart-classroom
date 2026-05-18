import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./index.css";
import App from "./App.jsx";
import { AuthProvider } from "./context/AuthContext.jsx";
import { SessionProvider } from "./context/SessionContext.jsx";
import { useAuth } from "./hooks/useAuth";

function Providers({ children }) {
    const { token } = useAuth();
    return <SessionProvider token={token}>{children}</SessionProvider>;
}

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <AuthProvider>
        <Providers>
            <App />
        </Providers>
    </AuthProvider>
  </StrictMode>
);