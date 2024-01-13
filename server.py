import argparse
import threading
import logging
from flask import Flask, jsonify, request  
from websocket_server import WebSocketServer
from flask_cors import CORS  
import atexit

app = Flask(__name__)
CORS(app)  

# Logging configuration
LOG_FILE = 'server.log'
LOG_LEVEL = logging.INFO

logging.basicConfig(filename=LOG_FILE, level=LOG_LEVEL)
console_handler = logging.StreamHandler()
console_handler.setLevel(LOG_LEVEL)
logging.getLogger().addHandler(console_handler)

#data structures to keep track of the WebSocket servers
ports_in_used = []
threads = []
websocket_servers = []

def start_websocket_server(port):
    websocket_server = WebSocketServer(port)
    websocket_thread = threading.Thread(target=websocket_server.start)
    websocket_thread.start()
    threads.append(websocket_thread)
    ports_in_used.append(port)
    websocket_servers.append(websocket_server)

def on_exit():
    logging.info("Stopping all threads...")
    for thread in threads:
        thread.join(timeout=2)  
    logging.info("All threads stopped. exiting...")    

@app.route('/start_websocket_server/<int:port>', methods=['GET'])
def start_websocket_server_endpoint(port):
    if port in ports_in_used:
        return jsonify({"message": f"WebSocket server on port {port} is already running"})
    start_websocket_server(port)
    logging.info(f"Starting WebSocket server on port {port}")
    return jsonify({"message": f"WebSocket server started on port {port}"})  

@app.route('/remove_port/<int:port>', methods=['POST'])
def remove_port_endpoint(port):
    if port not in ports_in_used:
        return jsonify({"message": f"WebSocket server on port {port} is not in use"})

    ports_in_used.remove(port)
    logging.info(f"WebSocket server on port {port} removed from ports_in_used")
    return jsonify({"message": f"WebSocket server on port {port} removed"})

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run a Flask application with WebSocket server threads.')
    parser.add_argument('flask_port', type=int, help='Port number for the Flask application')
    args = parser.parse_args()

    #End the threads when the program exits
    atexit.register(on_exit)

    # Run Flask app
    app.run(port=args.flask_port, threaded=True)
