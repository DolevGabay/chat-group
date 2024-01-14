import argparse
import threading
import logging
from flask import Flask, jsonify, request  
from websocket_server import WebSocketServer
from flask_cors import CORS  
import atexit
import asyncio
import time
from logging_config import configure_logging  

app = Flask(__name__)
CORS(app)  

# Logging configuration
configure_logging()

# Data structures to keep track of the WebSocket servers
PORTS_IN_USE = []
THREADS = []
WEBSOCKET_SERVERS = []

def start_websocket_server(port):
    # Start the WebSocket server
    websocket_server = WebSocketServer(port)
    websocket_thread = threading.Thread(target=websocket_server.start)
    websocket_thread.start()
    THREADS.append(websocket_thread)
    PORTS_IN_USE.append(port)
    WEBSOCKET_SERVERS.append(websocket_server)

def on_exit():
    # End all threads
    logging.info("Stopping all threads...")
    for thread in THREADS:
        thread.join(timeout=2)  
    logging.info("All threads stopped. exiting...")    

@app.route('/start_websocket_server/<int:port>', methods=['GET'])
def start_websocket_server_endpoint(port):
    # Check if the port is already in use if not start the WebSocket server
    if port in PORTS_IN_USE:
        return jsonify({"message": f"WebSocket server on port {port} is already running"})
    start_websocket_server(port)
    time.sleep(1)
    logging.info(f"Starting WebSocket server on port {port}")
    return jsonify({"message": f"WebSocket server started on port {port}"})  

@app.route('/remove_port/<int:port>', methods=['POST'])
def remove_port_endpoint(port):
    # Remove the port from PORTS_IN_USE
    if port not in PORTS_IN_USE:
        return jsonify({"message": f"WebSocket server on port {port} is not in use"})

    PORTS_IN_USE.remove(port)
    logging.info(f"WebSocket server on port {port} removed from PORTS_IN_USE")
    return jsonify({"message": f"WebSocket server on port {port} removed"})

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run a Flask application with WebSocket server threads.')
    parser.add_argument('flask_port', type=int, help='Port number for the Flask application')
    args = parser.parse_args()

    # End the threads when the program exits
    atexit.register(on_exit)

    # Run Flask app
    app.run(port=args.flask_port, threaded=True)
