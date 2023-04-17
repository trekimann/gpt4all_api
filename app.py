import os
import io
import sys
import threading
from flask import Flask, request, jsonify
from llm_api import LLM_API
from flask_cors import CORS
from flask_socketio import SocketIO

from gevent import pywsgi
from geventwebsocket.handler import WebSocketHandler

api_port = 5001
websocket_port = 5000

output_buffer = io.StringIO()
sys.stdout = output_buffer
sys.stderr = output_buffer

app = Flask(__name__)

model_dir = './models'  # Replace with the path to your models directory
api = LLM_API(model_dir)

CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", engineio_logger=True)

if os.environ.get('DEBUG_MODE') == 'True':
    import debugpy
    debugpy.listen(("0.0.0.0", 5678))
    print("Waiting for debugger to attach...")
    debugpy.wait_for_client()

def new_text_callback(text: str):
    print(text, end="", flush=True)
    socketio.emit('llm_output', text)

def list_models():
    return [f for f in os.listdir(model_dir) if f.endswith('.bin')]

@app.route('/models', methods=['GET'])
def get_models():
    models = list_models()
    models_with_index = [{"index": idx, "name": model} for idx, model in enumerate(models)]
    return jsonify({"models": models_with_index})

@app.route('/models', methods=['POST'])
def load_model():
    data = request.json
    model_idx = data.get('model_idx', -1)
    models = list_models()

    if 0 <= model_idx < len(models):
        api.load_model(os.path.join(model_dir, models[model_idx]))
        return jsonify({"message": f"Model '{models[model_idx]}' loaded"})
    else:
        return jsonify({"error": "Invalid model index"}), 400

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    prompt = data.get('prompt', '')
    n_predict = data.get('n_predict', 55)
    n_threads = data.get('n_threads', 8)

    try:
        generated_text = api.generate_text(prompt, n_predict, n_threads, new_text_callback=new_text_callback)
        return jsonify({"generated_text": generated_text})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@socketio.on('connect')
def handle_connect():
    print('Client connected:', request.sid)

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected:', request.sid)

def run_api_server():
    api_server = pywsgi.WSGIServer(('0.0.0.0', api_port), app)
    api_server.serve_forever()

if __name__ == '__main__':
    api_server_thread = threading.Thread(target=run_api_server)
    api_server_thread.start()

    print("Starting WebSocket server...")
    socketio.run(app, host='0.0.0.0', port=websocket_port, debug=False, use_reloader=False)
    print("WebSocket server stopped.")


