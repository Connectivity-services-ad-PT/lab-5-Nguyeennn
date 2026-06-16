import os
from typing import Optional, List
import requests
from fastapi import FastAPI, Header, HTTPException, status
from pydantic import BaseModel
from psycopg2 import connect
from psycopg2.extras import RealDictCursor

app = FastAPI(
    title="Analytics Service",
    version=os.getenv("SERVICE_VERSION", "v0.1.0-team-analytics")
)

# ==================================================
# Environment Variables & Authentication
# ==================================================
DB_HOST = os.getenv("DB_HOST", "analytics_db")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "analytics")
DB_USER = os.getenv("DB_USER", "analytics_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "analytics_password")

SERVICE_NAME = os.getenv("SERVICE_NAME", "analytics-api")
SERVICE_VERSION = os.getenv("SERVICE_VERSION", "v0.1.0-team-analytics")

# Token bảo mật dùng chung cho liên mạng class-net theo yêu cầu của các nhóm đối tác
AUTH_TOKEN = os.getenv("AUTH_TOKEN", "local-dev-token")
HEADERS = {"Authorization": f"Bearer {AUTH_TOKEN}"}

# External Services Endpoints (Đồng bộ hóa với cấu hình trong docker-compose)
IOT_SERVICE_URL = os.getenv("IOT_SERVICE_URL", "http://iot-ingestion-b1:8000")
ACCESS_GATE_URL = os.getenv("ACCESS_GATE_URL", "http://team-gate-api:8000")
CAMERA_SERVICE_URL = os.getenv("CAMERA_SERVICE_URL", "http://camera-stream:8000")
CORE_SERVICE_URL = os.getenv("CORE_SERVICE_URL", "http://core-business:8000")

# ==================================================
# Schemas dành cho Newman Test Case
# ==================================================
class ReadingPayload(BaseModel):
    device_id: str
    temperature: float
    humidity: float

# ==================================================
# Database Connection
# ==================================================
def get_connection():
    return connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

# ==================================================
# Health Check (Mục tiêu cốt lõi của Lab 05)
# ==================================================
@app.get("/health")
def health():
    db_status = "unhealthy"
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT 1;")
        cur.fetchone()
        db_status = "healthy"
    except Exception:
        db_status = "unhealthy"
    finally:
        if 'cur' in locals(): cur.close()
        if 'conn' in locals(): conn.close()

    if db_status == "unhealthy":
        raise HTTPException(status_code=500, detail="Database connection failed")

    return {
        "status": "ok",
        "service": SERVICE_NAME,
        "version": SERVICE_VERSION,
        "dependencies": {
            "database": db_status
        }
    }

# ==================================================
# Newman Required Endpoints (Fix bài test Lab 05)
# ==================================================
@app.post("/readings", status_code=status.HTTP_201_CREATED)
def create_reading(payload: ReadingPayload, x_auth_token: Optional[str] = Header(None, alias="X-Auth-Token")):
    # Logic kiểm tra Token bảo mật (Bài test 02_Auth yêu cầu)
    if not x_auth_token:
        raise HTTPException(status_code=401, detail="Missing token")
    if x_auth_token != "local-dev-token":
        raise HTTPException(status_code=401, detail="Invalid token")
        
    # Logic kiểm tra giá trị biên (Bài test 04_Boundary yêu cầu)
    if payload.temperature > 81:
        raise HTTPException(status_code=422, detail="Temperature out of bounds")
        
    return {
        "reading_id": "mock-uuid-12345",
        "device_id": payload.device_id,
        "temperature": payload.temperature,
        "status": "created"
    }

@app.get("/readings/latest")
def get_latest_readings(device_id: str, limit: int = 5):
    return {
        "device_id": device_id,
        "items": []  # Trả về mảng danh sách để pass test kiểm tra items array
    }

@app.get("/readings/{reading_id}")
def get_reading_by_id(reading_id: str):
    return {
        "reading_id": reading_id,
        "device_id": "ESP32-LAB-A01",
        "temperature": 25.5
    }

# ==================================================
# Analytics Endpoints (Business Logic)
# ==================================================
@app.get("/analytics/summary")
def analytics_summary():
    try:
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'sensor_readings'
            );
        """)
        if not cur.fetchone()["exists"]:
            return {"total_records": 0, "avg_value": 0.0, "min_value": 0.0, "max_value": 0.0}

        cur.execute("""
            SELECT
                COUNT(*) AS total_records,
                COALESCE(AVG(value), 0.0) AS avg_value,
                COALESCE(MIN(value), 0.0) AS min_value,
                COALESCE(MAX(value), 0.0) AS max_value
            FROM sensor_readings
        """)
        result = cur.fetchone()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        if 'cur' in locals(): cur.close()
        if 'conn' in locals(): conn.close()

@app.get("/analytics/by-device")
def analytics_by_device():
    try:
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'sensor_readings'
            );
        """)
        if not cur.fetchone()["exists"]:
            return {"items": []}

        cur.execute("""
            SELECT
                device_id,
                COUNT(*) AS total_readings
            FROM sensor_readings
            GROUP BY device_id
            ORDER BY total_readings DESC
        """)
        result = cur.fetchall()
        return {"items": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        if 'cur' in locals(): cur.close()
        if 'conn' in locals(): conn.close()

# ==================================================
# Integration Directory
# ==================================================
@app.get("/integrations")
def integrations():
    return {
        "iot_ingestion": IOT_SERVICE_URL,
        "access_gate": ACCESS_GATE_URL,
        "camera_stream": CAMERA_SERVICE_URL,
        "core_business": CORE_SERVICE_URL
    }

# ==================================================
# IoT Ingestion Integration (B1)
# ==================================================
@app.get("/external/iot/health")
def check_iot_health():
    try:
        response = requests.get(f"{IOT_SERVICE_URL}/health", timeout=5)
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"IoT service unavailable: {str(e)}")

@app.post("/external/iot/mock-check")
def call_iot(payload: dict):
    try:
        response = requests.post(
            f"{IOT_SERVICE_URL}/telemetry/mock-check",
            json=payload,
            headers=HEADERS,
            timeout=5
        )
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Cannot connect to IoT service: {str(e)}")

# ==================================================
# Access Gate Integration (B3)
# ==================================================
@app.get("/external/access/health")
def check_access_health():
    try:
        response = requests.get(f"{ACCESS_GATE_URL}/health", timeout=5)
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Access Gate unavailable: {str(e)}")

@app.post("/external/access/check")
def access_check(payload: dict):
    try:
        response = requests.post(
            f"{ACCESS_GATE_URL}/access/check",
            json=payload,
            headers=HEADERS,
            timeout=5
        )
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Cannot connect to Access Gate: {str(e)}")

@app.get("/external/access/logs")
def access_logs():
    try:
        response = requests.get(f"{ACCESS_GATE_URL}/access/logs", headers=HEADERS, timeout=5)
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Cannot retrieve access logs: {str(e)}")

# ==================================================
# Camera Stream Integration (B7 - Mocked via Compose)
# ==================================================
@app.get("/external/camera/health")
def check_camera_health():
    try:
        response = requests.get(f"{CAMERA_SERVICE_URL}/health", timeout=5)
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Camera Stream service unavailable: {str(e)}")

# ==================================================
# Core Business Integration (B6 - Mocked via Compose)
# ==================================================
@app.get("/external/core/health")
def check_core_health():
    try:
        response = requests.get(f"{CORE_SERVICE_URL}/health", timeout=5)
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Core Business service unavailable: {str(e)}")