import asyncio
import websockets
import json
import time
import logging
import threading
import argparse

# Logging configuration
LOG_FILE = 'server.log'
LOG_LEVEL = logging.INFO

logging.basicConfig(filename=LOG_FILE, level=LOG_LEVEL)
console_handler = logging.StreamHandler()
console_handler.setLevel(LOG_LEVEL)
logging.getLogger().addHandler(console_handler)

#data structure to store the clients and messages
CLIENTS_BY_USERNAME = {}
MESSAGES = []

async def send_to_all_messages():
    # Send the messages to all clients
    if CLIENTS_BY_USERNAME:
        for client in CLIENTS_BY_USERNAME.values():
            client_timestamp = float(client[1])
            filtered_messages = []
            for message in MESSAGES:
                if float(message["timestamp"]) > client_timestamp:
                    filtered_messages.append(message)
            await client[0].send(json.dumps({"type": "message", "messages": filtered_messages}))

async def send_to_all_new_user(username):
    # Send that a new user has connected to all clients
    logging.info(f"New user connected: {username}")
    logging.info(f"CLIENTS_BY_USERNAME: {CLIENTS_BY_USERNAME}")
    if CLIENTS_BY_USERNAME:
        tasks = [asyncio.create_task(client[0].send(json.dumps({"type": "notification", "username": username, "serverNotification": f"New client connected: {username}"}))) for client in CLIENTS_BY_USERNAME.values()]
        await asyncio.gather(*tasks)

async def send_to_all_user_disconnect(username):
    # Send that a user has disconnected to all clients
    logging.info(f"User disconnected: {username}")
    logging.info(f"CLIENTS_BY_USERNAME: {CLIENTS_BY_USERNAME}")
    if CLIENTS_BY_USERNAME:
        tasks = [asyncio.create_task(client[0].send(json.dumps({"type": "notification", "username": username, "serverNotification": f"user is disconnected: {username}"}))) for client in CLIENTS_BY_USERNAME.values()]
        await asyncio.gather(*tasks)

async def handle_client(websocket, path):
    try:
        while True:
            message = await websocket.recv()
            logging.info(f"Received message from the client: {message}")
            message_json = json.loads(message)
            
            if message_json["type"] == "message":
                timestamp = time.time()
                message_json["timestamp"] = timestamp
                MESSAGES.append(message_json)
                await send_to_all_messages()
            elif message_json["type"] == "connect":
                timestamp = time.time()
                CLIENTS_BY_USERNAME[message_json["username"]] = (websocket, timestamp)
                await send_to_all_new_user(message_json["username"])
            elif message_json["type"] == "disconnect":
                CLIENTS_BY_USERNAME.pop(message_json["username"], None)
                await send_to_all_user_disconnect(message_json["username"])
    except websockets.ConnectionClosed:
        logging.info(f"Client disconnected.")
    finally:
        username = message_json.get("username")
        if username in CLIENTS_BY_USERNAME:
            CLIENTS_BY_USERNAME.pop(username, None)
        if not websocket.closed:
            await websocket.close()
            logging.info(f"Closed connection with {username}")

async def run_server(port):
    server = await websockets.serve(handle_client, "localhost", port)
    logging.info(f"WebSocket server listening on ws://localhost:{port}")

    # Keep the server running
    await server.wait_closed()

def run_websocket_server(port):
    asyncio.run(run_server(port))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run a WebSocket server with a specified port.')
    parser.add_argument('port', type=int, help='Port number for the WebSocket server')
    args = parser.parse_args()

    # Start the WebSocket server in a separate thread
    websocket_thread = threading.Thread(target=run_websocket_server, args=(args.port,))
    websocket_thread.start()

    try:
        # Wait for the thread to finish, but allow KeyboardInterrupt 
        websocket_thread.join()
    except KeyboardInterrupt:
        # Handle Ctrl+C 
        logging.info("WebSocket server interrupted. Closing connections...")
    finally:
        logging.info("WebSocket server thread joined. Exiting.")



