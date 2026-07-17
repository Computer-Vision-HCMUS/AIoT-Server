# Sprint Setup and Endpoint Testing

Tài liệu này mô tả toàn bộ các bước cần làm để hoàn thành sprint hiện tại của
EmotiCare AIoT Internet Service và test các endpoint chính. Flow deploy sprint
dùng Vercel cho FastAPI API, Supabase cho PostgreSQL + Storage, không dùng
Docker cho demo cloud.

## 1. Mục tiêu sprint

Các hạng mục cần hoàn thành:

1. Tích hợp Gemini API cho chat và sinh lý do recommendation.
2. Tích hợp Whisper STT qua `faster-whisper`.
3. Cài các hàm gọi Gemini và Whisper trong backend.
4. Chuẩn bị dataset media: 10 file nhạc và 10 file podcast, mỗi file 20 giây.
5. Cài và test các nhóm endpoint:
   - `recommend-action`
   - `recommend-music`
   - `recommend-podcast`
   - `chat`
   - `statistics`
6. Deploy backend FastAPI lên Vercel, dùng Supabase làm database/storage.

## 2. Chuẩn bị tài khoản và secret

Cần chuẩn bị:

- Vercel account để deploy FastAPI.
- Supabase project để dùng PostgreSQL và Storage.
- Google AI Studio API key cho Gemini.
- 20 file `.mp3` hợp lệ bản quyền cho demo media.

Tạo Supabase resources:

1. Tạo project Supabase.
2. Tạo Storage bucket tên `media-demo`.
3. Lấy PostgreSQL connection string.
4. Lấy `SUPABASE_URL`.
5. Lấy `SUPABASE_SERVICE_ROLE_KEY` để upload object từ script backend.

## 3. Cài môi trường local

Tại thư mục repo:

```bash
pip install -r requirements.txt
```

Tạo file `.env` từ `.env.example`, sau đó điền các biến:

```env
DATABASE_URL=postgresql://postgres.<project-ref>:<db-password>@<pooler-host>:5432/postgres?sslmode=require
MIGRATION_DATABASE_URL=postgresql://postgres:<db-password>@db.<project-ref>.supabase.co:5432/postgres?sslmode=require
SUPABASE_URL=https://<project-ref>.supabase.co
SUPABASE_SERVICE_ROLE_KEY=<service-role-key>
SUPABASE_MEDIA_BUCKET=media-demo
GEMINI_API_KEY=<google-ai-studio-api-key>
GEMINI_MODEL=gemini-2.5-flash
WHISPER_MODEL_SIZE=base
CORS_ORIGINS=https://<frontend-domain>,http://localhost:3000,http://localhost:5173
```

Nếu chỉ test local offline nhanh, có thể dùng SQLite:

```env
DATABASE_URL=sqlite:///./aiot.db
MIGRATION_DATABASE_URL=sqlite:///./aiot.db
```

## 4. Migration và seed database

Chạy migration:

```bash
alembic upgrade head
```

Kiểm tra migration head:

```bash
alembic heads
```

Kết quả mong đợi:

```text
e003_drop_global_client_unique (head)
```

Seed dữ liệu demo:

```bash
python -m app.seed
```

Sau seed có thể dùng demo device token:

```text
demo-emoticare-device-token-local-dev
```

## 5. Chuẩn bị dataset nhạc và podcast

Dataset cần đúng cấu trúc:

```text
media-dataset/
  music/
    01-calm-morning-pad.mp3
    ...
    10-small-energy-rise.mp3
  podcast/
    01-breathing-478.mp3
    ...
    10-name-the-feeling.mp3
```

Mỗi file:

- Định dạng `.mp3`.
- Thời lượng 20 giây.
- Có quyền sử dụng hợp lệ cho demo.

Cắt file mẫu bằng `ffmpeg` nếu cần:

```bash
ffmpeg -i source.mp3 -ss 00:00:10 -t 20 -vn -acodec libmp3lame -b:a 128k output.mp3
```

Upload lên Supabase Storage:

```bash
python scripts/upload_media_dataset.py --dataset-dir ./media-dataset
```

Sau khi upload, chạy lại seed để metadata trong `media_items` có `source_url`:

```bash
python -m app.seed
```

## 6. Chạy local để kiểm tra trước

Khởi động API local:

```bash
uvicorn app.main:app --reload
```

Mở Swagger:

```text
http://localhost:8000/docs
```

Chạy test tự động:

```bash
python -m pytest
```

Kết quả mong đợi:

```text
11 passed
```

## 7. Deploy FastAPI lên Vercel

Repo đã có `vercel.json` cấu hình function cho `app/main.py`.
Repo cũng đã có thư mục `supabase/` ở root để các công cụ Supabase nhận diện
project structure.

Nếu giao diện hỏi:

```text
Working directory
Relative path to the directory containing your supabase/ folder
```

thì điền:

```text
.
```

vì cấu trúc repo là:

```text
AIoT-Server/
  supabase/
  app/
  alembic/
  docs/
```

Các bước deploy:

1. Push repo lên Git provider.
2. Import project vào Vercel.
3. Đảm bảo Vercel nhận diện Python/FastAPI app từ `app/main.py`.
4. Thêm Environment Variables trong Vercel:
   - `DATABASE_URL`
   - `MIGRATION_DATABASE_URL`
   - `SUPABASE_URL`
   - `SUPABASE_SERVICE_ROLE_KEY`
   - `SUPABASE_MEDIA_BUCKET`
   - `GEMINI_API_KEY`
   - `GEMINI_MODEL`
   - `WHISPER_MODEL_SIZE`
   - `CORS_ORIGINS`
5. Deploy project.

Sau deploy, đặt Postman variable:

```text
BASE_URL=https://<your-vercel-project>.vercel.app
```

Kiểm tra API:

```http
GET {{BASE_URL}}/
```

Swagger:

```text
{{BASE_URL}}/docs
```

## 8. Cấu hình Postman

Tạo collection variable:

```text
BASE_URL=https://<your-vercel-project>.vercel.app
DEVICE_TOKEN=demo-emoticare-device-token-local-dev
```

Header mặc định cho các endpoint cần auth:

```http
X-Device-Token: {{DEVICE_TOKEN}}
Content-Type: application/json
```

Với STT, dùng `multipart/form-data` thay cho JSON.

## 9. Test endpoint theo thứ tự

### 9.1. Pair device

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

Kết quả mong đợi: response có `device_token`. Có thể dùng token này thay cho demo token.

### 9.2. Heartbeat

```http
POST {{BASE_URL}}/api/devices/heartbeat
X-Device-Token: {{DEVICE_TOKEN}}
Content-Type: application/json
```

```json
{
  "firmware_version": "1.0.1"
}
```

Kết quả mong đợi: response có `server_time`, `status`, `config_version`.

### 9.3. Sync emotion session

```http
POST {{BASE_URL}}/api/emotion-sessions/sync
X-Device-Token: {{DEVICE_TOKEN}}
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

Lấy `session_id`:

```http
GET {{BASE_URL}}/api/emotion-sessions
X-Device-Token: {{DEVICE_TOKEN}}
```

### 9.4. Test B1/B3 - Gemini qua chat

```http
POST {{BASE_URL}}/api/conversations/respond
X-Device-Token: {{DEVICE_TOKEN}}
Content-Type: application/json
```

```json
{
  "session_id": "<emotion_sessions.id>",
  "user_message": "toi thay cang thang"
}
```

Kết quả mong đợi:

- Có `response_text`.
- Có `safety_flag`.
- Có card phù hợp để hiển thị TFT.
- Row mới được lưu vào `conversation_requests`.

### 9.5. Test B2/B3 - Whisper STT

```http
POST {{BASE_URL}}/api/stt/transcribe
X-Device-Token: {{DEVICE_TOKEN}}
Content-Type: multipart/form-data
```

Form-data:

```text
file=@sample.mp3
```

Kết quả mong đợi:

```json
{
  "transcript": "noi dung nhan dien",
  "language": "vi",
  "duration_sec": 20.0,
  "stored": false
}
```

### 9.6. Test B5 - recommend-action

```http
POST {{BASE_URL}}/api/recommendations/action
X-Device-Token: {{DEVICE_TOKEN}}
Content-Type: application/json
```

```json
{
  "session_id": "<emotion_sessions.id>"
}
```

Kết quả mong đợi: trả về action cards, mỗi card có `reason`.

### 9.7. Test B5 - recommend-music

```http
POST {{BASE_URL}}/api/media/music/recommend
X-Device-Token: {{DEVICE_TOKEN}}
Content-Type: application/json
```

```json
{
  "emotion_label": "stressed"
}
```

Kết quả mong đợi: trả về music cards có `source_url` trỏ Supabase Storage.

### 9.8. Test B5 - recommend-podcast

```http
POST {{BASE_URL}}/api/media/podcast/recommend
X-Device-Token: {{DEVICE_TOKEN}}
Content-Type: application/json
```

```json
{
  "emotion_label": "stressed"
}
```

Kết quả mong đợi: trả về podcast cards có `source_url` trỏ Supabase Storage.

### 9.9. Test recommendation tổng hợp

```http
POST {{BASE_URL}}/api/recommendations/request
X-Device-Token: {{DEVICE_TOKEN}}
Content-Type: application/json
```

```json
{
  "session_id": "<emotion_sessions.id>"
}
```

Kết quả mong đợi: trả về 1-5 mixed cards, gồm activity/song/podcast nếu có dữ liệu phù hợp.

### 9.10. Test media recommendation tổng hợp

```http
POST {{BASE_URL}}/api/media/recommendations
X-Device-Token: {{DEVICE_TOKEN}}
Content-Type: application/json
```

```json
{
  "media_type": "both",
  "emotion_label": "stressed",
  "user_intent": "calm down"
}
```

Kết quả mong đợi: trả về media cards và ghi log chọn media khi có feedback.

### 9.11. Test feedback

Activity feedback:

```http
POST {{BASE_URL}}/api/feedback/activity
X-Device-Token: {{DEVICE_TOKEN}}
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

Media feedback:

```http
POST {{BASE_URL}}/api/feedback/media
X-Device-Token: {{DEVICE_TOKEN}}
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

### 9.12. Test B5 - statistics

```http
GET {{BASE_URL}}/api/statistics/day
X-Device-Token: {{DEVICE_TOKEN}}
```

```http
GET {{BASE_URL}}/api/statistics/week
X-Device-Token: {{DEVICE_TOKEN}}
```

```http
GET {{BASE_URL}}/api/statistics/month
X-Device-Token: {{DEVICE_TOKEN}}
```

Kết quả mong đợi:

- `period_type` đúng với endpoint.
- Có summary cards cho TFT.
- Có dominant emotion hoặc dữ liệu tổng hợp tương ứng.
- Dữ liệu liên quan được lưu/đọc từ `tft_reports`.

### 9.13. Test report aliases

```http
GET {{BASE_URL}}/api/reports/tft-summary?period=daily
X-Device-Token: {{DEVICE_TOKEN}}
```

```http
POST {{BASE_URL}}/api/reports/generate
X-Device-Token: {{DEVICE_TOKEN}}
Content-Type: application/json
```

```json
{
  "period_type": "daily"
}
```

### 9.14. Test device config

```http
GET {{BASE_URL}}/api/device-config
X-Device-Token: {{DEVICE_TOKEN}}
```

Kết quả mong đợi: response có emotion labels, thresholds, quality flags, sync intervals và media categories.

## 10. Checklist nghiệm thu sprint

Sprint có thể xem là hoàn thành khi:

- Vercel URL mở được `/` và `/docs`.
- Supabase database đã migrate lên head.
- Seed tạo được demo user, device, media items.
- Storage bucket có đủ 10 music + 10 podcast files.
- `/api/conversations/respond` chạy được với Gemini hoặc fallback hợp lệ.
- `/api/stt/transcribe` nhận file audio và trả transcript.
- `/api/recommendations/action` trả action cards.
- `/api/media/music/recommend` trả music cards.
- `/api/media/podcast/recommend` trả podcast cards.
- `/api/statistics/day`, `/week`, `/month` trả TFT summary.
- `python -m pytest` pass toàn bộ test.
- Postman collection dùng `BASE_URL` Vercel, không còn phụ thuộc Docker.

## 11. Tài liệu liên quan

- `README.md`
- `docs/api/POSTMAN_TESTING.md`
- `docs/ai/cloud/gemini-whisper.md`
- `docs/datasets/MEDIA_DATASET.md`
- `docs/deployment/SUPABASE_DEPLOYMENT.md`
