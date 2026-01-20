import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from huggingface_hub import InferenceClient

app = Flask(__name__)
CORS(app)

# 1. Setup Token and Client
token = os.getenv("HF_TOKEN") 
# Explicitly use the hf-inference provider for stability
client = InferenceClient(api_key=token)

@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "Bhabagrahi welcomes you , hit /text for more!"})

# Renamed endpoint for text generation
@app.route('/text', methods=['POST'])
def text_gen():
    data = request.json
    user_prompt = data.get("prompt", "")
    
    if not user_prompt:
        return jsonify({"status": "error", "message": "No prompt provided"}), 400
    
    try:
        # Using Phi-3 for guaranteed free-tier stability
        print("HF_TOKEN Loaded:", "YES" if token else "NO")
        response = client.chat.completions.create(
            model="google/gemma-2-2b-it", 
            messages=[{"role": "user", "content": user_prompt}],
            max_tokens=500
        )
        
        answer = response.choices[0].message.content
        return jsonify({"status": "success", "result": answer})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# New placeholder endpoint for image generation
@app.route('/image', methods=['POST'])
def image_gen():
    return jsonify({
        "status": "success", 
        "message": "Coming Soon",
        "note": "This endpoint will eventually generate AI images."
    })

if __name__ == "__main__":
    # For GCP Cloud Run, we use the PORT env var; for local/HF, we default to 7860
    port = int(os.environ.get("PORT", 7860))
    app.run(host='0.0.0.0', port=port)