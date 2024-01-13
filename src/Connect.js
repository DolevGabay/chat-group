import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './Connect.css';

const Connect = () => {
  const [username, setUsername] = useState('');
  const [port, setPort] = useState('');
  const navigate = useNavigate();
  const DEFAULT_PORT = "3001";

  const handle_connect = () => {
    console.log(`Connecting with username: ${username} and port: ${port}`);
    
    if (port === '') {
      navigate('/chat', { state: { username, port: DEFAULT_PORT } }); // default port
    } else if (isNaN(port)) {
      alert('Port must be a valid number');
      setPort(''); 
    } else {
      navigate('/chat', { state: { username, port } });
    }
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
          <form>
            <input type="text" placeholder="USERNAME" value={username} onChange={handle_username_change} />
            <input type="text" placeholder="PORT" value={port} onChange={handle_port_change} />
            <button className="opacity" type="button" onClick={handle_connect}>
              Connect
            </button>
          </form>
          <div className="register-forget opacity">
            <a>DEFAULT PORT: {DEFAULT_PORT}</a>           
          </div>
        </div>
        <div className="circle circle-two"></div>
      </div>
      <div className="theme-btn-container"></div>
    </section>
  );
};

export default Connect;
