# EmotiCare API Mock Data and Postman Testing

Tài liệu này dùng để test Internet Service theo
`docs/Spectification/EmotiCareAIoT/05_Internet Service.md`.

## 1. Init database

PostgreSQL local trong `.env`:

```env
DATABASE_URL=postgresql://aiot_user:123@localhost:5432/aiot_db
MIGRATION_DATABASE_URL=postgresql://aiot_user:123@localhost:5432/aiot_db
```

Chạy migration và seed:

```bash
alembic upgrade head
python -m app.seed
uvicorn app.main:app --reload
```

Swagger UI:

```text
http://localhost:8000/docs
```

## 2. Demo token

Seed tạo user demo có pairing code:

```text
DEMO-001
```

Seed cũng tạo sẵn device demo với token:

```text
demo-emoticare-device-token-local-dev
```

Header dùng trong Postman:

```http
X-Device-Token: demo-emoticare-device-token-local-dev
```

hoặc:

```http
Authorization: Bearer demo-emoticare-device-token-local-dev
```

## 3. Pair device

```http
POST http://localhost:8000/api/devices/pair
Content-Type: application/json
```

```json
{
  "pairing_code": "DEMO-001",
  "device_name": "ESP32-S3 EmotiCare",
  "firmware_version": "1.0.0"
}
```

Lưu `device_token` trả về để test các endpoint còn lại.

## 4. Heartbeat

```http
POST http://localhost:8000/api/devices/heartbeat
X-Device-Token: demo-emoticare-device-token-local-dev
Content-Type: application/json
```

```json
{
  "firmware_version": "1.0.1"
}
```

Response có `server_time`, `status`, `config_version`.

## 5. Sync emotion sessions

```http
POST http://localhost:8000/api/emotion-sessions/sync
X-Device-Token: demo-emoticare-device-token-local-dev
Content-Type: application/json
```

```json
{
  "sessions": [
    {
      "client_session_id": "edge-session-001",
      "emotion_label": "stressed",
      "confidence_score": 0.82,
      "quality_flag": "clean",
      "inference_latency_ms": 850,
      "client_created_at": "2026-06-29T08:00:00Z"
    }
  ]
}
```

Endpoint này idempotent theo `device_id + client_session_id`.

Xem session đã sync:

```http
GET http://localhost:8000/api/emotion-sessions
X-Device-Token: demo-emoticare-device-token-local-dev
```

## 6. Recommendation request

Lấy `session_id` cloud trong database table `emotion_sessions`, rồi gọi:

```http
POST http://localhost:8000/api/recommendations/request
X-Device-Token: demo-emoticare-device-token-local-dev
Content-Type: application/json
```

```json
{
  "session_id": "<emotion_sessions.id>"
}
```

Kết quả lưu vào `recommendation_requests`.

Xem recommendation history:

```http
GET http://localhost:8000/api/recommendations
X-Device-Token: demo-emoticare-device-token-local-dev
```

## 7. Activity feedback

```http
POST http://localhost:8000/api/feedback/activity
X-Device-Token: demo-emoticare-device-token-local-dev
Content-Type: application/json
```

```json
{
  "recommendation_id": "<recommendation_requests.id>",
  "activity_type": "breathing",
  "selected": true,
  "feedback_score": 5
}
```

Kết quả lưu vào `activity_feedback`.

## 8. Media categories and recommendations

```http
GET http://localhost:8000/api/media/categories
X-Device-Token: demo-emoticare-device-token-local-dev
```

```http
POST http://localhost:8000/api/media/recommendations
X-Device-Token: demo-emoticare-device-token-local-dev
Content-Type: application/json
```

```json
{
  "media_type": "both",
  "emotion_label": "stressed",
  "user_intent": "calm down"
}
```

Media catalog nằm trong `media_items`.

Xem lịch sử chọn media:

```http
GET http://localhost:8000/api/media/history
X-Device-Token: demo-emoticare-device-token-local-dev
```

## 9. Media feedback

```http
POST http://localhost:8000/api/feedback/media
X-Device-Token: demo-emoticare-device-token-local-dev
Content-Type: application/json
```

```json
{
  "session_id": "<emotion_sessions.id>",
  "media_item_id": "<media_items.id>",
  "user_intent": "calm down",
  "feedback_score": 4
}
```

Kết quả lưu vào `media_selection_logs`.

## 10. Conversation response

```http
POST http://localhost:8000/api/conversations/respond
X-Device-Token: demo-emoticare-device-token-local-dev
Content-Type: application/json
```

```json
{
  "session_id": "<emotion_sessions.id>",
  "user_message": "toi thay cang thang"
}
```

Kết quả lưu vào `conversation_requests`.

Test safety high:

```json
{
  "session_id": "<emotion_sessions.id>",
  "user_message": "toi muon chet va khong muon song nua"
}
```

Kết quả đúng: `safety_flag = high`, card có `severity = alert`, `next_action = contact_support`.

## 11. TFT report

```http
GET http://localhost:8000/api/reports/tft-summary?period=daily
X-Device-Token: demo-emoticare-device-token-local-dev
```

```http
POST http://localhost:8000/api/reports/generate
X-Device-Token: demo-emoticare-device-token-local-dev
Content-Type: application/json
```

```json
{
  "period_type": "daily"
}
```

Kết quả lưu vào `tft_reports`.

Xem report history:

```http
GET http://localhost:8000/api/reports
X-Device-Token: demo-emoticare-device-token-local-dev
```

## 12. Device config

```http
GET http://localhost:8000/api/device-config
X-Device-Token: demo-emoticare-device-token-local-dev
```

Trả về emotion labels, thresholds, quality flags, sync intervals và media categories cho thiết bị.
