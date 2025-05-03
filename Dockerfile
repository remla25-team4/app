FROM node:18-alpine
WORKDIR /app
RUN mkdir -p /app/app-frontend /app/app-service /app/lib-version

WORKDIR /app/app-service
COPY app-service/package*.json ./
RUN npm install
COPY app-service/ ./

WORKDIR /app/app-frontend
COPY app-frontend/package*.json ./
RUN npm install
COPY app-frontend/ ./
RUN npm run build

WORKDIR /app/lib-version
COPY lib-version/ ./

ENV MODEL_SERVICE_URL=http://model-service:8080

WORKDIR /app/app-service
EXPOSE 3001
CMD ["node", "index.js"]