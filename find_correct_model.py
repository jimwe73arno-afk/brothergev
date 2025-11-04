import google.generativeai as genai

api_key = "AIzaSyBU12YXDA4193bqQ6r5vP7rQ1WhKlVF8lU"

try:
    genai.configure(api_key=api_key)
    
    # 列出可用的模型
    print("可用的模型:")
    for model in genai.list_models():
        if 'generateContent' in model.supported_generation_methods:
            print(f"- {model.name}")
    
    # 测试几个常见的模型
    test_models = [
        'gemini-1.5-flash',
        'gemini-1.5-pro',
        'gemini-pro',
        'models/gemini-1.5-flash',
        'models/gemini-1.5-pro'
    ]
    
    print("\n测试模型:")
    for model_name in test_models:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content("Say hello in one word")
            print(f"✅ {model_name}: {response.text.strip()}")
            break  # 找到第一个可用的模型
        except Exception as e:
            print(f"❌ {model_name}: {e}")
            
except Exception as e:
    print(f"配置错误: {e}")
