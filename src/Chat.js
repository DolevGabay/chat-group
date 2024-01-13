import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import WebSocketService from './WebSocketService'; // Import WebSocketService
import './Chat.css';
import animals from './images/Animals';

const Chat = () => {
  const location = useLocation();
  const username = location.state && location.state.username;
  const port = location.state && location.state.port;
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [selectedAnimal, setSelectedAnimal] = useState(null);
  const [notification, setNotification] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    // Connect to WebSocket when component mounts
    WebSocketService.connect(username, port, setMessages, setNotification);

    return () => {
      // Close WebSocket connection when component unmounts
      WebSocketService.close();
    };
  }, [username, port]);

  const handle_send_message = () => {
    // Send message to the server
    if (WebSocketService.socket && WebSocketService.socket.readyState === WebSocket.OPEN) {
      const messageObject = {
        type: 'message',
        userName: username,
        text: newMessage,
      };

      WebSocketService.sendMessage(messageObject);
      setNewMessage('');
    } else {
      console.error('WebSocket connection is not open.');
    }
  };

  const handle_exit_chat = () => {
    // Disconnect from the server and navigate back to home
    WebSocketService.disconnect(username);
    navigate('/');
  };

  const handle_input_change = (event) => {
    setNewMessage(event.target.value);
  };

  useEffect(() => {
    // Select random animal image when component mounts
    if (!selectedAnimal) {
      const availableAnimals = animals.filter(animal => animal !== selectedAnimal);
      const randomAnimal = availableAnimals[Math.floor(Math.random() * availableAnimals.length)];
      setSelectedAnimal(randomAnimal);
    }
  }, [selectedAnimal]);

  useEffect(() => {
    const timeoutId = setTimeout(() => {
      setNotification(null);
    }, 3000);
  
    return () => {
      clearTimeout(timeoutId);
    };
  }, [notification]); 

  return (
    <div>
      <div className="chat">
        <div className="chat-title">
          <h1>{username} </h1>
          <button type="submit" className="quit-btn" onClick={handle_exit_chat}>
            Quit
          </button>
          <figure className="avatar">
            <img src={selectedAnimal} alt="Profile Avatar" />
          </figure>
        </div>

        <div className="messages-content">
        {messages.map((message, index) => (
          <div className={message.userName === username ? 'left' : 'right'} key={index}>
            <span>{message.userName}:</span>
            <p>{message.text}</p>
          </div>
        ))}
      </div>

        <div className="message-box">
        <textarea
            type="text"
            className="message-input"
            placeholder="Type message..."
            value={newMessage}
            onChange={handle_input_change}
          ></textarea>
          <button type="submit" className="message-submit" onClick={handle_send_message}>
            Send
          </button>

        </div>
      </div>
      <div className="bg"></div>

      <div id="notification-modal" style={{ display: notification ? 'block' : 'none' }}>
        <img
          src="https://static-00.iconduck.com/assets.00/notification-icon-1661x2048-24eo7df9.png"  
          alt="Information Icon"
          style={{ width: '24px', height: '24px', marginRight: '8px' }} 
        />
        <p id="notification-message">{notification}</p>
      </div>
    </div>
  );
};

export default Chat;
