from flask import Flask, request, jsonify
import os
import logging
import google.generativeai as genai

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# 从环境变量读取配置
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

logger.info(f"Gemini Model: {GEMINI_MODEL}")
logger.info(f"Gemini API Key configured: {bool(GEMINI_API_KEY)}")

# 配置 Gemini
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

def call_gemini(question):
    """调用 Gemini API"""
    if not GEMINI_API_KEY:
        logger.error("No Gemini API key available")
        return None
    
    try:
        logger.info(f"Calling Gemini API with question: {question[:100]}...")
        
        # 创建模型实例
        model = genai.GenerativeModel(GEMINI_MODEL)
        
        # 构建针对电动汽车领域的专业提示
        prompt = f"""你是一个专业的电动汽车和充电专家。请用中文专业、准确地回答以下问题：

问题：{question}

请提供：
1. 专业准确的答案
2. 相关技术细节（如适用）
3. 实用的建议（如适用）

请确保回答专业、准确且易于理解："""
        
        # 调用 API
        response = model.generate_content(prompt)
        
        if response and response.text:
            logger.info("Gemini API call successful")
            return response.text
        else:
            logger.error("Gemini API returned empty response")
            return None
            
    except Exception as e:
        logger.error(f"Gemini API call failed: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        return None

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy", 
        "api_key_configured": bool(GEMINI_API_KEY),
        "model": GEMINI_MODEL,
        "provider": "gemini"
    })

@app.route('/ask', methods=['POST'])
def ask():
    try:
        data = request.get_json() or {}
        question = data.get('q', '').strip()
        
        if not question:
            return jsonify({"status": "error", "answer": "请提供问题"}), 400
        
        logger.info(f"Received question: {question}")
        
        # 调用 Gemini
        answer = call_gemini(question)
        if answer:
            return jsonify({
                "status": "success", 
                "answer": answer,
                "provider": "gemini",
                "model": GEMINI_MODEL
            })
        else:
            return jsonify({"status": "error", "answer": "无法获取 AI 响应，请检查 API Key 和服务配置"}), 500
    
    except Exception as e:
        logger.error(f"Error in /ask: {str(e)}")
        return jsonify({"status": "error", "answer": f"服务器错误: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
