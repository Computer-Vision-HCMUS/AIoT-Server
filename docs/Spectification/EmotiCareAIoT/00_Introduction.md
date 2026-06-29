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

**EmotiCare AIoT** là thiết bị AIoT ứng dụng trí tuệ nhân tạo nhằm hỗ trợ người dùng nhận biết, thấu hiểu và quản lý cảm xúc trong cuộc sống hằng ngày. Thiết bị nhận diện trạng thái cảm xúc thông qua giọng nói, đưa ra gợi ý hoặc tương tác phù hợp để cải thiện tâm trạng, đồng thời thống kê và phân tích xu hướng cảm xúc theo ngày, tháng và năm.

Điểm khác biệt của sản phẩm là cách tiếp cận **Edge-first nhưng Cloud-assisted**: tác vụ nhận diện cảm xúc cốt lõi được xử lý trực tiếp trên thiết bị để giảm độ trễ và tăng tính riêng tư, trong khi các chức năng gợi ý hoạt động, trò chuyện hỗ trợ và báo cáo dài hạn phối hợp với Internet/Cloud Service. Toàn bộ kết quả theo dõi, báo cáo và trạng thái đồng bộ được hiển thị trên TFT screen của thiết bị.

> **EmotiCare AIoT - Understand your feelings, care for your mind.**

## 0.3. Document Life-Cycle và Sign-off

### 0.3.1. Revision history

| Phiên bản | Ngày | Người cập nhật | Phase | Nội dung thay đổi |
| --------- | ---- | -------------- | ----- | ----------------- |
| 1.0 | 26/05/2026 | Project team | Initial Draft | Khởi tạo đặc tả thiết bị thông minh |
| 2.0 | 13/06/2026 | Project team | Working Update | Cập nhật đặc tả theo hướng sản phẩm trước đó |
| 3.0 | 25/06/2026 | Project team | Product Redesign | Chuyển đổi đặc tả sang EmotiCare AIoT |
| 3.1 | 25/06/2026 | Project team | Specification Refinement | Viết lại có dấu, chi tiết hóa background, objective, Edge AI, Internet Service, screen flow và user manual |
| 3.2 | 29/06/2026 | Project team | SRS Alignment | Bổ sung cấu trúc theo mẫu Software Requirements Specification |

### 0.3.2. Sign-off

| Vai trò | Người/nhóm phụ trách | Trách nhiệm xác nhận | Trạng thái |
| ------- | -------------------- | -------------------- | ---------- |
| Product Owner | Project team | Xác nhận phạm vi sản phẩm, mục tiêu và use case | Pending |
| Hardware Lead | Project team | Xác nhận phần cứng, chi phí prototype và screen flow TFT | Pending |
| Edge AI Lead | Project team | Xác nhận pipeline Speech Emotion Recognition và yêu cầu riêng tư | Pending |
| Cloud/API Lead | Project team | Xác nhận database, API và flow Edge-Cloud-TFT | Pending |
| Reviewer/Instructor | Course reviewer | Đánh giá tính đầy đủ của specification | Pending |

## 0.4. Intended Audience

| Đối tượng đọc | Phần nên đọc kỹ | Mục đích sử dụng tài liệu |
| ------------- | --------------- | -------------------------- |
| Nhóm phần cứng | Chương 02, 08, 10 | Chọn linh kiện, thiết kế luồng màn hình TFT và chuẩn bị prototype |
| Nhóm Edge AI | Chương 03, 04, 06, 07 | Xây dựng pipeline SER, xác định input/output và tiêu chí đánh giá |
| Nhóm Cloud/API | Chương 05, 06, 07, 10 | Thiết kế database, API, đồng bộ dữ liệu và report cards |
| Nhóm kiểm thử | Chương 03, 06, 07, 08 | Viết test case theo use case, functional requirement và non-functional requirement |
| Giảng viên/reviewer | Toàn bộ tài liệu | Đánh giá tính nhất quán, phạm vi và khả thi của sản phẩm |

## 0.5. Definitions, Standards, and Framework

| Nhóm | Nội dung áp dụng |
| ---- | --------------- |
| Working definitions | Edge Device, Edge AI, Speech Emotion Recognition, Emotion Session, TFT Report Card, Media Recommendation Service được định nghĩa trong Appendix |
| SRS style | Tài liệu được tổ chức theo hướng Software Requirements Specification: purpose, scope, context, use case, functional requirement, non-functional requirement, other requirement và forward plan |
| API style | Cloud Service ưu tiên REST API, JSON response, device token hoặc signed request |
| Data format | Dữ liệu trao đổi chính dùng JSON; audio thô không upload mặc định; log/report có thể export dạng CSV hoặc JSON trong các phiên bản sau |
| Privacy framework | Ưu tiên privacy-by-design: xử lý SER tại Edge, chỉ đồng bộ emotion context và metadata cần thiết |
| Safety framework | Phản hồi cloud không chẩn đoán y khoa, không thay thế chuyên gia và có safety filter cho tín hiệu nguy cấp |

## 0.6. How to Use this Document

| Bước | Cách sử dụng |
| ---- | ------------ |
| 1 | Đọc chương 01 để hiểu bối cảnh, mục đích sản phẩm, người dùng mục tiêu và phạm vi |
| 2 | Đọc chương 02 để nắm kiến trúc Edge-Cloud-TFT, phần cứng và giả định triển khai |
| 3 | Đọc chương 03 để hiểu SMART objective, use case, input/output và diagrams |
| 4 | Đọc chương 04 nếu cần triển khai hoặc đánh giá Edge AI/SER |
| 5 | Đọc chương 05 nếu cần triển khai Cloud API, database và flow đồng bộ |
| 6 | Dùng chương 06 và 07 để viết checklist phát triển, test case và tiêu chí nghiệm thu |
| 7 | Dùng chương 08 để demo thao tác trên thiết bị phần cứng/TFT |
| 8 | Dùng chương 10 để tra thuật ngữ, schema, API summary, metadata, data formats và references |

## 0.7. Thông tin thành viên

| STT | Thành viên | MSSV | Số điện thoại | Email |
| --- | ---------- | ---- | ------------- | ----- |
| 1 | Trần Hải Đức | 23127173 | 0916821170 | thduc23@clc.fitus.edu.vn |
| 2 | Nguyễn Trọng Tài | 23127008 | 0377425510 | nttai23@clc.fitus.edu.vn |
| 3 | Nguyễn Công Chiến | 23127331 | 0369314655 | ncchien23@clc.fitus.edu.vn |
| 4 | Phạm Nguyễn Gia Bảo | 20127119 | 0926127333 | pngbao20@clc.fitus.edu.vn |

## 0.8. Phạm vi cập nhật đặc tả

| Hạng mục | Đặc tả trước | Đặc tả cập nhật |
| -------- | ------------ | --------------- |
| Định hướng sản phẩm | Thiết bị thông minh cá nhân với nhiều chức năng rời rạc | Thiết bị đồng hành cảm xúc tập trung vào nhận diện, hỗ trợ và phân tích cảm xúc |
| Objective 1 | Theo dõi phiên học/tác vụ cá nhân | Speech Emotion Recognition trên Edge Device trong 15 giây |
| Objective 2 | Tạo báo cáo cho một nhóm chức năng khác | Cloud-assisted recommendation, media selection và conversation trong 20 giây |
| Objective 3 | Giao diện web theo dõi phiên sử dụng | Báo cáo cảm xúc hiển thị trên TFT theo ngày, tháng, năm trong 180 giây |
| Edge AI | Xử lý cục bộ cho một tác vụ giới hạn | Phân tích đặc trưng giọng nói và ngữ cảnh sức khỏe cảm xúc tại thiết bị |
| Internet Service | Đồng bộ và giao diện web cơ bản | Thiết kế DB, API, cloud recommendation/conversation/report service và flow Edge-Cloud-TFT |
| User Manual | Hướng dẫn theo luồng cũ | Hướng dẫn theo luồng phần cứng mới của EmotiCare AIoT |

## 0.9. Lịch sử phiên bản

| Phiên bản | Ngày | Người cập nhật | Nội dung |
| --------- | ---- | -------------- | -------- |
| 1.0 | 26/05/2026 | Project team | Khởi tạo đặc tả thiết bị thông minh |
| 2.0 | 13/06/2026 | Project team | Cập nhật đặc tả theo hướng sản phẩm trước đó |
| 3.0 | 25/06/2026 | Project team | Chuyển đổi đặc tả sang EmotiCare AIoT |
| 3.1 | 25/06/2026 | Project team | Viết lại có dấu, chi tiết hóa background, objective, Edge AI, Internet Service, screen flow và user manual |
| 3.2 | 29/06/2026 | Project team | Bổ sung các phần theo mẫu SRS: audience, sign-off, how-to-use, assumptions, mapping, metadata và forward plan |

## 0.10. Cấu trúc tài liệu

| Chương | Nội dung |
| ------ | -------- |
| 01. Background | Bối cảnh, nguồn cảm hứng từ EMO, vấn đề, người dùng mục tiêu và sơ đồ suy ra mục tiêu |
| 02. Architecture & Hardware | Kiến trúc Edge-Server, thành phần phần cứng và luồng dữ liệu hệ thống |
| 03. Objectives | SMART objective, use case, input/output, bảng use case và diagram |
| 04. EdgeAI | Thiết kế Edge AI cho Speech Emotion Recognition, dữ liệu đầu vào, đặc trưng âm thanh, mô hình và đánh giá |
| 05. Internet Service | Thiết kế database, API và flow tương tác giữa Edge Device, Cloud Service và TFT screen |
| 06. Functional Requirement | Yêu cầu chức năng được truy vết theo objective và use case |
| 07. Non-Functional Requirement | Yêu cầu phi chức năng về hiệu năng, bảo mật, riêng tư, độ tin cậy và an toàn cảm xúc |
| 08. User Manual | Hướng dẫn sử dụng thiết bị phần cứng, TFT screen và đồng bộ Internet |
| 09. Conclusion | Tổng kết, lợi ích, giới hạn và hướng phát triển |
| 10. Appendix & Reference | Thuật ngữ, bảng dữ liệu, API summary và tài liệu tham khảo |
