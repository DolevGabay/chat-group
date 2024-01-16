import socketio
import eventlet
import threading
from datetime import datetime
import logging
import uuid

def start_group_chat(port, port_manager):
    group_sio = socketio.Server(cors_allowed_origins="http://localhost:3000")
    group_app = socketio.WSGIApp(group_sio)

    port_manager.update_port_in_use(port)
    MESSAGES = []
    CLIENTS = []

    @group_sio.event
    def connect(sid, environ):
        logging.info(f"Client {sid} connected to the group chat on port {port}")

    @group_sio.event
    def join(sid, uuid):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        CLIENTS.append({'sid': sid, 'timestamp': timestamp, 'uuid': uuid})
        logging.info(f"Client {sid} joined the group chat on port {port} at {timestamp} with uuid {uuid}")
        logging.info(CLIENTS)  

    @group_sio.event
    def message(sid, data):
        logging.info(f"Message from {sid}: {data}")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data['timestamp'] = timestamp
        data['sid'] = sid
        MESSAGES.append(data)
        logging.info(MESSAGES)

        for client in CLIENTS:
            client_timestamp = client['timestamp']
            client_sid = client['sid']
            filtered_messages = [msg for msg in MESSAGES if msg['timestamp'] > client_timestamp]
            group_sio.emit('messages', filtered_messages, room=client_sid)

    @group_sio.event
    def notify_all(sid, message):
        logging.info(f"Notify from {sid}: {message}")

        for client in CLIENTS:
            if client['sid'] == sid:
                continue
            group_sio.emit('notify', message, room=client['sid'])        

    @group_sio.event
    def disconnect(sid):
        logging.info(f"Client {sid} disconnected from the group chat on port {port}")
        
        client_to_remove = next((client for client in CLIENTS if client['sid'] == sid), None)
        
        if client_to_remove:
            CLIENTS.remove(client_to_remove)
            logging.info(CLIENTS)

    eventlet.wsgi.server(eventlet.listen(('localhost', int(port))), group_app)

def generate_uuid():
    return uuid.uuid4().hex
