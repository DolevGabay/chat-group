import React, { useState, useEffect } from 'react';
import './Connect.css';
import io from 'socket.io-client';
import { useNavigate } from 'react-router-dom';

const Connect = () => {
  const [username, setUsername] = useState('');
  const [port, setPort] = useState('');
  const [loading, setLoading] = useState(false);
  const [mainSocketConnection, setMainSocketConnection] = useState(null);

  const navigate = useNavigate();  // Correct hook for navigation

  const isValidPort = (port) => {
    return !isNaN(port) && port >= 1024 && port <= 65535 && port !== 8000 && port !== 3000;
  };

  const handleConnect = () => {
    if (!isValidPort(port)) {
      alert('Invalid port number. Port must be between 1024 and 65535, excluding 8000 and 3000.');
      setPort('');
      return;
    }

    setLoading(true);
    connectToChatServer();
  };

  const handleUsernameChange = (event) => {
    setUsername(event.target.value);
  };

  const handlePortChange = (event) => {
    setPort(event.target.value);
  };

  const connectToChatServer = () => {
    const clientData = { username, port };
    mainSocketConnection.emit('open_chat', { clientData });
  };

  useEffect(() => {
    // Connect to the main server
    const socketInstance = io('http://localhost:8000');
    setMainSocketConnection(socketInstance);

    return () => {
      // Clean up event listeners when the component is unmounted
      socketInstance.disconnect();
    };
  }, []);

  const handleChatOpened = (message) => {
    console.log(message);
    navigate('/chat', { state: { username:message.username, port:message.port, uuid: message.uuid } });
  };

  const handleDisconnect = () => {
    console.log('Disconnected from Main server');
  };

  useEffect(() => {
    // Event listeners for main server
    if (mainSocketConnection) {
      mainSocketConnection.on('chat_opened', handleChatOpened);
      mainSocketConnection.on('disconnect', handleDisconnect);
      mainSocketConnection.on('connect', () => {
        console.log('Connected to Main server');
        setLoading(false);
      });
    }

    return () => {
      // Clean up event listeners when the component is unmounted
      if (mainSocketConnection) {
        mainSocketConnection.off('chat_opened', handleChatOpened);
        mainSocketConnection.off('disconnect', handleDisconnect);
      }
    };
  }, [mainSocketConnection, navigate]);

  return (
    <section className="container">
      <div className="login-container">
        <div className="circle circle-one"></div>
        <div className="form-container">
          <img src="https://raw.githubusercontent.com/hicodersofficial/glassmorphism-login-form/master/assets/illustration.png" alt="illustration" className="illustration" />
          <h1 className="opacity">Chat</h1>
          <h1 className="opacity">Log In</h1>
          {loading ? <div className="loader" /> : ''}
          <form>
            <input type="text" placeholder="USERNAME" value={username} onChange={handleUsernameChange} />
            <input type="text" placeholder="PORT" value={port} onChange={handlePortChange} />
            <button className="opacity" type="button" onClick={handleConnect}>
              {loading ? 'Connecting...' : 'Connect'}
            </button>
          </form>
          <div className="register-forget opacity">
            <a>SERVER PORT: 8000</a>           
            <a>FRONT PORT: 3000</a>           
          </div>
        </div>
        <div className="circle circle-two"></div>
      </div>
      <div className="theme-btn-container"></div>
    </section>
  );
};

export default Connect;
