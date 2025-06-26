# Stage 1: Build the 'stable' React frontend
FROM node:20-alpine AS stable-frontend-builder
WORKDIR /app
COPY app-frontend/package*.json ./
RUN npm install
COPY app-frontend/ .
RUN npm run build

# Build the 'canary' React frontend
FROM node:20-alpine AS canary-frontend-builder
WORKDIR /app
COPY app-frontend-version2/package*.json ./
RUN npm install
COPY app-frontend-version2/ .
RUN npm run build

# Create the final Python production image
FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /app

# Copy Python requirements and install dependencies
COPY app-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Flask application source code
COPY app-service/ ./app-service

# Copy the built 'stable' frontend from Stage 1
COPY --from=stable-frontend-builder /app/dist ./app-frontend/dist

# Copy the built 'canary' frontend from Stage 2
COPY --from=canary-frontend-builder /app/dist ./app-frontend-version2/dist

# Set the final working directory
WORKDIR /app/app-service

# Expose the port and set the run command
EXPOSE 3001
CMD ["python", "app-service.py"]