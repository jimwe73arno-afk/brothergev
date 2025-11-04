import os, logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI

app = Flask(__name__)
CORS(app)
logging.basicConfig(level=logging.INFO)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

@app.get("/health")
def health():
    return jsonify({
        "status": "healthy",
        "ai_enabled": bool(OPENAI_API_KEY),
        "model": OPENAI_MODEL
    })

@app.route("/ask", methods=["POST", "GET"])
def ask():
    try:
        if request.method == "POST":
            data = request.get_json(force=True) or {}
            q = (data.get("q") or data.get("question") or "").strip()
        else:
            q = (request.args.get("q") or request.args.get("question") or "").strip()
        
        if not q:
            return jsonify({"error": "Question 'q' is required"}), 400
        
        if not client:
            return jsonify({"status": "error", "answer": "AI service configuring"}), 200
        
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {
                    "role": "system", 
                    "content": "You are a Tesla & EV decision expert. Answer in ENGLISH. Be concise and practical."
                },
                {
                    "role": "user", 
                    "content": q
                }
            ],
            temperature=0.3,
            max_tokens=400
        )
        
        answer = (response.choices[0].message.content or "").strip()
        return jsonify({
            "status": "success",
            "question": q,
            "answer": answer,
            "ai_used": True
        }), 200
        
    except Exception as e:
        logging.error("API error: %s", e)
        return jsonify({
            "status": "error",
            "answer": "System temporarily unavailable"
        }), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)
