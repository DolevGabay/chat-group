import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './Connect.css';

const Connect = () => {
  const [username, setUsername] = useState('');
  const [port, setPort] = useState('');
  const [loading, setLoading] = useState(false); 
  const navigate = useNavigate();

  const isValidPort = (port) => {
    return !isNaN(port) && port >= 1024 && port <= 65535 && port !== 8000 && port !== 3000;
  };
  
  const handle_connect = async () => {
    try {
      setLoading(true);
  
      if (!isValidPort(port)) {
        alert('Invalid port number. Port must be between 1024 and 65535, excluding 8000 and 3000.');
        setPort('');
        setLoading(false);
        return;
      }
  
      // Send HTTP request to start the WebSocket server
      const serverResponse = await fetch(`http://localhost:8000/start_websocket_server/${port}`, {
        method: 'GET',
      });
      const serverData = await serverResponse.json();
      console.log(serverData.message);
      const uuid = generate_uuid();
      navigate('/chat', { state: { username, port, uuid } });
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };
  

  const generate_uuid = () => {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
      const r = Math.random() * 16 | 0,
            v = c === 'x' ? r : (r & 0x3 | 0x8);
      return v.toString(16);
    });
  };  
  
  const handle_username_change = (event) => {
    setUsername(event.target.value);
  };

  const handle_port_change = (event) => {
    setPort(event.target.value);
  };

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
            <input type="text" placeholder="USERNAME" value={username} onChange={handle_username_change} />
            <input type="text" placeholder="PORT" value={port} onChange={handle_port_change} />
            <button className="opacity" type="button" onClick={handle_connect}>
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
