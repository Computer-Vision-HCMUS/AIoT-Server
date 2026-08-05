# 05. Yêu cầu chức năng

## 5.1. Tổng quan

Yêu cầu chức năng của EmotiCare AIoT tập trung vào trải nghiệm trên màn hình thiết bị. Mục tiêu 1 được xử lý ngay trên thiết bị; Mục tiêu 2 và Mục tiêu 3 cần kết nối Internet để nhận hỗ trợ từ máy chủ.

* **UC-01:** Nhận diện cảm xúc bằng giọng nói tại thiết bị.
* **UC-02:** Gợi ý hoạt động cải thiện tâm trạng từ máy chủ.
* **UC-03:** Lựa chọn bài hát hoặc podcast theo chủ đích.
* **UC-04:** Trò chuyện hỗ trợ cảm xúc.
* **UC-05:** Thống kê và phân tích xu hướng cảm xúc trên màn hình thiết bị.

## 5.2. Nhóm chức năng nhận diện cảm xúc trên Edge

| ID | Yêu cầu chức năng | Use case liên quan | Độ ưu tiên |
| -- | ----------------- | ------------------ | ---------- |
| FR-01 | Hệ thống phải cho phép người dùng kích hoạt phiên check-in bằng nút vật lý hoặc thao tác tương đương trên thiết bị. | UC-01 | Bắt buộc |
| FR-02 | Thiết bị phải hiển thị rõ trạng thái đang ghi âm trên TFT trong suốt thời gian thu giọng nói. | UC-01 | Bắt buộc |
| FR-03 | Thiết bị phải ghi âm trong thời lượng giới hạn và tự dừng khi đủ dữ liệu hoặc hết thời gian. | UC-01 | Bắt buộc |
| FR-04 | Edge AI phải tiền xử lý âm thanh, giảm nhiễu cơ bản và trích xuất đặc trưng SER như Log-Mel Spectrogram, MFCC, pitch hoặc energy. | UC-01 | Bắt buộc |
| FR-05 | Mô hình SER trên firmware phải phân loại thành tám nhãn RAVDESS: `angry`, `calm`, `disgust`, `fearful`, `happy`, `neutral`, `sad`, `surprised`; UI đánh dấu low-confidence để người dùng xác nhận lại. | UC-01 | Bắt buộc |
| FR-06 | Hệ thống phải trả kết quả cảm xúc trên TFT trong vòng 30 giây sau khi nhận được giọng nói hợp lệ. | UC-01 | Bắt buộc |
| FR-07 | Cloud phải lưu emotion session gồm ID Cloud, `client_session_id`, user ID, device ID, emotion label, confidence score, quality flag, `inference_latency_ms` nếu có, `client_created_at` và `created_at`. | UC-01 | Bắt buộc |
| FR-08 | Nếu dữ liệu âm thanh không hợp lệ hoặc confidence thấp, hệ thống phải yêu cầu người dùng nói lại hoặc đánh dấu kết quả là không chắc chắn. | UC-01 | Nên làm |

## 5.3. Nhóm chức năng đồng bộ dữ liệu

| ID | Yêu cầu chức năng | Use case liên quan | Độ ưu tiên |
| -- | ----------------- | ------------------ | ---------- |
| FR-09 | Khi mất Internet, firmware lưu trạng thái emotion đã xác nhận gần nhất vào bộ nhớ cục bộ; trạng thái mới ghi đè trạng thái cũ. | UC-01 | Bắt buộc |
| FR-10 | Firmware chỉ thử đồng bộ emotion session ngay lúc người dùng xác nhận check-in và Wi-Fi/pairing khả dụng; hàng đợi session pending và retry tự động chưa được triển khai. | UC-01 | Bắt buộc |
| FR-11 | API đồng bộ phải xử lý idempotent theo `device_id + client_session_id` để tránh tạo trùng session. | UC-01 | Bắt buộc |
| FR-12 | TFT phải hiển thị trạng thái mạng hiện có: `Online`, `Unpaired`, `Setup AP` hoặc `Offline`. | UC-01 đến UC-05 | Bắt buộc |
| FR-13 | Khi khởi động với Wi-Fi và pairing hợp lệ, firmware phải gọi heartbeat để xác minh máy chủ và cập nhật trạng thái thiết bị. | UC-01 đến UC-05 | Nên làm |

## 5.4. Nhóm chức năng gợi ý hoạt động qua máy chủ

| ID | Yêu cầu chức năng | Use case liên quan | Độ ưu tiên |
| -- | ----------------- | ------------------ | ---------- |
| FR-14 | Sau khi người dùng xác nhận kết quả check-in, thiết bị phải cho phép mở Support và gửi session gần nhất lên Cloud Recommendation API khi có thể. | UC-02 | Bắt buộc |
| FR-15 | Cloud có thể trả danh sách recommendation card phù hợp với emotion label; khi không có kết quả, firmware phải dùng hoạt động fallback cục bộ. | UC-02 | Bắt buộc |
| FR-16 | Recommendation card phải được rút gọn để hiển thị được trên TFT, gồm title, type, body ngắn, reason text và action ID nếu có. | UC-02 | Bắt buộc |
| FR-17 | Kết quả gợi ý phải hiển thị trên TFT trong vòng 20 giây sau khi UC-01 hoàn tất và thiết bị có Internet. | UC-02 | Bắt buộc |
| FR-18 | Người dùng phải có thể duyệt danh sách và mở chi tiết hoạt động được gợi ý trên thiết bị. | UC-02 | Bắt buộc |
| FR-19 | Việc bỏ qua hoặc đánh giá hoạt động để cá nhân hóa chưa được triển khai trên TFT. | UC-02 | Out of scope |
| FR-20 | Nếu không có Internet hoặc Cloud lỗi, TFT phải tiếp tục hiển thị hoạt động fallback cục bộ. | UC-02 | Bắt buộc |

## 5.5. Nhóm chức năng lựa chọn bài hát hoặc podcast theo chủ đích

| ID | Yêu cầu chức năng | Use case liên quan | Độ ưu tiên |
| -- | ----------------- | ------------------ | ---------- |
| FR-21 | Thiết bị phải cho phép người dùng mở Discover từ HOME và chọn một trong hai danh sách Music hoặc Podcast. | UC-03 | Bắt buộc |
| FR-22 | Discover phải hiển thị hai lựa chọn Music và Podcast, kèm ngữ cảnh cảm xúc gần nhất hoặc `Neutral (default)`. | UC-03 | Bắt buộc |
| FR-23 | Firmware phải lấy catalog Music/Podcast và, khi có cảm xúc, dùng emotion context để ưu tiên các mục do AI đề xuất. | UC-03 | Bắt buộc |
| FR-24 | Cloud Media Recommendation Service phải lọc và xếp hạng bài hát/podcast theo category, emotion label, lịch sử lựa chọn và feedback. | UC-03 | Bắt buộc |
| FR-25 | TFT phải hiển thị danh sách cuộn Music/Podcast gồm title, category, duration và nhãn `AI` cho mục được ưu tiên. | UC-03 | Bắt buộc |
| FR-26 | Người dùng phải có thể chọn nội dung để phát bằng S3 và dừng bằng S2. | UC-03 | Bắt buộc |
| FR-27 | Lưu media selection log hoặc media feedback trên TFT chưa được triển khai. | UC-03 | Out of scope |

## 5.6. Nhóm chức năng trò chuyện hỗ trợ qua máy chủ

| ID | Yêu cầu chức năng | Use case liên quan | Độ ưu tiên |
| -- | ----------------- | ------------------ | ---------- |
| FR-28 | Thiết bị phải cho phép người dùng mở Companion Chat trực tiếp từ HOME; nếu chưa có session check-in, firmware thử tạo session `neutral` trước khi gửi audio. | UC-04 | Bắt buộc |
| FR-29 | Firmware phải gửi PCM 16-bit, 16 kHz tối đa 10 giây cùng `session_id` lên Cloud Voice Conversation API; Server chuyển âm thanh thành transcript trước khi tạo phản hồi. | UC-04 | Bắt buộc |
| FR-30 | Cloud Conversation Service phải tạo phản hồi đồng cảm, ngắn gọn và phù hợp với TFT. | UC-04 | Bắt buộc |
| FR-31 | Phản hồi đầu tiên phải hiển thị trên TFT trong vòng 20 giây sau khi nhận input hợp lệ và có Internet. | UC-04 | Bắt buộc |
| FR-32 | Cloud phải áp dụng safety filter để tránh chẩn đoán y khoa, phán xét người dùng hoặc đưa lời khuyên nguy hiểm. | UC-04 | Bắt buộc |
| FR-33 | Khi phát hiện tín hiệu nguy cấp, Cloud phải trả thông điệp khuyên liên hệ người thân, chuyên gia hoặc dịch vụ hỗ trợ phù hợp. | UC-04 | Bắt buộc |
| FR-34 | Cloud chỉ lưu transcript tóm tắt và phản hồi hội thoại; audio PCM đầu vào không được lưu. | UC-04 | Bắt buộc |

## 5.7. Nhóm chức năng báo cáo trên màn hình qua máy chủ

| ID | Yêu cầu chức năng | Use case liên quan | Độ ưu tiên |
| -- | ----------------- | ------------------ | ---------- |
| FR-35 | Thiết bị phải cho phép người dùng mở Insights từ HOME và chọn kỳ `Day`, `Week` hoặc `Month` trên TFT. | UC-05 | Bắt buộc |
| FR-36 | Firmware phải gọi `GET /api/statistics/day`, `/week` hoặc `/month` để lấy báo cáo rút gọn theo period đã chọn. | UC-05 | Bắt buộc |
| FR-37 | Firmware phải đọc `emotion_distribution` gồm tám nhãn cảm xúc để hiển thị thanh tỷ lệ; phần diễn giải AI được lấy riêng qua API `/explain`. | UC-05 | Bắt buộc |
| FR-38 | Nếu API thống kê lỗi, thiếu hoặc rỗng `emotion_distribution`, firmware phải hiển thị bảng fallback cục bộ. | UC-05 | Bắt buộc |
| FR-39 | Báo cáo rút gọn phải hiển thị trên TFT trong vòng 180 giây sau khi người dùng yêu cầu. | UC-05 | Bắt buộc |
| FR-40 | TFT không hiển thị trạng thái `limited_data`; dữ liệu fallback được dùng khi không có thống kê hợp lệ. | UC-05 | Bắt buộc |
| FR-41 | Khi mất Internet, biểu đồ Insights vẫn dùng dữ liệu fallback; riêng AI assessment hiển thị thông báo kiểm tra Wi-Fi và máy chủ nếu API lỗi. | UC-05 | Bắt buộc |

## 5.8. Nhóm chức năng quản lý dữ liệu người dùng

| ID | Yêu cầu chức năng | Use case liên quan | Độ ưu tiên |
| -- | ----------------- | ------------------ | ---------- |
| FR-42 | Hệ thống phải liên kết mỗi thiết bị với đúng một tài khoản người dùng tại một thời điểm. | UC-02, UC-03, UC-04, UC-05 | Bắt buộc |
| FR-43 | Xem lịch sử emotion session theo các phiên gần nhất chưa được triển khai trên TFT. | UC-05 | Out of scope |
| FR-44 | Xóa dữ liệu cục bộ từ TFT chưa được triển khai. | UC-01, UC-05 | Out of scope |
| FR-45 | Hệ thống phải áp dụng chính sách lưu trữ hiện tại: không lưu audio thô, lưu transcript tóm tắt/response hội thoại và media feedback phục vụ báo cáo. | UC-03, UC-04, UC-05 | Bắt buộc |

## 5.9. Ma trận truy vết

| Objective | Use case | Functional requirements |
| --------- | -------- | ----------------------- |
| SMART Objective 1 | UC-01 | FR-01 đến FR-09, FR-44 |
| SMART Objective 2 | UC-02 | FR-12 đến FR-20, FR-42 |
| SMART Objective 2 | UC-03 | FR-12, FR-21 đến FR-27, FR-42, FR-45 |
| SMART Objective 2 | UC-04 | FR-12, FR-28 đến FR-34, FR-42, FR-45 |
| SMART Objective 3 | UC-05 | FR-09 đến FR-13, FR-35 đến FR-45 |

## 5.10. Tóm tắt theo nhóm yêu cầu

| Domain | Requirement range | Thành phần chịu trách nhiệm | Ghi chú kiểm thử |
| ------ | ----------------- | -------------------------- | ---------------- |
| Edge AI | FR-01 đến FR-08 | Edge Device, SER Engine, TFT | Kiểm thử thu âm, inference, confidence và quality flag |
| Sync/Data | FR-09 đến FR-13 | Edge Device, Cloud API, Cloud Database | Kiểm thử pending cache, retry và idempotency |
| Recommendation | FR-14 đến FR-20 | Cloud Recommendation Service, TFT | Kiểm thử 5 activity cards và feedback hoạt động |
| Media | FR-21 đến FR-27 | Cloud Media Recommendation Service, TFT | Kiểm thử Discover, media list, ưu tiên AI và phát/dừng |
| Conversation | FR-28 đến FR-34 | Cloud Conversation Service, Safety Filter, TFT | Kiểm thử phản hồi đồng cảm và tình huống safety |
| Report | FR-35 đến FR-41 | Cloud Report Engine, TFT | Kiểm thử Insights ngày/tuần/tháng, AI assessment và fallback |
| User Data | FR-42 đến FR-45 | Device Auth, Local Cache, Cloud Database | Kiểm thử pairing và chính sách lưu trữ audio |
