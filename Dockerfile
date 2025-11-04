FROM python:3.11-slim
ENV APP_HOME=/app PORT=8080 PYTHONUNBUFFERED=1
WORKDIR $APP_HOME
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 main:app
