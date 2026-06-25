# 00. Giới thiệu

## 0.1. Thông tin tài liệu

Tài liệu này mô tả đặc tả sản phẩm **EmotiCare AIoT - Intelligent Emotional Companion**, một thiết bị AIoT thông minh có vai trò đồng hành, nhận biết và hỗ trợ người dùng chăm sóc sức khỏe cảm xúc trong đời sống hằng ngày. Tài liệu được dùng làm cơ sở thống nhất giữa nhóm phát triển phần cứng, Edge AI, server/cloud service, TFT screen và tài liệu hướng dẫn sử dụng.

| Trường thông tin | Giá trị |
| ---------------- | ------- |
| Tên sản phẩm | EmotiCare AIoT |
| Tên đầy đủ | EmotiCare AIoT - Intelligent Emotional Companion |
| Tên tiếng Việt | Thiết bị AIoT thông minh đồng hành và chăm sóc sức khỏe cảm xúc |
| Loại tài liệu | AIoT Product Specification |
| Môn học | Introduction to Smart Device Programming |
| Lớp | 23CLC02 |
| Phiên bản | 3.1 |
| Ngày cập nhật | 25/06/2026 |

## 0.2. Định vị sản phẩm

**EmotiCare AIoT** là thiết bị AIoT ứng dụng trí tuệ nhân tạo nhằm hỗ trợ người dùng nhận biết, thấu hiểu và quản lý cảm xúc trong cuộc sống hằng ngày. Thiết bị nhận diện trạng thái cảm xúc thông qua giọng nói, đưa ra gợi ý hoặc tương tác phù hợp để cải thiện tâm trạng, đồng thời thống kê và phân tích xu hướng cảm xúc theo ngày, tuần, tháng và năm.

Điểm khác biệt của sản phẩm là cách tiếp cận **Edge-first nhưng Cloud-assisted**: tác vụ nhận diện cảm xúc cốt lõi được xử lý trực tiếp trên thiết bị để giảm độ trễ và tăng tính riêng tư, trong khi các chức năng gợi ý hoạt động, trò chuyện hỗ trợ và báo cáo dài hạn phối hợp với Internet/Cloud Service. Toàn bộ kết quả theo dõi, báo cáo và trạng thái đồng bộ được hiển thị trên TFT screen của thiết bị.

> **EmotiCare AIoT - Understand your feelings, care for your mind.**

## 0.3. Mục đích sản phẩm

EmotiCare AIoT giúp người dùng chủ động chăm sóc sức khỏe tinh thần bằng cách:

* Nhận diện cảm xúc trong vòng 15 giây sau mỗi lần tương tác bằng giọng nói hợp lệ.
* Đưa ra ít nhất một hoạt động, bài hát, podcast hoặc một phản hồi đồng cảm trong vòng 20 giây sau khi có kết quả cảm xúc và có Internet.
* Lưu lại từng phiên cảm xúc để người dùng có thể nhìn lại lịch sử của mình.
* Tạo tóm tắt cảm xúc theo ngày, tuần, tháng và năm trong vòng 180 giây sau khi người dùng yêu cầu hoặc sau một chu kỳ đồng bộ.
* Phân tích hiệu quả của các hoạt động, bài hát và podcast cải thiện tâm trạng để gợi ý ngày càng phù hợp hơn.

## 0.4. Thông tin thành viên

| STT | Thành viên | MSSV | Số điện thoại | Email |
| --- | ---------- | ---- | ------------- | ----- |
| 1 | Trần Hải Đức | 23127173 | 0916821170 | thduc23@clc.fitus.edu.vn |
| 2 | Nguyễn Trọng Tài | 23127008 | 0377425510 | nttai23@clc.fitus.edu.vn |
| 3 | Nguyễn Công Chiến | 23127331 | 0369314655 | ncchien23@clc.fitus.edu.vn |
| 4 | Phạm Nguyễn Gia Bảo | 20127119 | 0926127333 | pngbao20@clc.fitus.edu.vn |

## 0.5. Phạm vi cập nhật đặc tả

| Hạng mục | Đặc tả trước | Đặc tả cập nhật |
| -------- | ------------ | --------------- |
| Định hướng sản phẩm | Thiết bị thông minh cá nhân với nhiều chức năng rời rạc | Thiết bị đồng hành cảm xúc tập trung vào nhận diện, hỗ trợ và phân tích cảm xúc |
| Objective 1 | Theo dõi phiên học/tác vụ cá nhân | Speech Emotion Recognition trên Edge Device trong 15 giây |
| Objective 2 | Tạo báo cáo cho một nhóm chức năng khác | Cloud-assisted recommendation, media selection và conversation trong 20 giây |
| Objective 3 | Giao diện web theo dõi phiên sử dụng | Báo cáo cảm xúc hiển thị trên TFT theo ngày, tuần, tháng, năm trong 180 giây |
| Edge AI | Xử lý cục bộ cho một tác vụ giới hạn | Phân tích đặc trưng giọng nói và ngữ cảnh sức khỏe cảm xúc tại thiết bị |
| Internet Service | Đồng bộ và giao diện web cơ bản | Thiết kế DB, API, cloud recommendation/conversation/report service và flow Edge-Cloud-TFT |
| User Manual | Hướng dẫn theo luồng cũ | Hướng dẫn theo luồng phần cứng mới của EmotiCare AIoT |

## 0.6. Lịch sử phiên bản

| Phiên bản | Ngày | Người cập nhật | Nội dung |
| --------- | ---- | -------------- | -------- |
| 1.0 | 26/05/2026 | Project team | Khởi tạo đặc tả thiết bị thông minh |
| 2.0 | 13/06/2026 | Project team | Cập nhật đặc tả theo hướng sản phẩm trước đó |
| 3.0 | 25/06/2026 | Project team | Chuyển đổi đặc tả sang EmotiCare AIoT |
| 3.1 | 25/06/2026 | Project team | Viết lại có dấu, chi tiết hóa background, objective, Edge AI, Internet Service, screen flow và user manual |

## 0.7. Cấu trúc tài liệu

| Chương | Nội dung |
| ------ | -------- |
| 01. Background | Bối cảnh, nguồn cảm hứng từ EMO, vấn đề, người dùng mục tiêu và sơ đồ suy ra mục tiêu |
| 02. Architecture & Hardware | Kiến trúc Edge-Server, thành phần phần cứng và luồng dữ liệu hệ thống |
| 03. Objectives | SMART objective, use case, input/output, bảng use case và Mermaid diagram |
| 04. EdgeAI | Thiết kế Edge AI cho Speech Emotion Recognition, dữ liệu đầu vào, đặc trưng âm thanh, mô hình và đánh giá |
| 05. Internet Service | Thiết kế database, API và flow tương tác giữa Edge Device, Cloud Service và TFT screen |
| 06. Functional Requirement | Yêu cầu chức năng được truy vết theo objective và use case |
| 07. Non-Functional Requirement | Yêu cầu phi chức năng về hiệu năng, bảo mật, riêng tư, độ tin cậy và an toàn cảm xúc |
| 08. User Manual | Hướng dẫn sử dụng thiết bị phần cứng, TFT screen và đồng bộ Internet |
| 09. Conclusion | Tổng kết, lợi ích, giới hạn và hướng phát triển |
| 10. Appendix & Reference | Thuật ngữ, bảng dữ liệu, API summary và tài liệu tham khảo |
