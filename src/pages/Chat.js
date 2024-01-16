import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import './Chat.css';
import animals from '../images/Animals';
import io from 'socket.io-client';

const Chat = () => {
  const location = useLocation();
  const username = location.state && location.state.username;
  const port = location.state && location.state.port;
  const uuid = location.state && location.state.uuid;
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [selectedAnimal, setSelectedAnimal] = useState(null);
  const [notification, setNotification] = useState(null);
  const [socketConnection, setSocketConnection] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    // Connect to the chat server
    console.log(`C ${port}`);
    const socket = io(`http://localhost:${port}`);
    setSocketConnection(socket);

    return () => {
      socket.disconnect();
    };
  }, []);

  const handleDisconnect = () => {
    console.log('Disconnected from Main server');
  };

  const handleMessages = (messages) => {
    console.log(messages)
    setMessages(messages)
  };

  const handleConnect = () => {
    console.log('Connected to Chat server');
        const message = `${username} has joined the chat.`
        socketConnection.emit('join', uuid);
        socketConnection.emit('notify_all', message);
  };

  const handleNotify = (notification) => {
    setNotification(notification);
    setTimeout(() => {
      setNotification(null);
    }, 3000);
  };

  useEffect(() => {
    if (socketConnection) {
      socketConnection.on('disconnect', handleDisconnect);
      socketConnection.on('messages', handleMessages);
      socketConnection.on('connect', handleConnect);
      socketConnection.on('notify', handleNotify);
    }

    return () => {
      // Clean up event listeners when the component is unmounted
      if (socketConnection) {
        socketConnection.off('disconnect', handleDisconnect);
      }
    };
  }, [socketConnection]);

  const handle_submit = () => {
    console.log(newMessage)
    if (newMessage.trim() === '') {
      setNotification('Message cannot be empty.');
      return;
    }

    // Emit the new message to the server
    socketConnection.emit('message', { userName: username, text: newMessage, uuid });

    // Clear the input field
    setNewMessage('');
  };

  const handle_exit_chat = () => {
    // Disconnect from the server and navigate back to home
    const message = `${username} has left the chat.`;
    socketConnection.emit('notify_all', message);
    socketConnection.disconnect();
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
          <h2>{port}</h2>
          <button type="submit" className="quit-btn" onClick={handle_exit_chat}>
            Quit
          </button>
          <figure className="avatar">
            <img src={selectedAnimal} alt="Profile Avatar" />
          </figure>
        </div>

        <div className="messages-content">
        {messages.map((message, index) => (
          <div className={message.uuid === uuid ? 'left' : 'right'} key={index}>
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
          <button type="submit" className="message-submit" onClick={handle_submit}>
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
