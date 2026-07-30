# 06. Yêu cầu phi chức năng

## 6.1. Tổng quan

Yêu cầu phi chức năng được điều chỉnh theo phạm vi mới: màn hình thiết bị là giao diện theo dõi chính, Mục tiêu 1 chạy tại thiết bị, còn Mục tiêu 2 và 3 cần máy chủ. Vì đây là đồ án sinh viên, các mục tiêu hiệu năng được đặt ở mức khả thi cho bản mẫu.

## 6.2. Hiệu năng

| ID | Yêu cầu | Mục tiêu | Độ ưu tiên |
| -- | ------ | -------- | ---------- |
| NFR-01 | Độ trễ nhận diện cảm xúc bằng giọng nói | Không quá 30 giây sau tương tác giọng nói hợp lệ | Bắt buộc |
| NFR-02 | Độ trễ gợi ý hoạt động hoặc nội dung | Không quá 20 giây sau khi người dùng yêu cầu hỗ trợ và có Internet; nếu có nhãn cảm xúc thì dùng để cá nhân hóa | Bắt buộc |
| NFR-03 | Độ trễ phản hồi hội thoại | Không quá 20 giây sau khi có dữ liệu hợp lệ và có Internet | Bắt buộc |
| NFR-04 | Độ trễ danh sách bài hát/podcast theo chủ đích | Không quá 20 giây sau khi người dùng chọn category và có Internet | Must |
| NFR-05 | Độ trễ tạo báo cáo TFT | Không quá 180 giây sau yêu cầu của người dùng | Must |
| NFR-06 | Độ trễ chuyển màn hình TFT | Thao tác menu phản hồi trong vòng 1 giây | Should |

## 6.3. Độ tin cậy và khả dụng

| ID | Yêu cầu | Mục tiêu | Độ ưu tiên |
| -- | ------ | -------- | ---------- |
| NFR-07 | Hoạt động khi mất kết nối của Mục tiêu 1 | Thiết bị vẫn nhận diện cảm xúc và lưu trạng thái cảm xúc đã xác nhận gần nhất khi mất Internet | Bắt buộc |
| NFR-08 | Phụ thuộc Internet của Mục tiêu 2 và 3 | Khi mất kết nối, màn hình phải thông báo rõ rằng gợi ý, nội dung nghe, hội thoại và báo cáo mới cần máy chủ | Bắt buộc |
| NFR-09 | Lưu trạng thái khi mất kết nối | Phần mềm thiết bị chỉ giữ cảm xúc đã xác nhận gần nhất trong bộ nhớ cục bộ; trạng thái mới ghi đè trạng thái cũ | Bắt buộc |
| NFR-10 | Thử đồng bộ lại | Chưa có chức năng tự thử đồng bộ lại khi Internet khả dụng | Khuyến nghị |
| NFR-11 | Không tạo trùng dữ liệu | Máy chủ không tạo trùng phiên khi nhận lại cùng `client_session_id` từ một thiết bị | Bắt buộc |
| NFR-12 | Theo dõi trạng thái | Màn hình hiển thị trạng thái có hoặc không có kết nối, số phiên chờ và lần đồng bộ gần nhất | Bắt buộc |

## 6.4. Bảo mật và quyền riêng tư

| ID | Yêu cầu | Mục tiêu | Độ ưu tiên |
| -- | ------ | -------- | ---------- |
| NFR-13 | Bảo vệ âm thanh | Âm thanh dùng để kiểm tra cảm xúc không được gửi lên máy chủ. Âm thanh trò chuyện chỉ được gửi khi người dùng chủ động bắt đầu hội thoại, được xử lý tạm thời thành văn bản và không được lưu | Bắt buộc |
| NFR-14 | Minh bạch ghi âm | TFT hiển thị rõ khi thiết bị đang nghe/ghi âm | Must |
| NFR-15 | Xác thực thiết bị | Edge API yêu cầu device token hoặc signed request | Must |
| NFR-16 | Phân quyền dữ liệu | Cloud chỉ chấp nhận dữ liệu từ thiết bị đã ghép với user hợp lệ | Must |
| NFR-17 | Xóa dữ liệu cục bộ | Người dùng có cơ chế xóa cache hoặc lịch sử gần trên thiết bị | Should |
| NFR-18 | Bảo mật truyền tải | API dùng HTTPS trong triển khai thực tế | Must |

## 6.5. An toàn cảm xúc

| ID | Yêu cầu | Mục tiêu | Độ ưu tiên |
| -- | ------ | -------- | ---------- |
| NFR-19 | Không chẩn đoán | Hệ thống không tuyên bố chẩn đoán bệnh lý tâm thần | Must |
| NFR-20 | Ngôn ngữ đồng cảm | Phản hồi cloud phải bình tĩnh, tôn trọng và không phán xét | Must |
| NFR-21 | Xử lý tín hiệu nguy cấp | Cloud trả thông điệp liên hệ hỗ trợ phù hợp thay vì tiếp tục hội thoại thông thường | Must |
| NFR-22 | Quyền tự chủ | Người dùng có thể bỏ qua gợi ý, dừng hội thoại, không chọn nội dung nghe hoặc xóa dữ liệu cục bộ | Must |

## 6.6. Khả dụng và trải nghiệm TFT

| ID | Yêu cầu | Mục tiêu | Độ ưu tiên |
| -- | ------ | -------- | ---------- |
| NFR-23 | Thao tác đơn giản | Người dùng bắt đầu check-in bằng một thao tác rõ ràng | Must |
| NFR-24 | Kết quả dễ đọc | Emotion label, confidence, gợi ý và danh sách bài hát/podcast phải vừa màn hình TFT | Must |
| NFR-25 | Luồng màn hình nhất quán | Trang chủ, Kiểm tra cảm xúc, Kết quả, Hỗ trợ, Hoạt động, Nhạc-Podcast, Trò chuyện, Trạng thái và Báo cáo liên kết rõ | Must |
| NFR-26 | Báo cáo TFT dễ hiểu | Các thẻ báo cáo phải ngắn, ưu tiên nhận định chính thay vì bảng dài | Must |
| NFR-27 | Khả năng tiếp cận | Màu sắc, font và tương phản đủ rõ trên màn hình nhỏ | Should |

## 6.7. Khả năng bảo trì và mở rộng

| ID | Yêu cầu | Mục tiêu | Độ ưu tiên |
| -- | ------ | -------- | ---------- |
| NFR-28 | Pipeline tách module | SER, sync, recommendation, media recommendation, conversation và report có thể cập nhật độc lập | Should |
| NFR-29 | Mở rộng emotion taxonomy | Có thể thêm lớp cảm xúc mới mà không phá vỡ schema chính | Should |
| NFR-30 | Mở rộng thư viện hoạt động/nội dung | Có thể thêm hoạt động, bài hát, podcast hoặc category mới trong Cloud Service | Should |
| NFR-31 | Truy vết yêu cầu | Objective, use case, requirement và API có ID rõ ràng | Should |
