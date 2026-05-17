import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import ProtectedRoute from "./components/ProtectedRoute";
import Home from "./pages/Home";
import Sessions from "./pages/Sessions";
import Students from "./pages/Students";
import Admin from "./pages/Admin";
import Auth from "./pages/Auth";
import LiveView from "./pages/LiveView";
import Layout from "./components/Layout";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Auth />} />
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <Layout />
            </ProtectedRoute>
          }
        >
          <Route index element={<Home />} />
          <Route path="sessions" element={<Sessions />} />
          <Route path="students" element={<Students />} />
          <Route path="admin" element={<Admin />} />
        </Route>
        <Route path="/live/:sessionId" element={<LiveView />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;