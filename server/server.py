import socketio
import eventlet
import threading
import uuid
from datetime import datetime
import logging
from logging_config import configure_logging
from group_chat_server import start_group_chat
from port_manager import PortManager

configure_logging()

sio = socketio.Server(cors_allowed_origins="http://localhost:3000")
app = socketio.WSGIApp(sio)

port_manager = PortManager()

@sio.event
def connect(sid, environ):
    logging.info(f"Client {sid} connected to the main chat")

@sio.event
def open_chat(sid, data):
    logging.info(f"Message from {sid}: {data}")
    logging.info(port_manager.get_port_in_use())
    port = data.get('clientData').get('port')
    username = data.get('clientData').get('username')
    uuid = generate_uuid()

    if port_manager.is_port_in_use(port):
        sio.emit('chat_opened', {"message": f"Port {port} is already in use","username":username, "port":port, "uuid": uuid}, room=sid)
        return

    threading.Thread(target=start_group_chat, args=(port, port_manager), daemon=True).start()

    sio.emit('chat_opened', {"message": f"Group chat opened on port {port}","username":username, "port":port, "uuid": uuid}, room=sid)

@sio.event
def disconnect(sid):
    logging.info(f"Client {sid} disconnected from the main chat")

def generate_uuid():
    return uuid.uuid4().hex

if __name__ == '__main__':
    eventlet.wsgi.server(eventlet.listen(('localhost', 8000)), app)
