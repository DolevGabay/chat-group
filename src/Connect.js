import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './Connect.css';

const Connect = () => {
  const [username, setUsername] = useState('');
  const [port, setPort] = useState('');
  const navigate = useNavigate();

  const handleConnect = () => {
    console.log(`Connecting with username: ${username} and port: ${port}`);
    
    if (port === '') {
      const defaultPort = "3001";
      navigate('/chat', { state: { username, port: defaultPort } }); // default port
    } else if (isNaN(port)) {
      alert('Port must be a valid number');
      setPort(''); 
    } else {
      navigate('/chat', { state: { username, port } });
    }
  };  
  
  const handleUsernameChange = (event) => {
    setUsername(event.target.value);
  };

  const handlePortChange = (event) => {
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
          <form>
            <input type="text" placeholder="USERNAME" value={username} onChange={handleUsernameChange} />
            <input type="text" placeholder="PORT" value={port} onChange={handlePortChange} />
            <button className="opacity" type="button" onClick={handleConnect}>
              Connect
            </button>
          </form>
          <div className="register-forget opacity">
              <a>DEFAULT PORT: 3001</a>           
          </div>
        </div>
        <div className="circle circle-two"></div>
      </div>
      <div className="theme-btn-container"></div>
    </section>
  );
};

export default Connect;
