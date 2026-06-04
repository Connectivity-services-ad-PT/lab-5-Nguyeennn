# RUN_LOCAL.md – Analytics Service (Lab05)

## Prerequisites

* Docker Desktop
* Docker Compose v2

---

## 1. Clone repository

```bash
git clone <repo-url>
cd lab04-Nguyeennn
```

---

## 2. Create external network

```bash
docker network create class-net
```

If the network already exists, Docker will show a warning and continue.

---

## 3. Build services

```bash
docker compose build
```

---

## 4. Start services

```bash
docker compose up -d
```

Check status:

```bash
docker ps
```

Expected containers:

* analytics_db
* analytics_api

Both containers should be healthy.

---

## 5. Test API

### Health Check

```bash
curl http://localhost:8000/health
```

Expected response:

```json
{
  "status": "ok",
  "service": "analytics-api"
}
```

### Analytics Summary

```bash
curl http://localhost:8000/analytics/summary
```

### Analytics By Device

```bash
curl http://localhost:8000/analytics/by-device
```

---

## 6. Check PostgreSQL

Connect to database:

```bash
docker exec -it analytics_db psql -U analytics_user -d analytics
```

View sample data:

```sql
SELECT * FROM sensor_readings;
```

Exit:

```sql
\q
```

---

## 7. Stop services

```bash
docker compose down
```

Remove containers and volumes:

```bash
docker compose down -v
```
