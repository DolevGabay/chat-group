// WebSocketService.js
class WebSocketService {
    constructor() {
      this.socket = null;
    }
  
    connect(username, port, onMessageCallback, onNotificationCallback, onConnectCallback, onCloseCallback) {
      this.socket = new WebSocket(`ws://localhost:${port}`);
  
      this.socket.addEventListener('open', (event) => {
        console.log('Connected to the server');
        this.socket.send(JSON.stringify({ type: 'connect', username }));
        onConnectCallback && onConnectCallback();
      });
  
      this.socket.addEventListener('message', (event) => {
        const receivedMessages = JSON.parse(event.data);
        if (receivedMessages.type === 'message') {
          onMessageCallback && onMessageCallback(receivedMessages.messages);
        } else if (receivedMessages.type === 'notification' && receivedMessages.username !== username) {
          onNotificationCallback && onNotificationCallback(receivedMessages.serverNotification);
        } 
      });
  
      this.socket.addEventListener('close', (event) => {
        console.log('Connection closed');
        onCloseCallback && onCloseCallback();
      });
    }
  
    sendMessage(messageObject) {
      if (this.socket && this.socket.readyState === WebSocket.OPEN) {
        this.socket.send(JSON.stringify(messageObject));
      } else {
        console.error('WebSocket connection is not open.');
      }
    }
  
    disconnect(username) {
      if (this.socket && this.socket.readyState === WebSocket.OPEN) {
        this.socket.send(JSON.stringify({ type: 'disconnect', username }));
        this.socket.close();
      }
    }
  
    close() {
      if (this.socket && this.socket.readyState !== WebSocket.CLOSED) {
        this.socket.close();
      }
    }
  }
  
  export default new WebSocketService();
  