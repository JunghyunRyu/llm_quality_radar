FROM python:3.11-slim

# Node.js 20 설치
RUN apt-get update && apt-get install -y curl gnupg git && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app

# Python deps
RUN pip install --no-cache-dir -r requirements.txt

# Node deps (optional). npx로 @playwright/mcp 실행 예정
RUN npm install -g npm@latest

# 컨테이너 포트 공개 (FastAPI, MCP 3001)
EXPOSE 8001 3001

# FastAPI + 공식 Playwright MCP 동시 기동 (포트 3001)
CMD sh -c "npx @playwright/mcp --port 3001 --headless & \
           uvicorn apps.auto_test_api:AutoTestAPI().app --host 0.0.0.0 --port 8001"


