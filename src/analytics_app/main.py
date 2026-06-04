# src/analytics_app/main.py

import os
from fastapi import FastAPI
from psycopg2 import connect
from psycopg2.extras import RealDictCursor

app = FastAPI(
    title="Analytics Service",
    version="1.0.0"
)

DB_HOST = os.getenv("DB_HOST", "analytics_db")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "analytics")
DB_USER = os.getenv("DB_USER", "analytics_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "analytics_password")


def get_connection():
    return connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "analytics-api"
    }


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