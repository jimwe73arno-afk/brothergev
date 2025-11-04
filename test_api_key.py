import os
import google.generativeai as genai

api_key = "AIzaSyBU12YXDA4193bqQ6r5vP7rQ1WhKlVF8lU"

try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.0-pro')
    response = model.generate_content("Say hello in one word")
    print(f"✅ API 密钥有效！响应: {response.text}")
except Exception as e:
    print(f"❌ API 密钥无效或错误: {e}")
