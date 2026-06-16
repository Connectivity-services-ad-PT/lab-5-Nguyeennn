# Readiness Checklist – Lab 05 (Team Analytics)

Đây là danh sách kiểm tra (checklist) để đảm bảo stack Docker Compose của phân hệ Analytics đã sẵn sàng vận hành ổn định trước khi nộp bài và tham gia Plug-a-thon.

- [x] **Database ready:** Container cơ sở dữ liệu `analytics_db` đã khởi chạy và phản hồi trạng thái hoạt động tốt. Kiểm tra độ sẵn sàng bằng lệnh: `docker exec -it analytics_db pg_isready -U analytics_user -d analytics`.
- [x] **Mock Services Ready:** Toàn bộ cụm dịch vụ liên đới đã được mô phỏng thành công qua Nginx inline (`iot-ingestion-b1`, `team-gate-api`, `camera-stream`, `core-business`) và phản hồi mã trạng thái `200 OK` cho endpoint `/health` trên cổng nội bộ `8000`.
- [x] **API ready:** Container chính `analytics_api` trả về mã `200 OK` cho endpoint `/health`, đồng thời thực hiện cơ chế Deep Health Check (kiểm tra sâu) kết nối thực tế tới Database thành công.
- [x] **Environment variables:** File cấu hình môi trường `.env` đã được thiết lập đồng bộ với `.env.example`, bao gồm cấu hình tách biệt cho các biến `SERVICE_VERSION`, hệ thống Storage (`POSTGRES_*`) và các URL nội bộ mạng. Tuyệt đối không commit mã secret thật lên GitHub.
- [x] **Network & Ports:** Mạng cục bộ `team-internal` hoạt động ổn định; API gọi được sang các dịch vụ đối tác thông qua các hostname nội bộ. Cổng đích của API điều phối ra ngoài máy cá nhân được map chính xác về cổng `8005` (`8005:8000`) để tránh xung đột hệ thống của lớp.
- [x] **Image tags:** Hệ thống ứng dụng đã được đóng gói Multi-stage build tinh gọn, chuyển đổi sang quyền user non-root (`appuser`), gắn thẻ phiên bản chuẩn quy ước `v0.1.0-team-analytics` và sẵn sàng đẩy lên registry.

---

### Ghi chú thêm những vấn đề gặp phải hoặc điều chỉnh: