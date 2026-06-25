# 06. Functional Requirement

## 6.1. Tổng quan

Yêu cầu chức năng của EmotiCare AIoT được cập nhật theo phạm vi mới: người dùng theo dõi toàn bộ trên TFT screen, Objective 1 chạy bằng Edge AI, còn Objective 2 và Objective 3 phối hợp Internet/Cloud.

* **UC-01:** Speech Emotion Recognition trên Edge Device.
* **UC-02:** Gợi ý hoạt động, bài hát và podcast cải thiện tâm trạng qua Cloud Recommendation Service.
* **UC-03:** Lựa chọn bài hát hoặc podcast theo chủ đích qua Cloud Media Recommendation Service.
* **UC-04:** Trò chuyện hỗ trợ cảm xúc qua Cloud Conversation Service.
* **UC-05:** Thống kê và phân tích xu hướng cảm xúc qua Cloud Report Engine, hiển thị trên TFT.

## 6.2. Nhóm chức năng nhận diện cảm xúc trên Edge

| ID | Yêu cầu chức năng | Use case liên quan | Độ ưu tiên |
| -- | ----------------- | ------------------ | ---------- |
| FR-01 | Hệ thống phải cho phép người dùng kích hoạt phiên check-in bằng nút vật lý hoặc thao tác tương đương trên thiết bị. | UC-01 | Must |
| FR-02 | Thiết bị phải hiển thị rõ trạng thái đang ghi âm trên TFT trong suốt thời gian thu giọng nói. | UC-01 | Must |
| FR-03 | Thiết bị phải ghi âm trong thời lượng giới hạn và tự dừng khi đủ dữ liệu hoặc hết thời gian. | UC-01 | Must |
| FR-04 | Edge AI phải tiền xử lý âm thanh, giảm nhiễu cơ bản và trích xuất đặc trưng SER như Log-Mel Spectrogram, MFCC, pitch hoặc energy. | UC-01 | Must |
| FR-05 | Mô hình SER phải phân loại cảm xúc thành các nhóm sản phẩm: vui vẻ, bình thường, căng thẳng, buồn bã, tức giận, mệt mỏi hoặc không chắc chắn. | UC-01 | Must |
| FR-06 | Hệ thống phải trả kết quả cảm xúc trên TFT trong vòng 15 giây sau khi nhận được giọng nói hợp lệ. | UC-01 | Must |
| FR-07 | Hệ thống phải lưu emotion session gồm session ID, user ID, device ID, emotion label, confidence score, quality flag, timestamp và sync status. | UC-01 | Must |
| FR-08 | Nếu dữ liệu âm thanh không hợp lệ hoặc confidence thấp, hệ thống phải yêu cầu người dùng nói lại hoặc đánh dấu kết quả là không chắc chắn. | UC-01 | Should |

## 6.3. Nhóm chức năng đồng bộ nền tảng

| ID | Yêu cầu chức năng | Use case liên quan | Độ ưu tiên |
| -- | ----------------- | ------------------ | ---------- |
| FR-09 | Edge Device phải lưu tạm emotion sessions khi mất Internet. | UC-01, UC-05 | Must |
| FR-10 | Edge Device phải đồng bộ các session pending lên Cloud khi Internet khả dụng. | UC-02, UC-03, UC-04, UC-05 | Must |
| FR-11 | API đồng bộ phải xử lý idempotent theo `device_id + client_session_id` để tránh tạo trùng session. | UC-05 | Must |
| FR-12 | TFT phải hiển thị trạng thái Online, Offline, Sync pending, Waiting cloud và Cloud result ready. | UC-02, UC-03, UC-04, UC-05 | Must |
| FR-13 | Thiết bị phải gửi heartbeat định kỳ để Cloud biết trạng thái thiết bị. | UC-02, UC-03, UC-04, UC-05 | Should |

## 6.4. Nhóm chức năng gợi ý hoạt động và nội dung qua Cloud

| ID | Yêu cầu chức năng | Use case liên quan | Độ ưu tiên |
| -- | ----------------- | ------------------ | ---------- |
| FR-14 | Khi có Internet, thiết bị phải cho phép người dùng mở Activity từ HOME hoặc sau check-in; thiết bị gửi emotion context lên Cloud Recommendation API nếu có. | UC-02 | Must |
| FR-15 | Cloud phải trả ít nhất một recommendation card phù hợp với emotion label hiện tại. | UC-02 | Must |
| FR-16 | Recommendation card phải được rút gọn để hiển thị được trên TFT, gồm title, type, body ngắn, reason text và action ID nếu có. | UC-02 | Must |
| FR-17 | Kết quả gợi ý phải hiển thị trên TFT trong vòng 20 giây sau khi UC-01 hoàn tất và thiết bị có Internet. | UC-02 | Must |
| FR-18 | Người dùng phải có thể chọn, bỏ qua hoặc đánh giá hoạt động, bài hát hoặc podcast được gợi ý trên thiết bị. | UC-02 | Should |
| FR-19 | Thiết bị phải gửi feedback hoạt động/nội dung lên Cloud để phục vụ cá nhân hóa sau này. | UC-02, UC-05 | Should |
| FR-20 | Nếu không có Internet, TFT phải thông báo rằng chức năng gợi ý cần kết nối Cloud. | UC-02 | Must |

## 6.5. Nhóm chức năng lựa chọn bài hát hoặc podcast theo chủ đích

| ID | Yêu cầu chức năng | Use case liên quan | Độ ưu tiên |
| -- | ----------------- | ------------------ | ---------- |
| FR-21 | Khi có Internet, thiết bị phải cho phép người dùng mở Music/Podcast Mode trực tiếp từ HOME hoặc từ màn hình SUPPORT. | UC-03 | Must |
| FR-22 | TFT phải hiển thị danh sách category nội dung gồm thư giãn, tập trung, ngủ nghỉ, vui vẻ, xoa dịu buồn bã, giải tỏa tức giận và phục hồi năng lượng. | UC-03 | Must |
| FR-23 | Thiết bị phải gửi category, media type, user intent và emotion context nếu có lên Cloud Media Recommendation API. | UC-03 | Must |
| FR-24 | Cloud Media Recommendation Service phải lọc và xếp hạng bài hát/podcast theo category, emotion label, lịch sử lựa chọn và feedback. | UC-03 | Must |
| FR-25 | TFT phải hiển thị danh sách bài hát/podcast rút gọn, bao gồm title, creator, duration, category và reason text. | UC-03 | Must |
| FR-26 | Người dùng phải có thể chọn nội dung để nghe, lưu lại, bỏ qua hoặc đánh giá sau khi nghe. | UC-03 | Should |
| FR-27 | Thiết bị phải đồng bộ media selection log và media feedback lên Cloud khi có kết nối. | UC-03, UC-05 | Must |

## 6.6. Nhóm chức năng trò chuyện hỗ trợ qua Cloud

| ID | Yêu cầu chức năng | Use case liên quan | Độ ưu tiên |
| -- | ----------------- | ------------------ | ---------- |
| FR-28 | Khi có Internet, thiết bị phải cho phép người dùng mở Conversation Mode trực tiếp từ HOME hoặc sau khi có emotion label. | UC-04 | Must |
| FR-29 | Thiết bị phải gửi user utterance và emotion context lên Cloud Conversation API. | UC-04 | Must |
| FR-30 | Cloud Conversation Service phải tạo phản hồi đồng cảm, ngắn gọn và phù hợp với TFT. | UC-04 | Must |
| FR-31 | Phản hồi đầu tiên phải hiển thị trên TFT trong vòng 20 giây sau khi nhận input hợp lệ và có Internet. | UC-04 | Must |
| FR-32 | Cloud phải áp dụng safety filter để tránh chẩn đoán y khoa, phán xét người dùng hoặc đưa lời khuyên nguy hiểm. | UC-04 | Must |
| FR-33 | Khi phát hiện tín hiệu nguy cấp, Cloud phải trả thông điệp khuyên liên hệ người thân, chuyên gia hoặc dịch vụ hỗ trợ phù hợp. | UC-04 | Must |
| FR-34 | Hệ thống chỉ lưu nội dung tóm tắt hội thoại khi người dùng cho phép. | UC-04 | Must |

## 6.7. Nhóm chức năng báo cáo trên TFT qua Cloud

| ID | Yêu cầu chức năng | Use case liên quan | Độ ưu tiên |
| -- | ----------------- | ------------------ | ---------- |
| FR-35 | Thiết bị phải cho phép người dùng mở Report từ HOME và chọn report period trên TFT: ngày, tháng hoặc năm. | UC-05 | Must |
| FR-36 | Thiết bị phải gọi Cloud Report API để lấy báo cáo rút gọn theo period đã chọn. | UC-05 | Must |
| FR-37 | Cloud Report Engine phải tính tỷ lệ từng cảm xúc, xu hướng thay đổi, hiệu quả hoạt động và hiệu quả nội dung đã nghe dựa trên dữ liệu đã đồng bộ. | UC-05 | Must |
| FR-38 | Cloud phải trả report dưới dạng TFT cards, mỗi card ngắn gọn và có thể đọc trên màn hình nhỏ; prototype có thể hiển thị dữ liệu giả lập khi chưa đủ dữ liệu thật. | UC-05 | Must |
| FR-39 | Báo cáo rút gọn phải hiển thị trên TFT trong vòng 180 giây sau khi người dùng yêu cầu hoặc sau chu kỳ đồng bộ. | UC-05 | Must |
| FR-40 | Nếu dữ liệu chưa đủ, Cloud phải trả trạng thái `limited_data` và TFT phải hiển thị thông báo khuyến nghị check-in thêm. | UC-05 | Must |
| FR-41 | Thiết bị phải lưu bản report gần nhất để người dùng xem lại nhanh khi mất Internet. | UC-05 | Should |

## 6.8. Nhóm chức năng quản lý dữ liệu người dùng

| ID | Yêu cầu chức năng | Use case liên quan | Độ ưu tiên |
| -- | ----------------- | ------------------ | ---------- |
| FR-42 | Hệ thống phải liên kết mỗi thiết bị với đúng một tài khoản người dùng tại một thời điểm. | UC-02, UC-03, UC-04, UC-05 | Must |
| FR-43 | Người dùng phải có thể xem lịch sử cảm xúc rút gọn trên TFT theo các phiên gần nhất. | UC-05 | Should |
| FR-44 | Người dùng phải có cơ chế xóa dữ liệu cục bộ trên thiết bị. | UC-01, UC-05 | Should |
| FR-45 | Hệ thống phải lưu consent của người dùng liên quan đến dữ liệu âm thanh, hội thoại và lựa chọn nội dung. | UC-03, UC-04, UC-05 | Must |

## 6.9. Traceability Matrix

| Objective | Use case | Functional requirements |
| --------- | -------- | ----------------------- |
| SMART Objective 1 | UC-01 | FR-01 đến FR-09, FR-44 |
| SMART Objective 2 | UC-02 | FR-12 đến FR-20, FR-42 |
| SMART Objective 2 | UC-03 | FR-12, FR-21 đến FR-27, FR-42, FR-45 |
| SMART Objective 2 | UC-04 | FR-12, FR-28 đến FR-34, FR-42, FR-45 |
| SMART Objective 3 | UC-05 | FR-09 đến FR-13, FR-35 đến FR-45 |
