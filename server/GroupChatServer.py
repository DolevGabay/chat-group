import socketio
import eventlet
import threading
from datetime import datetime
import logging
import uuid
from config import SOCKET_IO_CONFIG

def start_group_chat(port, port_manager):
    SIO = socketio.Server(**SOCKET_IO_CONFIG)
    GROUP_APP = socketio.WSGIApp(GROUP_SIO)

    port_manager.update_port_in_use(port)
    MESSAGES = []
    CLIENTS = []

    #handle client connection
    @GROUP_SIO.event
    def connect(sid, environ):
        logging.info(f"Client {sid} connected to the group chat on port {port}")

    #handle store new client data
    @GROUP_SIO.event
    def join(sid, uuid):
        TIMESTAMP = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        CLIENTS.append({'sid': sid, 'timestamp': TIMESTAMP, 'uuid': uuid})
        logging.info(f"Client {sid} joined the group chat on port {port} at {TIMESTAMP} with uuid {uuid}")
        logging.info(CLIENTS)  

    #handle broadcast messages
    @GROUP_SIO.event
    def message(sid, data):
        logging.info(f"Message from {sid}: {data}")
        TIMESTAMP = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data['timestamp'] = TIMESTAMP
        data['sid'] = sid
        MESSAGES.append(data)
        logging.info(MESSAGES)

        for client in CLIENTS:
            CLIENT_TIMESTAMP = client['timestamp']
            CLIENT_SID = client['sid']
            FILTERED_MESSAGES = [MSG for MSG in MESSAGES if MSG['timestamp'] > CLIENT_TIMESTAMP]
            GROUP_SIO.emit('messages', FILTERED_MESSAGES, room=CLIENT_SID)

    #handle notify all clients
    @GROUP_SIO.event
    def notify_all(sid, message):
        logging.info(f"Notify from {sid}: {message}")

        for CLIENT in CLIENTS:
            if CLIENT['sid'] == sid:
                continue
            GROUP_SIO.emit('notify', message, room=CLIENT['sid'])        

    #handle client disconnection
    @GROUP_SIO.event
    def disconnect(sid):
        logging.info(f"Client {sid} disconnected from the group chat on port {port}")
        
        CLIENT_TO_REMOVE = next((CLIENT for CLIENT in CLIENTS if CLIENT['sid'] == sid), None)
        
        if CLIENT_TO_REMOVE:
            CLIENTS.remove(CLIENT_TO_REMOVE)
            logging.info(CLIENTS)

    #start group chat server
    eventlet.wsgi.server(eventlet.listen(('localhost', int(port))), GROUP_APP)

def generate_uuid():
    return uuid.uuid4().hex
