# 07. Hướng dẫn sử dụng

## 7.1. Tổng quan

EmotiCare AIoT được sử dụng trực tiếp trên thiết bị phần cứng. Cảm xúc hiện tại, gợi ý hoạt động, danh sách bài hát/podcast, phản hồi trò chuyện, trạng thái đồng bộ và báo cáo rút gọn đều được hiển thị trên màn hình TFT.

Luồng sử dụng chính:

```text
TRANG CHỦ -> KIỂM TRA CẢM XÚC / HOẠT ĐỘNG / NHẠC-PODCAST / TRÒ CHUYỆN / BÁO CÁO / TRẠNG THÁI
KIỂM TRA CẢM XÚC -> KẾT QUẢ -> HỖ TRỢ -> HOẠT ĐỘNG / NHẠC-PODCAST / TRÒ CHUYỆN
```

## 7.2. Luồng màn hình thiết bị

| Màn hình | Mục đích | Thao tác chính |
| -------- | -------- | -------------- |
| Trang chủ | Xem trạng thái kết nối, cảm xúc gần nhất và số phiên đang chờ đồng bộ | Chuyển trực tiếp sang kiểm tra cảm xúc, hoạt động, nhạc/podcast, trò chuyện, báo cáo hoặc trạng thái |
| Kiểm tra cảm xúc | Ghi âm giọng nói khi người dùng chủ động kích hoạt | Bắt đầu/dừng ghi âm |
| Kết quả | Hiển thị nhãn cảm xúc và độ tin cậy từ Edge AI | Xem kết quả, chuyển sang phần hỗ trợ |
| Hỗ trợ | Chọn hướng hỗ trợ sau khi kiểm tra cảm xúc; các chức năng này cũng có thể mở trực tiếp từ trang chủ | Chọn hoạt động, nhạc/podcast hoặc trò chuyện |
| Hoạt động | Hiển thị 5 gợi ý hoạt động từ dịch vụ gợi ý Cloud | Chọn, bỏ qua hoặc đánh giá hoạt động |
| Nhạc-Podcast | Chọn bài hát hoặc podcast theo chủ đích và nhóm nội dung | Chọn nhóm nội dung, xem danh sách, chọn nội dung để nghe |
| Trò chuyện | Hiển thị phản hồi từ dịch vụ trò chuyện Cloud | Nói tiếp, nhận phản hồi, kết thúc |
| Trạng thái | Xem trực tuyến/ngoại tuyến, số phiên chờ và lần đồng bộ gần nhất | Thử đồng bộ lại |
| Báo cáo | Xem tóm tắt ngày/tuần/tháng từ bộ tạo báo cáo Cloud | Chọn mốc thời gian và xem các thẻ báo cáo |

## 7.3. Thiết lập lần đầu

| Bước | Hành động | Kết quả mong đợi |
| ---- | --------- | ---------------- |
| 1 | Bật nguồn thiết bị | Màn hình Trang chủ hiển thị tên EmotiCare AIoT |
| 2 | Kết nối Wi-Fi hoặc điểm phát sóng | Trạng thái mạng chuyển sang trực tuyến |
| 3 | Nhập mã ghép thiết bị hoặc quét mã theo hướng dẫn của nhóm | Thiết bị được liên kết với người dùng trên Cloud |
| 4 | Kiểm tra microphone | Thiết bị sẵn sàng để kiểm tra cảm xúc |
| 5 | Kiểm tra Trạng thái | TFT hiển thị trạng thái trực tuyến, lần đồng bộ gần nhất và số phiên chờ |

## 7.4. Kiểm tra cảm xúc bằng giọng nói

| Bước | Hành động của người dùng | Hành vi của thiết bị |
| ---- | ----------------------- | -------------------- |
| 1 | Từ Trang chủ chọn Kiểm tra cảm xúc | Màn hình chuyển sang Kiểm tra cảm xúc |
| 2 | Nhấn Start và nói một câu ngắn | Thiết bị hiển thị trạng thái đang nghe |
| 3 | Chờ xử lý | Edge AI phân tích giọng nói trong vòng 30 giây |
| 4 | Xem kết quả | TFT hiển thị nhãn cảm xúc và độ tin cậy |
| 5 | Chọn bước tiếp theo | Chuyển sang Hoạt động, Nhạc/Podcast hoặc Trò chuyện nếu có Internet; người dùng cũng có thể quay về Trang chủ |

Ví dụ kết quả:

| Trường | Giá trị |
| ------ | ------- |
| Cảm xúc | Căng thẳng |
| Độ tin cậy | 0.74 |
| Trạng thái đồng bộ | Đang chờ hoặc đã đồng bộ |
| Gợi ý tiếp theo | Kết nối Cloud để nhận hoạt động, nhạc/podcast hoặc phản hồi trò chuyện |

## 7.5. Sử dụng các dịch vụ hỗ trợ qua Cloud

Gợi ý hoạt động cần Internet và một phiên cảm xúc đã được đồng bộ. Người dùng chọn Hoạt động từ Trang chủ sau khi check-in; thiết bị gửi `session_id` lên Cloud. Kết quả luôn là 5 thẻ hoạt động hiển thị trên TFT, được xếp hạng theo cảm xúc, feedback hoạt động và lịch sử card gần đây. Nhạc/podcast được chọn trong màn hình riêng tại mục 6.6.

| Cảm xúc | Hoạt động ưu tiên mẫu |
| ------- | ---------------------- |
| Vui vẻ | Vận động nhẹ, ghi nhận điều tích cực, kết nối |
| Bình thường | Chia nhỏ việc, vận động nhẹ, hít thở |
| Căng thẳng | Hít thở, neo hiện tại, nghỉ mắt/uống nước |
| Buồn bã | Nghỉ ngơi, kết nối với người tin cậy, viết |
| Tức giận | Hít thở, neo hiện tại, vận động nhẹ |
| Mệt mỏi | Nghỉ mắt/uống nước, nghỉ ngơi, quét cơ thể |

Nếu thiết bị ngoại tuyến, TFT hiển thị thông báo: `Cần Internet để lấy gợi ý từ Cloud`.

## 7.6. Chọn bài hát hoặc podcast theo chủ đích

Chế độ Nhạc/Podcast dành cho trường hợp người dùng muốn chủ động chọn nội dung thay vì chỉ nhận gợi ý tự động. Người dùng có thể mở Nhạc/Podcast trực tiếp từ Trang chủ, chọn loại nội dung, nhóm nội dung và chủ đích ngắn trên TFT; dịch vụ gợi ý nội dung trên Cloud sẽ trả về danh sách phù hợp. Ngữ cảnh cảm xúc chỉ là dữ liệu bổ sung nếu người dùng đã kiểm tra cảm xúc trước đó.

| Nhóm nội dung | Nội dung thường gặp | Khi nên chọn |
| -------- | ------------------ | ------------ |
| Thư giãn | Nhạc nhẹ, ambient, podcast thở chậm | Khi căng thẳng |
| Tập trung | Nhạc không lời, white noise, podcast tập trung | Khi học tập hoặc làm việc |
| Ngủ nghỉ | Nhạc chậm, sleep story, podcast thiền ngủ | Khi chuẩn bị nghỉ ngơi |
| Vui vẻ | Nhạc tích cực, podcast truyền cảm hứng | Khi muốn duy trì cảm xúc tốt |
| Xoa dịu buồn bã | Nhạc ấm, podcast chia sẻ cảm xúc | Khi cần cảm giác được đồng hành |
| Giải tỏa tức giận | Nhạc grounding, podcast kiểm soát cảm xúc | Khi cần tạm dừng và hạ nhịp |
| Phục hồi năng lượng | Nhạc nhẹ có nhịp vừa, podcast self-care | Khi mệt mỏi |

| Bước | Hành động | Kết quả |
| ---- | --------- | ------- |
| 1 | Chọn Nhạc/Podcast từ Trang chủ hoặc Hỗ trợ | Thiết bị kiểm tra Internet |
| 2 | Chọn Music, Podcast hoặc Both | TFT hiển thị danh sách category |
| 3 | Chọn category hoặc nói chủ đích ngắn | Thiết bị gửi intent lên Cloud |
| 4 | Chờ danh sách gợi ý | Cloud trả song/podcast cards |
| 5 | Chọn nội dung để nghe hoặc lưu lại | Thiết bị ghi nhận media selection log |

## 7.7. Sử dụng trò chuyện hỗ trợ cảm xúc qua Cloud

Chế độ Trò chuyện cần Internet và một emotion session đã được đồng bộ từ lần check-in gần nhất. Người dùng có thể mở Trò chuyện từ Trang chủ hoặc Hỗ trợ sau check-in. Thiết bị gửi PCM 16-bit, 16 kHz của phần chia sẻ (tối đa 10 giây) cùng `session_id` lên Cloud; Cloud chuyển giọng nói thành transcript, tạo phản hồi rút gọn và có thể trả audio TTS. Audio đầu vào chỉ xử lý tạm thời, không được lưu.

| Bước | Hành động | Kết quả |
| ---- | --------- | ------- |
| 1 | Sau check-in đã đồng bộ, chọn Trò chuyện từ Trang chủ hoặc Hỗ trợ | Thiết bị kiểm tra Internet và session |
| 2 | Chia sẻ ngắn bằng giọng nói (tối đa 10 giây) | Thiết bị gửi PCM và `session_id` lên Cloud |
| 3 | Đợi phản hồi | Cloud trả phản hồi trong mục tiêu 20 giây |
| 4 | Đọc phản hồi trên TFT | Người dùng có thể tiếp tục hoặc kết thúc |

Lưu ý: EmotiCare AIoT không thay thế chuyên gia sức khỏe tinh thần. Nếu người dùng có cảm giác nguy hiểm cho bản thân hoặc người khác, cần liên hệ ngay người thân, chuyên gia hoặc dịch vụ hỗ trợ khẩn cấp tại địa phương.

## 7.8. Xem trạng thái đồng bộ

| Trạng thái | Ý nghĩa | Hành động đề xuất |
| ---------- | ------- | ----------------- |
| Online | Thiết bị đang kết nối Cloud | Có thể dùng Activity, Music/Podcast, Conversation và Report |
| Ngoại tuyến | Thiết bị không có Internet | Chỉ Mục tiêu 1 hoạt động; dữ liệu được lưu chờ đồng bộ |
| Có phiên chờ | Có phiên chưa đồng bộ | Kiểm tra Wi-Fi hoặc chọn đồng bộ ngay |
| Đang chờ Cloud | Thiết bị đang chờ Cloud trả kết quả | Giữ kết nối và đợi phản hồi |
| Có kết quả từ Cloud | Có kết quả mới từ Cloud | Mở màn hình tương ứng để xem |

## 7.9. Xem báo cáo trên TFT

Màn hình Báo cáo có thể mở trực tiếp từ Trang chủ. Người dùng chọn mốc thống kê cần xem, gồm ngày, tuần hoặc tháng. Báo cáo được tạo trên máy chủ và trả về thành các thẻ ngắn; nếu dữ liệu chưa đủ, thiết bị thông báo rõ để người dùng hiểu kết quả chỉ mang tính tham khảo.

| Lựa chọn trên màn hình | Ý nghĩa | Giá trị gửi tới máy chủ |
| ----------------- | ------- | ------------ |
| Ngày | Xem thống kê trong một ngày | `GET /api/statistics/day` |
| Tuần | Xem thống kê trong một tuần | `GET /api/statistics/week` |
| Tháng | Xem thống kê trong một tháng | `GET /api/statistics/month` |

| Nội dung hiển thị | Ý nghĩa |
| ----------------- | ------- |
| Phân bố cảm xúc | Tỷ lệ các cảm xúc chính trong kỳ |
| Xu hướng | Dấu hiệu cải thiện, ổn định hoặc cần chú ý |
| Chuỗi cảm xúc khó chịu | Số lần buồn bã hoặc tức giận liên tiếp nếu có |
| Hoạt động hữu ích | Hoạt động được đánh giá hữu ích nhất |
| Nội dung hữu ích | Bài hát hoặc podcast được chọn hay đánh giá tích cực |
| Mức độ đầy đủ của dữ liệu | Đủ dữ liệu hoặc cần thêm dữ liệu |

Ví dụ kết quả giả lập trả về trên TFT:

| Kỳ thống kê | Phân bố cảm xúc | Xu hướng | Hoạt động hữu ích | Nội dung hữu ích | Mức độ đầy đủ của dữ liệu |
| ----------- | ---------------- | -------- | ----------------- | ---------------- | -------------------------- |
| Ngày | Vui vẻ 35%, bình thường 30%, bình tĩnh 25%, buồn bã 10% | Bình tĩnh tăng nhẹ vào buổi tối | Hít thở 4-7-8 | Podcast thở chậm 5 phút | Đủ dữ liệu |
| Tuần | Bình thường 37%, vui vẻ 25%, bình tĩnh 20%, buồn bã 10%, tức giận 8% | Nhịp cảm xúc ổn định hơn vào nửa cuối tuần | Neo lại hiện tại | Podcast tập trung ngắn | Đủ dữ liệu |
| Tháng | Bình thường 40%, vui vẻ 28%, bình tĩnh 20%, buồn bã 8%, sợ hãi 4% | Cảm xúc ổn định hơn sau tuần 2 | Nghỉ 5 phút khỏi màn hình | Danh sách nhạc tập trung nhẹ | Đủ dữ liệu |

Nếu thiết bị không có kết nối Internet, màn hình thông báo cần kết nối để lấy hoặc tạo báo cáo; phiên bản hiện tại không lưu báo cáo trên thiết bị.

## 7.10. Xử lý sự cố

| Vấn đề | Nguyên nhân có thể | Cách xử lý |
| ------ | ------------------ | ---------- |
| Thiết bị không nghe rõ | Microphone bị che hoặc môi trường quá ồn | Nói gần hơn, giảm nhiễu nền |
| Kết quả là không chắc chắn | Câu nói quá ngắn hoặc confidence thấp | Check-in lại bằng câu rõ hơn |
| Không lấy được gợi ý | Thiết bị offline hoặc Cloud timeout | Kiểm tra Wi-Fi và thử lại |
| Không có danh sách bài hát/podcast | Chưa có Internet, category trống hoặc Cloud chưa trả kết quả | Mở Status, đổi category hoặc thử lại |
| Không có phản hồi hội thoại | Internet lỗi hoặc Cloud chưa trả kết quả | Mở Status để xem trạng thái |
| Báo cáo limited data | Chưa đủ session trong kỳ thống kê | Check-in đều hơn trong các ngày tiếp theo |
