import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from huggingface_hub import InferenceClient

app = Flask(__name__)
CORS(app)

token = os.getenv("HF_TOKEN")
if not token:
    raise RuntimeError("HF_TOKEN environment variable is missing")

client = InferenceClient(token=token, provider="hf-inference")
print("HF_TOKEN Loaded: YES")

@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Bhabagrahi welcomes you , hit /text for more!"})

@app.route("/text", methods=["POST"])
def text_gen():
    data = request.get_json(silent=True) or {}
    user_prompt = data.get("prompt", "").strip()

    if not user_prompt:
        return jsonify({"status": "error", "message": "No prompt provided"}), 400

    try:
        response = client.chat.completions.create(
            model="google/gemma-2-2b-it",
            messages=[{"role": "user", "content": user_prompt}],
            max_tokens=500
        )

        answer = response.choices[0].message.content
        return jsonify({"status": "success", "result": answer})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/image", methods=["POST"])
def image_gen():
    return jsonify({
        "status": "success",
        "message": "Coming Soon",
        "note": "This endpoint will eventually generate AI images."
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    app.run(host="0.0.0.0", port=port)