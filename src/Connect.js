import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const Connect = () => {
  const [username, setUsername] = useState('');
  const [port, setPort] = useState('');
  const navigate = useNavigate();

  const handleConnect = () => {
    console.log(`Signing in with email: ${username} and password: ${port}`);
    navigate('/chat', { state: { username } });
  };

  return (
    <div>
      <h2>Connect</h2>
      <form>
        <label>
          Username:
          <input
            type="email"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />
        </label>
        <br />
        <label>
          Port:
          <input
            type="Port"
            value={port}
            onChange={(e) => setPort(e.target.value)}
          />
        </label>
        <br />
        <button type="button" onClick={handleConnect}>
          Connect
        </button>
      </form>
    </div>
  );
};

export default Connect;
