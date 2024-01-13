import asyncio
import websockets
import json
import time
import logging
import requests  # Import the requests library

class WebSocketServer:
    def __init__(self, port):
        self.port = port
        self.server = None
        self.clients_by_username = {}
        self.messages = {}

    async def send_to_all_messages(self):
        if self.clients_by_username:
            for client in self.clients_by_username.values():
                client_timestamp = float(client[1])
                filtered_messages = []
                for message in self.messages.values():
                    if float(message["timestamp"]) > client_timestamp:
                        filtered_messages.append(message)
                await client[0].send(json.dumps({"type": "message", "messages": filtered_messages}))

    async def send_to_all_new_user(self, username, uuid):
        logging.info(f"New user connected: {username}")
        logging.info(f"Clients connected: {self.clients_by_username}")
        if self.clients_by_username:
            tasks = [asyncio.create_task(client[0].send(json.dumps({"type": "notification", "uuid": uuid, "serverNotification": f"New client connected: {username}"}))) for client in self.clients_by_username.values()]
            await asyncio.gather(*tasks)

    async def send_to_all_user_disconnect(self, username, uuid):
        logging.info(f"User disconnected: {username}")
        logging.info(f"Clients connected: {self.clients_by_username}")
        if self.clients_by_username:
            tasks = [asyncio.create_task(client[0].send(json.dumps({"type": "notification", "uuid": uuid, "serverNotification": f"User disconnected: {username}"}))) for client in self.clients_by_username.values()]
            await asyncio.gather(*tasks)

    def check_and_close_server(self):
        # Check if there are no more clients and the server is not None
        if not self.clients_by_username and self.server is not None:
            logging.info("No clients connected. Closing the WebSocket server.")
            self.server.close()

            # Send HTTP request to remove the port
            self.send_http_request()

    def send_http_request(self):
        # Replace the following URL with the appropriate endpoint to remove the port
        url = 'http://localhost:8000/remove_port/' + str(self.port)
        try:
            response = requests.post(url)
            if response.status_code == 200:
                logging.info(f"HTTP request to remove port {self.port} successful.")
            else:
                logging.warning(f"Failed to remove port {self.port}. HTTP status code: {response.status_code}")
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
                    self.messages[timestamp] = message_json
                    await self.send_to_all_messages()
                elif message_json["type"] == "connect":
                    timestamp = time.time()
                    self.clients_by_username[message_json["uuid"]] = (websocket, timestamp)
                    await self.send_to_all_new_user(message_json["username"], message_json["uuid"])
                elif message_json["type"] == "disconnect":
                    self.clients_by_username.pop(message_json["uuid"], None)
                    await self.send_to_all_user_disconnect(message_json["username"], message_json["uuid"])

                # Check and close the server if needed
                self.check_and_close_server()

        except websockets.ConnectionClosed:
            logging.info("Client disconnected.")
        finally:
            username = message_json.get("username")
            if username in self.clients_by_username:
                self.clients_by_username.pop(username, None)

            # Check and close the server if needed
            self.check_and_close_server()

    async def run_server(self):
        self.server = await websockets.serve(self.handle_client, "localhost", self.port)
        logging.info(f"WebSocket server listening on ws://localhost:{self.port}")

        # Keep the server running
        await self.server.wait_closed()

    def start(self):
        asyncio.run(self.run_server())
