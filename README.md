# MinIO FastAPI Demo

This project provides a full example showcasing:

- Python FastAPI application that uploads, lists and downloads objects to MinIO
- Environment-based configuration
- Structured logging
- Dockerfile for the app
- docker-compose to run MinIO + app locally
- Kubernetes manifests for deploying the app (and optional MinIO)

## Features

- `POST /upload` : upload file via multipart/form-data
- `GET /list` : list objects in the configured bucket
- `GET /download/{object_name}` : download an object

## Quickstart (local, using Docker)

1. Build & start services:

```bash
docker-compose up --build
```

2. Open API docs:

- FastAPI docs: http://localhost:8000/docs
- MinIO console: http://localhost:9001 (user: minioadmin / pass: minioadmin)

3. Example upload using curl:

```bash
curl -F "file=@./example.txt" http://localhost:8000/upload
```

4. List objects:

```bash
curl http://localhost:8000/list
```

5. Download:

```bash
curl -O http://localhost:8000/download/example.txt
```

## Running locally without Docker

1. Install Python deps:

```bash
pip install -r requirements.txt
```

2. Start MinIO (see earlier instructions) and update `.env` accordingly.

3. Run the app:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Deploying to Kubernetes (Docker Desktop)

These instructions are for **Docker Desktop** users deploying the FastAPI app to Kubernetes:

1. **Build the Docker image locally:**

```bash
docker build -t minio-fastapi-demo:latest .
```

2. **Tag the image (optional, if not already tagged):**

```bash
docker tag minio-fastapi-demo:latest minio-fastapi-demo:latest
```

3. **Ensure Docker Desktop is using the same Docker engine for Kubernetes:**

- By default, Docker Desktop shares images between Docker and its Kubernetes cluster.

4. **Set `imagePullPolicy: IfNotPresent` in your Kubernetes deployment YAML** (this is usually the default for `:latest` images):

- This ensures Kubernetes will use the local image if available.

5. **Apply the Kubernetes manifests:**

```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/secret-minio.yaml -n minio-demo
kubectl apply -f k8s/minio-deployment.yaml -n minio-demo
kubectl apply -f k8s/minio-service.yaml -n minio-demo
kubectl apply -f k8s/deployment.yaml -n minio-demo
kubectl apply -f k8s/service.yaml -n minio-demo
```

6. **Check pod status and logs:**

```bash
kubectl get pods -n minio-demo
kubectl logs <pod-name> -n minio-demo
```

7. **Port-forward to access services:**

```bash
kubectl port-forward deployment/minio-fastapi 8000:8000 -n minio-demo
kubectl port-forward deployment/minio 9001:9001 -n minio-demo
```

- FastAPI: http://localhost:8000
- MinIO Console: http://localhost:9001

**Note:** If you see an `ImagePullBackOff` error, ensure the image is built and available locally, and that you're using Docker Desktop (not a remote cluster).

## Kubernetes manifests

The `k8s/` folder contains:

- `namespace.yaml` : namespace `minio-demo`
- `secret-minio.yaml` : credentials for MinIO (base64 encoded)
- `deployment.yaml` : Deployment for the FastAPI app
- `service.yaml` : ClusterIP service exposing the app
- `minio-deployment.yaml` (optional) : MinIO deployment for testing in-cluster
- `minio-service.yaml` (optional) : Service for MinIO

```

Notes:

- The Kubernetes manifests use a Kubernetes Secret for MinIO credentials. Edit as needed.
- For production, configure proper storage class / persistent volumes for MinIO.

## Files in this repository

- `app/main.py` : FastAPI application
- `requirements.txt`
- `Dockerfile`
- `docker-compose.yml`
- `.env.example`
- `k8s/` : Kubernetes manifests
- `README.md`
```
