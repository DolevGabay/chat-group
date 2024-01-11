import React, { useState, useEffect } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useNavigate } from 'react-router-dom';

const Chat = () => {
  const location = useLocation();
  const username = location.state && location.state.username;
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [socket, setSocket] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    // Create a WebSocket connection
    const newSocket = new WebSocket('ws://localhost:3001');
    setSocket(newSocket);

    newSocket.addEventListener('open', (event) => {
      console.log('Connected to the server');
      newSocket.send(JSON.stringify({ type: 'connect', username }));
    });

    newSocket.addEventListener('message', (event) => {
        const receivedMessages = JSON.parse(event.data);
        if (receivedMessages.type === 'message') {
          setMessages(receivedMessages.messages);
        }
        else if (receivedMessages.type === 'notification' && receivedMessages.username !== username )
        alert(receivedMessages.serverNotification);
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

  return (
    <div>
      <h2>Chat</h2>
      <p>Welcome, {username || 'Guest'}!</p>

      <div style={{ height: '200px', border: '1px solid #ccc', overflowY: 'auto' }}>
        {messages.map((message, index) => (
          <div key={index}>
            <strong>{message.userName}:</strong> {message.text}
          </div>
        ))}
      </div>

      <div>
        <textarea
          rows="3"
          cols="50"
          value={newMessage}
          onChange={(e) => setNewMessage(e.target.value)}
        />
      </div>

      <div>
        <button onClick={handleSendMessage}>Send</button>
        <button onClick={handleExitChat}>Exit</button>
      </div>
    </div>
  );
};

export default Chat;
