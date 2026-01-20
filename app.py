import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from huggingface_hub import InferenceClient

app = Flask(__name__)
CORS(app)

# 1. Pull the token from your Secrets
token = os.getenv("HF_TOKEN") 

# 2. Use the standard InferenceClient
# We do NOT pass a model URL here anymore to avoid the 410 error
client = InferenceClient(api_key=token)

@app.route('/', methods=['GET'])
def greet_json():
    return {"message": "Bhabagrahi Welcomes you! API is Live."}

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    user_prompt = data.get("prompt", "")
    
    if not user_prompt:
        return jsonify({"status": "error", "message": "No prompt provided"}), 400

    try:
        # 3. THE MAGIC FIX: Append ':hf-inference' to the model name
        # This forces the free Hugging Face provider and skips paid ones like Nebius
        response = client.chat.completions.create(
            model="google/gemma-2-2b-it:hf-inference", 
            messages=[{"role": "user", "content": user_prompt}],
            max_tokens=500
        )
        
        answer = response.choices[0].message.content
        return jsonify({"status": "success", "result": answer})

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=7860)