import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { useNavigate } from 'react-router-dom';
import './Chat.css';
import animals from './images/Animals';

const Chat = () => {
  const location = useLocation();
  const username = location.state && location.state.username;
  const port = location.state && location.state.port;
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [socket, setSocket] = useState(null);
  const [selectedAnimal, setSelectedAnimal] = useState(null);
  const [notification, setNotification] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    // Create a WebSocket connection
    const newSocket = new WebSocket(`ws://localhost:${port}`);
    setSocket(newSocket);

    newSocket.addEventListener('open', (event) => {
      console.log('Connected to the server');
      newSocket.send(JSON.stringify({ type: 'connect', username }));
    });

    newSocket.addEventListener('message', (event) => {
      const receivedMessages = JSON.parse(event.data);
      if (receivedMessages.type === 'message') {
        setMessages(receivedMessages.messages);
        console.log(receivedMessages.messages);
      } else if (receivedMessages.type === 'notification' && receivedMessages.username !== username) {
        setNotification(receivedMessages.serverNotification);
        setTimeout(() => {
          setNotification(null);
        }, 3000); 
      }
    });

    newSocket.addEventListener('close', (event) => {
      console.log('Connection closed');
    });

    return () => {
        newSocket.close();
    };
  }, []);

  const handleSendMessage = () => {
    if (socket && socket.readyState === WebSocket.OPEN) {
      const messageObject = {
        type: 'message',
        userName: username,
        text: newMessage,
      };

      socket.send(JSON.stringify(messageObject));

      setNewMessage('');
    } else {
      console.error('WebSocket connection is not open.');
    }
  };

  const handleExitChat = () => {
    if (socket && socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify({ type: 'disconnect', username }));
        socket.close();
    }
    navigate('/');
  };

  const handleInputChange = (event) => {
    setNewMessage(event.target.value);
  };

  useEffect(() => {
    if (!selectedAnimal) {
      const availableAnimals = animals.filter(animal => animal !== selectedAnimal);
      const randomAnimal = availableAnimals[Math.floor(Math.random() * availableAnimals.length)];
      setSelectedAnimal(randomAnimal);
    }
  }, [selectedAnimal]);

  return (
    <div>
      <div className="chat">
        <div className="chat-title">
          <h1>{username} </h1>
          <button type="submit" className="quit-btn" onClick={handleExitChat}>
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
            onChange={handleInputChange}
          ></textarea>
          <button type="submit" className="message-submit" onClick={handleSendMessage}>
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
