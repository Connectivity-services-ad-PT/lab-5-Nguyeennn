# Analytics Team Integration Contract (B5)

## Thông tin chung

| Hạng mục           | Thông tin      |
| ------------------ | -------------- |
| Nhóm               | B5 – Analytics |
| Service name       | analytics-api  |
| Version            | 1.0.0          |
| Container port     | 8000           |
| Database           | PostgreSQL     |
| Docker healthcheck | Có             |
| OpenAPI version    | 3.0.3          |

---

# Vai trò của Analytics

Analytics Service chịu trách nhiệm:

* Tổng hợp dữ liệu đã được lưu trong PostgreSQL.
* Sinh các thống kê phục vụ Dashboard.
* Thực hiện kiểm tra khả năng kết nối tới các service khác.
* Cung cấp các endpoint phục vụ tích hợp liên nhóm.

---

# API nội bộ của Analytics

## Health Check

### Request

GET /health

### Response

```json
{
  "status": "ok",
  "service": "analytics-api",
  "version": "1.0.0"
}
```

---

## Analytics Summary

### Request

GET /analytics/summary

### Response

```json
{
  "total_records": 3,
  "avg_value": 41.8,
  "min_value": 28.5,
  "max_value": 65.2
}
```

---

## Analytics by Device

### Request

GET /analytics/by-device

### Response

```json
{
  "items": [
    {
      "device_id": "ESP32-LAB-A01",
      "total_readings": 2
    },
    {
      "device_id": "ESP32-LAB-B01",
      "total_readings": 1
    }
  ]
}
```

---

## Integration Status

### Request

GET /integrations

### Response

```json
{
  "iot_ingestion": "connected",
  "access_gate": "connected",
  "camera_stream": "pending_b2_integration",
  "core_business": "pending_b6_integration"
}
```

---

# Pair 06 – B1 (IoT Ingestion)

## Trạng thái

✅ Đã tích hợp.

---

## Service nguồn

| Hạng mục         | Thông tin                  |
| ---------------- | -------------------------- |
| Nhóm             | B1 – IoT Ingestion         |
| Service name     | iot-ingestion-b1           |
| Health endpoint  | GET /health                |
| Endpoint sử dụng | POST /telemetry/mock-check |
| URL class-net    | TBD                        |

---

## Analytics sử dụng

### Kiểm tra trạng thái B1

GET /external/iot/health

---

### Gửi dữ liệu thử nghiệm

POST /external/iot/mock-check

Body:

```json
{
  "device_id": "SENSOR-DHT22-01",
  "temperature": 28.5,
  "humidity": 60.0,
  "timestamp": "2026-06-09T13:45:00Z"
}
```

---

## Mục đích

* Kiểm tra khả năng kết nối tới B1.
* Xác minh định dạng telemetry.

---

# Pair 07 – B3 (Access Gate)

## Trạng thái

✅ Đã tích hợp.

---

## Service nguồn

| Hạng mục         | Thông tin          |
| ---------------- | ------------------ |
| Nhóm             | B3 – Access Gate   |
| Service name     | team-gate-api      |
| Health endpoint  | GET /health        |
| Endpoint sử dụng | POST /access/check |
| URL class-net    | TBD                |

---

## Analytics sử dụng

### Kiểm tra trạng thái B3

GET /external/access/health

---

### Kiểm tra quyền truy cập

POST /external/access/check

Body:

```json
{
  "card_uid": "A3B2C1D0",
  "gate_id": "GATE-MAIN-01"
}
```

Response:

```json
{
  "is_allowed": true,
  "employee_name": "Nguyen Van A",
  "timestamp": "2026-06-09T13:46:12Z"
}
```

---

## Mục đích

* Xác minh Access Gate hoạt động.
* Kiểm tra khả năng trao đổi dữ liệu giữa hai service.

---

# Pair 08 – B2 (Camera Stream)

## Trạng thái

⏳ Chờ tích hợp.

---

## Endpoint hiện có

GET /external/camera/info

---

## Response hiện tại

```json
{
  "status": "pending_b2_integration",
  "message": "Chờ nhóm B2 hoàn thiện module và cung cấp API kết nối luồng dữ liệu"
}
```

---

## Dự kiến tích hợp

Analytics sẽ sử dụng dữ liệu camera để:

* Thống kê mật độ người.
* Phân tích bất thường.
* Sinh báo cáo phục vụ Dashboard.

---

# Pair 09 – B6 (Core Business)

## Trạng thái

⏳ Chờ tích hợp.

---

## Endpoint hiện có

GET /external/core/info

---

## Response hiện tại

```json
{
  "status": "pending_b6_integration",
  "message": "Chờ nhóm B6 hoàn thiện module và cấu trúc nhận báo cáo tổng hợp"
}
```

---

## Dự kiến tích hợp

Analytics sẽ cung cấp dữ liệu tổng hợp phục vụ:

* Dashboard quản trị.
* KPI hệ thống.
* Báo cáo nghiệp vụ.

---

# Kiến trúc tích hợp hiện tại

```text
B1 (IoT Ingestion) ──────► Analytics (B5)
                                  │
B3 (Access Gate) ────────►        │
                                  │
                                  ▼
                           PostgreSQL
                                  │
                                  ▼
                             Dashboard
```

---

# Kiến trúc dự kiến sau khi hoàn thiện

```text
B1 (IoT) ───────────────┐
                        │
B2 (Camera) ────────────┤
                        │
B3 (Access Gate) ───────┼──► Analytics (B5)
                        │
B6 (Core Business) ─────┘
                                │
                                ▼
                           PostgreSQL
                                │
                                ▼
                             Dashboard
```

---

# Tổng quan trạng thái

| Nhóm               | Trạng thái     |
| ------------------ | -------------- |
| B1 – IoT Ingestion | ✅ Hoàn thành   |
| B3 – Access Gate   | ✅ Hoàn thành   |
| B2 – Camera Stream | ⏳ Chờ contract |
| B6 – Core Business | ⏳ Chờ contract |

---
