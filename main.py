from flask import Flask, request, jsonify
import os
from openai import OpenAI

app = Flask(__name__)

# 从环境变量获取API密钥
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy", 
        "ai_ready": bool(OPENAI_API_KEY),
        "service": "EV AI Assistant"
    })

@app.route('/ask', methods=['POST'])
def ask():
    try:
        data = request.get_json() or {}
        question = data.get('q', '').strip()
        
        if not question:
            return jsonify({"error": "No question provided"}), 400
        
        if not client:
            return jsonify({
                "question": question,
                "answer": "AI service is configuring...",
                "status": "configuring"
            })
        
        # 调用 OpenAI
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a Tesla and EV expert."},
                {"role": "user", "content": question}
            ],
            max_tokens=500
        )
        
        answer = response.choices[0].message.content
        return jsonify({
            "question": question,
            "answer": answer,
            "status": "success",
            "ai_used": True
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
