# Hardware — Hướng dẫn Test Kết Nối ESP32 với AIoT-Server

Tài liệu này mô tả cách xác nhận rằng firmware ESP32 đã nạp đúng và có thể thao tác thực sự với AIoT-Server qua Wi-Fi.

---

## Mục lục

1. [Yêu cầu trước khi test](#1-yêu-cầu-trước-khi-test)
2. [Bước 1 — Bật debug log](#2-bước-1--bật-debug-log)
3. [Bước 2 — Nạp firmware và mở Serial Monitor](#3-bước-2--nạp-firmware-và-mở-serial-monitor)
4. [Bước 3 — Provisioning và Pairing lần đầu](#4-bước-3--provisioning-và-pairing-lần-đầu)
5. [Bước 4 — Xác nhận từng Use Case qua Serial](#5-bước-4--xác-nhận-từng-use-case-qua-serial)
6. [Bước 5 — Verify thủ công bằng curl trước khi nạp](#6-bước-5--verify-thủ-công-bằng-curl-trước-khi-nạp)
7. [Đọc kết quả log — nhanh](#7-đọc-kết-quả-log--nhanh)
8. [Sau khi test xong](#8-sau-khi-test-xong)

---

## 1. Yêu cầu trước khi test

| Thứ cần có | Chi tiết |
|---|---|
| ESP32 board | MH-ET LIVE ESP32 DevKit (`mhetesp32devkit`) |
| AIoT-Server đang chạy | `uvicorn app.main:app --reload` trên cùng mạng LAN hoặc localhost |
| Pairing code | Tạo sẵn trong DB, ví dụ `DEMO-001` |
| PlatformIO | Cài trong VS Code hoặc CLI |
| Cable USB | Kết nối ESP32 với máy tính |

Đảm bảo server đang chạy và reachable:

```bash
curl http://<server-ip>:8000/
# Kỳ vọng: {"name":"EmotiCare AIoT Cloud API","status":"running",...}
```

---

## 2. Bước 1 — Bật debug log

Mở `Smart Device/platformio.ini`, thêm `-DEDGE_API_DEBUG=1` vào `build_flags`:

```ini
build_flags =
    -DUSER_SETUP_LOADED=1
    -DST7789_2_DRIVER
    ; ... các flag TFT giữ nguyên ...
    -DEDGE_API_DEBUG=1      ; <-- thêm dòng này
```

> **Lưu ý:** Nhớ xóa flag này trước khi build production để tiết kiệm bộ nhớ flash.

---

## 3. Bước 2 — Nạp firmware và mở Serial Monitor

```bash
# Build và nạp
pio run --environment mhetesp32devkit --target upload

# Mở Serial Monitor (115200 baud)
pio device monitor --baud 115200
```

Hoặc dùng VS Code: nhấn nút **Upload** rồi **Serial Monitor** trong PlatformIO toolbar.

Khi board boot, bạn sẽ thấy:

```
================================
AIoT Hardware Demo Starting...
================================

[Network] Setup AP: EmotiCare-Setup; open http://192.168.4.1
```

Nếu đã provisioning rồi (NVS có SSID):

```
[Network] Connected: <YourSSID>  IP: 192.168.1.xxx
```

---

## 4. Bước 3 — Provisioning và Pairing lần đầu

> Bỏ qua bước này nếu device đã paired (NVS có `device_token`).

**4.1** Kết nối điện thoại hoặc máy tính vào Wi-Fi AP `EmotiCare-Setup` (password: `emotioncare`)

**4.2** Mở trình duyệt vào `http://192.168.4.1`

**4.3** Điền form:

| Trường | Ví dụ |
|---|---|
| Wi-Fi SSID | `HomeNetwork` |
| Wi-Fi Password | `yourpassword` |
| Server URL | `http://192.168.1.10:8000` |
| Pairing Code | `DEMO-001` |

**4.4** Nhấn **Save & Pair**. Serial Monitor sẽ hiển thị:

```
[Network] Connected: HomeNetwork  IP: 192.168.1.105
[Network] POST http://192.168.1.10:8000/api/devices/pair → HTTP 201
[Network] Paired! device_id=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

Device tự restart và từ lần sau không cần pair lại.

---

## 5. Bước 4 — Xác nhận từng Use Case qua Serial

Sau khi paired và online, thao tác trên TFT và quan sát log:

### Quick Test — Heartbeat (không cần thao tác TFT)

Cách nhanh nhất xác nhận kết nối đã hoạt động:

```cpp
// Thêm vào demo_app.cpp hoặc main.cpp trong setup() sau khi paired:
if (edge_api_ && network_->isPaired()) {
    Serial.println("[Test] Sending heartbeat...");
    if (edge_api_->heartbeat()) {
        Serial.println("[Test] ✅ Server connection OK!");
    } else {
        Serial.println("[Test] ❌ Heartbeat failed — check logs");
    }
}
```

Log kỳ vọng khi thành công:

```
[Test] Sending heartbeat...
[EdgeAPI] POST http://192.168.1.10:8000/api/devices/heartbeat  body={"firmware_version":"1.0.0"}
[EdgeAPI] HTTP 200  resp={"device_id":"...","server_time":"...","status":"online",...}
[EdgeAPI] heartbeat OK — status=online  server_time=2025-01-01T12:00:00Z
[Test] ✅ Server connection OK!
```

Nếu thấy dòng cuối thì token + Wi-Fi + server đều hoạt động đúng.

---

### UC1 — Emotion Check-in

Vào màn hình **Check-in** → chờ phân tích cảm xúc

```
[EdgeAPI] POST .../api/emotion-sessions/sync  body={"sessions":[...]}
[EdgeAPI] HTTP 200  resp={"received_count":1,"total_submitted":1,...}
[EdgeAPI] GET .../api/emotion-sessions?limit=1
[EdgeAPI] HTTP 200  resp={"items":[{"id":"<session-uuid>",...}]}
```

### UC1 — Activity Recommendation

Tiếp tục từ Check-in → màn hình **Support**

```
[EdgeAPI] POST .../api/recommendations/request  body={"session_id":"<uuid>"}
[EdgeAPI] HTTP 200  resp={"recommendation_id":"...","cards":[...],...}
```

### UC2/UC3 — Music & Podcast

Vào **Discover** → **Music List** hoặc **Podcast List**

```
[EdgeAPI] POST .../api/media/recommendations  body={"media_type":"song"}
[EdgeAPI] HTTP 200  resp={"cards":[{"title":"...","media_type":"song",...},...]}
```

### UC4 — Companion Chat

Vào **Companion Chat** → gửi tin nhắn

```
[EdgeAPI] POST .../api/conversations/respond  body={"session_id":"<uuid>","user_message":"..."}
[EdgeAPI] HTTP 200  resp={"conversation_id":"...","safety_flag":"none","card":{...}}
```

### UC5 — Statistics

Vào **Insights** → chọn Day / Week / Month

```
[EdgeAPI] GET .../api/statistics/week
[EdgeAPI] HTTP 200  resp={"period_type":"weekly","emotion_distribution":{...},...}
```

---

## 6. Bước 5 — Verify thủ công bằng curl trước khi nạp

Cách nhanh nhất để kiểm tra server hoạt động đúng trước khi cần đến hardware:

```bash
# 1. Lấy device token (thay DEMO-001 bằng pairing code thực tế)
curl -s -X POST http://localhost:8000/api/devices/pair \
  -H "Content-Type: application/json" \
  -d '{"pairing_code":"DEMO-001","device_name":"test-esp32","firmware_version":"1.0.0"}'

# Copy giá trị "device_token" từ response, gán vào biến:
TOKEN="<device_token_từ_response>"

# 1b. Quick test — heartbeat (đơn giản nhất, chỉ cần token)
curl -s -X POST http://localhost:8000/api/devices/heartbeat \
  -H "X-Device-Token: $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"firmware_version":"1.0.0"}'
# Kỳ vọng: {"device_id":"...","server_time":"...","status":"online","config_version":"..."}

# 2. UC1 — Sync emotion session
curl -s -X POST http://localhost:8000/api/emotion-sessions/sync \
  -H "X-Device-Token: $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "sessions": [{
      "client_session_id": "test-001",
      "emotion_label": "happy",
      "confidence_score": 0.87,
      "quality_flag": "clean",
      "client_created_at": "2025-01-01T00:00:00Z"
    }]
  }'

# 3. UC1 — Lấy session UUID vừa tạo
SESSION_ID=$(curl -s "http://localhost:8000/api/emotion-sessions?limit=1" \
  -H "X-Device-Token: $TOKEN" | python -c "import sys,json; print(json.load(sys.stdin)['items'][0]['id'])")

# 4. UC1 — Activity recommendation
curl -s -X POST http://localhost:8000/api/recommendations/request \
  -H "X-Device-Token: $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"session_id\":\"$SESSION_ID\"}"

# 5. UC2/UC3 — Music catalog
curl -s -X POST http://localhost:8000/api/media/recommendations \
  -H "X-Device-Token: $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"media_type":"song"}'

# 6. UC4 — Companion chat
curl -s -X POST http://localhost:8000/api/conversations/respond \
  -H "X-Device-Token: $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"session_id\":\"$SESSION_ID\",\"user_message\":\"I feel calm today\"}"

# 7. UC5 — Statistics
curl -s http://localhost:8000/api/statistics/week \
  -H "X-Device-Token: $TOKEN"
```

Tất cả lệnh trên kỳ vọng trả về HTTP 200 với JSON hợp lệ. Nếu curl OK thì device nạp xong sẽ hoạt động vì dùng cùng endpoint và header.

> **Windows (PowerShell):** Thay `$TOKEN` bằng `$env:TOKEN` và dùng Invoke-RestMethod hoặc dùng Postman thay thế.

---

## 7. Đọc kết quả log — nhanh

| Log thấy | Nghĩa |
|---|---|
| `HTTP 200` hoặc `HTTP 201` | ✅ Server nhận và xử lý thành công |
| `HTTP 401` | ❌ Token sai hoặc chưa paired — chạy lại provisioning |
| `HTTP 404` | ❌ Session UUID không tồn tại — thử check-in lại trước |
| `HTTP 422` | ❌ Request body sai schema — xem log body và so sánh với schemas.py |
| `not connected — skip` | ⚠️ Wi-Fi chưa kết nối |
| `not paired — skip` | ⚠️ Chưa có token trong NVS — cần provisioning |
| `http.begin failed` | ❌ URL server sai hoặc server không chạy |
| Mock data xuất hiện trên TFT | ⚠️ API call thất bại, device dùng fallback — xem log để tìm nguyên nhân |

---

## 8. Sau khi test xong

Xóa flag debug trong `platformio.ini` trước khi build bản production:

```ini
; Xóa hoặc comment dòng này:
; -DEDGE_API_DEBUG=1
```

Rebuild và nạp lại:

```bash
pio run --environment mhetesp32devkit --target upload
```

---

*Tài liệu này áp dụng cho firmware EmotiCare ESP32 sử dụng `EdgeApiClient` kết nối trực tiếp với AIoT-Server (không qua edge-server trung gian).*
