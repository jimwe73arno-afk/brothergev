from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import logging

app = Flask(__name__)
CORS(app)
logging.basicConfig(level=logging.INFO)

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "EV AI Assistant",
        "version": "2.0"
    })

@app.route('/ask', methods=['POST', 'GET'])
def ask_question():
    try:
        if request.method == 'GET':
            question = request.args.get('q', '').strip()
        else:
            data = request.get_json() or {}
            question = data.get('q', '').strip()
        
        if not question:
            return jsonify({"error": "No question provided"}), 400
        
        # 简单回应（后续可集成AI）
        return jsonify({
            "question": question,
            "answer": f"Received your question: {question}. AI integration ready.",
            "status": "success"
        })
        
    except Exception as e:
        logging.error(f"Error: {e}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
