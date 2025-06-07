FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app
RUN mkdir -p /app/app-frontend /app/app-frontend-version2 /app/app-service /app/lib-version
ARG APP_FRONTEND_DIR=app-frontend

RUN apt-get update && apt-get install -y \
    git \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app/app-service
COPY app-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app-service/ ./

WORKDIR /app/app-frontend
COPY app-frontend/package*.json ./
RUN npm install
COPY app-frontend/ ./
RUN npm run build

WORKDIR /app/app-frontend-version2
COPY app-frontend-version2/package*.json ./
RUN npm install
COPY app-frontend-version2/ ./
RUN npm run build

ENV MODEL_SERVICE_URL=http://model-service:8080 \
    PORT=3001

WORKDIR /app/app-service
EXPOSE ${PORT}
CMD ["python", "app-service.py"]
