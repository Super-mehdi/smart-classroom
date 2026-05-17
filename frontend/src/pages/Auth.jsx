import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { signup } from "../api/client";
import { useAuth } from "../hooks/useAuth";
import styles from "./Auth.module.css";

export default function Auth() {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [role, setRole] = useState("teacher");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      if (isLogin) {
        const success = await login(email, password);
        if (success) {
          navigate("/");
        } else {
          setError("Invalid email or password");
        }
      } else {
        await signup({ email, password, name, role });
        // After signup, attempt to login or just switch to login mode
        setIsLogin(true);
        setError("Account created. Please sign in.");
      }
    } catch (err) {
      setError(err.message || "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  const toggleMode = () => {
    setIsLogin(!isLogin);
    setError("");
    setEmail("");
    setPassword("");
    setName("");
    setRole("teacher");
  };

  return (
    <div className={styles.container}>
      <div className={styles.leftColumn}>
        <div className={styles.formWrapper}>
          <div className={styles.logo}>SmartClass</div>
          
          <h1 className={styles.welcomeHeading}>
            {isLogin ? "Welcome back" : "Create account"}
          </h1>
          <p className={styles.subtitle}>
            {isLogin ? "Sign in to your account" : "Join SmartClass today"}
          </p>

          {error && <div className={styles.error}>{error}</div>}

          <form className={styles.form} onSubmit={handleSubmit}>
            {!isLogin && (
              <div className={styles.inputGroup}>
                <input
                  type="text"
                  placeholder="Full Name"
                  className={styles.input}
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  required
                />
              </div>
            )}

            <div className={styles.inputGroup}>
              <input
                type="email"
                placeholder="Email"
                className={styles.input}
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>

            <div className={styles.inputGroup}>
              <input
                type="password"
                placeholder="Password"
                className={styles.input}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>

            {!isLogin && (
              <div className={styles.inputGroup}>
                <select
                  className={styles.roleSelect}
                  value={role}
                  onChange={(e) => setRole(e.target.value)}
                >
                  <option value="teacher">Teacher</option>
                  <option value="superuser">Superuser</option>
                </select>
              </div>
            )}

            <button type="submit" className={styles.submitButton} disabled={loading}>
              {loading ? "Please wait..." : (isLogin ? "Sign In" : "Sign Up")}
            </button>
          </form>

          <div className={styles.toggleWrapper}>
            {isLogin ? "Don't have an account?" : "Already have an account?"}
            <button type="button" className={styles.toggleLink} onClick={toggleMode}>
              {isLogin ? "Sign up" : "Sign in"}
            </button>
          </div>
        </div>
      </div>

      <div className={styles.rightColumn}>
        <svg
          className={styles.illustration}
          viewBox="0 0 500 400"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          {/* Background / Floor */}
          <rect x="50" y="300" width="400" height="2" fill="#dadce0" />
          
          {/* Teacher */}
          <rect x="80" y="180" width="40" height="80" rx="4" fill="#1a73e8" />
          <circle cx="100" y="160" r="15" fill="#1a73e8" />
          
          {/* Desk for Teacher */}
          <rect x="70" y="260" width="60" height="40" rx="2" fill="#4285f4" />
          
          {/* Students */}
          <g transform="translate(200, 220)">
            <rect x="0" y="30" width="30" height="50" rx="4" fill="#34a853" opacity="0.8" />
            <circle cx="15" cy="15" r="12" fill="#34a853" opacity="0.8" />
            <rect x="-5" y="80" width="40" height="10" rx="2" fill="#dadce0" />
          </g>
          <g transform="translate(260, 220)">
            <rect x="0" y="30" width="30" height="50" rx="4" fill="#fbbc04" opacity="0.8" />
            <circle cx="15" cy="15" r="12" fill="#fbbc04" opacity="0.8" />
            <rect x="-5" y="80" width="40" height="10" rx="2" fill="#dadce0" />
          </g>
          <g transform="translate(320, 220)">
            <rect x="0" y="30" width="30" height="50" rx="4" fill="#4285f4" opacity="0.8" />
            <circle cx="15" cy="15" r="12" fill="#4285f4" opacity="0.8" />
            <rect x="-5" y="80" width="40" height="10" rx="2" fill="#dadce0" />
          </g>
          <g transform="translate(380, 220)">
            <rect x="0" y="30" width="30" height="50" rx="4" fill="#34a853" opacity="0.8" />
            <circle cx="15" cy="15" r="12" fill="#34a853" opacity="0.8" />
            <rect x="-5" y="80" width="40" height="10" rx="2" fill="#dadce0" />
          </g>

          {/* AI Camera */}
          <rect x="230" y="40" width="40" height="25" rx="5" fill="#5f6368" />
          <circle cx="250" cy="52.5" r="8" fill="#202124" />
          <circle cx="265" cy="48" r="3" fill="#d93025" />
          
          {/* Scanning lines/cone */}
          <path
            d="M250 65L150 300M250 65L350 300"
            stroke="#1a73e8"
            strokeWidth="1"
            strokeDasharray="4 4"
            opacity="0.3"
          />
        </svg>
      </div>
    </div>
  );
}
