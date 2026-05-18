import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { signup } from "../api/client";
import { useAuth } from "../hooks/useAuth";

export default function Auth() {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
        const success = await login(email, password);
        if (success) navigate("/");
        else setError("Invalid email or password");
    } catch (err) {
      setError(err.message || "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-screen">
      <div className="w-[45%] flex flex-col justify-center px-16 bg-white">
        <div className="text-blue-600 font-bold text-2xl mb-2">SmartClass</div>
        <p className="text-gray-400 text-sm mb-8">AI-powered engagement tracking</p>
        
        <h1 className="text-3xl font-light text-gray-900">Welcome back</h1>
        <p className="text-gray-500 text-sm mt-2 mb-8">Sign in to your account</p>

        {error && <div className="text-red-500 text-sm mb-4 bg-red-50 p-3 rounded">{error}</div>}

        <form className="space-y-6" onSubmit={handleSubmit}>
          <div>
            <label className="text-xs font-medium text-gray-600 uppercase tracking-wide">Email</label>
            <input type="email" className="w-full border-b-2 border-gray-200 focus:border-blue-500 outline-none py-2 text-gray-800 transition-colors bg-transparent" value={email} onChange={(e) => setEmail(e.target.value)} required />
          </div>
          <div>
            <label className="text-xs font-medium text-gray-600 uppercase tracking-wide">Password</label>
            <input type="password" className="w-full border-b-2 border-gray-200 focus:border-blue-500 outline-none py-2 text-gray-800 transition-colors bg-transparent" value={password} onChange={(e) => setPassword(e.target.value)} required />
          </div>
          <button type="submit" className="w-full bg-blue-600 hover:bg-blue-700 text-white py-3 rounded-lg font-medium transition-colors" disabled={loading}>
            {loading ? "Please wait..." : "Sign In"}
          </button>
        </form>
      </div>

      <div className="w-[55%] bg-gradient-to-br from-blue-600 to-blue-800 flex flex-col items-center justify-center text-white p-16">
        <svg viewBox="0 0 500 400" className="w-full max-w-sm" fill="none" xmlns="http://www.w3.org/2000/svg">
            {/* Simple abstract classroom */}
            <rect x="50" y="300" width="400" height="2" fill="white" fillOpacity="0.3" />
            <rect x="80" y="180" width="40" height="80" rx="4" fill="white" />
            <circle cx="100" cy="160" r="15" fill="white" />
            <rect x="200" y="250" width="30" height="50" rx="4" fill="white" fillOpacity="0.4" />
            <rect x="260" y="250" width="30" height="50" rx="4" fill="white" fillOpacity="0.4" />
            <rect x="230" y="40" width="40" height="25" rx="5" fill="white" />
        </svg>
        <h2 className="text-3xl font-light mt-8">Smart Monitoring</h2>
        <p className="text-blue-200 text-sm mt-2">AI-powered classroom engagement tracking</p>
      </div>
    </div>
  );
}