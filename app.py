import os
import json
from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS
from groq import Groq
from huggingface_hub import InferenceClient

app = Flask(__name__)
CORS(app)

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
hf_client = InferenceClient(
    api_key=os.getenv("HF_TOKEN")
)

@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Bhabagrahi welcomes you , hit /text for more!"})

@app.route("/models", methods=["GET"])
def list_models():
    provider = request.args.get('provider', 'groq')
    try:
        # models = client.models.list()
        if provider == "groq":
            models = groq_client.models.list()
        else:
            return jsonify({"error": "only grok available for now , for hf use url : https://huggingface.co/api/models"}), 400

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
    provider = data.get("provider", "groq")
    model = data.get("model","llama-3.1-8b-instant").strip()

    if not user_prompt:
        return jsonify({"status": "error", "message": "No prompt provided"}), 400

    try:
        # response = client.chat.completions.create(
        #     model="gemma2-2b-it",
        #     messages=[{"role": "user", "content": user_prompt}],
        #     max_tokens=400
        # )

        # response = client.chat.completions.create(
        #     model=model,
        #     messages=[{"role": "user", "content": user_prompt}],
        #     max_tokens=1024
        # )

        if provider == "groq":
            response = groq_client.chat.completions.create(
                model=model or "llama-3.1-8b-instant",
                messages=[{"role": "user", "content": user_prompt}],
                max_tokens=1024
            )
            output = response.choices[0].message.content

        elif provider == "hf":
            response = hf_client.chat.completions.create(
                model=model or "meta-llama/Llama-3.1-8B-Instruct",
                messages=[{"role": "user", "content": user_prompt}],
                max_tokens=1024
            )
            output = response.choices[0].message.content
        
        else:
            return jsonify({"error": "Invalid provider"}), 400

        return jsonify({
            "status": "success",
            "result": output
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/text-stream", methods=["POST"])
def text_gen_stream():
    data = request.get_json(silent=True) or {}
    user_prompt = data.get("prompt", "").strip()
    provider = data.get("provider", "groq")
    default_model = "llama-3.1-8b-instant" if provider == "groq" else "meta-llama/Llama-3.1-8B-Instruct"
    model_name = data.get("model", default_model).strip()

    if not user_prompt:
        return jsonify({"status": "error", "message": "No prompt provided"}), 400

    def generate():
        try:
            if provider == "groq":
                stream = groq_client.chat.completions.create(
                    model=model_name,
                    messages=[{"role": "user", "content": user_prompt}],
                    max_tokens=1024,
                    stream=True
                )
            elif provider == "hf":
                stream = hf_client.chat.completions.create(
                    model=model_name,
                    messages=[{"role": "user", "content": user_prompt}],
                    max_tokens=1024,
                    stream=True
                )
            else:
                yield f"data: {json.dumps({'error': 'Invalid provider'})}\n\n"
                return
            # stream = client.chat.completions.create(
            #     model=model,
            #     messages=[{"role": "user", "content": user_prompt}],
            #     max_tokens=1024,
            #     stream=True
            # )

            for chunk in stream:
                # Groq streaming gives delta content
                token = chunk.choices[0].delta.content or ""
                if token:
                    yield f"data: {json.dumps({'token': token})}\n\n"
                else:
                    # ✅ keep-alive ping to prevent Render/proxy timeout/buffering
                    yield ": ping\n\n"

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