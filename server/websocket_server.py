import asyncio
import websockets
import json
import time
import logging
import requests 

class WebSocketServer:
    def __init__(self, port):
        self.PORT = port
        self.SERVER = None
        self.CLIENTS_BY_USERNAME = {}
        self.MESSAGES = {}

    async def send_to_all_messages(self):
        # Send the message to all clients
        if self.CLIENTS_BY_USERNAME:
            for client in self.CLIENTS_BY_USERNAME.values():
                client_timestamp = float(client[1])
                filtered_messages = []
                for message in self.MESSAGES.values():
                    if float(message["timestamp"]) > client_timestamp:
                        filtered_messages.append(message)
                await client[0].send(json.dumps({"type": "message", "messages": filtered_messages}))

    async def send_to_all_new_user(self, username, uuid):
        # notify all clients that a new user has connected
        logging.info(f"New user connected: {username}")
        logging.info(f"Clients connected: {self.CLIENTS_BY_USERNAME}")
        if self.CLIENTS_BY_USERNAME:
            tasks = [asyncio.create_task(client[0].send(json.dumps({"type": "notification", "uuid": uuid, "serverNotification": f"New client connected: {username}"}))) for client in self.CLIENTS_BY_USERNAME.values()]
            await asyncio.gather(*tasks)

    async def send_to_all_user_disconnect(self, username, uuid):
        # notify all clients that a user has disconnected
        logging.info(f"User disconnected: {username}")
        logging.info(f"Clients connected: {self.CLIENTS_BY_USERNAME}")
        if self.CLIENTS_BY_USERNAME:
            tasks = [asyncio.create_task(client[0].send(json.dumps({"type": "notification", "uuid": uuid, "serverNotification": f"User disconnected: {username}"}))) for client in self.CLIENTS_BY_USERNAME.values()]
            await asyncio.gather(*tasks)

    def check_and_close_server(self):
        # Check if there are no more clients and the server is not None
        if not self.CLIENTS_BY_USERNAME and self.SERVER is not None:
            logging.info("No clients connected. Closing the WebSocket server.")
            self.SERVER.close()

            self.send_http_request()

    def send_http_request(self):
        url = 'http://localhost:8000/remove_port/' + str(self.PORT)
        try:
            response = requests.post(url)
            if response.status_code == 200:
                logging.info(f"HTTP request to remove port {self.PORT} successful.")
            else:
                logging.warning(f"Failed to remove port {self.PORT}. HTTP status code: {response.status_code}")
        except requests.RequestException as e:
            logging.error(f"Failed to send HTTP request: {e}")

    async def handle_client(self, websocket, path):
        try:
            while True:
                message = await websocket.recv()
                logging.info(f"Received message from the client: {message}")
                message_json = json.loads(message)

                if message_json["type"] == "message":
                    timestamp = time.time()
                    message_json["timestamp"] = timestamp
                    self.MESSAGES[timestamp] = message_json
                    await self.send_to_all_messages()
                elif message_json["type"] == "connect":
                    timestamp = time.time()
                    self.CLIENTS_BY_USERNAME[message_json["uuid"]] = (websocket, timestamp)
                    await self.send_to_all_new_user(message_json["username"], message_json["uuid"])
                elif message_json["type"] == "disconnect":
                    self.CLIENTS_BY_USERNAME.pop(message_json["uuid"], None)
                    await self.send_to_all_user_disconnect(message_json["username"], message_json["uuid"])

                self.check_and_close_server()

        except websockets.ConnectionClosed:
            logging.info("Client disconnected.")
        finally:
            username = message_json.get("username")
            if username in self.CLIENTS_BY_USERNAME:
                self.CLIENTS_BY_USERNAME.pop(username, None)

            # Check and close the server if needed
            self.check_and_close_server()

    async def run_server(self):
        self.SERVER = await websockets.serve(self.handle_client, "localhost", self.PORT)
        logging.info(f"WebSocket server listening on ws://localhost:{self.PORT}")

        # Keep the server running
        await self.SERVER.wait_closed()

    def start(self):
        asyncio.run(self.run_server())
