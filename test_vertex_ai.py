from google.cloud import aiplatform
from google.oauth2 import service_account
import os

# 设置环境变量
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = ""  # 使用默认凭据

try:
    # 初始化 Vertex AI
    aiplatform.init(project="brothergev-mvp-477006", location="us-central1")
    
    # 列出可用模型
    models = aiplatform.Model.list()
    print("可用的 Vertex AI 模型:")
    for model in models:
        print(f"- {model.display_name} ({model.name})")
        
    # 测试文本生成
    from google.cloud.aiplatform_v1.types import content as content_types
    from google.cloud.aiplatform_v1.services.prediction_service import clients
    
    print("✅ Vertex AI 初始化成功")
    
except Exception as e:
    print(f"❌ Vertex AI 错误: {e}")
