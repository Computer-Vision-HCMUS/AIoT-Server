# 07. Kết luận

## 7.1. Tổng kết

EmotiCare AIoT - Người bạn đồng hành cảm xúc thông minh là một thiết bị AIoT giúp người dùng nhận biết, chăm sóc và theo dõi cảm xúc trực tiếp trên màn hình TFT. Sản phẩm được xây dựng quanh ba năng lực chính:

1. Nhận diện cảm xúc bằng giọng nói trên Edge AI.
2. Gửi ngữ cảnh cảm xúc lên Cloud để nhận gợi ý hoạt động, bài hát, podcast hoặc phản hồi trò chuyện.
3. Tổng hợp xu hướng cảm xúc trên Cloud và trả báo cáo rút gọn về TFT.

Ba năng lực này tạo thành vòng lặp: **kiểm tra cảm xúc -> SER tại Edge -> hiển thị trên TFT -> đồng bộ Cloud -> hỗ trợ/báo cáo -> hiển thị trên TFT**.

## 7.2. Mức độ đáp ứng mục tiêu

| SMART Objective | Cách tài liệu đáp ứng |
| --------------- | --------------------- |
| Objective 1 | UC-01, Edge AI pipeline và FR-01 đến FR-08 mô tả nhận diện cảm xúc trong 15 giây, hiển thị TFT và lưu emotion session |
| Objective 2 | UC-02, UC-03, UC-04 và FR-14 đến FR-34 mô tả gợi ý hoạt động, lựa chọn bài hát/podcast, trò chuyện hỗ trợ qua Cloud và hiển thị trên TFT trong 20 giây |
| Objective 3 | UC-05, logic API/dữ liệu báo cáo trong Chương 03 và FR-35 đến FR-45 mô tả báo cáo ngày/tháng/năm trả về TFT trong 180 giây |

## 7.3. Lợi ích kỳ vọng

| Lợi ích | Mô tả |
| ------- | ----- |
| Tăng tự nhận thức | Người dùng gọi tên được cảm xúc hiện tại thông qua check-in bằng giọng nói |
| Hỗ trợ đúng lúc | Thiết bị hiển thị gợi ý hoạt động, bài hát/podcast hoặc phản hồi Cloud ngay trên TFT |
| Theo dõi dài hạn | TFT hiển thị report cards giúp người dùng nhìn lại xu hướng cảm xúc |
| Phù hợp prototype sinh viên | Edge xử lý phần cốt lõi, Cloud hỗ trợ các phần nặng hơn |
| Riêng tư hơn | Không upload âm thanh thô mặc định; chỉ đồng bộ emotion context cần thiết |

## 7.4. Giới hạn hiện tại

| Giới hạn | Ảnh hưởng |
| -------- | --------- |
| Nhận diện cảm xúc là bài toán xác suất | Kết quả có thể sai khi âm thanh nhiễu, câu nói quá ngắn hoặc cảm xúc phức tạp |
| Objective 2 và 3 phụ thuộc Internet | Khi offline, thiết bị chỉ nhận diện và lưu pending, chưa tạo hỗ trợ cloud mới |
| TFT có không gian hạn chế | Báo cáo và phản hồi phải rút gọn, không phù hợp trình bày bảng dài |
| Không phải thiết bị y tế | Không chẩn đoán, điều trị hoặc thay thế chuyên gia |
| Cá nhân hóa phụ thuộc feedback | Gợi ý sẽ tốt hơn khi người dùng đánh giá hoạt động, bài hát hoặc podcast sau khi trải nghiệm |

## 7.5. Hướng phát triển

| Hướng phát triển | Mô tả |
| ---------------- | ----- |
| Baseline cảm xúc cá nhân | Học ngưỡng cảm xúc riêng của từng người dùng |
| Model update | Cập nhật mô hình SER tối ưu hơn cho Edge Device |
| Cloud recommendation nâng cao | Cá nhân hóa hoạt động, bài hát và podcast dựa trên hiệu quả trong lịch sử |
| TFT visualization tốt hơn | Tối ưu biểu đồ nhỏ, biểu tượng cảm xúc và report cards |
| Tài nguyên hỗ trợ theo khu vực | Gợi ý hotline hoặc dịch vụ hỗ trợ phù hợp với địa phương khi cần |

## 7.6. Kế hoạch tiếp theo và các mốc thực hiện

| Mốc thực hiện | Kết quả bàn giao | Thời gian dự kiến | Trạng thái |
| --------- | ----------- | -------- | ------ |
| Lắp ráp phần cứng | ESP32-S AI Thinker, ST7789, INMP441, MAX98357, loa 3W và 5 nút bấm hoạt động ở mức mẫu thử | Tuần 1 | Dự kiến |
| Kiểm tra luồng màn hình TFT | Các màn hình chạy theo luồng demo | Tuần 1-2 | Đang thực hiện |
| SER nền tảng | Quy trình thu âm, trích xuất đặc trưng và phân loại nhãn cảm xúc cơ bản | Tuần 2 | Dự kiến |
| API Cloud mô phỏng | API mô phỏng cho đồng bộ, gợi ý, nội dung, trò chuyện và báo cáo | Tuần 2 | Dự kiến |
| Tích hợp cơ sở dữ liệu | Cấu trúc người dùng, thiết bị, phiên cảm xúc, nội dung và báo cáo có dữ liệu mẫu | Tuần 3 | Dự kiến |
| Demo đầu-cuối | Thiết bị biên gửi yêu cầu, Cloud trả thẻ, TFT hiển thị kết quả | Tuần 3 | Dự kiến |
| Kiểm tra yêu cầu | Kiểm tra FR/NFR, sơ đồ tình huống sử dụng, sơ đồ luồng và hướng dẫn sử dụng | Tuần 4 | Dự kiến |
| Rà soát đặc tả cuối cùng | Xây dựng lại `Specification.md` và rà soát tính thống nhất của tài liệu | Tuần 4 | Dự kiến |

## 7.7. Kết luận

EmotiCare AIoT không cố gắng thay thế con người trong việc chăm sóc cảm xúc. Sản phẩm đóng vai trò một thiết bị đồng hành nhỏ gọn, cho phép người dùng dừng lại, nhận biết cảm xúc, nhận hỗ trợ từ Cloud khi có Internet và theo dõi xu hướng ngay trên màn hình TFT.
