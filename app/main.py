import os
import logging
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from pydantic_settings import BaseSettings
from minio import Minio
from minio.error import S3Error
import uvicorn
from typing import List
from io import BytesIO

# Settings using environment variables
class Settings(BaseSettings):
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_SECURE: bool = False
    BUCKET_NAME: str = "testbucket"
    CREATE_BUCKET_ON_START: bool = True

    class Config:
        env_file = ".env"

settings = Settings()

# Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("minio-fastapi-demo")

# MinIO client
client = Minio(
    settings.MINIO_ENDPOINT,
    access_key=settings.MINIO_ACCESS_KEY,
    secret_key=settings.MINIO_SECRET_KEY,
    secure=settings.MINIO_SECURE
)

app = FastAPI(title="MinIO FastAPI Demo")

@app.on_event("startup")
def startup_event():
    try:
        if settings.CREATE_BUCKET_ON_START:
            if not client.bucket_exists(settings.BUCKET_NAME):
                client.make_bucket(settings.BUCKET_NAME)
                logger.info(f"Created bucket: {settings.BUCKET_NAME}")
            else:
                logger.info(f"Bucket already exists: {settings.BUCKET_NAME}")
    except Exception as e:
        logger.exception("Failed to ensure bucket exists on startup")

@app.post("/upload", summary="Upload file to MinIO")
async def upload_file(file: UploadFile = File(...)):
    try:
        data = await file.read()
        client.put_object(
            bucket_name=settings.BUCKET_NAME,
            object_name=file.filename,
            data=BytesIO(data),
            length=len(data),
            content_type=file.content_type or "application/octet-stream"
        )
        logger.info(f"Uploaded: {file.filename}")
        return {"message": "uploaded", "object_name": file.filename}
    except S3Error as e:
        logger.exception("S3 error during upload")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.exception("Unknown error during upload")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/download/{object_name}", summary="Download object from MinIO")
def download_file(object_name: str):
    try:
        response = client.get_object(settings.BUCKET_NAME, object_name)
        data = response.read()
        response.close()
        response.release_conn()
        logger.info(f"Downloaded: {object_name}")
        return StreamingResponse(BytesIO(data), media_type="application/octet-stream", headers={"Content-Disposition": f"attachment; filename={object_name}"})
    except S3Error as e:
        logger.exception("S3 error during download")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.exception("Unknown error during download")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/list", summary="List objects in bucket")
def list_objects():
    try:
        objects = client.list_objects(settings.BUCKET_NAME)
        names = [obj.object_name for obj in objects]
        logger.info(f"Listed objects: {len(names)}")
        return {"objects": names}
    except Exception as e:
        logger.exception("Failed to list objects")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.environ.get("PORT", 8000)), reload=True)
