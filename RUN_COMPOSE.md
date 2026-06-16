# RUN_COMPOSE.md – Hướng dẫn chạy Lab 05 (Team Analytics)

Tài liệu này hướng dẫn các thành viên hoặc kiểm thử viên thực hiện clone một cấu trúc mã nguồn sạch và tái khởi động lại toàn bộ cụm Stack Compose của Phân hệ Analytics - Lab 05.

## 1. Clone repo và truy cập thư mục dự án

```bash
git clone <repo-url>
cd FIT4110_lab05_docker_compose_readiness

```
## 2. Cài đặt các gói tài nguyên phục vụ kiểm thử (Tùy chọn)

```bash
npm install
```
## 3. Khởi tạo cấu hình cấu trúc và chạy cụm Stack Docker Compose
## Bước 3.1: Đồng bộ hóa tệp cấu hình môi trường

```bash
cp .env.example .env

```
## Bước 3.2: Khởi chạy và Build hệ thống dịch vụ

Hệ thống sẽ tự động khởi tạo các mạng hạ tầng cần thiết và kích hoạt các container thành phần:

```bash
make compose-up
```
Lệnh điều phối trên sẽ tạo lập và phân phối các container vận hành bao gồm:

analytics_db: Cơ sở dữ liệu lưu trữ, xử lý thông tin log phân tích dữ liệu.

analytics_api: Trung tâm xử lý thuật toán và cung cấp cổng API Analytics (Ánh xạ ngoài cổng: 8005).

iot-ingestion-b1, team-gate-api, camera-stream, core-business: Các cụm dịch vụ giả lập môi trường liên mạng Smart Campus (Hoạt động nội bộ trên cổng container: 8000).

## Bước 3.3: Theo dõi giám sát hệ thống nhật ký Logs
```bash
make logs
``` 
## Bước 3.4: Thực hiện kiểm tra trạng thái Readiness (Sẵn sàng) của các thành phần
```bash
# Kiểm tra trạng thái API chính và liên kết DB nội bộ
curl http://localhost:8005/health

# Kiểm tra danh mục danh sách liên kết Service Endpoints
curl http://localhost:8005/integrations

# Kiểm tra sâu kết nối tích hợp thử nghiệm sang phân hệ IoT Ingestion (Team B1)
curl http://localhost:8005/external/iot/health

# Kiểm tra sâu kết nối tích hợp thử nghiệm sang phân hệ Access Gate
curl http://localhost:8005/external/access/health

# Kiểm tra độ sẵn sàng thực tế của Database
docker exec -it analytics_db pg_isready -U analytics_user -d analytics
```
## 4. Chạy tiến trình kiểm thử tự động Newman E2E trên nền cụm Compose
Để xác thực độ chính xác của toàn bộ các luồng tích hợp, chạy lệnh:

```bash
make test-compose
```
Báo cáo kết quả kiểm thử (Test Reports) sẽ tự động xuất ra tại thư mục:
```bash

reports/newman-lab05-compose.xml

reports/newman-lab05-compose.html
```

## 5. Dừng vận hành Stack hệ thống
Giải phóng và hạ cụm dịch vụ: 
```bash 
make compose-down
```

Giải phóng cụm dịch vụ và xóa sạch hoàn toàn ổ đĩa cấu hình dữ liệu Database: 
```bash
make compose-down-v
```
## 6. Bảng tổng hợp các tập lệnh nhanh bằng Makefile
```bash
make compose-up
```
--> Tự động tạo lập mạng ngoại vi class-net, xây dựng cấu trúc và chạy nền toàn bộ cụm dịch vụ.

```bash
make compose-down
```
--> Dừng và gỡ bỏ trạng thái các dịch vụ trong cụm.

```bash
make logs 
```
--> Xem liên tục luồng log xuất ra từ cụm hệ thống.

```bash
make ps 
```
--> Xem nhanh danh sách trạng thái sống/chết của các container trong cụm.

## 7. Mẹo nhỏ xử lý sự cố và gỡ lỗi nhanh (Troubleshooting)
## 7.1. Lỗi liên quan đến Cơ sở dữ liệu (Database error):

Kiểm tra tính chính xác của các khóa cấu hình bắt đầu bằng tiền tố DB_* trong file cấu hình .env cục bộ.

Chạy lệnh make ps để đảm bảo container analytics_db không bị dính trạng thái lỗi và hiển thị up (healthy).

## 7.2. Lỗi Unauthorized (401) khi gọi API bên ngoài:

Đảm bảo biến cấu hình bảo mật AUTH_TOKEN tại file .env đã được thiết lập đồng nhất giá trị với Token xác thực của các nhóm đối tác.