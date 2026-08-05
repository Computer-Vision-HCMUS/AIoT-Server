# 09. Phụ lục và tài liệu tham khảo

## 9.1. Thuật ngữ

| Thuật ngữ | Mô tả |
| --------- | ----- |
| EmotiCare AIoT | Thiết bị AIoT thông minh đồng hành và chăm sóc sức khỏe cảm xúc |
| Thiết bị đồng hành cảm xúc thông minh | Định vị sản phẩm như một thiết bị đồng hành cảm xúc thông minh |
| Thiết bị biên | Thiết bị phần cứng đặt gần người dùng, có microphone, màn hình TFT, nút bấm và Wi-Fi |
| Màn hình TFT | Màn hình theo dõi chính của sản phẩm trong phiên bản này |
| Xử lý tại thiết bị | Mô hình chạy cục bộ để nhận diện cảm xúc bằng giọng nói |
| Dịch vụ máy chủ | Phần máy chủ phục vụ gợi ý, chọn nội dung, trò chuyện, báo cáo và đồng bộ dữ liệu |
| Dịch vụ gợi ý nội dung | Dịch vụ máy chủ chọn bài hát hoặc podcast theo ngữ cảnh cảm xúc, nhóm nội dung, chủ đích và lịch sử phản hồi |
| Phiên cảm xúc | Bản ghi của một lần kiểm tra cảm xúc |
| Nhãn cảm xúc | Tám nhãn SER hiện tại: vui vẻ, bình thường, bình tĩnh, buồn bã, tức giận, sợ hãi, ghê sợ và ngạc nhiên |
| Nhãn cảm xúc trong thiết bị | `angry`, `calm`, `disgust`, `fearful`, `happy`, `neutral`, `sad`, `surprised`; trạng thái kết quả chưa chắc chắn không thay thế nhãn dự đoán |
| Điểm tin cậy | Độ tin cậy của kết quả nhận diện cảm xúc |
| Thẻ hoạt động | Thẻ gợi ý hoạt động rút gọn để hiển thị trên TFT |
| Thẻ bài hát | Thẻ bài hát rút gọn gồm tiêu đề, người sáng tạo, thời lượng, nhóm nội dung và lý do gợi ý |
| Thẻ podcast | Thẻ podcast rút gọn gồm tiêu đề, người sáng tạo, thời lượng, nhóm nội dung và lý do gợi ý |
| Thẻ phản hồi | Thẻ phản hồi trò chuyện rút gọn để hiển thị trên TFT |
| Màn hình Insights | Màn hình thống kê gồm bộ chọn `Day`/`Week`/`Month`, tám thanh tỷ lệ cảm xúc và chế độ xem diễn giải AI |
| Dữ liệu fallback | Bảng tỷ lệ cảm xúc mẫu trong firmware, được dùng khi API thống kê không trả `emotion_distribution` hợp lệ |

## 9.2. Bảng tham chiếu tình huống sử dụng

| ID | Tình huống sử dụng | Đầu vào | Đầu ra | Xử lý chính | Mục tiêu thời gian |
| -- | -------- | ----- | ------ | ----------- | ------------------ |
| UC-01 | Nhận diện cảm xúc bằng giọng nói | Giọng nói người dùng | Nhãn cảm xúc và độ tin cậy | Xử lý tại thiết bị | Không quá 30 giây |
| UC-02 | Gợi ý hoạt động cải thiện tâm trạng | Kết quả cảm xúc và lịch sử đã đồng bộ | 5 thẻ hoạt động trên màn hình | Máy chủ và màn hình thiết bị | Không quá 20 giây khi có Internet |
| UC-03 | Lựa chọn bài hát hoặc podcast theo chủ đích | Nhóm nội dung, loại nội dung, chủ đích và ngữ cảnh cảm xúc nếu có | Danh sách bài hát hoặc podcast trên màn hình | Máy chủ và màn hình thiết bị | Không quá 20 giây khi có Internet |
| UC-04 | Trò chuyện hỗ trợ cảm xúc | Giọng nói hoặc câu hỏi và ngữ cảnh cảm xúc nếu có | Thẻ phản hồi trên màn hình | Máy chủ và màn hình thiết bị | Không quá 20 giây khi có Internet |
| UC-05 | Xem thống kê cảm xúc | Kỳ được chọn (`day`, `week` hoặc `month`) và dữ liệu phân bố cảm xúc từ API | Tám thanh tỷ lệ cảm xúc; diễn giải AI tùy chọn | Máy chủ và màn hình thiết bị; dùng fallback khi API lỗi | Không quá 180 giây |

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
| created_at | Timestamp | Thời điểm Server nhận và lưu session; được dùng để tính kỳ report vì firmware chưa có RTC đáng tin cậy |

### 9.3.1. Thông tin cần lưu

Các thông tin dưới đây là thông tin được lưu trên máy chủ, không phải toàn bộ đều do thiết bị gửi trực tiếp. Cụ thể, `device_id` và `user_id` được máy chủ xác định từ mã xác thực thiết bị; `created_at` do máy chủ gán khi nhận dữ liệu.

| Đối tượng dữ liệu | Thông tin cần lưu | Mục đích |
| ----------------- | ----------------- | -------- |
| `emotion_sessions` | `client_session_id`, `device_id`, `user_id`, `emotion_label`, `confidence_score`, `quality_flag`, `client_created_at`, `created_at` | Truy vết phiên cảm xúc, chống trùng lặp và phục vụ báo cáo |
| `recommendation_requests` | `session_id`, `request_payload`, `response_payload`, `status`, `created_at` | Lưu lịch sử gợi ý và đánh giá hiệu quả hỗ trợ |
| `media_items` | `media_type`, `title`, `creator`, `category`, `duration_sec`, `enabled` | Phân loại bài hát hoặc podcast theo nhóm nội dung |
| `media_selection_logs` | `session_id`, `media_item_id`, `user_intent`, `selected_category`, `feedback_score`, `created_at` | Theo dõi nội dung người dùng chọn để hỗ trợ cá nhân hóa |
| `conversation_requests` | `session_id`, `user_message_summary`, `response_text`, `safety_flag`, `created_at` | Lưu nội dung trò chuyện rút gọn và phản hồi; không lưu âm thanh thô |
| `tft_reports` | `user_id`, `period_type`, `period_start`, `period_end`, `emotion_distribution`, `generated_at` | Dữ liệu báo cáo phía máy chủ; firmware hiện chỉ đọc `emotion_distribution` để vẽ biểu đồ, không đọc `tft_cards` hoặc `data_quality` |

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

Đây là bảng tra cứu nhanh. Mô tả đầy đủ về dữ liệu gửi và nhận nằm tại Mục 4.2.

| Endpoint | Method | Mô tả |
| -------- | ------ | ----- |
| `/api/devices/pair` | POST | Ghép thiết bị với người dùng |
| `/api/devices/heartbeat` | POST | Cập nhật trạng thái online và firmware |
| `/api/emotion-sessions/sync` | POST | Đồng bộ emotion sessions từ Edge |
| `/api/recommendations/request` | POST | Lấy 5 activity cards từ Cloud |
| `/api/media/library` | GET | Firmware lấy catalog Music và Podcast để hiển thị danh sách Discover |
| `/api/media/recommendations` | POST | Firmware đánh dấu các mục Music/Podcast ưu tiên theo emotion context |
| `/api/media/music/recommend` | POST | API dự kiến; firmware hiện dùng `/api/media/recommendations` |
| `/api/media/podcast/recommend` | POST | API dự kiến; firmware hiện dùng `/api/media/recommendations` |
| `/api/conversations/respond` | POST | Lấy response card từ Cloud |
| `/api/conversations/voice` | POST | Gửi PCM 16-bit tạm thời cùng `session_id` để Whisper tạo transcript, phản hồi và audio TTS nếu khả dụng |
| `/api/conversations/voice-audio/{audio_id}` | GET | Lấy PCM phản hồi TTS còn hiệu lực của thiết bị |
| `/api/conversations/history` | GET | Lấy lịch sử trò chuyện rút gọn của thiết bị |
| `/api/feedback/activity` | POST | API dự kiến; chưa được firmware TFT hiện tại gọi |
| `/api/feedback/media` | POST | API dự kiến; chưa được firmware TFT hiện tại gọi |
| `/api/statistics/day` | GET | Firmware lấy phân bố cảm xúc cho biểu đồ Day |
| `/api/statistics/week` | GET | Firmware lấy phân bố cảm xúc cho biểu đồ Week |
| `/api/statistics/month` | GET | Firmware lấy phân bố cảm xúc cho biểu đồ Month |
| `/api/statistics/{period}/explain` | POST | Lấy diễn giải AI cho `day`, `week` hoặc `month` |
| `/api/device-config` | GET | Lấy cấu hình rút gọn cho thiết bị |

## 9.7. Luồng màn hình phần cứng

Luồng màn hình và thao tác của người dùng được mô tả tại Mục 7.2. Phần này không lặp lại để bảo đảm tài liệu chỉ có một nguồn mô tả giao diện.

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

## 9.9. Định dạng dữ liệu được hỗ trợ

| Định dạng | Phần mở rộng hoặc kiểu dữ liệu | Mục đích sử dụng | Trạng thái |
| ---------- | ------------------------------ | ---------------- | ---------- |
| JSON | `application/json` | Dữ liệu trao đổi, thẻ hiển thị và cấu hình | Có hỗ trợ |
| WAV/PCM cho nhận diện cảm xúc | `.wav`, vùng đệm PCM | Mẫu âm thanh được xử lý tại thiết bị | Chỉ xử lý cục bộ |
| PCM cho trò chuyện bằng giọng nói | `application/octet-stream`, PCM 16-bit, 16 kHz; tối đa 10 giây từ thiết bị và 30 giây ở máy chủ | Gửi tạm thời tới `/api/conversations/voice` để chuyển giọng nói thành văn bản | Có hỗ trợ, không lưu lâu dài |
| CSV | `text/csv` | Xuất nhật ký hoặc báo cáo trong phiên bản sau | Dự kiến |
| Markdown | `.md` | Tài liệu đặc tả và hướng dẫn sử dụng | Có hỗ trợ |
| PNG/JPG | `.png`, `.jpg` | Hình minh họa hoặc ảnh chụp mẫu thử | Có hỗ trợ |

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

