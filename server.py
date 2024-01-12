import asyncio
import websockets
import json
import time
import logging

# Configure logging to both console and file
logging.basicConfig(filename='server.log', level=logging.INFO)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
logging.getLogger().addHandler(console_handler)

clients_by_username = {}
messages = []

async def send_to_all_messages():
    # send all messages to all clients
    if clients_by_username:
        for client in clients_by_username.values():
            client_timestamp = float(client[1])  
            filtered_messages = []
            for message in messages:
                if float(message["timestamp"]) > client_timestamp:
                    filtered_messages.append(message)   
            await client[0].send(json.dumps({"type": "message", "messages": filtered_messages}))

async def send_to_all_new_user(username):
    # notiffy all users that new user is connected
    logging.info(f"New user connected: {username}")
    logging.info(f"clients_by_username: {clients_by_username}")
    if clients_by_username:
        tasks = [asyncio.create_task(client[0].send(json.dumps({"type": "notification", "username": username, "serverNotification": f"New client connected: {username}"}))) for client in clients_by_username.values()]
        await asyncio.gather(*tasks)

async def send_to_all_user_disconnect(username):
    # notiffy all users that user has disconnected
    logging.info(f"User disconnected: {username}")
    logging.info(f"clients_by_username: {clients_by_username}")
    if clients_by_username:
        tasks = [asyncio.create_task(client[0].send(json.dumps({"type": "notification", "username": username, "serverNotification": f"user is disconnected: {username}"}))) for client in clients_by_username.values()]
        await asyncio.gather(*tasks)

async def handle_client(websocket, path):
    try:
        while True:
            # Wait for a message from the client
            message = await websocket.recv()
            logging.info(f"Received message from the client: {message}")  # Log to file and console
            message_json = json.loads(message)
            if message_json["type"] == "message":
                timestamp = time.time()
                message_json["timestamp"] = timestamp
                messages.append(message_json)
                await send_to_all_messages()
            elif message_json["type"] == "connect":
                timestamp = time.time()
                clients_by_username[message_json["username"]] = (websocket, timestamp)
                await send_to_all_new_user(message_json["username"])
            elif message_json["type"] == "disconnect":
                clients_by_username.pop(message_json["username"], None)
                await send_to_all_user_disconnect(message_json["username"])
    except websockets.ConnectionClosed:
        print("Client disconnected.")
    finally:
        # Remove the client from the dictionary and close the connection
        username = message_json.get("username")
        if username in clients_by_username:
            clients_by_username.pop(username, None)
        if not websocket.closed:
            await websocket.close()
            logging.info(f"Closed connection with {username}")

# Set up the WebSocket server
async def run_server(port):
    server = await websockets.serve(handle_client, "localhost", port)
    logging.info(f"WebSocket server listening on ws://localhost:{port}")

    # Keep the server running
    await server.wait_closed()

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Run a WebSocket server with a specified port.')
    parser.add_argument('port', type=int, help='Port number for the WebSocket server')
    args = parser.parse_args()

    asyncio.run(run_server(args.port))
