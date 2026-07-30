# 00. Giới thiệu

## 0.1. Thông tin tài liệu

Tài liệu này mô tả đặc tả sản phẩm **EmotiCare AIoT - Người bạn đồng hành cảm xúc thông minh**, một thiết bị AIoT thông minh có vai trò đồng hành, nhận biết và hỗ trợ người dùng chăm sóc sức khỏe cảm xúc trong đời sống hằng ngày. Tài liệu là cơ sở thống nhất cho nhóm phát triển phần cứng, Edge AI, máy chủ/dịch vụ Cloud, màn hình TFT và hướng dẫn sử dụng.

| Trường thông tin | Giá trị |
| ---------------- | ------- |
| Tên sản phẩm | EmotiCare AIoT |
| Tên đầy đủ | EmotiCare AIoT - Intelligent Emotional Companion |
| Tên tiếng Việt | Thiết bị AIoT thông minh đồng hành và chăm sóc sức khỏe cảm xúc |
| Loại tài liệu | AIoT Product Specification |
| Môn học | Nhập môn lập trình thiết bị thông minh |
| Lớp | 23CLC02 |
| Phiên bản | 3.1 |
| Ngày cập nhật | 25/06/2026 |

## 0.2. Định vị sản phẩm

**EmotiCare AIoT** là thiết bị AIoT ứng dụng trí tuệ nhân tạo nhằm hỗ trợ người dùng nhận biết, thấu hiểu và quản lý cảm xúc trong cuộc sống hằng ngày. Thiết bị nhận diện trạng thái cảm xúc thông qua giọng nói, đưa ra gợi ý hoặc tương tác phù hợp để cải thiện tâm trạng, đồng thời thống kê và phân tích xu hướng cảm xúc theo ngày, tuần và tháng.

Điểm khác biệt của sản phẩm là cách tiếp cận **ưu tiên xử lý tại thiết bị, có Cloud hỗ trợ**: tác vụ nhận diện cảm xúc cốt lõi được xử lý trực tiếp trên thiết bị để giảm độ trễ và tăng tính riêng tư, trong khi các chức năng gợi ý hoạt động, trò chuyện hỗ trợ và báo cáo dài hạn phối hợp với dịch vụ Internet/Cloud. Toàn bộ kết quả theo dõi, báo cáo và trạng thái đồng bộ được hiển thị trên màn hình TFT của thiết bị.

> **EmotiCare AIoT - Thấu hiểu cảm xúc, chăm sóc tâm trí.**

## 0.3. Vòng đời tài liệu và xác nhận

### 0.3.1. Lịch sử cập nhật

| Phiên bản | Ngày | Người cập nhật | Phase | Nội dung thay đổi |
| --------- | ---- | -------------- | ----- | ----------------- |
| 1.0 | 26/05/2026 | Nhóm dự án | Bản nháp đầu tiên | Khởi tạo đặc tả thiết bị thông minh |
| 2.0 | 13/06/2026 | Nhóm dự án | Cập nhật trong quá trình thực hiện | Cập nhật đặc tả theo hướng sản phẩm trước đó |
| 3.0 | 25/06/2026 | Nhóm dự án | Thiết kế lại sản phẩm | Chuyển đổi đặc tả sang EmotiCare AIoT |
| 3.1 | 25/06/2026 | Nhóm dự án | Hoàn thiện đặc tả | Viết lại có dấu, chi tiết hóa bối cảnh, mục tiêu, Edge AI, dịch vụ Internet, luồng màn hình và hướng dẫn sử dụng |
| 3.2 | 29/06/2026 | Nhóm dự án | Đồng bộ theo SRS | Bổ sung cấu trúc theo mẫu đặc tả yêu cầu phần mềm |

### 0.3.2. Xác nhận

| Vai trò | Người/nhóm phụ trách | Trách nhiệm xác nhận | Trạng thái |
| ------- | -------------------- | -------------------- | ---------- |
| Chủ sở hữu sản phẩm | Nhóm dự án | Xác nhận phạm vi sản phẩm, mục tiêu và tình huống sử dụng | Chờ xác nhận |
| Phụ trách phần cứng | Nhóm dự án | Xác nhận phần cứng, chi phí mẫu thử và luồng màn hình TFT | Chờ xác nhận |
| Phụ trách Edge AI | Nhóm dự án | Xác nhận quy trình nhận diện cảm xúc bằng giọng nói và yêu cầu riêng tư | Chờ xác nhận |
| Phụ trách Cloud/API | Nhóm dự án | Xác nhận cơ sở dữ liệu, API và luồng Edge-Cloud-TFT | Chờ xác nhận |
| Người phản biện/Giảng viên | Giảng viên phụ trách | Đánh giá tính đầy đủ của đặc tả | Chờ xác nhận |

## 0.4. Đối tượng sử dụng tài liệu

| Đối tượng đọc | Phần nên đọc kỹ | Mục đích sử dụng tài liệu |
| ------------- | --------------- | -------------------------- |
| Nhóm phần cứng | Chương 02, 06, 08 | Chọn linh kiện, thiết kế luồng màn hình TFT và chuẩn bị mẫu thử |
| Nhóm Edge AI | Chương 03, 04, 05 | Xây dựng quy trình SER, xác định đầu vào/đầu ra và tiêu chí đánh giá |
| Nhóm Cloud/API | Chương 03, 04, 05, 08 | Thiết kế cơ sở dữ liệu, API, đồng bộ dữ liệu và các thẻ báo cáo |
| Nhóm kiểm thử | Chương 03, 04, 05, 06 | Viết trường hợp kiểm thử theo tình huống sử dụng, yêu cầu chức năng và yêu cầu phi chức năng |
| Giảng viên/reviewer | Toàn bộ tài liệu | Đánh giá tính nhất quán, phạm vi và khả thi của sản phẩm |

## 0.5. Thuật ngữ, tiêu chuẩn và nguyên tắc áp dụng

| Nhóm | Nội dung áp dụng |
| ---- | --------------- |
| Thuật ngữ sử dụng | Thiết bị biên, Edge AI, nhận diện cảm xúc bằng giọng nói, phiên cảm xúc, thẻ báo cáo TFT và dịch vụ gợi ý nội dung được định nghĩa trong phụ lục |
| Cách tổ chức SRS | Tài liệu được tổ chức theo hướng đặc tả yêu cầu phần mềm: mục đích, phạm vi, bối cảnh, tình huống sử dụng, yêu cầu chức năng, yêu cầu phi chức năng, yêu cầu khác và kế hoạch tiếp theo |
| Cách thiết kế API | Dịch vụ Cloud ưu tiên REST API, phản hồi JSON, mã thiết bị hoặc yêu cầu có chữ ký |
| Định dạng dữ liệu | Dữ liệu trao đổi chính dùng JSON. Audio check-in SER chỉ xử lý tại Edge; riêng Voice Conversation gửi PCM 16-bit tạm thời qua API để STT, không lưu audio thô. Nhật ký/báo cáo có thể xuất dạng CSV hoặc JSON trong các phiên bản sau |
| Nguyên tắc riêng tư | Ưu tiên bảo vệ riêng tư ngay từ thiết kế: xử lý SER tại Edge, chỉ đồng bộ ngữ cảnh cảm xúc và siêu dữ liệu cần thiết |
| Nguyên tắc an toàn | Phản hồi từ Cloud không chẩn đoán y khoa, không thay thế chuyên gia và có bộ lọc an toàn cho tín hiệu nguy cấp |

## 0.6. Cách sử dụng tài liệu này

| Bước | Cách sử dụng |
| ---- | ------------ |
| 1 | Đọc chương 01 để hiểu bối cảnh, mục đích sản phẩm, người dùng mục tiêu và phạm vi |
| 2 | Đọc chương 02 để nắm danh mục, kết nối, chi phí và ràng buộc phần cứng |
| 3 | Đọc chương 03 để hiểu mục tiêu SMART, tình huống sử dụng, đầu vào/đầu ra và sơ đồ |
| 4 | Đọc các phần UC trong chương 03 nếu cần triển khai hoặc đánh giá Edge AI, API Cloud, cơ sở dữ liệu và luồng đồng bộ |
| 5 | Dùng chương 04 và 05 để viết checklist phát triển, trường hợp kiểm thử và tiêu chí nghiệm thu |
| 6 | Dùng chương 06 để demo thao tác trên thiết bị phần cứng/TFT |
| 7 | Dùng chương 08 để tra thuật ngữ, cấu trúc dữ liệu, tóm tắt API, siêu dữ liệu, định dạng dữ liệu và tài liệu tham khảo |

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
| Mục tiêu 1 | Theo dõi phiên học hoặc tác vụ cá nhân | Nhận diện cảm xúc bằng giọng nói tại thiết bị trong 30 giây |
| Mục tiêu 2 | Tạo báo cáo cho một nhóm chức năng khác | Gợi ý hoạt động, nội dung nghe và trò chuyện qua Internet trong 20 giây |
| Mục tiêu 3 | Giao diện theo dõi phiên sử dụng | Báo cáo cảm xúc hiển thị trên màn hình theo ngày, tuần và tháng trong 180 giây |
| Xử lý tại thiết bị | Xử lý cục bộ cho một tác vụ giới hạn | Phân tích giọng nói và nhận diện cảm xúc ngay trên thiết bị |
| Dịch vụ Internet | Đồng bộ và hỗ trợ các chức năng trực tuyến | Đồng bộ dữ liệu, gợi ý, trò chuyện và báo cáo |
| Hướng dẫn sử dụng | Hướng dẫn theo luồng cũ | Hướng dẫn theo luồng phần cứng mới của EmotiCare AIoT |

## 0.9. Lịch sử phiên bản

| Phiên bản | Ngày | Người cập nhật | Nội dung |
| --------- | ---- | -------------- | -------- |
| 1.0 | 26/05/2026 | Project team | Khởi tạo đặc tả thiết bị thông minh |
| 2.0 | 13/06/2026 | Project team | Cập nhật đặc tả theo hướng sản phẩm trước đó |
| 3.0 | 25/06/2026 | Project team | Chuyển đổi đặc tả sang EmotiCare AIoT |
| 3.1 | 25/06/2026 | Nhóm dự án | Viết lại có dấu, chi tiết hóa bối cảnh, mục tiêu, Edge AI, dịch vụ Internet, luồng màn hình và hướng dẫn sử dụng |
| 3.2 | 29/06/2026 | Nhóm dự án | Bổ sung các phần theo mẫu SRS: đối tượng đọc, xác nhận, cách dùng, giả định, liên kết, siêu dữ liệu và kế hoạch tiếp theo |

## 0.10. Cấu trúc tài liệu

| Chương | Nội dung |
| ------ | -------- |
| 01. Bối cảnh | Bối cảnh, nguồn cảm hứng từ EMO, vấn đề, người dùng mục tiêu và sơ đồ suy ra mục tiêu |
| 02. Phần cứng | Thành phần phần cứng, kết nối, chi phí và ràng buộc triển khai |
| 03. Mục tiêu và tình huống sử dụng | Ba mục tiêu, tình huống sử dụng, dữ liệu chính và sơ đồ luồng |
| 04. Kết nối thiết bị và máy chủ | Quy trình kết nối, đồng bộ dữ liệu và thông tin trao đổi của năm tình huống sử dụng |
| 05. Yêu cầu chức năng | Yêu cầu chức năng được truy vết theo mục tiêu và tình huống sử dụng |
| 06. Yêu cầu phi chức năng | Yêu cầu phi chức năng về hiệu năng, bảo mật, riêng tư, độ tin cậy và an toàn cảm xúc |
| 07. Hướng dẫn sử dụng | Hướng dẫn sử dụng thiết bị phần cứng, màn hình TFT và đồng bộ Internet |
| 08. Kết luận | Tổng kết, lợi ích, giới hạn và hướng phát triển |
| 09. Phụ lục và tài liệu tham khảo | Thuật ngữ, bảng dữ liệu, tóm tắt API và tài liệu tham khảo |
