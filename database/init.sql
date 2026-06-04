CREATE TABLE IF NOT EXISTS sensor_readings (
    id SERIAL PRIMARY KEY,

    reading_id VARCHAR(50) UNIQUE NOT NULL,

    device_id VARCHAR(100) NOT NULL,

    metric VARCHAR(50) NOT NULL,

    value DOUBLE PRECISION NOT NULL,

    unit VARCHAR(50),

    reading_timestamp TIMESTAMP NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_sensor_device
ON sensor_readings(device_id);

CREATE INDEX IF NOT EXISTS idx_sensor_metric
ON sensor_readings(metric);

CREATE INDEX IF NOT EXISTS idx_sensor_timestamp
ON sensor_readings(reading_timestamp);


CREATE TABLE IF NOT EXISTS analytics_cache (
    id SERIAL PRIMARY KEY,

    metric VARCHAR(50) NOT NULL,

    avg_value DOUBLE PRECISION,

    min_value DOUBLE PRECISION,

    max_value DOUBLE PRECISION,

    total_records INTEGER,

    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO sensor_readings (
    reading_id,
    device_id,
    metric,
    value,
    unit,
    reading_timestamp
)
VALUES
(
    'R-20260530-0001',
    'ESP32-LAB-A01',
    'temperature',
    28.5,
    'celsius',
    NOW()
),
(
    'R-20260530-0002',
    'ESP32-LAB-A01',
    'humidity',
    65.2,
    'percent',
    NOW()
),
(
    'R-20260530-0003',
    'ESP32-LAB-B01',
    'temperature',
    31.7,
    'celsius',
    NOW()
)
ON CONFLICT (reading_id) DO NOTHING;