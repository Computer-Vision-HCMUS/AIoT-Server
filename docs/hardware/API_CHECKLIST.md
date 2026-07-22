# Hardware API Implementation Checklist

Danh sách đầy đủ các API đã implement trong `EdgeApiClient` — ESP32 gửi HTTP request → AIoT-Server.

---

## ✅ Connectivity & Setup

| # | Method | Endpoint | Auth? | Request | Response | Status |
|---|--------|----------|-------|---------|----------|--------|
| 1 | `healthCheck()` | `GET /` | ❌ | — | `{"name":"EmotiCare AIoT Cloud API",...}` | ✅ |
| 2 | `heartbeat()` | `POST /api/devices/heartbeat` | ✅ | `{"firmware_version":"1.0.0"}` | `{"device_id":"...","server_time":"...","status":"online"}` | ✅ |

---

## ✅ UC1 — Emotion Check-in

| # | Method | Endpoint | Auth? | Request | Response | Status |
|---|--------|----------|-------|---------|----------|--------|
| 3 | `syncEmotionSession()` | `POST /api/emotion-sessions/sync` | ✅ | `{"sessions":[{"client_session_id":"...","emotion_label":"happy","confidence_score":0.87,"quality_flag":"clean","client_created_at":"..."}]}` | `{"received_count":1,"total_submitted":1,"received_ids":["..."]}` | ✅ |
| 4 | (follow-up) | `GET /api/emotion-sessions?limit=1` | ✅ | — | `{"items":[{"id":"<uuid>",...}]}` | ✅ |
| 5 | `getActivityRecommendation()` | `POST /api/recommendations/request` | ✅ | `{"session_id":"<uuid>"}` | `{"recommendation_id":"...","emotion_label":"happy","cards":[{"type":"activity","title":"...","body":"..."}],"status":"success"}` | ✅ |

---

## ✅ UC2 — Content Recommendations (Emotion-based)

| # | Method | Endpoint | Auth? | Request | Response | Status |
|---|--------|----------|-------|---------|----------|--------|
| 6 | `getContentRecommendations()` | `POST /api/media/recommendations` | ✅ | `{"emotion_label":"happy","media_type":"both"}` | `{"category":"...","media_type":"both","cards":[{"media_id":"...","media_type":"song","title":"...","creator":"...","duration_sec":225,...}]}` | ✅ |

---

## ✅ UC3 — Full Catalog

| # | Method | Endpoint | Auth? | Request | Response | Status |
|---|--------|----------|-------|---------|----------|--------|
| 7 | `getMusicCatalog()` | `POST /api/media/recommendations` | ✅ | `{"media_type":"song"}` | `{"cards":[{"media_type":"song","title":"...","creator":"...","duration_sec":...},...]}` | ✅ |
| 8 | `getPodcastCatalog()` | `POST /api/media/recommendations` | ✅ | `{"media_type":"podcast"}` | `{"cards":[{"media_type":"podcast","title":"...","creator":"...","duration_sec":...},...]}` | ✅ |

---

## ✅ UC4 — Companion Chat

| # | Method | Endpoint | Auth? | Request Type | Request | Response | Status |
|---|--------|----------|-------|--------------|---------|----------|--------|
| 9 | `uploadAudio()` | `POST /api/stt/transcribe` | ✅ | **multipart/form-data** | `file=<raw PCM bytes>` (field name: `file`, content-type: `application/octet-stream`) | `{"transcript":"...","language":"vi","duration_sec":3.2,"stored":false}` | ✅ |
| 10 | `getCompanionReply()` | `POST /api/conversations/respond` | ✅ | JSON | `{"session_id":"<uuid>","user_message":"I feel calm today"}` | `{"conversation_id":"...","safety_flag":"none","card":{"title":"...","body":"...","next_action":"..."}}` | ✅ |

---

## ✅ UC5 — Emotion Statistics

| # | Method | Endpoint | Auth? | Request | Response | Status |
|---|--------|----------|-------|---------|----------|--------|
| 11 | `getStatistics("Day")` | `GET /api/statistics/day` | ✅ | — | `{"period_type":"daily","emotion_distribution":{"happy":60,"calm":25,...},"trend_summary":"...","data_quality":"enough_data"}` | ✅ |
| 12 | `getStatistics("Week")` | `GET /api/statistics/week` | ✅ | — | (same as above, period_type="weekly") | ✅ |
| 13 | `getStatistics("Month")` | `GET /api/statistics/month` | ✅ | — | (same as above, period_type="monthly") | ✅ |

---

## 📝 Tổng kết

| Tổng API | JSON POST | JSON GET | Multipart POST | Cần auth |
|----------|-----------|----------|----------------|----------|
| **13** | **9** | **3** | **1** | **12** (trừ healthCheck) |

---

## 🔑 Authentication

Mọi request có ✅ trong cột "Auth?" đều gửi header:

```
X-Device-Token: <plain_token_from_NVS>
```

Token được lấy từ:
1. Provisioning portal (captive AP) → nhập pairing code
2. ESP32 gọi `POST /api/devices/pair` → nhận token
3. `NetworkManager` lưu vào NVS namespace `aiot-net`, key `device_token`
4. Mọi lần boot → load token từ NVS

---

## 📂 Service Layer Mapping

Các hàm trong `service.cpp` gọi vào `EdgeApiClient`:

| Service Function | EdgeApiClient Method(s) | Fallback |
|------------------|-------------------------|----------|
| `runEmotionDetection()` | `syncEmotionSession()` | Mock: "Happy / 87%" |
| `getRecommendedActivity()` | `getActivityRecommendation()` | Emotion-based local text |
| `getRecommendedMusic()` | `getMusicCatalog()` | Hardcoded 8-track list |
| `getRecommendedPodcast()` | `getPodcastCatalog()` | Hardcoded 6-episode list |
| `stopAudioCapture()` | `uploadAudio()` | Mock transcript: "Hi AI, how are you?" |
| `getCompanionReply()` | `getCompanionReply()` | Rotating 4-reply mock |
| `getStatisticsByPeriod()` | `getStatistics()` | Hardcoded distribution tables |

---

## 🧪 Test nhanh với curl

```bash
# Lấy token
TOKEN=$(curl -s -X POST http://localhost:8000/api/devices/pair \
  -H "Content-Type: application/json" \
  -d '{"pairing_code":"DEMO-001","device_name":"test-esp32","firmware_version":"1.0.0"}' \
  | python -c "import sys,json; print(json.load(sys.stdin)['device_token'])")

# Test heartbeat (#2)
curl -s -X POST http://localhost:8000/api/devices/heartbeat \
  -H "X-Device-Token: $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"firmware_version":"1.0.0"}'

# Sync emotion (#3)
curl -s -X POST http://localhost:8000/api/emotion-sessions/sync \
  -H "X-Device-Token: $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"sessions":[{"client_session_id":"test-001","emotion_label":"happy","confidence_score":0.87,"quality_flag":"clean","client_created_at":"2025-01-01T00:00:00Z"}]}'

# Lấy session ID (#4)
SESSION_ID=$(curl -s "http://localhost:8000/api/emotion-sessions?limit=1" \
  -H "X-Device-Token: $TOKEN" \
  | python -c "import sys,json; print(json.load(sys.stdin)['items'][0]['id'])")

# Activity recommendation (#5)
curl -s -X POST http://localhost:8000/api/recommendations/request \
  -H "X-Device-Token: $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"session_id\":\"$SESSION_ID\"}"

# Music catalog (#7)
curl -s -X POST http://localhost:8000/api/media/recommendations \
  -H "X-Device-Token: $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"media_type":"song"}'

# Companion chat (#10)
curl -s -X POST http://localhost:8000/api/conversations/respond \
  -H "X-Device-Token: $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"session_id\":\"$SESSION_ID\",\"user_message\":\"I feel calm today\"}"

# Statistics (#11)
curl -s http://localhost:8000/api/statistics/week \
  -H "X-Device-Token: $TOKEN"
```

---

*Checklist cập nhật: 2025-07-21 — tất cả 13 API đều hoạt động và đã build verify thành công.*
