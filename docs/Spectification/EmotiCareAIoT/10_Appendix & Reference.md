# 10. Appendix & Reference

## 10.1. Thuật ngữ

| Thuật ngữ | Mô tả |
| --------- | ----- |
| EmotiCare AIoT | Thiết bị AIoT thông minh đồng hành và chăm sóc sức khỏe cảm xúc |
| Intelligent Emotional Companion | Định vị sản phẩm như một thiết bị đồng hành cảm xúc thông minh |
| Edge Device | Thiết bị phần cứng đặt gần người dùng, có microphone, TFT screen, nút bấm và Wi-Fi |
| TFT Screen | Màn hình theo dõi chính của sản phẩm trong phiên bản này |
| Edge AI | Mô hình AI chạy cục bộ để xử lý Speech Emotion Recognition |
| Cloud Service | Backend phục vụ recommendation, media selection, conversation, report và đồng bộ dữ liệu |
| Media Recommendation Service | Dịch vụ Cloud chọn bài hát/podcast theo emotion context, category, intent và lịch sử feedback |
| Emotion Session | Bản ghi của một lần check-in cảm xúc |
| Emotion Label | Nhãn cảm xúc như vui vẻ, bình thường, căng thẳng, buồn bã, tức giận, mệt mỏi |
| Confidence Score | Độ tin cậy của kết quả nhận diện cảm xúc |
| Activity Card | Thẻ gợi ý hoạt động rút gọn để hiển thị trên TFT |
| Song Card | Thẻ bài hát rút gọn gồm title, creator, duration, category và reason text |
| Podcast Card | Thẻ podcast rút gọn gồm title, creator, duration, category và reason text |
| Response Card | Thẻ phản hồi hội thoại rút gọn để hiển thị trên TFT |
| TFT Report Card | Thẻ báo cáo ngắn gồm insight chính theo ngày, tuần, tháng hoặc năm |
| Limited Data | Trạng thái báo cáo khi dữ liệu chưa đủ để tạo insight mạnh |

## 10.2. Bảng tham chiếu use case

| ID | Use case | Input | Output | Xử lý chính | Mục tiêu thời gian |
| -- | -------- | ----- | ------ | ----------- | ------------------ |
| UC-01 | Speech Emotion Recognition | Giọng nói người dùng | Emotion label, confidence, emotion session | Edge AI | <= 15 giây |
| UC-02 | Gợi ý hoạt động và nội dung cải thiện tâm trạng | Emotion label nếu có, confidence nếu có và lịch sử đã đồng bộ | Activity cards, song cards, podcast cards trên TFT | Cloud + TFT | <= 20 giây khi có Internet |
| UC-03 | Lựa chọn bài hát hoặc podcast theo chủ đích | Category, media type, user intent và emotion context nếu có | Danh sách bài hát/podcast trên TFT | Cloud + TFT | <= 20 giây khi có Internet |
| UC-04 | Trò chuyện hỗ trợ cảm xúc | Giọng nói/câu hỏi và emotion context nếu có | Response card trên TFT | Cloud + TFT | <= 20 giây khi có Internet |
| UC-05 | Thống kê và phân tích xu hướng cảm xúc | Lịch sử cảm xúc, hoạt động, media logs và conversation metadata | TFT report cards | Cloud + TFT | <= 180 giây |

## 10.3. Emotion session schema

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

## 10.4. Thư viện hoạt động mẫu

| Cảm xúc | Nhóm hoạt động | Hoạt động mẫu | Ý nghĩa |
| ------- | -------------- | ------------- | ------- |
| Căng thẳng | Breathing | Hít thở 4-7-8 trong 2 phút | Giảm nhịp căng và tạo khoảng dừng |
| Căng thẳng | Rest | Nghỉ 5 phút khỏi màn hình | Giảm kích thích tức thời |
| Buồn bã | Journaling | Viết 3 câu về cảm xúc hiện tại | Giúp gọi tên cảm xúc |
| Buồn bã | Social | Nhắn tin cho một người tin cậy | Tăng cảm giác được kết nối |
| Tức giận | Grounding | Đếm 10 nhịp thở trước khi phản hồi | Tránh phản ứng vội |
| Mệt mỏi | Rest | Uống nước và giãn cơ nhẹ | Hỗ trợ phục hồi năng lượng |
| Vui vẻ | Reflection | Ghi lại một điều tích cực trong ngày | Củng cố cảm xúc tích cực |
| Bình thường | Maintenance | Vận động nhẹ hoặc check-in cuối ngày | Duy trì thói quen ổn định |

## 10.5. Media category mẫu

| Category | Nội dung thường gặp | Trường hợp sử dụng |
| -------- | ------------------ | ------------------ |
| relax | Nhạc nhẹ, ambient, podcast thở chậm | Khi căng thẳng |
| focus | Nhạc không lời, white noise, podcast tập trung | Khi cần học/làm việc |
| sleep | Nhạc chậm, sleep story, podcast thiền ngủ | Khi cần nghỉ ngơi |
| happy | Nhạc tích cực, podcast truyền cảm hứng | Khi muốn duy trì năng lượng tốt |
| sad_support | Nhạc ấm, podcast chia sẻ cảm xúc | Khi buồn bã |
| anger_release | Nhạc grounding, podcast kiểm soát cảm xúc | Khi tức giận |
| energy_recover | Nhạc nhẹ có nhịp vừa, podcast self-care | Khi mệt mỏi |

## 10.6. API summary cho Edge Device

| Endpoint | Method | Mô tả |
| -------- | ------ | ----- |
| `/api/devices/pair` | POST | Ghép thiết bị với người dùng |
| `/api/devices/heartbeat` | POST | Cập nhật trạng thái online và firmware |
| `/api/emotion-sessions/sync` | POST | Đồng bộ emotion sessions từ Edge |
| `/api/recommendations/request` | POST | Lấy activity cards, song cards và podcast cards từ Cloud |
| `/api/media/categories` | GET | Lấy danh sách category bài hát/podcast |
| `/api/media/recommendations` | POST | Lấy bài hát/podcast theo chủ đích và category |
| `/api/conversations/respond` | POST | Lấy response card từ Cloud |
| `/api/feedback/activity` | POST | Lưu lựa chọn hoặc đánh giá hoạt động |
| `/api/feedback/media` | POST | Lưu lựa chọn hoặc đánh giá bài hát/podcast |
| `/api/reports/tft-summary` | GET | Lấy report cards theo ngày, tuần, tháng hoặc năm |
| `/api/reports/generate` | POST | Yêu cầu Cloud tạo report mới |
| `/api/device-config` | GET | Lấy cấu hình rút gọn cho thiết bị |

## 10.7. Screen flow phần cứng

```text
HOME -> CHECK-IN / ACTIVITY / MUSIC-PODCAST / CONVERSATION / REPORT / STATUS
CHECK-IN -> RESULT -> SUPPORT -> ACTIVITY / MUSIC-PODCAST / CONVERSATION
```

| Màn hình | Chức năng chính |
| -------- | --------------- |
| HOME | Hiển thị trạng thái thiết bị, cảm xúc gần nhất, pending sessions và lối vào nhanh đến Activity, Music/Podcast, Conversation, Report |
| CHECK-IN | Thu giọng nói có chủ đích |
| RESULT | Hiển thị emotion label và confidence |
| SUPPORT | Chọn hướng hỗ trợ: hoạt động, bài hát/podcast hoặc trò chuyện |
| ACTIVITY | Hiển thị activity cards, song cards và podcast cards từ Cloud |
| MUSIC-PODCAST | Chọn category và xem danh sách bài hát/podcast theo chủ đích |
| CONVERSATION | Hiển thị response card từ Cloud |
| STATUS | Kiểm tra online/offline, pending count và last sync |
| REPORT | Chọn ngày/tháng/năm và hiển thị TFT report cards từ Cloud hoặc dữ liệu giả lập khi demo |

## 10.8. Tham chiếu phần cứng

| Component | Vai trò | Ghi chú |
| --------- | ------- | ------- |
| ESP32-S3 hoặc tương đương | Bộ điều khiển chính | Điều khiển UI, Wi-Fi, cache và inference nhẹ |
| INMP441 Microphone | Thu giọng nói | Giao tiếp I2S, phù hợp prototype SER |
| TFT/OLED Display | Theo dõi chính | Cảm xúc, gợi ý, nội dung nghe, phản hồi, trạng thái sync và báo cáo |
| Buttons/Touch | Điều hướng | Mode, Action, Start, Next, Back |
| Speaker/Buzzer | Phản hồi âm thanh | Báo hiệu ghi âm, có kết quả mới hoặc phát nội dung ngắn nếu phần cứng hỗ trợ |
| Flash/Local Storage | Cache | Lưu session pending, media selection log pending và report gần nhất |
| Wi-Fi | Kết nối | Bắt buộc cho Objective 2 và Objective 3 |

## 10.9. References

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

[13] Espressif Systems, ESP32-S3-DevKitC-1 development board.  
https://www.espressif.com/en/products/devkits/esp32-s3-devkitc-1

[14] Waveshare, 2.4inch LCD Display Module, 240x320, SPI interface.  
https://www.waveshare.com/2.4inch-lcd-module.htm

[15] Adafruit, Tactile Button switch 6mm x 20 pack.  
https://www.adafruit.com/product/367

[16] Adafruit, Piezo Buzzer PS1240.  
https://www.adafruit.com/product/160

[17] Winbond, Serial NOR Flash Memory product family.  
https://www.winbond.com/hq/product/code-storage-flash-memory/serial-nor-flash/
