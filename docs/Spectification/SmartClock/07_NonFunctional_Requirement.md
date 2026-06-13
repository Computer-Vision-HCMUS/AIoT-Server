# 07. Non-Functional Requirement

## 7.1. Overview

Non-functional requirements mô tả các ràng buộc chất lượng cần có để SomniLearnAI vận hành ổn định trong vai trò một Edge Device AIoT kết hợp dashboard. Các yêu cầu này hỗ trợ trực tiếp cho functional requirements và 3 objective chính của hệ thống.

## 7.2. Performance

| ID | Non-Functional Requirement | Related Objective | Priority |
| --- | --- | --- | --- |
| NFR-01 | Màn hình Edge Device phải cập nhật thời gian, trạng thái phiên và dữ liệu realtime đủ nhanh để người dùng quan sát liên tục trong quá trình học hoặc ngủ. | Objective 1, Objective 2 | Must |
| NFR-02 | Báo cáo ngủ phải được tạo trong vòng 1 phút sau khi phiên ngủ kết thúc trong điều kiện thiết bị hoạt động bình thường. | Objective 2 | Must |
| NFR-03 | Dashboard phải cập nhật dữ liệu trong vòng 60 giây sau khi API Server nhận được phiên hợp lệ. | Objective 3 | Must |
| NFR-04 | Các thao tác chính bằng nút vật lý như chuyển màn hình, bắt đầu phiên, dừng phiên và bật/tắt báo thức phải phản hồi gần như tức thời với người dùng. | Objective 1, Objective 2 | Must |

## 7.3. Reliability and Availability

| ID | Non-Functional Requirement | Related Objective | Priority |
| --- | --- | --- | --- |
| NFR-05 | Pomodoro Timer, Sleep Monitoring cơ bản và Alarm Setting phải hoạt động cục bộ khi thiết bị không có Internet. | Objective 1, Objective 2 | Must |
| NFR-06 | Báo thức phải tiếp tục hoạt động dựa trên RTC hoặc đồng hồ hệ thống cục bộ khi mất kết nối mạng. | Objective 2 | Must |
| NFR-07 | Dữ liệu phiên chưa đồng bộ không được mất khi thiết bị tạm thời mất Internet trong quá trình sử dụng thông thường. | Objective 3 | Should |
| NFR-08 | Hệ thống phải có trạng thái rõ ràng cho các phiên pending, synced hoặc failed để hỗ trợ phục hồi đồng bộ. | Objective 3 | Should |

## 7.4. Data Storage and Retention

| ID | Non-Functional Requirement | Related Objective | Priority |
| --- | --- | --- | --- |
| NFR-09 | Lịch sử phiên ngủ phải được lưu tối thiểu 30 ngày trên Server hoặc bộ lưu trữ dashboard. | Objective 2, Objective 3 | Must |
| NFR-10 | Dữ liệu học tập và thuyết trình phải được lưu theo ngày và tháng để hỗ trợ thống kê tiến độ. | Objective 1, Objective 3 | Must |
| NFR-11 | Dữ liệu phiên phải có timestamp, loại phiên và userId để phục vụ truy vấn dashboard. | Objective 3 | Must |
| NFR-12 | Bộ nhớ cục bộ trên Edge Device chỉ nên lưu dữ liệu tối thiểu cần thiết cho đồng bộ lại, tránh lưu raw audio dài hạn nếu không cần. | Objective 1, Objective 3 | Should |

## 7.5. Security and Privacy

| ID | Non-Functional Requirement | Related Objective | Priority |
| --- | --- | --- | --- |
| NFR-13 | Dashboard phải có cơ chế xác thực để người dùng chỉ xem được dữ liệu phiên của mình. | Objective 3 | Must |
| NFR-14 | API Server phải validate dữ liệu phiên trước khi lưu để tránh dữ liệu thiếu thời gian bắt đầu, thời gian kết thúc hoặc loại phiên. | Objective 3 | Must |
| NFR-15 | Dữ liệu giấc ngủ, môi trường phòng ngủ và kết quả thuyết trình phải được xem là dữ liệu cá nhân cần bảo vệ. | Objective 1, Objective 2, Objective 3 | Must |
| NFR-16 | Khi gửi dữ liệu âm thanh hoặc đặc trưng âm thanh lên Server, hệ thống nên ưu tiên gửi feature summary thay vì raw audio nếu raw audio không cần thiết. | Objective 1 | Should |

## 7.6. Usability

| ID | Non-Functional Requirement | Related Objective | Priority |
| --- | --- | --- | --- |
| NFR-17 | Giao diện Edge Device phải dùng nhãn ngắn, trạng thái rõ ràng và luồng màn hình nhất quán để người dùng thao tác bằng nút vật lý. | Objective 1, Objective 2 | Must |
| NFR-18 | Dashboard phải tách rõ Study Sessions, Sleep Sessions và Presentation Sessions để người dùng dễ theo dõi từng nhóm dữ liệu. | Objective 3 | Must |
| NFR-19 | Các chỉ số quan trọng như số Pomodoro, tổng phút tập trung, điểm ngủ, thời lượng ngủ, giờ báo thức và điểm thuyết trình phải dễ nhìn trên màn hình tương ứng. | Objective 1, Objective 2, Objective 3 | Must |
| NFR-20 | Khi hệ thống offline hoặc đang chờ đồng bộ, giao diện phải hiển thị trạng thái dễ hiểu thay vì để người dùng tự suy đoán. | Objective 3 | Should |

## 7.7. Maintainability and Extensibility

| ID | Non-Functional Requirement | Related Objective | Priority |
| --- | --- | --- | --- |
| NFR-21 | Kiến trúc phần mềm nên tách rõ Edge Device, API Server, Session Database và Web Dashboard để dễ bảo trì. | Objective 3 | Should |
| NFR-22 | Mô hình dữ liệu phiên nên cho phép mở rộng thêm loại cảm biến hoặc trường phân tích mới mà không làm thay đổi luồng chính. | Objective 2, Objective 3 | Should |
| NFR-23 | Rule-based Sleep Scoring nên được thiết kế theo cấu hình ngưỡng để dễ điều chỉnh khi có dữ liệu thực nghiệm mới. | Objective 2 | Should |
| NFR-24 | API đồng bộ phiên nên dùng cấu trúc thống nhất cho study, sleep và presentation sessions để giảm trùng lặp xử lý. | Objective 3 | Should |
