# ==================================================
# Variables Config (Team Analytics - Lab 05)
# ==================================================
IMAGE_NAME ?= fit4110/analytics-api:v0.1.0-team-analytics
CONTAINER_NAME ?= analytics_api
PORT ?= 8005

# Local Setup & Linting (Tuỳ chọn)
install:
	npm install

lint:
	npm run lint:openapi

# ==================================================
# Lab 05: Docker Compose Commands (Mục tiêu chính)
# ==================================================

# SỬA: Tự động khởi tạo mạng external class-net nếu chưa tồn tại trên máy máy cá nhân để tránh lỗi crash cụm
compose-up:
	docker network create class-net || true
	docker compose up -d --build

compose-down:
	docker compose down

compose-down-v:
	docker compose down -v

logs:
	docker compose logs -f

# Kiểm tra nhanh trạng thái các container trong cụm
ps:
	docker compose ps

# ==================================================
# Health Check & E2E Testing
# ==================================================
health:
	curl http://localhost:$(PORT)/health

integrations:
	curl http://localhost:$(PORT)/integrations

# SỬA: Cập nhật chính xác tên file collection thực tế: FIT4110_lab04_iot_docker.postman_collection.json
# SỬA: Thêm lệnh khởi tạo thư mục reports/ tự động để Newman không bị lỗi phân quyền ghi file
test-compose:
	mkdir -p reports
	npx newman run postman/collections/FIT4110_lab04_iot_docker.postman_collection.json \
		-e postman/environments/team-analytics_local.postman_environment.json \
		-r cli,html,junit \
		--reporter-html-export reports/newman-lab05-compose.html \
		--reporter-junit-export reports/newman-lab05-compose.xml

# Clean Up
clean-reports:
	rm -f reports/*.xml reports/*.html reports/*.json

# ==================================================
# Single Container Commands (Development & Debug)
# ==================================================
docker-build-single:
	docker build -t $(IMAGE_NAME) -f Dockerfile.analytics .

docker-run-single:
	docker run --rm --name $(CONTAINER_NAME) -p $(PORT):8000 --env-file .env.example $(IMAGE_NAME)

docker-stop-single:
	docker stop $(CONTAINER_NAME) || true