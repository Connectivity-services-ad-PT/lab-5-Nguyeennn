"""
Simple AI service mock for Lab 05 - Team Analytics Integration.
This service exposes two endpoints to pass the E2E Postman automated testing.
"""

import os
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

SERVICE_NAME = os.getenv("SERVICE_NAME", "ai-service")
SERVICE_VERSION = os.getenv("SERVICE_VERSION", "v0.1.0-team-analytics-ai")

app = FastAPI(
    title="FIT4110 Lab 05 - AI Service Mock",
    version=SERVICE_VERSION,
    description="Mock AI service used in Docker Compose stack for Team Analytics.",
)

class Prediction(BaseModel):
    objects: List[str]
    confidence: List[float]

@app.get("/health")
def health() -> dict:
    return {
        "status": "ok", 
        "service": SERVICE_NAME, 
        "version": SERVICE_VERSION
    }

@app.post("/predict", response_model=Prediction)
def predict() -> Prediction:
    # Trả về dữ liệu giả lập nhận diện vật thể để pass qua các kịch bản test Newman
    return Prediction(objects=["person", "bicycle"], confidence=[0.98, 0.85])

if __name__ == "__main__":
    import uvicorn
    # Lấy port từ biến môi trường, mặc định là 8000 để tối ưu cho mạng nội bộ Docker
    APP_PORT = int(os.getenv("APP_PORT", "8000"))
    APP_HOST = os.getenv("APP_HOST", "0.0.0.0")
    uvicorn.run(app, host=APP_HOST, port=APP_PORT)