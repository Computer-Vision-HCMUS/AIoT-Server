# 06. Functional Requirement

## 6.1. Overview

Functional requirements của SomniLearnAI được xây dựng trực tiếp từ 3 objective trong tài liệu Objectives:

* **Objective 1:** ghi nhận và hiển thị tối thiểu 80% số phiên Pomodoro, tổng phút tập trung và điểm đánh giá thuyết trình.
* **Objective 2:** tự động tạo báo cáo trong vòng 1 phút sau mỗi phiên ngủ, bao gồm thời lượng ngủ, điểm chất lượng giấc ngủ, thời gian báo thức và các yếu tố môi trường, đồng thời lưu lịch sử tối thiểu 30 ngày.
* **Objective 3:** đồng bộ và cập nhật dashboard trong vòng 60 giây sau mỗi phiên học, ngủ hoặc thuyết trình.

## 6.2. Objective 1: Study and Presentation Support

| ID | Functional Requirement | Related Use Case | Priority |
| --- | --- | --- | --- |
| FR-01 | Hệ thống phải cho phép người dùng bắt đầu, tạm dừng, tiếp tục và kết thúc phiên Pomodoro trên Edge Device. | Pomodoro Timer | Must |
| FR-02 | Hệ thống phải cho phép người dùng tùy chỉnh thời gian học và thời gian nghỉ cho phiên Pomodoro. | Pomodoro Timer | Should |
| FR-03 | Hệ thống phải hiển thị giờ hiện tại, trạng thái Study/Break, thời gian còn lại và số Pomodoro đã hoàn thành trong ngày. | Pomodoro Timer | Must |
| FR-04 | Hệ thống phải phát tín hiệu khi kết thúc phiên học hoặc phiên nghỉ. | Pomodoro Timer | Must |
| FR-05 | Hệ thống phải lưu số Pomodoro hoàn thành và tổng phút tập trung để đồng bộ dashboard. | Pomodoro Timer | Must |
| FR-06 | Hệ thống phải cho phép người dùng bắt đầu và kết thúc phiên luyện tập thuyết trình. | Seminar Practice | Must |
| FR-07 | Hệ thống phải ghi nhận thời lượng trình bày và dữ liệu âm thanh hoặc đặc trưng âm thanh cần thiết cho phiên thuyết trình. | Seminar Practice | Must |
| FR-08 | Hệ thống phải lưu tạm phiên thuyết trình khi thiết bị offline và gửi lên Server khi có kết nối. | Seminar Practice | Should |
| FR-09 | Server phải xử lý phiên thuyết trình và trả về điểm đánh giá cùng nhận xét ngắn khi dữ liệu hợp lệ. | Seminar Practice | Should |
| FR-10 | Hệ thống phải hiển thị điểm đánh giá thuyết trình, trạng thái xử lý và nhận xét ngắn sau khi Server xử lý xong. | Seminar Practice | Must |

## 6.3. Objective 2: Sleep Report and Alarm Support

| ID | Functional Requirement | Related Use Case | Priority |
| --- | --- | --- | --- |
| FR-11 | Hệ thống phải cho phép người dùng bật và dừng Sleep Monitoring trên Edge Device. | Sleep Monitoring Edge AI | Must |
| FR-12 | Hệ thống phải ghi nhận thời gian bắt đầu, thời gian kết thúc và tổng thời lượng ngủ của mỗi phiên ngủ. | Sleep Monitoring Edge AI | Must |
| FR-13 | Hệ thống phải hiển thị realtime các chỉ số môi trường phòng ngủ như ánh sáng, tiếng ồn, nhiệt độ, độ ẩm và CO₂ khi có cảm biến tương ứng. | Sleep Monitoring Edge AI | Must |
| FR-14 | Hệ thống phải dùng Edge AI hoặc rule-based scoring để tạo điểm chất lượng giấc ngủ và nhận xét ngắn sau phiên ngủ. | Sleep Monitoring Edge AI | Must |
| FR-15 | Hệ thống phải tự động tạo báo cáo trong vòng 1 phút sau khi phiên ngủ kết thúc. | Sleep Monitoring Edge AI | Must |
| FR-16 | Báo cáo ngủ phải bao gồm thời lượng ngủ, điểm chất lượng giấc ngủ, thời gian báo thức và các yếu tố môi trường ảnh hưởng. | Sleep Monitoring Edge AI | Must |
| FR-17 | Hệ thống phải lưu trữ lịch sử phiên ngủ tối thiểu 30 ngày để người dùng theo dõi thói quen ngủ. | Sleep Sessions Dashboard | Must |
| FR-18 | Hệ thống phải cho phép người dùng đặt giờ và phút báo thức trực tiếp trên Edge Device. | Alarm Setting | Must |
| FR-19 | Hệ thống phải cho phép người dùng bật hoặc tắt báo thức và xem trạng thái báo thức hiện tại. | Alarm Setting | Must |
| FR-20 | Báo thức phải hoạt động cục bộ trên Edge Device ngay cả khi không có Internet. | Alarm Setting | Must |
| FR-21 | Khi đến giờ báo thức, hệ thống phải phát âm báo hoặc tín hiệu cảnh báo phù hợp với phần cứng được triển khai. | Alarm Setting | Must |

## 6.4. Objective 3: Dashboard and Synchronization

| ID | Functional Requirement | Related Use Case | Priority |
| --- | --- | --- | --- |
| FR-22 | Hệ thống phải đồng bộ phiên học, phiên ngủ và phiên thuyết trình từ Edge Device lên API Server khi có kết nối Internet. | Session Synchronization | Must |
| FR-23 | Dashboard phải cập nhật dữ liệu trong vòng 60 giây sau khi phiên được đồng bộ thành công. | Session Synchronization | Must |
| FR-24 | Dashboard phải hiển thị thống kê phiên học theo ngày, tuần và tháng, bao gồm số Pomodoro và tổng phút tập trung. | Study Sessions Dashboard | Must |
| FR-25 | Dashboard phải hiển thị thống kê phiên ngủ theo ngày, tuần và tháng, bao gồm điểm ngủ, thời lượng ngủ và tác nhân môi trường thường gặp. | Sleep Sessions Dashboard | Must |
| FR-26 | Dashboard phải hiển thị lịch sử phiên thuyết trình, điểm đánh giá, thời lượng nói và xu hướng cải thiện. | Presentation Sessions Dashboard | Must |
| FR-27 | Hệ thống phải hỗ trợ lọc hoặc xem dữ liệu dashboard theo khoảng thời gian để người dùng theo dõi tiến bộ. | Dashboard Observation | Should |
| FR-28 | Hệ thống phải gắn dữ liệu phiên với người dùng tương ứng để tránh lẫn dữ liệu giữa nhiều người dùng. | Dashboard Observation | Must |

## 6.5. Offline and Recovery Behavior

| ID | Functional Requirement | Related Use Case | Priority |
| --- | --- | --- | --- |
| FR-29 | Khi offline, thiết bị vẫn phải cho phép dùng Pomodoro Timer, Alarm Setting và Sleep Monitoring cơ bản. | Offline Mode | Must |
| FR-30 | Khi offline, thiết bị phải lưu tạm các phiên chưa đồng bộ với trạng thái pending. | Offline Mode | Should |
| FR-31 | Khi kết nối Internet trở lại, thiết bị phải gửi các phiên pending lên Server theo thứ tự thời gian. | Reconnect Sync | Should |
| FR-32 | Hệ thống phải hiển thị trạng thái Online/Offline hoặc Sync Pending để người dùng biết tình trạng đồng bộ. | Status Screen | Should |
