import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq

app = Flask(__name__)
CORS(app)

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Bhabagrahi welcomes you , hit /text for more!"})

@app.route("/models", methods=["GET"])
def list_models():
    try:
        models = client.models.list()
        return jsonify({
            "status": "success",
            "models": [m.id for m in models.data]
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/text", methods=["POST"])
def text_gen():
    data = request.get_json(silent=True) or {}
    user_prompt = data.get("prompt", "").strip()

    if not user_prompt:
        return jsonify({"status": "error", "message": "No prompt provided"}), 400

    try:
        response = client.chat.completions.create(
            model="gemma2-2b-it",
            messages=[{"role": "user", "content": user_prompt}],
            max_tokens=400
        )

        return jsonify({
            "status": "success",
            "result": response.choices[0].message.content
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    app.run(host="0.0.0.0", port=port)