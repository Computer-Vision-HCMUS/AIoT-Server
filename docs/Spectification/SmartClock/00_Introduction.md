# 00. Introduction

## 0.1. Document Information

Tài liệu này mô tả đặc tả hệ thống **SomniLearnAI**, một sản phẩm đồng hồ thông minh AIoT hỗ trợ học tập, luyện tập thuyết trình, quan sát giấc ngủ và dashboard quản lý dữ liệu cá nhân. Tài liệu được dùng làm cơ sở thống nhất giữa nhóm phát triển, phần cứng Edge Device, server và giao diện dashboard.

| Field | Value |
| ----- | ----- |
| Product name | SomniLearnAI |
| Previous name | SmartClock |
| Document type | AIoT Product Specification |
| Course | Introduction to Smart Device Programming |
| Class | 23CLC02 |
| Version | 2.0 |
| Last updated | 08/06/2026 |

## 0.2. Product Identity

**SomniLearnAI** được định hướng là một thiết bị đồng hồ thông minh đặt tại bàn học hoặc phòng ngủ, kết hợp giữa Edge AI và Internet Service để hỗ trợ người dùng cải thiện khả năng tập trung, luyện tập thuyết trình và theo dõi giấc ngủ.

Sản phẩm không chỉ hiển thị thời gian như một đồng hồ thông thường, mà còn ghi nhận các phiên học Pomodoro, phiên luyện tập thuyết trình và phiên ngủ. Dữ liệu được hiển thị trực tiếp trên màn hình thiết bị khi người dùng đang sử dụng, đồng thời có thể đồng bộ lên dashboard để xem lại theo ngày, tháng hoặc từng loại phiên.

> **SomniLearnAI - Learn better, sleep smarter, improve with data.**

## 0.3. Member Information

| STT | Member | Student ID | Phone Number | Email |
| --- | ------ | ---------- | ------------ | ----- |
| 1 | Trần Hải Đức | 23127173 | 0916821170 | thduc23@clc.fitus.edu.vn |
| 2 | Nguyễn Trọng Tài | 23127008 | 0377425510 | nttai23@clc.fitus.edu.vn |
| 3 | Nguyễn Công Chiến | 23127331 | 0369314655 | ncchien23@clc.fitus.edu.vn |
| 4 | Phạm Nguyễn Gia Bảo | 20127119 | 0926127333 | pngbao20@clc.fitus.edu.vn |

## 0.4. Specification Change Comparison

| Area | Previous specification | Updated specification |
| ---- | ---------------------- | --------------------- |
| Product name | SmartClock | SomniLearnAI |
| Objective 1 | Hỗ trợ tập trung và làm việc hiệu quả | Hỗ trợ cải thiện khả năng tập trung khi học theo Pomodoro, kết hợp luyện tập và chấm điểm thuyết trình |
| Objective 2 | Hỗ trợ giấc ngủ và đặt báo thức | Hỗ trợ cải thiện giấc ngủ, quan sát Edge AI và phát hiện tác nhân môi trường làm giấc ngủ không ngon |
| Objective 3 | Giải trí và trang trí góc làm việc | Dashboard quản lý phiên học, phiên thuyết trình và phiên ngủ |
| Sleep use case | Theo dõi giấc ngủ và đặt báo thức | Giữ use case quan sát giấc ngủ Edge AI, bỏ use case đặt báo thức |
| Internet Service | Chưa có nội dung chi tiết | Bổ sung dashboard theo Objective 3 |
| Data history | Chưa nhấn mạnh lịch sử phiên | Bổ sung lịch sử phiên học, phiên ngủ, phiên thuyết trình và tổng kết theo tháng |

## 0.5. Revision History

| Version | Date | Changed by | Description |
| ------- | ---- | ---------- | ----------- |
| 1.0 | 26/05/2026 | Project team | Khởi tạo đặc tả SmartClock với các mục tiêu Pomodoro, giấc ngủ và giải trí |
| 1.1 | 05/06/2026 | Project team | Bổ sung Edge AI cho quan sát giấc ngủ và hướng dẫn sử dụng thiết bị |
| 2.0 | 08/06/2026 | Project team | Đổi tên sản phẩm thành SomniLearnAI, cập nhật objective theo SMART, bỏ báo thức khỏi sleep use case và thêm dashboard quản lý phiên |

## 0.6. Document Structure

| Chapter | Content |
| ------- | ------- |
| 01. Background | Bối cảnh, động lực và nhóm người dùng mục tiêu |
| 02. Architecture & Hardware | Kiến trúc Edge-Server và phần cứng hệ thống |
| 03. Objectives | Mục tiêu SMART, use case và Mermaid diagram |
| 04. EdgeAI | Mô hình Edge AI và dữ liệu cảm biến |
| 05. Internet Service | Dashboard quản lý phiên học, ngủ và thuyết trình |
| 06. User Manual | Hướng dẫn thao tác cho người dùng |
| 07. Conclusion | Tổng kết, giới hạn và hướng phát triển |
| 08. Appendix & Reference | Phụ lục và tài liệu tham khảo |
