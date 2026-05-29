# AIoT Backend Database and Server Guide

Tài liệu này là tài liệu database duy nhất của project. Nó gộp lại phần kiến trúc database, migration, PostgreSQL local, Supabase và cách hiểu vì sao dữ liệu có thể xuất hiện ở SQLite nhưng không thấy trong pgAdmin.

## 1. Tổng quan kiến trúc

Server hiện tại là một FastAPI backend cho 2 nhóm thiết bị:

- **SmartClock**: Pomodoro, Sleep Monitoring, Alarm, Seminar Practice, Game Score.
- **VisionDriveAI**: Trip tracking, distraction detection, safety score.

Luồng tổng thể:

```text
ESP32 / Web Dashboard / Postman
        |
        v
FastAPI Server
        |
        v
Database
```

## 2. Server structure

Các file server chính:

| File | Vai trò |
|---|---|
| `app/main.py` | Tạo FastAPI app, CORS, route `/`, include routers |
| `app/config.py` | Đọc `.env` bằng Pydantic Settings |
| `app/database.py` | Tạo SQLAlchemy engine/session |
| `app/auth.py` | Xác thực thiết bị bằng `device_token` |
| `app/schemas.py` | Pydantic request/response schemas |
| `app/routers/health.py` | Health check |
| `app/routers/devices.py` | Register device, get current device |
| `app/routers/smartclock.py` | SmartClock APIs |
| `app/routers/visiondrive.py` | VisionDrive APIs |
| `app/models/*.py` | SQLAlchemy database models |
| `app/seed.py` | Seed dữ liệu mock |

Các endpoint chính:

| Endpoint | Mục đích |
|---|---|
| `GET /` | Trang gốc, trả thông tin server |
| `GET /health` | Kiểm tra server và database |
| `POST /devices/register` | Đăng ký thiết bị |
| `GET /devices/me` | Kiểm tra token thiết bị hiện tại |
| `GET /smartclock/timer-config` | Lấy cấu hình Pomodoro |
| `PUT /smartclock/timer-config` | Cập nhật cấu hình Pomodoro |
| `GET /smartclock/sleep-config` | Lấy cấu hình sleep/alarm |
| `PUT /smartclock/sleep-config` | Cập nhật cấu hình sleep/alarm |
| `POST /smartclock/pomodoro-sessions` | Ghi log Pomodoro |
| `POST /smartclock/sleep-sessions` | Bắt đầu sleep session |
| `POST /smartclock/sleep-sessions/{id}/sensor-batches` | Gửi batch cảm biến sleep |
| `PUT /smartclock/sleep-sessions/{id}/quality-report` | Tạo/cập nhật sleep quality report |
| `GET /smartclock/sleep-sessions/{id}/quality-report` | Đọc sleep quality report |
| `POST /smartclock/game-scores` | Ghi điểm game |
| `POST /visiondrive/trips` | Bắt đầu trip |
| `POST /visiondrive/trips/{id}/distraction-events` | Ghi event mất tập trung |
| `POST /visiondrive/trips/{id}/end` | Kết thúc trip |


Các file Alembic:

| File | Vai trò |
|---|---|
| `alembic.ini` | Cấu hình Alembic |
| `alembic/env.py` | Nối Alembic với SQLAlchemy metadata và database URL |
| `alembic/versions/*.py` | Các migration cụ thể |

Lệnh thường dùng:

```bash
alembic current
alembic heads
alembic history
alembic upgrade head
alembic downgrade -1
alembic revision --autogenerate -m "message"
```

## 5. Entity relationship

```mermaid
erDiagram
    devices {
        int id PK
        string device_id UK
        enum device_type
        string device_token UK
        datetime created_at
        datetime last_seen_at
    }

    timer_configs {
        int id PK
        int device_id FK
        int study_duration
        int break_duration
        datetime updated_at
    }

    sleep_configs {
        int id PK
        int device_id FK
        bool alarm_enabled
        string alarm_time
        int sleep_duration
        datetime updated_at
    }

    pomodoro_sessions {
        int id PK
        int device_id FK
        datetime timestamp
        int duration
        enum session_type
        datetime created_at
    }

    sleep_sessions {
        int id PK
        int device_id FK
        datetime start_time
        datetime end_time
        enum status
        float sleep_score
    }

    sleep_sensor_batches {
        int id PK
        int sleep_session_id FK
        datetime timestamp
        float sound_level
        float light_level
    }

    sleep_quality_reports {
        int id PK
        int sleep_session_id FK
        float duration_minutes
        enum quality_label
        float duration_score
        float sound_score
        float light_score
        float avg_sound_level
        float avg_light_level
        bool duration_issue
        bool noise_issue
        bool light_issue
        text recommendation
        datetime generated_at
    }

    seminar_recordings {
        int id PK
        int device_id FK
        string file_path
        float duration
        enum status
        float clarity_score
        float speed_score
        float noise_score
        float confidence_score
        datetime created_at
        datetime evaluated_at
    }

    game_scores {
        int id PK
        int device_id FK
        int score
        datetime timestamp
        datetime created_at
    }

    trips {
        int id PK
        int device_id FK
        datetime start_time
        datetime end_time
        enum status
        float safety_score
    }

    distraction_events {
        int id PK
        int trip_id FK
        datetime timestamp
        enum event_type
        enum severity
    }

    devices ||--o| timer_configs : has
    devices ||--o| sleep_configs : has
    devices ||--o{ pomodoro_sessions : logs
    devices ||--o{ sleep_sessions : monitors
    devices ||--o{ seminar_recordings : records
    devices ||--o{ game_scores : plays
    devices ||--o{ trips : drives
    sleep_sessions ||--o{ sleep_sensor_batches : batches
    sleep_sessions ||--o| sleep_quality_reports : summarizes
    trips ||--o{ distraction_events : detects
```

## 6. Table summary

| Table | Thuộc về | Mô tả |
|---|---|---|
| `devices` | Core | Thiết bị ESP32 đã đăng ký |
| `timer_configs` | SmartClock | Cấu hình Pomodoro |
| `sleep_configs` | SmartClock | Cấu hình báo thức và giấc ngủ |
| `pomodoro_sessions` | SmartClock | Log phiên Pomodoro |
| `sleep_sessions` | SmartClock | Phiên theo dõi giấc ngủ |
| `sleep_sensor_batches` | SmartClock | Dữ liệu âm thanh/ánh sáng theo thời gian |
| `sleep_quality_reports` | SmartClock | Báo cáo chất lượng ngủ, issue và recommendation |
| `seminar_recordings` | SmartClock | File audio và kết quả đánh giá seminar |
| `game_scores` | SmartClock | Điểm game |
| `trips` | VisionDrive | Chuyến đi |
| `distraction_events` | VisionDrive | Sự kiện mất tập trung trong chuyến đi |

## 7. Indexes

| Table | Index | Mục đích |
|---|---|---|
| `devices` | `ix_devices_device_id` | Lookup device khi auth/register |
| `pomodoro_sessions` | `ix_pomodoro_device_timestamp` | Query lịch sử Pomodoro theo device/time |
| `sleep_sessions` | `ix_sleep_device_start` | Query lịch sử ngủ |
| `sleep_sensor_batches` | `ix_sleep_batch_session_ts` | Query batch cảm biến theo session/time |
| `sleep_quality_reports` | `ix_sleep_quality_generated` | Query report theo thời gian tạo |
| `seminar_recordings` | `ix_seminar_device_created` | Query recording theo device/time |
| `game_scores` | `ix_game_device_score` | Leaderboard/query score |
| `trips` | `ix_trip_device_start` | Query trip theo device/time |
| `distraction_events` | `ix_distraction_trip_ts` | Query event theo trip/time |

## 8. Enum values

| Enum | Values |
|---|---|
| `device_type` | `smartclock`, `visiondrive` |
| `pomodoro_type` | `study`, `break` |
| `sleep_status` | `active`, `completed` |
| `sleep_quality_label` | `poor`, `fair`, `good`, `excellent` |
| `seminar_status` | `pending`, `processing`, `completed`, `failed` |
| `trip_status` | `active`, `completed` |
| `distraction_type` | `drowsiness`, `gaze_distraction`, `phone_use` |
| `distraction_severity` | `low`, `medium`, `high` |

## 9. Sleep use case mapping

Theo docs submission, Sleep Monitoring cần:

- Ghi nhận thời gian bắt đầu/kết thúc ngủ.
- Tính tổng thời lượng ngủ.
- Theo dõi ánh sáng và âm thanh môi trường.
- Đánh giá chất lượng ngủ.
- Phân tích nguyên nhân ngủ chưa tốt.
- Đưa ra gợi ý cải thiện.

Mapping sang DB:

| Nhu cầu use case | Bảng/cột |
|---|---|
| Bắt đầu/kết thúc ngủ | `sleep_sessions.start_time`, `sleep_sessions.end_time` |
| Điểm ngủ tổng quan | `sleep_sessions.sleep_score` |
| Âm thanh/ánh sáng theo thời gian | `sleep_sensor_batches` |
| Báo cáo chất lượng | `sleep_quality_reports.quality_label` |
| Điểm thành phần | `duration_score`, `sound_score`, `light_score` |
| Vấn đề chính | `duration_issue`, `noise_issue`, `light_issue` |
| Gợi ý cải thiện | `recommendation` |

## 10. Database URL modes

### SQLite local

Dùng để test nhanh trên máy, seed mock, Postman:

```env
DATABASE_URL=sqlite:///./aiot.db
MIGRATION_DATABASE_URL=sqlite:///./aiot.db
```

Khi dùng mode này:

- Database là file `aiot.db` trong project.
- pgAdmin không thấy bảng vì pgAdmin không đọc SQLite.
- Dùng SQLite viewer hoặc API server để xem dữ liệu.

### PostgreSQL local

Dùng khi muốn xem bảng bằng pgAdmin:

```env
DATABASE_URL=postgresql://aiot_user:123@localhost:5432/aiot_db
MIGRATION_DATABASE_URL=postgresql://aiot_user:123@localhost:5432/aiot_db
```

Sau khi đổi `.env`, cần chạy:

```bash
alembic upgrade head
python -m app.seed
```

Lúc đó pgAdmin mới thấy bảng trong `Schemas > public > Tables`.

### Supabase PostgreSQL

Dùng khi muốn database cloud:

```env
DATABASE_URL=postgresql://postgres.<project-ref>:<db-password>@<pooler-host>:5432/postgres?sslmode=require
MIGRATION_DATABASE_URL=postgresql://postgres:<db-password>@db.<project-ref>.supabase.co:5432/postgres?sslmode=require
```

Gợi ý:

- `DATABASE_URL`: dùng Session Pooler nếu app chạy ở môi trường không chắc IPv6.
- `MIGRATION_DATABASE_URL`: dùng Direct connection nếu mạng hỗ trợ.
- Nếu Direct connection lỗi, có thể đặt `MIGRATION_DATABASE_URL` giống `DATABASE_URL`.

## 11. Setup local SQLite để test Postman

```bash
alembic upgrade head
python -m app.seed
uvicorn app.main:app --reload
```

Mở:

```text
http://127.0.0.1:8000/
http://127.0.0.1:8000/docs
http://127.0.0.1:8000/health
```

Token mock:

```text
SmartClock: dev-smartclock-token
VisionDrive: dev-visiondrive-token
```

Header Postman:

```http
Authorization: Bearer dev-smartclock-token
```

## 12. Setup PostgreSQL để xem trong pgAdmin

Bước chuẩn:

1. Tạo database trong PostgreSQL, ví dụ `aiot_db`.
2. Tạo user, ví dụ `aiot_user`.
3. Cấp quyền cho user trên database.
4. Đổi `.env` sang PostgreSQL URL.
5. Chạy migration và seed.

Ví dụ SQL trong pgAdmin Query Tool hoặc `psql`:

```sql
CREATE DATABASE aiot_db;
CREATE USER aiot_user WITH PASSWORD '123';
GRANT ALL PRIVILEGES ON DATABASE aiot_db TO aiot_user;
```

Sau đó mở `.env`:

```env
DATABASE_URL=postgresql://aiot_user:123@localhost:5432/aiot_db
MIGRATION_DATABASE_URL=postgresql://aiot_user:123@localhost:5432/aiot_db
```

Chạy:

```bash
alembic upgrade head
python -m app.seed
```

Cuối cùng trong pgAdmin:

```text
Databases
└── aiot_db
    └── Schemas
        └── public
            └── Tables
```

Nếu không thấy bảng:

- Right click `Tables` > `Refresh`.
- Kiểm tra bạn đang mở đúng database.
- Kiểm tra `.env` có thật sự dùng PostgreSQL chưa.
- Chạy `alembic current`, nếu không hiện revision `bc260fe3aabc` thì migration chưa chạy vào database đó.


## 14. Quy tắc làm việc

- Không commit `.env`.
- Không commit `aiot.db`.
- Mỗi lần sửa SQLAlchemy model thì tạo migration mới.
- Muốn bảng xuất hiện ở database nào thì `.env` phải trỏ đúng database đó trước khi chạy `alembic upgrade head`.
- Với PostgreSQL/Supabase thật, luôn kiểm tra migration file trước khi chạy.
