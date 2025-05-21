"use client";
import React, { useState } from "react";

const Login: React.FC<{ onLogin: (token: string) => void }> = ({ onLogin }) => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);

  const handleLogin = () => {
    setError(null);
    try {
      // Use a static token for simplicity
      const token = "simple-static-token";
      onLogin(token); // Pass the token to the parent component
    } catch (err) {
      setError("Failed to log in.");
      console.error("Login error:", err);
    }
  };

  return (
    <div style={{ margin: "20px auto", padding: "20px", border: "1px solid #333", borderRadius: "8px", maxWidth: "400px", backgroundColor: "#f9f9f9" }}>
      <h2 style={{ textAlign: "center", color: "#333", marginBottom: "20px" }}>Login</h2>
      <div style={{ marginBottom: "10px" }}>
        <label>Username:</label>
        <input
          type="text"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          style={{ padding: "8px", width: "100%" }}
        />
      </div>
      <div style={{ marginBottom: "10px" }}>
        <label>Password:</label>
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          style={{ padding: "8px", width: "100%" }}
        />
      </div>
      {error && <p style={{ color: "red" }}>{error}</p>}
      <button
        onClick={handleLogin}
        style={{
          padding: "10px 20px",
          backgroundColor: "#4CAF50",
          color: "white",
          border: "none",
          borderRadius: "4px",
          cursor: "pointer",
          width: "100%",
        }}
      >
        Login
      </button>
    </div>
  );
};

export default Login;
