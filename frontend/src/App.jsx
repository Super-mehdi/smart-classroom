import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import ProtectedRoute from "../components/ProtectedRoute";
import Home from "../pages/Home";
import Auth from "../pages/Auth";
import LiveView from "../pages/LiveView";
import AlertConfigPage from "../pages/AlertConfigPage";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Auth />} />
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <Home />
            </ProtectedRoute>
          }
        />
        <Route
          path="/classes/:classId/alert-config"
          element={
            <ProtectedRoute>
              <AlertConfigPage />
            </ProtectedRoute>
          }
        />
        <Route path="/live/:sessionId" element={<LiveView />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;