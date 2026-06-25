# 07. Non-Functional Requirement

## 7.1. Tổng quan

Non-functional requirements được điều chỉnh theo phạm vi mới: TFT screen là giao diện theo dõi chính, Objective 1 chạy trên Edge, Objective 2 và 3 cần Cloud. Vì nhóm phát triển là sinh viên, các mục tiêu hiệu năng được đặt ở mức khả thi cho prototype.

## 7.2. Hiệu năng

| ID | Yêu cầu | Mục tiêu | Độ ưu tiên |
| -- | ------ | -------- | ---------- |
| NFR-01 | Độ trễ Speech Emotion Recognition | Không quá 15 giây sau tương tác giọng nói hợp lệ | Must |
| NFR-02 | Độ trễ gợi ý hoạt động/nội dung cloud-assisted | Không quá 20 giây sau khi người dùng yêu cầu hỗ trợ và có Internet; nếu có emotion label thì dùng để cá nhân hóa | Must |
| NFR-03 | Độ trễ phản hồi hội thoại cloud-assisted | Không quá 20 giây sau khi có input hợp lệ và có Internet | Must |
| NFR-04 | Độ trễ danh sách bài hát/podcast theo chủ đích | Không quá 20 giây sau khi người dùng chọn category và có Internet | Must |
| NFR-05 | Độ trễ tạo báo cáo TFT | Không quá 180 giây sau yêu cầu hoặc chu kỳ đồng bộ | Must |
| NFR-06 | Độ trễ chuyển màn hình TFT | Thao tác menu phản hồi trong vòng 1 giây | Should |

## 7.3. Độ tin cậy và khả dụng

| ID | Yêu cầu | Mục tiêu | Độ ưu tiên |
| -- | ------ | -------- | ---------- |
| NFR-07 | Hoạt động offline cho Objective 1 | Thiết bị vẫn nhận diện cảm xúc và lưu session khi mất Internet | Must |
| NFR-08 | Phụ thuộc Internet cho Objective 2 và 3 | Khi offline, TFT phải thông báo rõ rằng gợi ý, bài hát/podcast, hội thoại và báo cáo cần Cloud | Must |
| NFR-09 | Không mất dữ liệu pending | Session pending và media feedback pending được giữ cho đến khi sync thành công hoặc bị người dùng xóa | Must |
| NFR-10 | Retry đồng bộ | Thiết bị tự retry khi Internet khả dụng | Should |
| NFR-11 | Idempotency | Server không tạo trùng session khi Edge gửi lại cùng client_session_id | Must |
| NFR-12 | Quan sát trạng thái | TFT hiển thị online/offline, pending count và last sync | Must |

## 7.4. Bảo mật và quyền riêng tư

| ID | Yêu cầu | Mục tiêu | Độ ưu tiên |
| -- | ------ | -------- | ---------- |
| NFR-13 | Không upload audio mặc định | Âm thanh thô không được gửi lên cloud nếu người dùng chưa cho phép | Must |
| NFR-14 | Minh bạch ghi âm | TFT hiển thị rõ khi thiết bị đang nghe/ghi âm | Must |
| NFR-15 | Xác thực thiết bị | Edge API yêu cầu device token hoặc signed request | Must |
| NFR-16 | Phân quyền dữ liệu | Cloud chỉ chấp nhận dữ liệu từ thiết bị đã ghép với user hợp lệ | Must |
| NFR-17 | Xóa dữ liệu cục bộ | Người dùng có cơ chế xóa cache hoặc lịch sử gần trên thiết bị | Should |
| NFR-18 | Bảo mật truyền tải | API dùng HTTPS trong triển khai thực tế | Must |

## 7.5. An toàn cảm xúc

| ID | Yêu cầu | Mục tiêu | Độ ưu tiên |
| -- | ------ | -------- | ---------- |
| NFR-19 | Không chẩn đoán | Hệ thống không tuyên bố chẩn đoán bệnh lý tâm thần | Must |
| NFR-20 | Ngôn ngữ đồng cảm | Phản hồi cloud phải bình tĩnh, tôn trọng và không phán xét | Must |
| NFR-21 | Xử lý tín hiệu nguy cấp | Cloud trả thông điệp liên hệ hỗ trợ phù hợp thay vì tiếp tục hội thoại thông thường | Must |
| NFR-22 | Quyền tự chủ | Người dùng có thể bỏ qua gợi ý, dừng hội thoại, không chọn nội dung nghe hoặc xóa dữ liệu cục bộ | Must |

## 7.6. Khả dụng và trải nghiệm TFT

| ID | Yêu cầu | Mục tiêu | Độ ưu tiên |
| -- | ------ | -------- | ---------- |
| NFR-23 | Thao tác đơn giản | Người dùng bắt đầu check-in bằng một thao tác rõ ràng | Must |
| NFR-24 | Kết quả dễ đọc | Emotion label, confidence, gợi ý và danh sách bài hát/podcast phải vừa màn hình TFT | Must |
| NFR-25 | Screen flow nhất quán | HOME, CHECK-IN, RESULT, SUPPORT, ACTIVITY, MUSIC-PODCAST, CONVERSATION, STATUS, REPORT liên kết rõ | Must |
| NFR-26 | Báo cáo TFT dễ hiểu | Report cards phải ngắn, ưu tiên insight chính thay vì bảng dài | Must |
| NFR-27 | Khả năng tiếp cận | Màu sắc, font và tương phản đủ rõ trên màn hình nhỏ | Should |

## 7.7. Khả năng bảo trì và mở rộng

| ID | Yêu cầu | Mục tiêu | Độ ưu tiên |
| -- | ------ | -------- | ---------- |
| NFR-28 | Pipeline tách module | SER, sync, recommendation, media recommendation, conversation và report có thể cập nhật độc lập | Should |
| NFR-29 | Mở rộng emotion taxonomy | Có thể thêm lớp cảm xúc mới mà không phá vỡ schema chính | Should |
| NFR-30 | Mở rộng thư viện hoạt động/nội dung | Có thể thêm hoạt động, bài hát, podcast hoặc category mới trong Cloud Service | Should |
| NFR-31 | Truy vết yêu cầu | Objective, use case, requirement và API có ID rõ ràng | Should |
