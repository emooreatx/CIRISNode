"use client"; // Ensure this is a client component if using hooks directly or importing client components
import React, { useState } from 'react';
import TestConnection from '../components/TestConnection';
import SimpleBenchRunner from '../components/SimpleBenchRunner';
import Login from '../components/Login';

export default function Home() {
  const [token, setToken] = useState(null);

  const handleLogin = (newToken) => {
    setToken(newToken);
    localStorage.setItem('jwt', newToken); // Store the token in localStorage for persistence
  };

  return (
    <div style={{ fontFamily: 'Arial, sans-serif', padding: '20px' }}>
      <h1 style={{ textAlign: 'center', marginBottom: '30px', color: '#222' }}>CIRISNode Dashboard</h1>
      
      {!token ? (
        <Login onLogin={handleLogin} />
      ) : (
        <>
          <TestConnection />
          <hr style={{ margin: '40px 0', borderColor: '#ccc' }} />
          <SimpleBenchRunner />
        </>
      )}
    </div>
  );
}
