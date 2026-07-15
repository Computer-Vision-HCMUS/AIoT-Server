# EmotiCare Database and pgAdmin Guide

Tài liệu này mô tả database/backend hiện tại của **EmotiCare AIoT Internet Service** theo
`docs/Spectification/EmotiCareAIoT/05_Internet Service.md`.

Mục tiêu chính:

- Tạo đúng schema DB cho UC01-UC05.
- Test được API và thấy dữ liệu ghi vào từng bảng.
- Quan sát database bằng pgAdmin.

## 1. Kiến trúc hiện tại

Backend là một **FastAPI modular monolith**:

```text
Edge Device / Postman / Swagger
        |
        v
FastAPI Cloud API
        |
        v
SQLAlchemy ORM
        |
        v
PostgreSQL database
```

Các file chính:

| File | Vai trò |
|---|---|
| `app/main.py` | Tạo FastAPI app, CORS, include các router `/api/*` |
| `app/config.py` | Đọc `.env` bằng Pydantic Settings |
| `app/database.py` | Tạo SQLAlchemy engine/session |
| `app/auth.py` | Xác thực device token bằng SHA-256 hash |
| `app/models/emoticare.py` | SQLAlchemy models cho toàn bộ EmotiCare schema |
| `app/schemas.py` | Pydantic request/response schemas |
| `app/seed.py` | Seed user demo, device demo và media catalog |
| `alembic/versions/*` | Database migrations |

## 2. Bảng database

| Table | Use case | Mục đích |
|---|---|---|
| `users` | Core | Người dùng, pairing code, consent lưu dữ liệu |
| `devices` | Core | Thiết bị Edge đã ghép với user, token hash, firmware, last seen |
| `emotion_sessions` | UC01, UC05 | Emotion session đồng bộ từ Edge AI lên Cloud |
| `recommendation_requests` | UC02, UC05 | Lưu request/response gợi ý hoạt động, bài hát, podcast |
| `activity_feedback` | UC02, UC05 | Lưu lựa chọn/đánh giá activity |
| `media_items` | UC02, UC03 | Catalog bài hát/podcast |
| `media_selection_logs` | UC03, UC05 | Lưu nội dung người dùng chọn và feedback media |
| `conversation_requests` | UC04, UC05 | Lưu phản hồi hội thoại và safety flag |
| `tft_reports` | UC05 | Báo cáo rút gọn để trả về TFT |

## 3. ER diagram

```mermaid
erDiagram
    users ||--o{ devices : owns
    users ||--o{ emotion_sessions : has
    users ||--o{ tft_reports : receives

    devices ||--o{ emotion_sessions : syncs

    emotion_sessions ||--o{ recommendation_requests : requests
    recommendation_requests ||--o{ activity_feedback : receives

    emotion_sessions ||--o{ conversation_requests : starts
    emotion_sessions ||--o{ media_selection_logs : logs
    media_items ||--o{ media_selection_logs : selected

    users {
        uuid id PK
        varchar name
        varchar pairing_code UK
        boolean consent_audio_storage
        timestamp created_at
        timestamp updated_at
    }

    devices {
        uuid id PK
        uuid user_id FK
        varchar name
        varchar device_token_hash
        varchar firmware_version
        timestamp last_seen_at
        varchar status
        timestamp created_at
    }

    emotion_sessions {
        uuid id PK
        varchar client_session_id
        uuid user_id FK
        uuid device_id FK
        varchar emotion_label
        numeric confidence_score
        varchar quality_flag
        int inference_latency_ms
        timestamp client_created_at
        timestamp created_at
    }

    recommendation_requests {
        uuid id PK
        uuid session_id FK
        jsonb request_payload
        jsonb response_payload
        varchar status
        timestamp created_at
    }

    activity_feedback {
        uuid id PK
        uuid recommendation_id FK
        varchar activity_type
        boolean selected
        int feedback_score
        timestamp created_at
    }

    media_items {
        uuid id PK
        varchar media_type
        varchar title
        varchar creator
        varchar category
        int duration_sec
        text source_url
        boolean enabled
    }

    media_selection_logs {
        uuid id PK
        uuid session_id FK
        uuid media_item_id FK
        varchar user_intent
        varchar selected_category
        int feedback_score
        timestamp created_at
    }

    conversation_requests {
        uuid id PK
        uuid session_id FK
        text user_message_summary
        varchar response_text
        varchar safety_flag
        timestamp created_at
    }

    tft_reports {
        uuid id PK
        uuid user_id FK
        varchar period_type
        date period_start
        date period_end
        jsonb tft_cards
        jsonb emotion_distribution
        varchar trend_summary
        varchar data_quality
        timestamp generated_at
    }
```

## 4. API ghi vào bảng nào

| API | Method | Bảng đọc/ghi chính |
|---|---|---|
| `/api/devices/pair` | POST | đọc `users`, ghi `devices` |
| `/api/devices/heartbeat` | POST | cập nhật `devices` |
| `/api/emotion-sessions/sync` | POST | ghi `emotion_sessions` |
| `/api/emotion-sessions` | GET | đọc `emotion_sessions` của device hiện tại |
| `/api/recommendations/request` | POST | đọc `emotion_sessions`, `media_items`; ghi `recommendation_requests` |
| `/api/recommendations/action` | POST | đọc `emotion_sessions`; ghi `recommendation_requests` |
| `/api/recommendations` | GET | đọc `recommendation_requests` của device hiện tại |
| `/api/media/categories` | GET | trả category static |
| `/api/media/recommendations` | POST | đọc `media_items` |
| `/api/media/music/recommend` | POST | đọc `media_items` loại `song` |
| `/api/media/podcast/recommend` | POST | đọc `media_items` loại `podcast` |
| `/api/media/history` | GET | đọc `media_selection_logs` của device hiện tại |
| `/api/conversations/respond` | POST | đọc `emotion_sessions`; ghi `conversation_requests` |
| `/api/stt/transcribe` | POST | xử lý audio tạm thời bằng Whisper; mặc định không ghi DB |
| `/api/feedback/activity` | POST | đọc `recommendation_requests`; ghi `activity_feedback` |
| `/api/feedback/media` | POST | đọc `emotion_sessions`, `media_items`; ghi `media_selection_logs` |
| `/api/reports/tft-summary` | GET | đọc logs; ghi/đọc `tft_reports` |
| `/api/reports/generate` | POST | đọc logs; ghi `tft_reports` |
| `/api/reports` | GET | đọc `tft_reports` của user hiện tại |
| `/api/statistics/day` | GET | đọc logs; ghi/đọc `tft_reports` daily |
| `/api/statistics/week` | GET | đọc logs; ghi/đọc `tft_reports` weekly |
| `/api/statistics/month` | GET | đọc logs; ghi/đọc `tft_reports` monthly |
| `/api/device-config` | GET | trả config static cho Edge |

## 5. Setup nhanh bằng Docker Compose

Đây là cách dễ nhất để có API, PostgreSQL và pgAdmin chạy cùng lúc.

```bash
docker compose up --build
```

Docker Compose tạo:

| Service | URL/Port | Credential |
|---|---|---|
| API | `http://localhost:8000` | N/A |
| Swagger | `http://localhost:8000/docs` | N/A |
| PostgreSQL | `localhost:5432` | `aiot_user` / `aiot_password` |
| pgAdmin | `http://localhost:5050` | `admin@aiot.local` / `admin` |

API container tự chạy:

```bash
alembic upgrade head
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Seed demo data:

```bash
docker compose exec api python -m app.seed
```

Demo token sau khi seed:

```text
demo-emoticare-device-token-local-dev
```

## 6. Mở database trong pgAdmin khi dùng Docker

1. Mở:

```text
http://localhost:5050
```

2. Đăng nhập:

```text
Email: admin@aiot.local
Password: admin
```

3. Add server:

```text
Object Explorer > Servers > Register > Server
```

Tab **General**:

```text
Name: AIoT Docker PostgreSQL
```

Tab **Connection**:

```text
Host name/address: postgres
Port: 5432
Maintenance database: aiot_db
Username: aiot_user
Password: aiot_password
```

4. Xem bảng:

```text
Servers
└── AIoT Docker PostgreSQL
    └── Databases
        └── aiot_db
            └── Schemas
                └── public
                    └── Tables
```

Nếu pgAdmin chạy ngoài Docker thay vì service `pgadmin`, dùng host:

```text
Host name/address: localhost
Port: 5432
Username: aiot_user
Password: aiot_password
```

## 7. Setup PostgreSQL local trên máy

Dùng cách này nếu bạn chạy PostgreSQL bằng installer/local service, không dùng container PostgreSQL.

Tạo database/user trong pgAdmin Query Tool khi đang connect vào database `postgres`:

```sql
CREATE DATABASE aiot_db;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT FROM pg_catalog.pg_roles WHERE rolname = 'aiot_user'
    ) THEN
        CREATE USER aiot_user WITH PASSWORD '123';
    END IF;
END
$$;

ALTER USER aiot_user WITH PASSWORD '123';
```

Sau đó connect sang database `aiot_db` và chạy:

```sql
GRANT ALL PRIVILEGES ON DATABASE aiot_db TO aiot_user;
GRANT ALL ON SCHEMA public TO aiot_user;
ALTER SCHEMA public OWNER TO aiot_user;
```

`.env` khi dùng PostgreSQL local:

```env
DATABASE_URL=postgresql://aiot_user:123@localhost:5432/aiot_db
MIGRATION_DATABASE_URL=postgresql://aiot_user:123@localhost:5432/aiot_db
APP_HOST=0.0.0.0
APP_PORT=8000
APP_DEBUG=false
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

Chạy migration, seed và server:

```bash
alembic upgrade head
python -m app.seed
uvicorn app.main:app --reload
```

Kiểm tra migration:

```bash
alembic current
```

Kết quả đúng:

```text
e003_drop_global_client_unique (head)
```

## 8. Quan sát dữ liệu sau khi test API

Sau khi gọi API bằng Swagger/Postman, mở pgAdmin:

```text
Databases > aiot_db > Schemas > public > Tables
```

Right click từng bảng:

```text
View/Edit Data > All Rows
```

Các bảng nên có dữ liệu sau seed:

| Bảng | Dữ liệu seed |
|---|---|
| `users` | 1 demo user, pairing code `DEMO-001` |
| `devices` | 1 demo device |
| `media_items` | 20 file MP3 demo: 10 bài nhạc + 10 podcast |

Các bảng có dữ liệu sau khi gọi API:

| API đã gọi | Bảng sẽ thấy thêm dòng |
|---|---|
| `/api/emotion-sessions/sync` | `emotion_sessions` |
| `/api/recommendations/request` | `recommendation_requests` |
| `/api/recommendations/action` | `recommendation_requests` |
| `/api/feedback/activity` | `activity_feedback` |
| `/api/feedback/media` | `media_selection_logs` |
| `/api/conversations/respond` | `conversation_requests` |
| `/api/reports/generate` | `tft_reports` |
| `/api/statistics/day|week|month` | `tft_reports` |

## 9. SQL query mẫu trong pgAdmin

Đếm số dòng từng bảng:

```sql
SELECT 'users' AS table_name, COUNT(*) FROM users
UNION ALL SELECT 'devices', COUNT(*) FROM devices
UNION ALL SELECT 'emotion_sessions', COUNT(*) FROM emotion_sessions
UNION ALL SELECT 'recommendation_requests', COUNT(*) FROM recommendation_requests
UNION ALL SELECT 'activity_feedback', COUNT(*) FROM activity_feedback
UNION ALL SELECT 'media_items', COUNT(*) FROM media_items
UNION ALL SELECT 'media_selection_logs', COUNT(*) FROM media_selection_logs
UNION ALL SELECT 'conversation_requests', COUNT(*) FROM conversation_requests
UNION ALL SELECT 'tft_reports', COUNT(*) FROM tft_reports;
```

Xem emotion sessions mới nhất:

```sql
SELECT
    es.id,
    es.client_session_id,
    d.name AS device_name,
    es.emotion_label,
    es.confidence_score,
    es.quality_flag,
    es.client_created_at,
    es.created_at
FROM emotion_sessions es
JOIN devices d ON d.id = es.device_id
ORDER BY es.created_at DESC
LIMIT 20;
```

Xem recommendation payload:

```sql
SELECT
    rr.id,
    es.emotion_label,
    rr.status,
    rr.response_payload,
    rr.created_at
FROM recommendation_requests rr
JOIN emotion_sessions es ON es.id = rr.session_id
ORDER BY rr.created_at DESC
LIMIT 10;
```

Xem media feedback:

```sql
SELECT
    msl.id,
    mi.title,
    mi.media_type,
    msl.selected_category,
    msl.user_intent,
    msl.feedback_score,
    msl.created_at
FROM media_selection_logs msl
JOIN media_items mi ON mi.id = msl.media_item_id
ORDER BY msl.created_at DESC
LIMIT 20;
```

Xem report TFT:

```sql
SELECT
    id,
    period_type,
    period_start,
    period_end,
    data_quality,
    emotion_distribution,
    tft_cards,
    generated_at
FROM tft_reports
ORDER BY generated_at DESC
LIMIT 10;
```

## 10. Test API mẫu

Chi tiết request Postman nằm ở:

```text
docs/api/POSTMAN_TESTING.md
```

Luồng test tối thiểu:

1. Seed database.
2. Dùng token `demo-emoticare-device-token-local-dev`.
3. Sync emotion session.
4. Mở pgAdmin, kiểm tra `emotion_sessions`.
5. Gọi recommendation.
6. Kiểm tra `recommendation_requests`.
7. Gọi feedback/media/conversation/report.
8. Kiểm tra các bảng còn lại.

Các API đọc nhanh để demo không cần mở bảng thủ công:

```text
GET /api/emotion-sessions
GET /api/recommendations
GET /api/media/history
GET /api/reports
```

## 11. Troubleshooting pgAdmin

Nếu không thấy bảng:

- Right click `Tables` > `Refresh`.
- Kiểm tra đang mở đúng database `aiot_db`.
- Kiểm tra `.env` có trỏ đúng PostgreSQL không.
- Chạy `alembic current`, phải thấy `e003_drop_global_client_unique (head)`.
- Chạy `alembic upgrade head` nếu migration chưa lên head.
- Nếu dùng Docker pgAdmin, host nên là `postgres`; nếu dùng pgAdmin cài trên máy, host nên là `localhost`.

Nếu API ghi dữ liệu nhưng pgAdmin không thấy:

- Có thể API đang trỏ sang database khác với database pgAdmin đang mở.
- Kiểm tra biến `DATABASE_URL` trong `.env` hoặc `docker-compose.yml`.
- Với Docker Compose, API dùng `postgres:5432`, còn pgAdmin ngoài Docker dùng `localhost:5432`.

## 12. Quy tắc làm việc với DB

- Không commit `.env`.
- Không commit file database local như `aiot.db`.
- Khi sửa SQLAlchemy model, tạo Alembic migration mới.
- Với PostgreSQL/Supabase thật, kiểm tra migration trước khi chạy.
- Muốn pgAdmin thấy bảng ở database nào thì `DATABASE_URL`/`MIGRATION_DATABASE_URL` phải trỏ đúng database đó trước khi chạy migration.
