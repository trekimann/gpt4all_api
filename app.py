import os
from flask import Flask, request, jsonify
import ptvsd
from llm_api import LLM_API
from flask_cors import CORS


ptvsd.enable_attach(address=('0.0.0.0', 5678), redirect_output=True)
print("Waiting for debugger to attach...")
ptvsd.wait_for_attach()


app = Flask(__name__)

model_dir = './models'  # Replace with the path to your models directory
api = LLM_API(model_dir)

CORS(app)

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
        generated_text = api.generate_text(prompt, n_predict, n_threads)
        return jsonify({"generated_text": generated_text})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
