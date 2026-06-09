# src/analytics_app/main.py

import os
import requests

from fastapi import FastAPI, HTTPException
from psycopg2 import connect
from psycopg2.extras import RealDictCursor


app = FastAPI(
    title="Analytics Service",
    version=os.getenv("SERVICE_VERSION", "1.0.0")
)

# ==================================================
# Environment Variables
# ==================================================

DB_HOST = os.getenv("DB_HOST", "analytics_db")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "analytics")
DB_USER = os.getenv("DB_USER", "analytics_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "analytics_password")

SERVICE_NAME = os.getenv("SERVICE_NAME", "analytics-api")
SERVICE_VERSION = os.getenv("SERVICE_VERSION", "1.0.0")

# External Services
IOT_SERVICE_URL = os.getenv(
    "IOT_SERVICE_URL",
    "http://iot-ingestion-b1:8000"
)

ACCESS_GATE_URL = os.getenv(
    "ACCESS_GATE_URL",
    "http://team-gate-api:8000"
)

CAMERA_SERVICE_URL = os.getenv(
    "CAMERA_SERVICE_URL",
    "TBD"
)

CORE_SERVICE_URL = os.getenv(
    "CORE_SERVICE_URL",
    "TBD"
)


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
# Health Check
# ==================================================

@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": SERVICE_NAME,
        "version": SERVICE_VERSION
    }


# ==================================================
# Analytics Endpoints
# ==================================================

@app.get("/analytics/summary")
def analytics_summary():

    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        SELECT
            COUNT(*) AS total_records,
            AVG(value) AS avg_value,
            MIN(value) AS min_value,
            MAX(value) AS max_value
        FROM sensor_readings
    """)

    result = cur.fetchone()

    cur.close()
    conn.close()

    return result


@app.get("/analytics/by-device")
def analytics_by_device():

    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        SELECT
            device_id,
            COUNT(*) AS total_readings
        FROM sensor_readings
        GROUP BY device_id
        ORDER BY total_readings DESC
    """)

    result = cur.fetchall()

    cur.close()
    conn.close()

    return {
        "items": result
    }


# ==================================================
# Integration Information
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

        response = requests.get(
            f"{IOT_SERVICE_URL}/health",
            timeout=5
        )

        return response.json()

    except Exception as e:

        raise HTTPException(
            status_code=503,
            detail=f"IoT service unavailable: {str(e)}"
        )


@app.post("/external/iot/mock-check")
def call_iot(payload: dict):

    try:

        response = requests.post(
            f"{IOT_SERVICE_URL}/telemetry/mock-check",
            json=payload,
            timeout=5
        )

        return response.json()

    except Exception as e:

        raise HTTPException(
            status_code=503,
            detail=f"Cannot connect to IoT service: {str(e)}"
        )


# ==================================================
# Access Gate Integration (B3)
# ==================================================

@app.get("/external/access/health")
def check_access_health():

    try:

        response = requests.get(
            f"{ACCESS_GATE_URL}/health",
            timeout=5
        )

        return response.json()

    except Exception as e:

        raise HTTPException(
            status_code=503,
            detail=f"Access Gate unavailable: {str(e)}"
        )


@app.post("/external/access/check")
def access_check(payload: dict):

    try:

        response = requests.post(
            f"{ACCESS_GATE_URL}/access/check",
            json=payload,
            timeout=5
        )

        return response.json()

    except Exception as e:

        raise HTTPException(
            status_code=503,
            detail=f"Cannot connect to Access Gate: {str(e)}"
        )

@app.get("/external/access/logs")
def access_logs():

    try:

        response = requests.get(
            f"{ACCESS_GATE_URL}/access/logs",
            timeout=5
        )

        return response.json()

    except Exception as e:

        raise HTTPException(
            status_code=503,
            detail=f"Cannot retrieve access logs: {str(e)}"
        )
# ==================================================
# Camera Stream Integration (Pending)
# ==================================================

@app.get("/external/camera/info")
def camera_info():

    return {
        "status": "pending",
        "message": "Waiting for Camera Stream contract",
        "service_url": CAMERA_SERVICE_URL
    }


# ==================================================
# Core Business Integration (Pending)
# ==================================================

@app.get("/external/core/info")
def core_info():

    return {
        "status": "pending",
        "message": "Waiting for Core Business contract",
        "service_url": CORE_SERVICE_URL
    }