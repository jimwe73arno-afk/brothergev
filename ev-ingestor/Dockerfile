# SOP v13.2 - Nhan MVP Cloud Pack
# 1. 基礎環境：使用官方 Python 乾淨環境
FROM python:3.12-slim

# 2. 設定環境變數
ENV PYTHONUNBUFFERED True

# 3. 設定雲端工作目錄
WORKDIR /app

# 4. 複製依賴包列表
COPY ev-ingestor/requirements.txt .

# 5. 安裝依賴包
RUN pip install --no-cache-dir -r requirements.txt

# 6. 複製 ev-ingestor 資料夾中的所有程式碼
COPY ev-ingestor/ /app/ev-ingestor/

# 7. 暴露雲端端口 (Cloud Run Job 也需要一個服務來接收 http 觸發)
EXPOSE 8080

# 8. 啟動 Ingestor 伺服器
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "1", "--threads", "8", "--timeout", "0", "ev-ingestor.main:app"]
