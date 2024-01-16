import socketio
import eventlet
import threading
import uuid
from datetime import datetime

# Create a new Socket.IO server for the main chat
sio = socketio.Server(cors_allowed_origins="http://localhost:3000")

# Wrap the Socket.IO server as a WSGI application
app = socketio.WSGIApp(sio)

PORT_IN_USE = []

# Define a handler for the 'connect' event on the main chat
@sio.event
def connect(sid, environ):
    print(f"Client {sid} connected to the main chat")

# Define a handler for the 'message' event on the main chat
@sio.event
def open_chat(sid, data):
    print(f"Message from {sid}: {data}")
    print(PORT_IN_USE)
    port = data.get('clientData').get('port')
    username = data.get('clientData').get('username')
    uuid = generate_uuid()

    if port in PORT_IN_USE:
        sio.emit('chat_opened', {"message": f"Port {port} is already in use","username":username, "port":port, "uuid": uuid}, room=sid)
        return

    # Start a group chat on the specified port
    threading.Thread(target=start_group_chat, args=(port,), daemon=True).start()

    sio.emit('chat_opened', {"message": f"Group chat opened on port {port}","username":username, "port":port, "uuid": uuid}, room=sid)

# Define a handler for the 'disconnect' event on the main chat
@sio.event
def disconnect(sid):
    print(f"Client {sid} disconnected from the main chat")

def start_group_chat(port):
    # Create a new Socket.IO server for the group chat with a custom namespace
    group_sio = socketio.Server(cors_allowed_origins="http://localhost:3000")

    # Wrap the Socket.IO server as a WSGI application
    group_app = socketio.WSGIApp(group_sio)  # Use a custom namespace

    PORT_IN_USE.append(port)

    MESSAGES = []
    CLIENTS = []

    # Define a handler for the 'connect' event on the group chat
    @group_sio.event
    def connect(sid, environ):
        print(f"Client {sid} connected to the group chat on port {port}")

    @group_sio.event
    def join(sid, uuid):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        CLIENTS.append({'sid': sid, 'timestamp': timestamp, 'uuid': uuid})
        print(f"Client {sid} joined the group chat on port {port} at {timestamp} with uuid {uuid}")
        print(CLIENTS)  

    # Define a handler for the 'message' event on the group chat
    @group_sio.event
    def message(sid, data):
        print(f"Message from {sid}: {data}")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data['timestamp'] = timestamp
        data['sid'] = sid
        MESSAGES.append(data)
        print(MESSAGES)

        for client in CLIENTS:
            client_timestamp = client['timestamp']
            client_sid = client['sid']
            filtered_messages = [msg for msg in MESSAGES if msg['timestamp'] > client_timestamp]
            group_sio.emit('messages', filtered_messages, room=client_sid)

    @group_sio.event
    def notify_all(sid, message):
        print(f"Notify from {sid}: {message}")

        for client in CLIENTS:
            if client['sid'] == sid:
                continue
            group_sio.emit('notify', message, room=client['sid'])        

    # Define a handler for the 'disconnect' event on the group chat
    @group_sio.event
    def disconnect(sid):
        print(f"Client {sid} disconnected from the group chat on port {port}")
        
        # Find the dictionary with matching 'sid'
        client_to_remove = next((client for client in CLIENTS if client['sid'] == sid), None)
        
        # Remove the dictionary from the list
        if client_to_remove:
            CLIENTS.remove(client_to_remove)
            print(CLIENTS)

    # Use eventlet to run the Socket.IO server for the group chat on the specified port
    eventlet.wsgi.server(eventlet.listen(('localhost', int(port))), group_app)


def generate_uuid():
    return uuid.uuid4().hex

if __name__ == '__main__':
    # Use eventlet to run the main Socket.IO server on port 8000
    eventlet.wsgi.server(eventlet.listen(('localhost', 8000)), app)
