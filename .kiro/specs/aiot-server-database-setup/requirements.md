# Requirements Document

## Introduction

Feature này thiết lập nền tảng backend cho dự án **SmartDesk Buddy (SmartClock)** — một thiết bị AIoT chạy trên ESP32-S3 hỗ trợ học tập, theo dõi giấc ngủ và giải trí. Phạm vi của feature bao gồm:

1. Khởi tạo Python server (FastAPI) với cấu trúc project chuẩn, có thể mở rộng.
2. Thiết kế và tạo database schema đầy đủ cho tất cả chức năng của SmartClock (Pomodoro, Seminar, Sleep Monitoring, Flappy Bird, Config Sync).
3. Kết nối server với database và xác minh kết nối hoạt động.
4. Seed mock data để kiểm thử mà không cần thiết bị ESP32 thật.

Feature này **chưa** implement business logic API cho từng chức năng — chỉ cần server chạy được, DB được thiết kế đúng và kết nối thành công. Các API endpoint cụ thể sẽ được implement ở các feature tiếp theo.

---

## Glossary

- **Server**: Python FastAPI backend server của dự án SmartDesk Buddy.
- **Database**: Hệ thống lưu trữ dữ liệu quan hệ (SQLite cho development, PostgreSQL cho production).
- **ORM**: Object-Relational Mapper — thư viện ánh xạ Python class sang database table (SQLAlchemy).
- **Migration**: Quá trình tạo hoặc cập nhật cấu trúc database schema theo phiên bản (Alembic).
- **Schema**: Cấu trúc tổng thể của database bao gồm các bảng, cột, kiểu dữ liệu và ràng buộc.
- **Device**: Một thiết bị ESP32 đã đăng ký với Server (SmartClock).
- **Pomodoro_Session**: Một phiên học tập hoặc nghỉ ngơi theo phương pháp Pomodoro, có `session_type` là `study` hoặc `break`.
- **Sleep_Session**: Một phiên theo dõi giấc ngủ, bao gồm nhiều Sensor_Batch và một Sleep_Score khi kết thúc.
- **Sensor_Batch**: Một lô dữ liệu cảm biến (sound_level, light_level) được ghi nhận mỗi 240 giây trong Sleep_Session.
- **Seminar_Recording**: Một bản ghi âm bài thuyết trình cùng kết quả đánh giá AI (clarity, speed, noise, confidence).
- **Game_Score**: Điểm số của một lượt chơi Flappy Bird, dùng cho leaderboard.
- **Timer_Config**: Cấu hình thời gian Pomodoro (study_duration, break_duration) của một Device.
- **Sleep_Config**: Cấu hình giấc ngủ (alarm_enabled, alarm_time, sleep_duration) của một Device.
- **Seed_Script**: Script Python tạo mock data vào database để phục vụ kiểm thử.
- **Health_Check**: Endpoint kiểm tra trạng thái hoạt động của Server và kết nối Database.
- **Environment_Variable**: Biến môi trường dùng để cấu hình server (DATABASE_URL, HOST, PORT, v.v.).
- **Mock_Data**: Dữ liệu giả lập được tạo bởi Seed_Script để kiểm thử API mà không cần thiết bị thật.

---

## Requirements

### Requirement 1: Cấu trúc project và khởi tạo server

**User Story:** Là một developer, tôi muốn server có cấu trúc project rõ ràng và chuẩn hóa, để có thể dễ dàng mở rộng thêm các module API trong tương lai mà không cần tái cấu trúc lại.

#### Acceptance Criteria

1. THE Server SHALL được xây dựng bằng Python với framework FastAPI.
2. THE Server SHALL tổ chức code theo cấu trúc thư mục phân tách rõ ràng: `app/` chứa toàn bộ application code, `app/models/` chứa ORM models, `app/schemas/` chứa Pydantic schemas, `app/routers/` chứa API route handlers, `app/core/` chứa cấu hình và database connection, `app/services/` chứa business logic (để trống ở phase này), và `scripts/` chứa utility scripts bao gồm Seed_Script.
3. THE Server SHALL đọc tất cả cấu hình từ Environment_Variable thông qua file `.env` và cung cấp file `.env.example` mô tả tất cả biến cần thiết.
4. THE Server SHALL cung cấp endpoint `GET /health` trả về HTTP 200 với JSON chứa trạng thái của Server và trạng thái kết nối Database.
5. WHEN Server khởi động, THE Server SHALL tự động kiểm tra kết nối Database và ghi log kết quả ra stdout.
6. IF kết nối Database thất bại khi khởi động, THEN THE Server SHALL ghi log lỗi chi tiết và thoát với exit code khác 0.
7. THE Server SHALL cung cấp tài liệu API tự động (OpenAPI/Swagger) tại endpoint `/docs` và ReDoc tại `/redoc`.
8. THE Server SHALL hỗ trợ CORS để cho phép web dashboard truy cập API từ browser, với danh sách allowed origins được cấu hình qua Environment_Variable.

---

### Requirement 2: Thiết kế và tạo database schema

**User Story:** Là một developer, tôi muốn database có schema đầy đủ và đúng đắn cho tất cả chức năng của SmartClock, để không cần thay đổi cấu trúc khi implement các API endpoint sau này.

#### Acceptance Criteria

1. THE Database SHALL chứa bảng `devices` với các cột: `id` (primary key), `device_id` (unique string), `device_type` (string, giá trị `smartclock`), `created_at` (UTC timestamp), `last_seen_at` (UTC timestamp).
2. THE Database SHALL chứa bảng `timer_configs` với các cột: `id` (primary key), `device_id` (foreign key → `devices.id`), `study_duration` (integer, đơn vị phút), `break_duration` (integer, đơn vị phút), `updated_at` (UTC timestamp). Mỗi Device có tối đa một Timer_Config (quan hệ one-to-one).
3. THE Database SHALL chứa bảng `sleep_configs` với các cột: `id` (primary key), `device_id` (foreign key → `devices.id`), `alarm_enabled` (boolean), `alarm_time` (string, định dạng `HH:MM`, nullable), `sleep_duration` (integer, đơn vị phút), `updated_at` (UTC timestamp). Mỗi Device có tối đa một Sleep_Config (quan hệ one-to-one).
4. THE Database SHALL chứa bảng `pomodoro_sessions` với các cột: `id` (primary key), `device_id` (foreign key → `devices.id`), `session_type` (string, giá trị `study` hoặc `break`), `duration` (integer, đơn vị giây), `timestamp` (UTC timestamp), `created_at` (UTC timestamp).
5. THE Database SHALL chứa bảng `sleep_sessions` với các cột: `id` (primary key), `device_id` (foreign key → `devices.id`), `status` (string, giá trị `active` hoặc `completed`), `start_time` (UTC timestamp), `end_time` (UTC timestamp, nullable), `sleep_score` (float, nullable, thang 0–100), `created_at` (UTC timestamp).
6. THE Database SHALL chứa bảng `sleep_sensor_batches` với các cột: `id` (primary key), `session_id` (foreign key → `sleep_sessions.id`), `sound_level` (float, đơn vị dB), `light_level` (float, đơn vị lux), `timestamp` (UTC timestamp). Mỗi Sleep_Session có nhiều Sensor_Batch (quan hệ one-to-many).
7. THE Database SHALL chứa bảng `seminar_recordings` với các cột: `id` (primary key), `device_id` (foreign key → `devices.id`), `file_path` (string), `duration` (float, đơn vị giây, nullable), `status` (string, giá trị `pending`, `processing` hoặc `completed`), `clarity_score` (float, nullable, thang 0–100), `speed_score` (float, nullable, thang 0–100), `noise_score` (float, nullable, thang 0–100), `confidence_score` (float, nullable, thang 0–100), `created_at` (UTC timestamp).
8. THE Database SHALL chứa bảng `game_scores` với các cột: `id` (primary key), `device_id` (foreign key → `devices.id`), `score` (integer, không âm), `timestamp` (UTC timestamp), `created_at` (UTC timestamp).
9. THE Database SHALL đánh index trên các cột thường xuyên được truy vấn: `devices.device_id`, `pomodoro_sessions.device_id`, `pomodoro_sessions.timestamp`, `sleep_sessions.device_id`, `sleep_sensor_batches.session_id`, `seminar_recordings.device_id`, `game_scores.device_id` và `game_scores.score`.
10. THE Database SHALL sử dụng UTC ISO 8601 cho tất cả trường timestamp.
11. THE Database SHALL đảm bảo tính toàn vẹn dữ liệu thông qua foreign key constraints — khi xóa một Device, tất cả dữ liệu liên quan SHALL bị xóa theo (cascade delete).

---

### Requirement 3: Kết nối server với database qua ORM

**User Story:** Là một developer, tôi muốn server kết nối với database thông qua ORM (SQLAlchemy), để code truy vấn database nhất quán, an toàn và dễ bảo trì.

#### Acceptance Criteria

1. THE Server SHALL sử dụng SQLAlchemy làm ORM để định nghĩa tất cả database models và thực hiện truy vấn.
2. THE Server SHALL sử dụng Alembic để quản lý database migrations, với migration đầu tiên tạo toàn bộ schema từ Requirement 2.
3. WHEN Server khởi động, THE Server SHALL tự động chạy pending migrations để đảm bảo database schema luôn đồng bộ với code.
4. THE Server SHALL hỗ trợ SQLite cho môi trường development và PostgreSQL cho production, được chuyển đổi thông qua Environment_Variable `DATABASE_URL` mà không cần thay đổi code.
5. THE Server SHALL sử dụng connection pooling để quản lý kết nối database hiệu quả, với pool size được cấu hình qua Environment_Variable.
6. IF truy vấn database gặp lỗi, THEN THE Server SHALL log lỗi chi tiết bao gồm loại lỗi và context, và trả về HTTP 500 với thông báo lỗi chung (không expose chi tiết database ra ngoài).
7. THE Server SHALL định nghĩa tất cả ORM models tương ứng 1-1 với các bảng trong Requirement 2, với đầy đủ relationships (foreign keys, back-references).

---

### Requirement 4: Quản lý cấu hình qua biến môi trường

**User Story:** Là một developer, tôi muốn toàn bộ cấu hình server được quản lý qua biến môi trường, để có thể deploy lên các môi trường khác nhau (development, staging, production) mà không cần sửa code.

#### Acceptance Criteria

1. THE Server SHALL đọc cấu hình từ các Environment_Variable sau: `DATABASE_URL` (connection string), `HOST` (địa chỉ bind, mặc định `0.0.0.0`), `PORT` (cổng lắng nghe, mặc định `8000`), `DEBUG` (chế độ debug, mặc định `false`), `CORS_ORIGINS` (danh sách allowed origins, mặc định `*`), `UPLOAD_DIR` (thư mục lưu file audio, mặc định `./uploads`).
2. THE Server SHALL cung cấp file `.env.example` liệt kê tất cả Environment_Variable với giá trị mặc định và mô tả ngắn gọn cho từng biến.
3. IF một Environment_Variable bắt buộc (`DATABASE_URL`) không được cung cấp, THEN THE Server SHALL ghi log lỗi rõ ràng và thoát với exit code khác 0 khi khởi động.
4. THE Server SHALL hỗ trợ đọc Environment_Variable từ file `.env` trong thư mục gốc của project khi chạy ở môi trường development.
5. THE Server SHALL cung cấp file `requirements.txt` hoặc `pyproject.toml` liệt kê tất cả Python dependencies với phiên bản cụ thể (pinned versions).

---

### Requirement 5: Seed mock data

**User Story:** Là một developer, tôi muốn có mock data sẵn có trong database sau khi chạy một lệnh duy nhất, để có thể kiểm thử các API endpoint ngay lập tức mà không cần thiết bị ESP32 thật.

#### Acceptance Criteria

1. THE Seed_Script SHALL tạo ít nhất 2 Device với `device_type` là `smartclock` và dữ liệu đầy đủ cho cả hai.
2. THE Seed_Script SHALL tạo Timer_Config và Sleep_Config cho mỗi Device được tạo.
3. THE Seed_Script SHALL tạo tối thiểu 10 Pomodoro_Session phân bổ đều giữa các Device, với mix giữa `session_type` `study` và `break`, trải dài trong 7 ngày gần nhất.
4. THE Seed_Script SHALL tạo tối thiểu 3 Sleep_Session với trạng thái `completed`, mỗi session có tối thiểu 3 Sensor_Batch và một `sleep_score` hợp lệ (0–100).
5. THE Seed_Script SHALL tạo tối thiểu 2 Seminar_Recording với trạng thái `completed` và đầy đủ 4 điểm số đánh giá (`clarity_score`, `speed_score`, `noise_score`, `confidence_score`).
6. THE Seed_Script SHALL tạo tối thiểu 5 Game_Score phân bổ giữa các Device với các giá trị điểm số khác nhau.
7. WHEN Seed_Script được chạy, THE Seed_Script SHALL xóa toàn bộ dữ liệu hiện có và tạo lại từ đầu để đảm bảo tính nhất quán và idempotency.
8. WHEN Seed_Script hoàn thành, THE Seed_Script SHALL in ra stdout tóm tắt số lượng bản ghi đã tạo cho từng loại entity.
9. THE Seed_Script SHALL có thể chạy bằng lệnh `python scripts/seed.py` từ thư mục gốc của project.

---

### Requirement 6: Khả năng mở rộng và chuẩn bị cho các API tiếp theo

**User Story:** Là một developer, tôi muốn cấu trúc server được thiết kế để dễ dàng thêm API endpoint mới, để các feature tiếp theo (Pomodoro API, Sleep API, v.v.) có thể được implement mà không cần refactor nền tảng.

#### Acceptance Criteria

1. THE Server SHALL tổ chức API routes theo module trong thư mục `app/routers/`, với mỗi domain (devices, pomodoro, sleep, seminar, game) có file router riêng biệt, ngay cả khi chưa có endpoint nào được implement.
2. THE Server SHALL sử dụng FastAPI `APIRouter` với prefix và tags cho từng module để tự động phân nhóm trong tài liệu Swagger.
3. THE Server SHALL định nghĩa Pydantic schemas trong `app/schemas/` tương ứng với từng entity trong database, bao gồm schemas cho request body và response, ngay cả khi chưa có endpoint sử dụng.
4. THE Server SHALL tổ chức business logic trong `app/services/` tách biệt khỏi route handlers, để route handlers chỉ xử lý HTTP concerns (validation, serialization) còn services xử lý logic.
5. THE Server SHALL cung cấp một `app/core/database.py` module tập trung quản lý database session, với dependency injection pattern của FastAPI (`Depends`) để inject database session vào route handlers.
6. THE Server SHALL có file `README.md` mô tả cách cài đặt dependencies, cấu hình environment, chạy server, chạy migrations và chạy seed script.

