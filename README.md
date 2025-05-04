# App

A React frontend-app that is served by an express server via a simple REST api.

---

## Run with Docker

### 1. Build the image

```bash
docker build -t app-image .
```

### 2. Run the container

```bash
docker run -p 3001:3001 -e MODEL_SERVICE_URL=http://localhost:8080 app-image
```
Note: you have to run the model service container.
---