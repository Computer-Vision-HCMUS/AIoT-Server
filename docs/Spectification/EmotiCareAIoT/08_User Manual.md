# 08. User Manual

## 8.1. Tổng quan

EmotiCare AIoT được sử dụng trực tiếp trên thiết bị phần cứng. Toàn bộ cảm xúc hiện tại, gợi ý hoạt động, danh sách bài hát/podcast, phản hồi hội thoại, trạng thái đồng bộ và báo cáo rút gọn được hiển thị trên TFT screen.

Luồng sử dụng chính:

```text
HOME -> CHECK-IN / ACTIVITY / MUSIC-PODCAST / CONVERSATION / REPORT / STATUS
CHECK-IN -> RESULT -> SUPPORT -> ACTIVITY / MUSIC-PODCAST / CONVERSATION
```

## 8.2. Luồng màn hình thiết bị

| Màn hình | Mục đích | Thao tác chính |
| -------- | -------- | -------------- |
| HOME | Xem trạng thái kết nối, cảm xúc gần nhất và số session pending | Chuyển trực tiếp sang Check-in, Activity, Music/Podcast, Conversation, Report hoặc Status |
| CHECK-IN | Ghi âm giọng nói khi người dùng chủ động kích hoạt | Bắt đầu/dừng ghi âm |
| RESULT | Hiển thị emotion label và confidence từ Edge AI | Xem kết quả, chuyển sang hỗ trợ |
| SUPPORT | Chọn hướng hỗ trợ sau khi check-in; các chức năng này cũng có thể mở trực tiếp từ HOME | Chọn Activity, Music/Podcast hoặc Conversation |
| ACTIVITY | Hiển thị gợi ý hoạt động, bài hát và podcast từ Cloud Recommendation Service | Chọn, bỏ qua hoặc đánh giá gợi ý |
| MUSIC-PODCAST | Chọn bài hát hoặc podcast theo chủ đích và category | Chọn category, xem danh sách, chọn nội dung để nghe |
| CONVERSATION | Hiển thị phản hồi từ Cloud Conversation Service | Nói tiếp, nhận phản hồi, kết thúc |
| STATUS | Xem online/offline, pending count, last sync | Thử đồng bộ lại |
| REPORT | Xem tóm tắt ngày/tháng/năm từ Cloud Report Engine | Chọn period và xem report cards |

## 8.3. Thiết lập lần đầu

| Bước | Hành động | Kết quả mong đợi |
| ---- | --------- | ---------------- |
| 1 | Bật nguồn thiết bị | Màn hình HOME hiển thị tên EmotiCare AIoT |
| 2 | Kết nối Wi-Fi hoặc hotspot | Trạng thái Network chuyển sang Online |
| 3 | Nhập pairing code hoặc quét mã ghép thiết bị theo hướng dẫn của nhóm | Thiết bị được liên kết với user trên Cloud |
| 4 | Kiểm tra microphone | Thiết bị sẵn sàng cho Check-in |
| 5 | Kiểm tra Status | TFT hiển thị Online, last sync và pending count |

## 8.4. Check-in cảm xúc bằng giọng nói

| Bước | Hành động của người dùng | Hành vi của thiết bị |
| ---- | ----------------------- | -------------------- |
| 1 | Từ HOME chọn Check-in | Màn hình chuyển sang CHECK-IN |
| 2 | Nhấn Start và nói một câu ngắn | Thiết bị hiển thị trạng thái đang nghe |
| 3 | Chờ xử lý | Edge AI phân tích giọng nói trong vòng 15 giây |
| 4 | Xem kết quả | TFT hiển thị emotion label và confidence |
| 5 | Chọn bước tiếp theo | Chuyển sang Activity, Music/Podcast hoặc Conversation nếu có Internet; người dùng cũng có thể quay về HOME |

Ví dụ kết quả:

| Trường | Giá trị |
| ------ | ------- |
| Cảm xúc | Căng thẳng |
| Confidence | 0.74 |
| Trạng thái sync | Pending hoặc Synced |
| Gợi ý tiếp theo | Kết nối Cloud để nhận activity, music/podcast hoặc conversation |

## 8.5. Sử dụng gợi ý hoạt động và nội dung qua Cloud

Gợi ý hoạt động và nội dung cần Internet. Người dùng có thể chọn Activity trực tiếp từ HOME mà không cần check-in cảm xúc trước. Nếu đã có emotion label từ phiên check-in gần nhất, thiết bị gửi emotion context lên Cloud; nếu chưa có, Cloud dùng chế độ gợi ý chung an toàn dựa trên lịch sử gần nhất. Kết quả trả về là 1-5 recommendation cards hiển thị trên TFT, có thể là hoạt động, bài hát hoặc podcast phù hợp.

| Cảm xúc | Hoạt động mẫu | Bài hát/podcast mẫu |
| ------- | ------------- | ------------------- |
| Vui vẻ | Ghi lại một điều tích cực, duy trì hoạt động hiện tại | Nhạc tích cực, podcast truyền cảm hứng |
| Bình thường | Vận động nhẹ, uống nước, check-in lại vào cuối ngày | Nhạc nền nhẹ, podcast tập trung |
| Căng thẳng | Hít thở 4-7-8, nghỉ 5 phút, giảm kích thích | Nhạc thư giãn, podcast thở chậm |
| Buồn bã | Viết nhật ký cảm xúc, liên hệ người thân | Nhạc ấm, podcast chia sẻ cảm xúc |
| Tức giận | Tạm dừng, thở chậm, rời khỏi tác nhân gây căng | Nhạc grounding, podcast kiểm soát cảm xúc |
| Mệt mỏi | Nghỉ ngắn, uống nước, giãn cơ | Nhạc nhẹ có nhịp vừa, podcast self-care |

Nếu thiết bị offline, TFT hiển thị thông báo: `Cần Internet để lấy gợi ý từ Cloud`.

## 8.6. Chọn bài hát hoặc podcast theo chủ đích

Music/Podcast Mode dành cho trường hợp người dùng muốn chủ động chọn nội dung thay vì chỉ nhận gợi ý tự động. Người dùng có thể mở Music/Podcast trực tiếp từ HOME, chọn loại nội dung, category và chủ đích ngắn trên TFT; Cloud Media Recommendation Service sẽ trả về danh sách phù hợp. Emotion context chỉ là dữ liệu bổ sung nếu người dùng đã check-in trước đó.

| Category | Nội dung thường gặp | Khi nên chọn |
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
| 1 | Chọn Music/Podcast từ HOME hoặc SUPPORT | Thiết bị kiểm tra Internet |
| 2 | Chọn Music, Podcast hoặc Both | TFT hiển thị danh sách category |
| 3 | Chọn category hoặc nói chủ đích ngắn | Thiết bị gửi intent lên Cloud |
| 4 | Chờ danh sách gợi ý | Cloud trả song/podcast cards |
| 5 | Chọn nội dung để nghe hoặc lưu lại | Thiết bị ghi nhận media selection log |

## 8.7. Sử dụng trò chuyện hỗ trợ cảm xúc qua Cloud

Conversation Mode cũng cần Internet. Người dùng có thể mở Conversation trực tiếp từ HOME mà không cần dự đoán cảm xúc trước. Thiết bị gửi nội dung chia sẻ của người dùng lên Cloud Conversation Service; nếu có emotion context gần nhất thì gửi kèm để phản hồi tinh tế hơn, sau đó hiển thị phản hồi rút gọn trên TFT.

| Bước | Hành động | Kết quả |
| ---- | --------- | ------- |
| 1 | Chọn Conversation từ HOME hoặc SUPPORT | Thiết bị kiểm tra Internet |
| 2 | Chia sẻ ngắn bằng giọng nói | Thiết bị gửi context lên Cloud |
| 3 | Đợi phản hồi | Cloud trả phản hồi trong mục tiêu 20 giây |
| 4 | Đọc phản hồi trên TFT | Người dùng có thể tiếp tục hoặc kết thúc |

Lưu ý: EmotiCare AIoT không thay thế chuyên gia sức khỏe tinh thần. Nếu người dùng có cảm giác nguy hiểm cho bản thân hoặc người khác, cần liên hệ ngay người thân, chuyên gia hoặc dịch vụ hỗ trợ khẩn cấp tại địa phương.

## 8.8. Xem trạng thái đồng bộ

| Trạng thái | Ý nghĩa | Hành động đề xuất |
| ---------- | ------- | ----------------- |
| Online | Thiết bị đang kết nối Cloud | Có thể dùng Activity, Music/Podcast, Conversation và Report |
| Offline | Thiết bị không có Internet | Chỉ Objective 1 hoạt động; dữ liệu lưu pending |
| Pending > 0 | Có session chưa đồng bộ | Kiểm tra Wi-Fi hoặc chọn Sync now |
| Waiting Cloud | Thiết bị đang chờ Cloud trả kết quả | Giữ kết nối và đợi phản hồi |
| Cloud result ready | Có kết quả mới từ Cloud | Mở màn hình tương ứng để xem |

## 8.9. Xem báo cáo trên TFT

Màn hình REPORT có thể mở trực tiếp từ HOME. Người dùng chọn mốc thống kê cần xem, gồm ngày, tháng hoặc năm. Báo cáo được tạo trên Cloud và trả về thành các card ngắn; nếu đang demo hoặc dữ liệu thật chưa đủ, thiết bị có thể hiển thị kết quả giả lập để mô phỏng cách Cloud trả về.

| Lựa chọn trên TFT | Ý nghĩa | Ví dụ period |
| ----------------- | ------- | ------------ |
| Daily | Xem thống kê trong một ngày | 25/06/2026 |
| Monthly | Xem thống kê trong một tháng | 06/2026 |
| Yearly | Xem thống kê trong một năm | 2026 |

| Report card | Nội dung |
| ----------- | -------- |
| Emotion mix | Tỷ lệ cảm xúc chính trong period |
| Trend | Xu hướng tích cực, ổn định hoặc tiêu cực |
| Stress streak | Số phiên căng thẳng/buồn/tức giận liên tiếp nếu có |
| Helpful activity | Hoạt động được đánh giá hữu ích nhất |
| Helpful content | Bài hát hoặc podcast được chọn/đánh giá tích cực |
| Data quality | enough_data hoặc limited_data |

Ví dụ kết quả giả lập trả về trên TFT:

| Period | Emotion mix | Trend | Helpful activity | Helpful content | Data quality |
| ------ | ----------- | ----- | ---------------- | --------------- | ------------ |
| Ngày | Vui vẻ 35%, bình thường 30%, căng thẳng 25%, mệt mỏi 10% | Căng thẳng tăng nhẹ vào buổi tối | Hít thở 4-7-8 | Podcast thở chậm 5 phút | enough_data |
| Tháng | Bình thường 40%, vui vẻ 28%, căng thẳng 20%, buồn bã 8%, mệt mỏi 4% | Cảm xúc ổn định hơn sau tuần 2 | Nghỉ 5 phút khỏi màn hình | Playlist tập trung nhẹ | enough_data |
| Năm | Bình thường 38%, vui vẻ 30%, căng thẳng 22%, buồn bã 6%, tức giận 4% | Xu hướng tích cực tăng trong các tháng gần đây | Vận động nhẹ | Podcast self-care | limited_data |

Nếu thiết bị offline, TFT hiển thị report gần nhất đã cache nếu có, kèm thông báo dữ liệu có thể chưa mới.

## 8.10. Xử lý sự cố

| Vấn đề | Nguyên nhân có thể | Cách xử lý |
| ------ | ------------------ | ---------- |
| Thiết bị không nghe rõ | Microphone bị che hoặc môi trường quá ồn | Nói gần hơn, giảm nhiễu nền |
| Kết quả là không chắc chắn | Câu nói quá ngắn hoặc confidence thấp | Check-in lại bằng câu rõ hơn |
| Không lấy được gợi ý | Thiết bị offline hoặc Cloud timeout | Kiểm tra Wi-Fi và thử lại |
| Không có danh sách bài hát/podcast | Chưa có Internet, category trống hoặc Cloud chưa trả kết quả | Mở Status, đổi category hoặc thử lại |
| Không có phản hồi hội thoại | Internet lỗi hoặc Cloud chưa trả kết quả | Mở Status để xem trạng thái |
| Báo cáo limited data | Chưa đủ session trong kỳ thống kê | Check-in đều hơn trong các ngày tiếp theo |
