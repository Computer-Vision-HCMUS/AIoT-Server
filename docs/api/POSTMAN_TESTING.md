# EmotiCare API Endpoint Testing

Tài liệu này dùng để test Internet Service theo
`docs/Spectification/EmotiCareAIoT/05_Internet Service.md`.

## 0. Base URL

Khi deploy trên Vercel, đặt biến Postman:

```text
BASE_URL=https://<your-vercel-project>.vercel.app
```

Nếu test local trước khi deploy:

```text
BASE_URL=http://localhost:8000
```

Swagger UI:

```text
{{BASE_URL}}/docs
```

## 1. B1 - Tích hợp API Gemini

Mục tiêu test: xác nhận Gemini được dùng cho phần sinh câu trả lời chat và lý do gợi ý.

Biến môi trường cần có trên Vercel:

```env
GEMINI_API_KEY=<google-ai-studio-api-key>
GEMINI_MODEL=gemini-2.5-flash
```

Endpoint test chính:

```http
POST {{BASE_URL}}/api/conversations/respond
X-Device-Token: demo-emoticare-device-token-local-dev
Content-Type: application/json
```

```json
{
  "session_id": "<emotion_sessions.id>",
  "user_message": "toi thay cang thang"
}
```

Kết quả mong đợi: response có `response_text`, `safety_flag`, `cards`; dữ liệu được lưu vào `conversation_requests`.

## 2. B2 - Tải Whisper cho STT

Mục tiêu test: xác nhận endpoint nhận audio và gọi model Whisper qua `faster-whisper`.

Biến môi trường:

```env
WHISPER_MODEL_SIZE=base
```

Endpoint:

```http
POST {{BASE_URL}}/api/stt/transcribe
X-Device-Token: demo-emoticare-device-token-local-dev
Content-Type: multipart/form-data
```

Form-data:

```text
file=@sample.mp3
```

Response mẫu:

```json
{
  "transcript": "noi dung nhan dien",
  "language": "vi",
  "duration_sec": 20.0,
  "stored": false
}
```

## 3. B3 - Cài các hàm gọi API Gemini và model Whisper

Các hàm cần test gián tiếp qua endpoint:

- Gemini: `chat`, sinh `reason` trong recommendation cards.
- Whisper: `stt_service.transcribe_upload`.

Test Gemini qua recommendation:

```http
POST {{BASE_URL}}/api/recommendations/action
X-Device-Token: demo-emoticare-device-token-local-dev
Content-Type: application/json
```

```json
{
  "session_id": "<emotion_sessions.id>"
}
```

Kết quả mong đợi: mỗi card có `reason` ngắn, phù hợp emotion label.

Test Whisper qua `/api/stt/transcribe` như B2.

## 4. B4 - Tải dataset nhạc và podcast

Dataset demo gồm:

- 10 file nhạc, mỗi file 20 giây.
- 10 file podcast/spoken-audio, mỗi file 20 giây.
- File được upload lên Supabase Storage bucket `media-demo`.
- Metadata được seed vào bảng `media_items`.

Chạy upload và seed từ máy local, trỏ `.env` tới Supabase:

```bash
python scripts/upload_media_dataset.py --dataset-dir ./media-dataset
alembic upgrade head
python -m app.seed
```

Kiểm tra category:

```http
GET {{BASE_URL}}/api/media/categories
X-Device-Token: demo-emoticare-device-token-local-dev
```

Test recommend nhạc:

```http
POST {{BASE_URL}}/api/media/music/recommend
X-Device-Token: demo-emoticare-device-token-local-dev
Content-Type: application/json
```

```json
{
  "emotion_label": "stressed"
}
```

Test recommend podcast:

```http
POST {{BASE_URL}}/api/media/podcast/recommend
X-Device-Token: demo-emoticare-device-token-local-dev
Content-Type: application/json
```

```json
{
  "emotion_label": "stressed"
}
```

Kết quả mong đợi: response trả về card có `media_item_id`, `title`, `media_type`, `duration_sec = 20`, `source_url`.

## 5. B5 - Test recommend-action, recommend-music, recommend-podcast, chat và statistic

Trước khi test B5, cần có `session_id`. Tạo session bằng endpoint sync:

```http
POST {{BASE_URL}}/api/emotion-sessions/sync
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

Lấy session đã sync:

```http
GET {{BASE_URL}}/api/emotion-sessions
X-Device-Token: demo-emoticare-device-token-local-dev
```

### 5.1. recommend-action

```http
POST {{BASE_URL}}/api/recommendations/action
X-Device-Token: demo-emoticare-device-token-local-dev
Content-Type: application/json
```

```json
{
  "session_id": "<emotion_sessions.id>"
}
```

### 5.2. recommend-music

```http
POST {{BASE_URL}}/api/media/music/recommend
X-Device-Token: demo-emoticare-device-token-local-dev
Content-Type: application/json
```

```json
{
  "emotion_label": "stressed"
}
```

### 5.3. recommend-podcast

```http
POST {{BASE_URL}}/api/media/podcast/recommend
X-Device-Token: demo-emoticare-device-token-local-dev
Content-Type: application/json
```

```json
{
  "emotion_label": "stressed"
}
```

### 5.4. chat

```http
POST {{BASE_URL}}/api/conversations/respond
X-Device-Token: demo-emoticare-device-token-local-dev
Content-Type: application/json
```

```json
{
  "session_id": "<emotion_sessions.id>",
  "user_message": "toi can mot loi khuyen ngan"
}
```

### 5.5. statistic

Nhóm endpoint statistic theo thiết kế gồm ngày, tuần, tháng:

```http
GET {{BASE_URL}}/api/statistics/day
X-Device-Token: demo-emoticare-device-token-local-dev
```

```http
GET {{BASE_URL}}/api/statistics/week
X-Device-Token: demo-emoticare-device-token-local-dev
```

```http
GET {{BASE_URL}}/api/statistics/month
X-Device-Token: demo-emoticare-device-token-local-dev
```

Kết quả mong đợi: response theo schema TFT summary, có `period_type`, `summary_cards`, `dominant_emotion`, dữ liệu lưu/đọc từ `tft_reports`.

## 6. Deploy trên Vercel thay cho Docker

Không cần chạy `docker compose` cho flow deploy demo. Cách chạy mới:

1. Tạo Supabase project, lấy PostgreSQL URL và Storage bucket `media-demo`.
2. Deploy repo lên Vercel.
3. Thêm Environment Variables trong Vercel: `DATABASE_URL`, `MIGRATION_DATABASE_URL`, `GEMINI_API_KEY`, `GEMINI_MODEL`, `WHISPER_MODEL_SIZE`, `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `SUPABASE_MEDIA_BUCKET`, `CORS_ORIGINS`.
4. Từ máy local, chạy `alembic upgrade head`, upload dataset và `python -m app.seed` với `.env` trỏ tới Supabase.
5. Test toàn bộ endpoint bằng `{{BASE_URL}} = https://<your-vercel-project>.vercel.app`.

## 7. Demo token

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

## 8. Pair device

```http
POST {{BASE_URL}}/api/devices/pair
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

## 9. Heartbeat

```http
POST {{BASE_URL}}/api/devices/heartbeat
X-Device-Token: demo-emoticare-device-token-local-dev
Content-Type: application/json
```

```json
{
  "firmware_version": "1.0.1"
}
```

Response có `server_time`, `status`, `config_version`.

## 10. Các endpoint bổ sung

### Recommendation tổng hợp

Lấy activity + music + podcast cards:

```http
POST {{BASE_URL}}/api/recommendations/request
X-Device-Token: demo-emoticare-device-token-local-dev
Content-Type: application/json
```

```json
{
  "session_id": "<emotion_sessions.id>"
}
```

Kết quả lưu vào `recommendation_requests`.

### Recommendation history

```http
GET {{BASE_URL}}/api/recommendations
X-Device-Token: demo-emoticare-device-token-local-dev
```

### Activity feedback

```http
POST {{BASE_URL}}/api/feedback/activity
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

### Media recommendation tổng hợp

```http
POST {{BASE_URL}}/api/media/recommendations
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

### Media history

```http
GET {{BASE_URL}}/api/media/history
X-Device-Token: demo-emoticare-device-token-local-dev
```

### Media feedback

```http
POST {{BASE_URL}}/api/feedback/media
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

### Conversation safety high

Test safety high:

```http
POST {{BASE_URL}}/api/conversations/respond
X-Device-Token: demo-emoticare-device-token-local-dev
Content-Type: application/json
```

```json
{
  "session_id": "<emotion_sessions.id>",
  "user_message": "toi muon chet va khong muon song nua"
}
```

Kết quả đúng: `safety_flag = high`, card có `severity = alert`, `next_action = contact_support`.

### TFT report

```http
GET {{BASE_URL}}/api/reports/tft-summary?period=daily
X-Device-Token: demo-emoticare-device-token-local-dev
```

```http
POST {{BASE_URL}}/api/reports/generate
X-Device-Token: demo-emoticare-device-token-local-dev
Content-Type: application/json
```

```json
{
  "period_type": "daily"
}
```

Kết quả lưu vào `tft_reports`.

### Report history

```http
GET {{BASE_URL}}/api/reports
X-Device-Token: demo-emoticare-device-token-local-dev
```

### Device config

```http
GET {{BASE_URL}}/api/device-config
X-Device-Token: demo-emoticare-device-token-local-dev
```

Trả về emotion labels, thresholds, quality flags, sync intervals và media categories cho thiết bị.
