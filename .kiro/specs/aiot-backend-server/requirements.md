# Requirements Document

## Introduction

AIoT Backend Server là hệ thống backend Python phục vụ hai sản phẩm trong dự án SmartDesk Buddy:

- **SmartClock** — Thiết bị hỗ trợ học tập và sinh hoạt chạy trên ESP32-S3, bao gồm Pomodoro Timer, Sleep Monitoring, Seminar Practice, Flappy Bird và Music Player.
- **VisionDriveAI** — Thiết bị phát hiện mất tập trung cho người lái xe máy, bao gồm phát hiện ngủ gật, cầm điện thoại, cảnh báo leo thang và chấm điểm an toàn theo chuyến đi.

Server đóng vai trò trung tâm tiếp nhận dữ liệu từ các thiết bị ESP32 qua WiFi, lưu trữ dữ liệu time-series và session logs, cung cấp REST API cho ESP32 và web dashboard, đồng thời hỗ trợ phân tích AI (sleep scoring, seminar evaluation, safety scoring).

Scope ban đầu: thiết kế database + xây dựng server + REST API endpoints + mock data để testing.

---

## Glossary

- **ESP32**: Vi điều khiển ESP32-S3 chạy firmware SmartClock hoặc VisionDriveAI.
- **Server**: Python backend server của dự án AIoT SmartDesk Buddy.
- **API**: REST API do Server cung cấp để ESP32 và client giao tiếp.
- **Device**: Một thiết bị ESP32 đã đăng ký với Server (SmartClock hoặc VisionDriveAI).
- **Session**: Một phiên hoạt động có thời điểm bắt đầu và kết thúc (Pomodoro session, Sleep session, Trip session).
- **Pomodoro_Session**: Một phiên học tập hoặc nghỉ ngơi theo phương pháp Pomodoro.
- **Sleep_Session**: Một phiên theo dõi giấc ngủ, bao gồm nhiều sensor batch.
- **Sensor_Batch**: Một lô dữ liệu cảm biến (sound level, light level) được gửi mỗi 240 giây trong Sleep_Session.
- **Seminar_Recording**: Một bản ghi âm bài thuyết trình cùng kết quả đánh giá AI.
- **Game_Score**: Điểm số của một lượt chơi Flappy Bird.
- **Timer_Config**: Cấu hình thời gian Pomodoro (study duration, break duration) của một Device.
- **Sleep_Config**: Cấu hình giấc ngủ (alarm time, sleep duration) của một Device.
- **Trip**: Một chuyến đi của VisionDriveAI, bao gồm nhiều distraction event.
- **Distraction_Event**: Một sự kiện mất tập trung được phát hiện trong Trip (ngủ gật, nhìn lạc hướng, cầm điện thoại).
- **Safety_Score**: Điểm an toàn từ 0–100 được tính sau khi kết thúc Trip.
- **Sleep_Score**: Điểm chất lượng giấc ngủ từ 0–100 được tính sau khi kết thúc Sleep_Session.
- **Mock_Data**: Dữ liệu giả lập dùng để kiểm thử API mà không cần thiết bị thật.

---

## Requirements

### Requirement 1: Quản lý thiết bị (Device Management)

**User Story:** Là một ESP32 device, tôi muốn đăng ký và xác thực với Server, để Server có thể nhận diện và phân biệt dữ liệu từ từng thiết bị.

#### Tiêu chí chấp nhận

1. WHEN một ESP32 gửi yêu cầu đăng ký với `device_id` và `device_type` (`smartclock` hoặc `visiondrive`), THE Server SHALL tạo bản ghi Device mới và trả về `device_token` để xác thực các request tiếp theo.
2. IF một ESP32 gửi yêu cầu đăng ký với `device_id` đã tồn tại, THEN THE Server SHALL trả về `device_token` hiện có thay vì tạo bản ghi mới.
3. WHEN một ESP32 gửi request kèm `device_token` hợp lệ, THE Server SHALL xử lý request đó.
4. IF một ESP32 gửi request với `device_token` không hợp lệ hoặc thiếu, THEN THE Server SHALL trả về HTTP 401 kèm thông báo lỗi mô tả rõ nguyên nhân.
5. THE Server SHALL lưu trữ `device_id`, `device_type`, `created_at` và `last_seen_at` cho mỗi Device.
6. WHEN một ESP32 gửi bất kỳ request nào thành công, THE Server SHALL cập nhật `last_seen_at` của Device tương ứng.

---

### Yêu cầu 2: Đồng bộ cấu hình Pomodoro (Timer Config Sync)

**User Story:** Là một SmartClock device, tôi muốn lưu và lấy cấu hình Pomodoro từ Server, để cấu hình được khôi phục sau khi thiết bị khởi động lại.

#### Tiêu chí chấp nhận

1. WHEN một SmartClock gửi yêu cầu cập nhật Timer_Config với `study_duration` và `break_duration` hợp lệ, THE Server SHALL lưu cấu hình và trả về cấu hình đã lưu.
2. WHEN một SmartClock gửi yêu cầu lấy Timer_Config, THE Server SHALL trả về cấu hình hiện tại của Device đó.
3. IF một SmartClock chưa có Timer_Config, THEN THE Server SHALL trả về cấu hình mặc định (`study_duration` = 25 phút, `break_duration` = 5 phút).
4. IF `study_duration` hoặc `break_duration` nhỏ hơn 1 phút hoặc lớn hơn 120 phút, THEN THE Server SHALL trả về HTTP 422 kèm thông báo lỗi mô tả giá trị không hợp lệ.
5. THE Server SHALL lưu trữ `study_duration`, `break_duration` và `updated_at` cho mỗi Timer_Config.

---

### Yêu cầu 3: Ghi nhận phiên Pomodoro (Pomodoro Session Logging)

**User Story:** Là một SmartClock device, tôi muốn ghi lại mỗi phiên Pomodoro hoàn thành lên Server, để người dùng có thể xem lịch sử và thống kê năng suất.

#### Tiêu chí chấp nhận

1. WHEN một SmartClock gửi dữ liệu Pomodoro_Session với `timestamp`, `duration` và `session_type` hợp lệ, THE Server SHALL lưu session và trả về `session_id` cùng dữ liệu đã lưu.
2. THE Server SHALL chấp nhận `session_type` là `study` hoặc `break`.
3. IF `session_type` không phải `study` hoặc `break`, THEN THE Server SHALL trả về HTTP 422 kèm thông báo lỗi.
4. IF `duration` nhỏ hơn hoặc bằng 0, THEN THE Server SHALL trả về HTTP 422 kèm thông báo lỗi.
5. WHEN một client gửi yêu cầu lấy danh sách Pomodoro_Session của một Device, THE Server SHALL trả về danh sách session được sắp xếp theo `timestamp` giảm dần.
6. THE Server SHALL hỗ trợ lọc danh sách Pomodoro_Session theo khoảng thời gian (`from_date`, `to_date`).

---

### Yêu cầu 4: Theo dõi giấc ngủ (Sleep Monitoring)

**User Story:** Là một SmartClock device, tôi muốn gửi dữ liệu cảm biến trong quá trình ngủ và nhận Sleep_Score sau khi kết thúc, để người dùng biết chất lượng giấc ngủ của mình.

#### Tiêu chí chấp nhận

1. WHEN một SmartClock gửi yêu cầu bắt đầu Sleep_Session, THE Server SHALL tạo Sleep_Session mới với trạng thái `active` và trả về `session_id`.
2. WHILE một Sleep_Session đang ở trạng thái `active`, WHEN một SmartClock gửi Sensor_Batch với `sound_level`, `light_level` và `timestamp`, THE Server SHALL lưu batch đó vào Sleep_Session tương ứng.
3. IF một SmartClock gửi Sensor_Batch cho một `session_id` không tồn tại hoặc không ở trạng thái `active`, THEN THE Server SHALL trả về HTTP 404 hoặc HTTP 409 kèm thông báo lỗi phù hợp.
4. WHEN một SmartClock gửi yêu cầu kết thúc Sleep_Session, THE Server SHALL cập nhật trạng thái thành `completed`, tính Sleep_Score dựa trên `duration`, `sound_level` trung bình và `light_level` trung bình, rồi trả về Sleep_Score.
5. THE Server SHALL tính Sleep_Score theo thang điểm từ 0 đến 100.
6. WHEN một client gửi yêu cầu lấy lịch sử Sleep_Session của một Device, THE Server SHALL trả về danh sách session được sắp xếp theo thời gian bắt đầu giảm dần.
7. THE Server SHALL lưu trữ `start_time`, `end_time`, `sleep_score` và danh sách Sensor_Batch cho mỗi Sleep_Session.

---

### Yêu cầu 5: Đồng bộ cấu hình giấc ngủ (Sleep Config Sync)

**User Story:** Là một SmartClock device, tôi muốn lưu và lấy cấu hình báo thức từ Server, để cấu hình được khôi phục sau khi thiết bị khởi động lại.

#### Tiêu chí chấp nhận

1. WHEN một SmartClock gửi yêu cầu cập nhật Sleep_Config với `alarm_enabled`, `alarm_time` và `sleep_duration` hợp lệ, THE Server SHALL lưu cấu hình và trả về cấu hình đã lưu.
2. WHEN một SmartClock gửi yêu cầu lấy Sleep_Config, THE Server SHALL trả về cấu hình hiện tại của Device đó.
3. IF một SmartClock chưa có Sleep_Config, THEN THE Server SHALL trả về cấu hình mặc định (`alarm_enabled` = false, `sleep_duration` = 480 phút).
4. IF `alarm_time` được cung cấp nhưng không đúng định dạng `HH:MM`, THEN THE Server SHALL trả về HTTP 422 kèm thông báo lỗi.
5. IF `sleep_duration` nhỏ hơn 30 phút hoặc lớn hơn 720 phút, THEN THE Server SHALL trả về HTTP 422 kèm thông báo lỗi.

---

### Yêu cầu 6: Đánh giá bài thuyết trình (Seminar Evaluation)

**User Story:** Là một SmartClock device, tôi muốn gửi bản ghi âm bài thuyết trình lên Server và nhận kết quả đánh giá AI, để người dùng cải thiện kỹ năng trình bày.

#### Tiêu chí chấp nhận

1. WHEN một SmartClock gửi file audio hợp lệ (WAV hoặc MP3) lên Server, THE Server SHALL lưu file và tạo Seminar_Recording với trạng thái `pending`.
2. WHEN một Seminar_Recording ở trạng thái `pending`, THE Server SHALL xử lý đánh giá và cập nhật kết quả bao gồm `clarity_score`, `speed_score`, `noise_score` và `confidence_score`.
3. THE Server SHALL trả về kết quả đánh giá với các điểm số theo thang 0–100 cho từng metric.
4. WHEN một SmartClock gửi yêu cầu lấy kết quả của một Seminar_Recording, THE Server SHALL trả về trạng thái hiện tại và kết quả đánh giá nếu đã hoàn thành.
5. IF file audio gửi lên không phải định dạng WAV hoặc MP3, THEN THE Server SHALL trả về HTTP 422 kèm thông báo lỗi.
6. IF file audio vượt quá 50MB, THEN THE Server SHALL trả về HTTP 413 kèm thông báo lỗi.
7. WHEN một client gửi yêu cầu lấy danh sách Seminar_Recording của một Device, THE Server SHALL trả về danh sách được sắp xếp theo thời gian tạo giảm dần.
8. THE Server SHALL lưu trữ `file_path`, `duration`, `created_at`, `status` và kết quả đánh giá cho mỗi Seminar_Recording.

---

### Yêu cầu 7: Bảng xếp hạng Flappy Bird (Game Leaderboard)

**User Story:** Là một SmartClock device, tôi muốn gửi điểm số Flappy Bird lên Server và xem bảng xếp hạng, để người dùng có thể so sánh thành tích.

#### Tiêu chí chấp nhận

1. WHEN một SmartClock gửi Game_Score với `score` và `timestamp` hợp lệ, THE Server SHALL lưu điểm số và trả về `score_id` cùng thứ hạng hiện tại của Device đó.
2. IF `score` nhỏ hơn 0, THEN THE Server SHALL trả về HTTP 422 kèm thông báo lỗi.
3. WHEN một client gửi yêu cầu lấy bảng xếp hạng, THE Server SHALL trả về danh sách top điểm số cao nhất, mỗi Device chỉ xuất hiện một lần với điểm cao nhất.
4. THE Server SHALL hỗ trợ tham số `limit` để giới hạn số lượng kết quả trả về trong bảng xếp hạng (mặc định 10, tối đa 100).
5. WHEN một client gửi yêu cầu lấy lịch sử Game_Score của một Device, THE Server SHALL trả về tất cả điểm số của Device đó được sắp xếp theo `score` giảm dần.

---

### Yêu cầu 8: Theo dõi chuyến đi VisionDriveAI (Trip Tracking)

**User Story:** Là một VisionDriveAI device, tôi muốn ghi lại các sự kiện mất tập trung trong chuyến đi và nhận Safety_Score sau khi kết thúc, để người lái hiểu được chất lượng lái xe của mình.

#### Tiêu chí chấp nhận

1. WHEN một VisionDriveAI device gửi yêu cầu bắt đầu Trip, THE Server SHALL tạo Trip mới với trạng thái `active` và trả về `trip_id`.
2. WHILE một Trip đang ở trạng thái `active`, WHEN một VisionDriveAI device gửi Distraction_Event với `timestamp`, `event_type` và `severity`, THE Server SHALL lưu event vào Trip tương ứng.
3. THE Server SHALL chấp nhận `event_type` là `drowsiness` (ngủ gật), `gaze_distraction` (nhìn lạc hướng) hoặc `phone_use` (cầm điện thoại).
4. THE Server SHALL chấp nhận `severity` là `low`, `medium` hoặc `high`.
5. IF một VisionDriveAI device gửi Distraction_Event cho `trip_id` không tồn tại hoặc không ở trạng thái `active`, THEN THE Server SHALL trả về HTTP 404 hoặc HTTP 409 kèm thông báo lỗi phù hợp.
6. WHEN một VisionDriveAI device gửi yêu cầu kết thúc Trip, THE Server SHALL cập nhật trạng thái thành `completed`, tính Safety_Score dựa trên số lượng và mức độ nghiêm trọng của Distraction_Event, rồi trả về Safety_Score.
7. THE Server SHALL tính Safety_Score theo thang điểm từ 0 đến 100, trong đó 100 là không có sự kiện mất tập trung.
8. WHEN một client gửi yêu cầu lấy lịch sử Trip của một Device, THE Server SHALL trả về danh sách Trip được sắp xếp theo thời gian bắt đầu giảm dần.
9. THE Server SHALL lưu trữ `start_time`, `end_time`, `safety_score` và danh sách Distraction_Event cho mỗi Trip.

---

### Yêu cầu 9: REST API và cấu trúc response chuẩn

**User Story:** Là một developer, tôi muốn Server có REST API nhất quán và dễ dự đoán, để việc tích hợp từ ESP32 và web dashboard trở nên đơn giản.

#### Tiêu chí chấp nhận

1. THE Server SHALL trả về tất cả response dưới dạng JSON với `Content-Type: application/json`.
2. THE Server SHALL sử dụng HTTP status code chuẩn: 200 cho thành công, 201 cho tạo mới, 400 cho request không hợp lệ, 401 cho xác thực thất bại, 404 cho resource không tìm thấy, 409 cho conflict, 413 cho payload quá lớn, 422 cho dữ liệu không hợp lệ, 500 cho lỗi server.
3. IF Server gặp lỗi, THEN THE Server SHALL trả về JSON với trường `error` mô tả lỗi và trường `detail` cung cấp thông tin chi tiết.
4. THE Server SHALL cung cấp endpoint `GET /health` trả về trạng thái hoạt động của Server và database.
5. THE Server SHALL cung cấp tài liệu API tự động (OpenAPI/Swagger) tại endpoint `/docs`.
6. THE Server SHALL hỗ trợ CORS để cho phép web dashboard truy cập API từ browser.

---

### Yêu cầu 10: Mock data và môi trường testing

**User Story:** Là một developer, tôi muốn có mock data sẵn có trong môi trường development, để có thể kiểm thử API mà không cần thiết bị ESP32 thật.

#### Tiêu chí chấp nhận

1. THE Server SHALL cung cấp script seed data tạo ít nhất 2 SmartClock device và 1 VisionDriveAI device với dữ liệu mẫu đầy đủ.
2. THE Server SHALL tạo mock data bao gồm: tối thiểu 10 Pomodoro_Session, 3 Sleep_Session với Sensor_Batch, 2 Seminar_Recording, 5 Game_Score và 3 Trip với Distraction_Event.
3. WHEN script seed data được chạy, THE Server SHALL xóa dữ liệu cũ và tạo lại toàn bộ mock data để đảm bảo tính nhất quán.
4. THE Server SHALL cung cấp file `.env.example` mô tả tất cả biến môi trường cần thiết để chạy server.
5. THE Server SHALL có thể khởi động và phục vụ tất cả API endpoints mà không cần kết nối đến thiết bị ESP32 thật.

---

### Yêu cầu 11: Thiết kế database phù hợp với IoT

**User Story:** Là một developer, tôi muốn database được thiết kế phù hợp với đặc thù IoT (time-series data, nhiều device, session logs), để hệ thống có thể mở rộng và truy vấn hiệu quả.

#### Tiêu chí chấp nhận

1. THE Server SHALL sử dụng SQLite cho môi trường development và hỗ trợ cấu hình chuyển sang PostgreSQL cho production thông qua biến môi trường.
2. THE Server SHALL tổ chức schema database với các bảng riêng biệt cho: `devices`, `timer_configs`, `sleep_configs`, `pomodoro_sessions`, `sleep_sessions`, `sleep_sensor_batches`, `seminar_recordings`, `game_scores`, `trips` và `distraction_events`.
3. THE Server SHALL đánh index trên các cột thường xuyên được truy vấn: `device_id`, `timestamp`, `session_id`, `trip_id` và `created_at`.
4. THE Server SHALL sử dụng timestamp dạng UTC ISO 8601 cho tất cả trường thời gian.
5. THE Server SHALL đảm bảo tính toàn vẹn dữ liệu thông qua foreign key constraints giữa các bảng liên quan.
