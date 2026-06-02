# API Mock Data and Postman Testing

Tài liệu này hướng dẫn init database bằng dữ liệu mock để test API bằng Postman.

## 1. Chuẩn bị `.env`

Nếu dùng Supabase, điền connection string thật:

```env
DATABASE_URL=postgresql://postgres.<project-ref>:<db-password>@<pooler-host>:5432/postgres?sslmode=require
MIGRATION_DATABASE_URL=postgresql://postgres:<db-password>@db.<project-ref>.supabase.co:5432/postgres?sslmode=require
```

Nếu chỉ test local bằng SQLite:

```env
DATABASE_URL=sqlite:///./aiot.db
MIGRATION_DATABASE_URL=sqlite:///./aiot.db
```

## 2. Init schema và seed data

Chạy migration trước để tạo toàn bộ bảng:

```bash
alembic upgrade head
```

Sau đó insert dữ liệu mock:

```bash
python -m app.seed
```

Seed script là idempotent cho 2 thiết bị demo. Chạy lại script sẽ refresh dữ liệu mock của 2 thiết bị này.

## 3. Token mẫu

SmartClock:

```text
dev-smartclock-token
```

VisionDrive:

```text
dev-visiondrive-token
```

Trong Postman, thêm header:

```http
Authorization: Bearer dev-smartclock-token
```

hoặc:

```http
X-Device-Token: dev-smartclock-token
```

## 4. Chạy server

```bash
uvicorn app.main:app --reload
```

Base URL:

```text
http://localhost:8000
```

Swagger UI:

```text
http://localhost:8000/docs
```

## 5. Request mẫu cho Postman

### Health check

```http
GET http://localhost:8000/health
```

### Get current SmartClock

```http
GET http://localhost:8000/devices/me
Authorization: Bearer dev-smartclock-token
```

### Register new device

```http
POST http://localhost:8000/devices/register
Content-Type: application/json
```

```json
{
  "device_id": "smartclock-postman-001",
  "device_type": "smartclock"
}
```

### Get SmartClock timer config

```http
GET http://localhost:8000/smartclock/timer-config
Authorization: Bearer dev-smartclock-token
```

### Update SmartClock sleep config

```http
PUT http://localhost:8000/smartclock/sleep-config
Authorization: Bearer dev-smartclock-token
Content-Type: application/json
```

```json
{
  "alarm_enabled": true,
  "alarm_time": "06:45",
  "sleep_duration": 480
}
```

### Create Pomodoro session

```http
POST http://localhost:8000/smartclock/pomodoro-sessions
Authorization: Bearer dev-smartclock-token
Content-Type: application/json
```

```json
{
  "timestamp": "2026-05-29T08:00:00Z",
  "duration": 1500,
  "session_type": "study"
}
```

### Create Sleep session

```http
POST http://localhost:8000/smartclock/sleep-sessions
Authorization: Bearer dev-smartclock-token
Content-Type: application/json
```

```json
{
  "start_time": "2026-05-29T23:00:00Z"
}
```

Ghi lại `id` trong response để dùng cho các API tiếp theo.

### Add Sleep sensor batch

```http
POST http://localhost:8000/smartclock/sleep-sessions/{session_id}/sensor-batches
Authorization: Bearer dev-smartclock-token
Content-Type: application/json
```

```json
{
  "timestamp": "2026-05-30T01:00:00Z",
  "sound_level": 21.5,
  "light_level": 8.0
}
```

### Upsert Sleep quality report

```http
PUT http://localhost:8000/smartclock/sleep-sessions/{session_id}/quality-report
Authorization: Bearer dev-smartclock-token
Content-Type: application/json
```

```json
{
  "duration_minutes": 450,
  "quality_label": "good",
  "duration_score": 37,
  "sound_score": 25,
  "light_score": 28,
  "avg_sound_level": 18.2,
  "avg_light_level": 7.5,
  "duration_issue": true,
  "noise_issue": false,
  "light_issue": false,
  "recommendation": "Try sleeping 30 minutes longer to reach the 8-hour target."
}
```

### Get Sleep quality report

```http
GET http://localhost:8000/smartclock/sleep-sessions/{session_id}/quality-report
Authorization: Bearer dev-smartclock-token
```

### Start VisionDrive trip

```http
POST http://localhost:8000/visiondrive/trips
Authorization: Bearer dev-visiondrive-token
Content-Type: application/json
```

```json
{
  "start_time": "2026-05-29T09:00:00Z"
}
```

### Add distraction event

```http
POST http://localhost:8000/visiondrive/trips/{trip_id}/distraction-events
Authorization: Bearer dev-visiondrive-token
Content-Type: application/json
```

```json
{
  "timestamp": "2026-05-29T09:05:00Z",
  "event_type": "phone_use",
  "severity": "high"
}
```

### End VisionDrive trip

```http
POST http://localhost:8000/visiondrive/trips/{trip_id}/end
Authorization: Bearer dev-visiondrive-token
Content-Type: application/json
```

```json
{
  "end_time": "2026-05-29T09:30:00Z",
  "safety_score": 82
}
```

## 6. Test lỗi auth nhanh

Dùng SmartClock token gọi VisionDrive API:

```http
POST http://localhost:8000/visiondrive/trips
Authorization: Bearer dev-smartclock-token
Content-Type: application/json
```

```json
{
  "start_time": "2026-05-29T09:00:00Z"
}
```

Kết quả đúng là HTTP `403`, vì token SmartClock không được gọi API VisionDrive.
