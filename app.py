import os
from flask import Flask, request, jsonify, Response, stream_with_context
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
        # response = client.chat.completions.create(
        #     model="gemma2-2b-it",
        #     messages=[{"role": "user", "content": user_prompt}],
        #     max_tokens=400
        # )

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": user_prompt}],
            max_tokens=400
        )

        return jsonify({
            "status": "success",
            "result": response.choices[0].message.content
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/text-stream", methods=["POST"])
def text_gen_stream():
    data = request.get_json(silent=True) or {}
    user_prompt = data.get("prompt", "").strip()

    if not user_prompt:
        return jsonify({"status": "error", "message": "No prompt provided"}), 400

    def generate():
        try:
            stream = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": user_prompt}],
                max_tokens=400,
                stream=True
            )

            for chunk in stream:
                # Groq streaming gives delta content
                token = chunk.choices[0].delta.content or ""
                if token:
                    yield f"data: {json.dumps({'token': token})}\n\n"

            yield f"data: {json.dumps({'done': True})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"  # helps on nginx to not buffer
        }
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    app.run(host="0.0.0.0", port=port, threaded=True)