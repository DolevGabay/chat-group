import socketio
import eventlet
import threading
import uuid
from datetime import datetime
import logging
from LoggingConfig import configure_logging
from GroupChatServer import start_group_chat
from PortManager import PortManager

# Logging configuration
configure_logging()

SIO = socketio.Server(cors_allowed_origins="http://3.71.7.179:3000")
App = socketio.WSGIApp(SIO)

PORT_MANAGER = PortManager()

#handle client connection
@SIO.event
def connect(sid, environ):
    logging.info(f"Client {sid} connected to the main chat")

#handle open chat request
@SIO.event
def open_chat(sid, data):
    logging.info(f"Message from {sid}: {data}")
    logging.info(PORT_MANAGER.get_port_in_use())
    PORT = data.get('clientData').get('port')
    USER_NAME = data.get('clientData').get('username')
    UUID = generate_uuid()

    if PORT_MANAGER.is_port_in_use(PORT):
        SIO.emit('chat_opened', {"message": f"Port {PORT} is already in use","username":USER_NAME, "port":PORT, "uuid": UUID}, room=sid)
        return

    #start group chat server in a new thread
    threading.Thread(target=start_group_chat, args=(PORT, PORT_MANAGER), daemon=True).start()

    SIO.emit('chat_opened', {"message": f"Group chat opened on port {PORT}","username":USER_NAME, "port":PORT, "uuid": UUID}, room=sid)

#handle client disconnection
@SIO.event
def disconnect(sid):
    logging.info(f"Client {sid} disconnected from the main chat")

def generate_uuid():
    return uuid.uuid4().hex

if __name__ == '__main__':
    eventlet.wsgi.server(eventlet.listen(('3.71.7.179', 8000)), App)
