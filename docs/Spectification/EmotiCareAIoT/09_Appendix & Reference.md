# 09. Phụ lục và tài liệu tham khảo

## 9.1. Thuật ngữ

| Thuật ngữ | Mô tả |
| --------- | ----- |
| EmotiCare AIoT | Thiết bị AIoT thông minh đồng hành và chăm sóc sức khỏe cảm xúc |
| Intelligent Emotional Companion | Định vị sản phẩm như một thiết bị đồng hành cảm xúc thông minh |
| Thiết bị biên | Thiết bị phần cứng đặt gần người dùng, có microphone, màn hình TFT, nút bấm và Wi-Fi |
| Màn hình TFT | Màn hình theo dõi chính của sản phẩm trong phiên bản này |
| Edge AI | Mô hình AI chạy cục bộ để xử lý nhận diện cảm xúc bằng giọng nói |
| Dịch vụ Cloud | Phần máy chủ phục vụ gợi ý, chọn nội dung, trò chuyện, báo cáo và đồng bộ dữ liệu |
| Dịch vụ gợi ý nội dung | Dịch vụ Cloud chọn bài hát/podcast theo ngữ cảnh cảm xúc, nhóm nội dung, chủ đích và lịch sử phản hồi |
| Phiên cảm xúc | Bản ghi của một lần kiểm tra cảm xúc |
| Nhãn cảm xúc | Nhãn cảm xúc như vui vẻ, bình thường, căng thẳng, buồn bã, tức giận, mệt mỏi |
| Điểm tin cậy | Độ tin cậy của kết quả nhận diện cảm xúc |
| Thẻ hoạt động | Thẻ gợi ý hoạt động rút gọn để hiển thị trên TFT |
| Thẻ bài hát | Thẻ bài hát rút gọn gồm tiêu đề, người sáng tạo, thời lượng, nhóm nội dung và lý do gợi ý |
| Thẻ podcast | Thẻ podcast rút gọn gồm tiêu đề, người sáng tạo, thời lượng, nhóm nội dung và lý do gợi ý |
| Thẻ phản hồi | Thẻ phản hồi trò chuyện rút gọn để hiển thị trên TFT |
| Thẻ báo cáo TFT | Thẻ báo cáo ngắn gồm nhận định chính theo ngày, tuần hoặc tháng |
| Dữ liệu chưa đủ | Trạng thái báo cáo khi dữ liệu chưa đủ để tạo nhận định rõ ràng |

## 9.2. Bảng tham chiếu tình huống sử dụng

| ID | Tình huống sử dụng | Đầu vào | Đầu ra | Xử lý chính | Mục tiêu thời gian |
| -- | -------- | ----- | ------ | ----------- | ------------------ |
| UC-01 | Speech Emotion Recognition | Giọng nói người dùng | Emotion label, confidence, emotion session | Edge AI | <= 15 giây |
| UC-02 | Gợi ý hoạt động cải thiện tâm trạng | Emotion label và lịch sử đã đồng bộ | 5 activity cards trên TFT | Cloud + TFT | <= 20 giây khi có Internet |
| UC-03 | Lựa chọn bài hát hoặc podcast theo chủ đích | Category, media type, user intent và emotion context nếu có | Danh sách bài hát/podcast trên TFT | Cloud + TFT | <= 20 giây khi có Internet |
| UC-04 | Trò chuyện hỗ trợ cảm xúc | Giọng nói/câu hỏi và emotion context nếu có | Response card trên TFT | Cloud + TFT | <= 20 giây khi có Internet |
| UC-05 | Thống kê và phân tích xu hướng cảm xúc | Lịch sử cảm xúc, hoạt động, media logs và conversation metadata | TFT report cards | Cloud + TFT | <= 180 giây |

## 9.3. Cấu trúc dữ liệu phiên cảm xúc

| Trường | Kiểu dữ liệu | Mô tả |
| ------ | ------------ | ----- |
| id | UUID | ID phiên trên cloud |
| client_session_id | UUID/String | ID phiên sinh từ Edge Device |
| user_id | UUID | Người dùng sở hữu session |
| device_id | UUID | Thiết bị tạo session |
| emotion_label | String | Nhãn cảm xúc |
| confidence_score | Decimal | Độ tin cậy từ 0 đến 1 |
| quality_flag | String | clean, noisy, too_short, low_confidence |
| inference_latency_ms | Integer | Thời gian inference trên Edge |
| client_created_at | Timestamp | Thời điểm tạo trên thiết bị |
| sync_status | String | pending, synced, duplicated, rejected |

## 9.4. Danh mục hoạt động hỗ trợ

| Activity type | Hoạt động | Ý nghĩa |
| ------------- | --------- | ------- |
| `breathing` | Hít thở chậm 4-7-8 | Hạ nhịp và tạo khoảng dừng |
| `grounding` | Neo hiện tại theo bài 5-4-3-2-1 | Giảm quá tải và quay về hiện tại |
| `rest` | Nghỉ yên tĩnh 10–15 phút | Giảm kích thích tức thời |
| `rest_water` | Uống nước, nghỉ mắt | Tạo nhịp phục hồi ngắn |
| `movement` | Kéo giãn hoặc đi bộ ngắn | Đổi nhịp cơ thể nhẹ nhàng |
| `journaling` | Viết 3 câu về điều đang nghĩ | Giúp gọi tên cảm xúc |
| `body_scan` | Quét và thả lỏng cơ thể | Nhận biết vùng đang căng |
| `task_reset` | Chia nhỏ một việc trong 5 phút | Khởi động lại sự tập trung |
| `gratitude` | Ghi nhận ba điều đang ổn | Củng cố cảm xúc tích cực |
| `reach_out` | Kết nối với người tin cậy | Tăng cảm giác được hỗ trợ |

## 9.5. Nhóm nội dung mẫu

| Category | Nội dung thường gặp | Trường hợp sử dụng |
| -------- | ------------------ | ------------------ |
| relax | Nhạc nhẹ, ambient, podcast thở chậm | Khi căng thẳng |
| focus | Nhạc không lời, white noise, podcast tập trung | Khi cần học/làm việc |
| sleep | Nhạc chậm, sleep story, podcast thiền ngủ | Khi cần nghỉ ngơi |
| happy | Nhạc tích cực, podcast truyền cảm hứng | Khi muốn duy trì năng lượng tốt |
| sad_support | Nhạc ấm, podcast chia sẻ cảm xúc | Khi buồn bã |
| anger_release | Nhạc grounding, podcast kiểm soát cảm xúc | Khi tức giận |
| energy_recover | Nhạc nhẹ có nhịp vừa, podcast self-care | Khi mệt mỏi |

## 9.6. Tóm tắt API cho thiết bị biên

| Endpoint | Method | Mô tả |
| -------- | ------ | ----- |
| `/api/devices/pair` | POST | Ghép thiết bị với người dùng |
| `/api/devices/heartbeat` | POST | Cập nhật trạng thái online và firmware |
| `/api/emotion-sessions/sync` | POST | Đồng bộ emotion sessions từ Edge |
| `/api/recommendations/request` | POST | Lấy 5 activity cards từ Cloud |
| `/api/media/categories` | GET | Lấy danh sách category bài hát/podcast |
| `/api/media/recommendations` | POST | Lấy bài hát/podcast theo chủ đích và category |
| `/api/conversations/respond` | POST | Lấy response card từ Cloud |
| `/api/conversations/history` | GET | Lấy lịch sử trò chuyện rút gọn của thiết bị |
| `/api/feedback/activity` | POST | Lưu lựa chọn hoặc đánh giá hoạt động |
| `/api/feedback/media` | POST | Lưu lựa chọn hoặc đánh giá bài hát/podcast |
| `/api/reports/tft-summary` | GET | Lấy report cards theo ngày, tuần hoặc tháng |
| `/api/reports/generate` | POST | Yêu cầu Cloud tạo report mới |
| `/api/device-config` | GET | Lấy cấu hình rút gọn cho thiết bị |

## 9.7. Luồng màn hình phần cứng

```text
TRANG CHỦ -> KIỂM TRA CẢM XÚC / HOẠT ĐỘNG / NHẠC-PODCAST / TRÒ CHUYỆN / BÁO CÁO / TRẠNG THÁI
KIỂM TRA CẢM XÚC -> KẾT QUẢ -> HỖ TRỢ -> HOẠT ĐỘNG / NHẠC-PODCAST / TRÒ CHUYỆN
```

| Màn hình | Chức năng chính |
| -------- | --------------- |
| Trang chủ | Hiển thị trạng thái thiết bị, cảm xúc gần nhất, số phiên chờ đồng bộ và lối vào nhanh đến các chức năng |
| Kiểm tra cảm xúc | Thu giọng nói có chủ đích |
| Kết quả | Hiển thị nhãn cảm xúc và độ tin cậy |
| Hỗ trợ | Chọn hướng hỗ trợ: hoạt động, bài hát/podcast hoặc trò chuyện |
| Hoạt động | Hiển thị các thẻ gợi ý từ Cloud |
| Nhạc-Podcast | Chọn nhóm nội dung và xem danh sách bài hát/podcast theo chủ đích |
| Trò chuyện | Hiển thị thẻ phản hồi từ Cloud |
| Trạng thái | Kiểm tra trực tuyến/ngoại tuyến, số phiên chờ và lần đồng bộ gần nhất |
| Báo cáo | Chọn ngày/tuần/tháng và hiển thị thẻ báo cáo TFT từ Cloud hoặc dữ liệu giả lập khi demo |

## 9.8. Tham chiếu phần cứng

| Thành phần | Vai trò | Ghi chú |
| --------- | ------- | ------- |
| ESP32-S AI Thinker | Bộ điều khiển chính | Điều khiển giao diện, Wi-Fi và các thiết bị ngoại vi |
| LCD TFT ST7789 | Theo dõi chính | Hiển thị cảm xúc, gợi ý, nội dung nghe, phản hồi, trạng thái và báo cáo |
| INMP441 | Thu giọng nói | Giao tiếp I2S |
| MAX98357 I2S và loa 3W | Phản hồi âm thanh | Khuếch đại và phát âm thanh |
| Module nút bấm 5 cái | Điều hướng | Điều hướng và xác nhận thao tác |
| Breadboard, dây nối mạch, dây nối nguồn | Lắp ráp mẫu thử | Kết nối mạch và cấp nguồn |
| Bao bì phần cứng | Hoàn thiện thiết bị | Bảo vệ và tạo hình thức bên ngoài |

## 9.9. Yêu cầu khác: Siêu dữ liệu và định dạng dữ liệu được hỗ trợ

### 9.9.1. Siêu dữ liệu bắt buộc

| Data object | Required metadata | Mục đích |
| ----------- | ----------------- | -------- |
| `emotion_sessions` | `client_session_id`, `device_id`, `user_id`, `emotion_label`, `confidence_score`, `quality_flag`, `client_created_at`, `sync_status` | Truy vết phiên cảm xúc, chống trùng session và phục vụ report |
| `recommendation_requests` | `session_id` nếu có, `request_payload`, `response_payload`, `status`, `created_at` | Lưu lịch sử gợi ý và đánh giá hiệu quả hỗ trợ |
| `media_items` | `media_type`, `title`, `creator`, `category`, `duration_sec`, `enabled` | Phân loại bài hát/podcast và lọc nội dung theo category |
| `media_selection_logs` | `session_id` nếu có, `media_item_id`, `user_intent`, `selected_category`, `feedback_score`, `created_at` | Theo dõi nội dung người dùng chọn và cá nhân hóa gợi ý |
| `conversation_requests` | `session_id` nếu có, `user_message_summary`, `response_text`, `safety_flag`, `created_at` | Lưu metadata hội thoại khi được phép và kiểm tra safety |
| `tft_reports` | `user_id`, `period_type`, `period_start`, `period_end`, `tft_cards`, `emotion_distribution`, `data_quality`, `generated_at` | Hiển thị report cards trên TFT và cache report gần nhất |

### 9.9.2. Định dạng dữ liệu được hỗ trợ

| Format | Extension/MIME | Dùng cho | Trạng thái |
| ------ | -------------- | -------- | ---------- |
| JSON | `application/json` | API request/response, TFT cards, config payload | Supported |
| WAV/PCM local | `.wav`, PCM buffer | Audio sample xử lý cục bộ cho SER | Local only |
| CSV | `text/csv` | Export log/report trong phiên bản sau | Planned |
| Markdown | `.md` | Tài liệu specification và user manual | Supported |
| PNG/JPG | `.png`, `.jpg` | Hình minh họa, prototype screenshot nếu cần | Supported |

## 9.10. Tài liệu tham khảo

[1] PubMed Central, bài tham khảo về Speech Emotion Recognition.  
https://pmc.ncbi.nlm.nih.gov/articles/PMC8898841/

[2] RAVDESS Emotional Speech Audio, Kaggle dataset.  
https://www.kaggle.com/datasets/uwrfkaggler/ravdess-emotional-speech-audio

[3] Kannan Venkataramanan and Haresh Rengaraj Rajamohan, "Emotion Recognition from Speech", arXiv:1912.10458.  
https://arxiv.org/abs/1912.10458

[4] ESP32 Series, Espressif Systems.  
https://www.espressif.com/en/products/socs/esp32

[5] INMP441 MEMS Microphone Module, TDK InvenSense.  
https://invensense.tdk.com/products/digital/inmp441/

[6] Mel-frequency cepstrum, Wikipedia.  
https://en.wikipedia.org/wiki/Mel-frequency_cepstrum

[7] Emotion recognition, Wikipedia.  
https://en.wikipedia.org/wiki/Emotion_recognition

[8] World Health Organization - Mental health.  
https://www.who.int/health-topics/mental-health

[9] National Institute of Mental Health - Caring for Your Mental Health.  
https://www.nimh.nih.gov/health/topics/caring-for-your-mental-health

[10] World Health Organization, "World mental health report: Transforming mental health for all", 2022.  
https://www.who.int/publications/i/item/9789240049338

[11] LivingAI, EMO - AI Desktop Pet product page.  
https://living.ai/product/emo/

[12] ElliQ, Companion Robot for Seniors, Older Adults & Aging Loved Ones.  
https://elliq.com/

[13] Livingstone, S. R. & Russo, F. A., "The Ryerson Audio-Visual Database of Emotional Speech and Song (RAVDESS)", PLOS ONE, 2018.
https://doi.org/10.1371/journal.pone.0196391

[14] Embedded Audio Emotion — tài liệu tham chiếu xuất mô hình nhúng bằng emlearn.
https://github.com/prasenjit52282/embedded-audio-emotion

