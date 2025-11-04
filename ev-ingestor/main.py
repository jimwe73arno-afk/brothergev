# SOP v13.2 - Nanshan MVP Cloud Pack
# 檔案: ev-ingestor/main.py (自動數據抓取器)

import os
import json
import praw # Reddit API
from fastapi import FastAPI, HTTPException, Request
from google.cloud import storage, secretmanager

# --- 1. 讀取環境變數 (由 Cloud Run UI 設定) ---
PROJECT_ID = os.environ.get("PROJECT_ID")
BUCKET_NAME = os.environ.get("BUCKET_NAME")
SCRAPED_FILE_NAME = "external_snippets.jsonl"
REDDIT_USER_AGENT = "BrotherG_Fetcher_v1.0"

# --- 2. 初始化 FastAPI 和雲端武器 ---
app = FastAPI()
storage_client = storage.Client(project=PROJECT_ID)
secret_client = secretmanager.SecretManagerServiceClient()

# --- 3. 核心輔助函數 ---

def get_secret(secret_id):
    """從 Secret Manager 安全地讀取金鑰"""
    try:
        name = f"projects/{PROJECT_ID}/secrets/{secret_id}/versions/latest"
        response = secret_client.access_secret_version(request={"name": name})
        return response.payload.data.decode("UTF-8")
    except Exception as e:
        print(f"Error fetching secret {secret_id}: {e}")
        # 在 Job 模式下，如果拿不到 Key，就必須失敗
        raise HTTPException(status_code=500, detail=f"Could not fetch secret: {secret_id}")

def fetch_from_reddit(subreddits: str, limit: int):
    """
    SOP v13.1: 連接 Reddit 抓取數據
    """
    print("Fetching secrets for Reddit...")
    client_id = get_secret("reddit_client_id")
    client_secret = get_secret("reddit_client_secret")
    
    reddit = praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        user_agent=REDDIT_USER_AGENT,
    )
    
    print(f"Connecting to Reddit... Fetching from {subreddits}")
    # PRAW 允許用 "+" 來合併多個 subreddits
    subreddit_list = subreddits.replace(",", "+")
    subreddit = reddit.subreddit(subreddit_list)
    
    results = []
    # 抓取 "hot" (熱門) 的文章
    for submission in subreddit.hot(limit=limit * 2): # 多抓一點以防過濾掉
        if results:
            break
        if not submission.stickied and submission.selftext: # 跳過置頂文 & 必須有內文
            print(f"Fetching [Reddit]: {submission.title}")
            snippet = {
                "id": f"reddit-{submission.id}",
                "source": "reddit",
                "market": "US", # 暫時都標記為 US
                "tags": [submission.subreddit.display_name, "hot"],
                "q": submission.title,
                "a": submission.selftext[:500], # 只取前 500 字
                "ts": int(submission.created_utc)
            }
            results.append(snippet)
            
    print(f"Fetched {len(results)} snippets from Reddit.")
    return results

def store_to_gcs(snippets: list):
    """
    SOP v13.1: 實現數據「雙向通用」
    將抓取的數據存入 GCS 雲端倉庫
    """
    if not snippets:
        print("No snippets to store.")
        return 0
        
    try:
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(SCRAPED_FILE_NAME)
        
        # 將 snippets 轉為 jsonl 格式 (一行一個 json)
        data_to_upload = "\n".join([json.dumps(r) for r in snippets])
        
        blob.upload_from_string(data_to_upload, content_type="application/jsonl")
        print(f"Successfully uploaded {len(snippets)} snippets to gs://{BUCKET_NAME}/{SCRAPED_FILE_NAME}")
        return len(snippets)
    except Exception as e:
        print(f"Error uploading to GCS: {e}")
        raise HTTPException(status_code=500, detail="Failed to upload data to GCS")

# --- 4. API 端口定義 ---

@app.get("/healthz", tags=["Monitoring"])
async def health_check():
    """
    健康檢查 (GPT 用的 `healthz` 是 GCP 標準，很好)
    """
    return {"status": "ok", "service": "ev-ingestor"}

@app.get("/ingest/reddit", tags=["Ingestion"])
async def ingest_reddit(
    request: Request,
    subs: str = "TeslaMotors,ModelY,electricvehicles", # 預設的 subreddits
    limit: int = 50 # 預設抓 50 條
):
    """
    SOP v13.1: 雲端抓取 (Cloud Scheduler 會調用這個端口)
    """
    print(f"Ingest job triggered for Reddit. Subs: {subs}, Limit: {limit}")
    
    # 驗證是否為 Cloud Scheduler 的調用 (增加安全性)
    # 這裡我們先簡化，允許手動觸發
    
    try:
        # 1. 抓取
        snippets = fetch_from_reddit(subreddits=subs, limit=limit)
        
        # 2. 儲存
        count = store_to_gcs(snippets)
        
        # 3. (可選) 自動觸發 ev-api 的 /ingest
        # 這裡我們先不自動觸發，由 Cloud Scheduler 分兩步調用
        
        return {"status": "success", "fetched_count": count}
        
    except Exception as e:
        print(f"Ingestion failed: {e}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))
