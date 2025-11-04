import google.generativeai as genai

api_key = "AIzaSyBU12YXDA4193bqQ6r5vP7rQ1WhKlVF8lU"

try:
    print("测试 Gemini API 密钥...")
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.0-pro')
    response = model.generate_content("Say hello in one word")
    print(f"✅ API 密钥有效！响应: {response.text}")
except Exception as e:
    print(f"❌ API 密钥错误: {e}")
    print("请检查：")
    print("1. API 密钥是否正确")
    print("2. 是否在 Google AI Studio 中启用了 API")
    print("3. 项目是否有有效的账单账户")
