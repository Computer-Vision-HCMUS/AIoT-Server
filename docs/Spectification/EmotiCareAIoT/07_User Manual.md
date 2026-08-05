# 07. Hướng dẫn sử dụng

## 7.1. Tổng quan

EmotiCare AIoT được sử dụng trực tiếp trên thiết bị phần cứng. Cảm xúc hiện tại, gợi ý hoạt động, danh sách bài hát/podcast, phản hồi trò chuyện, trạng thái đồng bộ và biểu đồ thống kê cảm xúc đều được hiển thị trên màn hình TFT.

Luồng sử dụng chính:

![Sơ đồ luồng sử dụng chính](user-flow-v2.png)

`HOME` mở các mục `CHECK-IN`, `DISCOVER`, `COMPANION CHAT`, `INSIGHTS`, `TEST MIC`, `TEST BUTTONS` và `WIFI SETUP`. Sau `CHECK-IN`, người dùng xem **Kết quả**, **Xác nhận** rồi mới mở **Support**. Discover dẫn đến danh sách Music hoặc Podcast.

## 7.2. Luồng màn hình thiết bị

| Màn hình | Mục đích | Thao tác chính |
| -------- | -------- | -------------- |
| Trang chủ | Hiển thị trạng thái Wi-Fi, cảm xúc gần nhất và bảy mục điều hướng | Mở Check-In, Discover, Companion Chat, Insights, Test Mic, Test Buttons hoặc WiFi Setup |
| Check-In | Ghi âm, xử lý và yêu cầu xác nhận kết quả cảm xúc | S1 ghi âm; S2/S3 thực thi, xác nhận và mở Support |
| Support | Hiển thị danh sách hoạt động từ máy chủ hoặc fallback cục bộ | Mở chi tiết hoạt động, chuyển mục hoặc quay về màn hình trước |
| Discover | Chọn Music hoặc Podcast | Mở danh sách nội dung tương ứng |
| Nhạc/Podcast | Hiển thị danh sách cuộn và phát nội dung được chọn | S3 phát, S2 dừng, S4/S5 cuộn, S1 quay lại Discover |
| Companion Chat | Thu âm chia sẻ và hiển thị phản hồi hội thoại | S1 bắt đầu thu; sau khi thu xong, S2/S3 gửi yêu cầu |
| WiFi Setup | Hiển thị trạng thái `Online`, `Unpaired`, `Setup AP` hoặc `Offline` | Mở captive portal hoặc thử kết nối lại |
| Insights | Xem thống kê cảm xúc ngày/tuần/tháng | Chọn mốc thời gian và xem tám thanh tỷ lệ cảm xúc hoặc phần diễn giải AI |

## 7.3. Thiết lập lần đầu

| Bước | Hành động | Kết quả mong đợi |
| ---- | --------- | ---------------- |
| 1 | Bật nguồn và mở **WiFi Setup** nếu thiết bị chưa trực tuyến | TFT hiển thị trạng thái mạng hiện tại |
| 2 | Khi thấy `Setup AP`, kết nối điện thoại vào Wi-Fi `EmotiCare-Setup` (mật khẩu `12345678`) | Điện thoại kết nối với captive portal của thiết bị |
| 3 | Mở `http://192.168.4.1`, chọn Wi-Fi, nhập mật khẩu, Server URL và pairing code | Thiết bị kết nối Wi-Fi, pair với máy chủ rồi khởi động lại |
| 4 | Mở **Test Mic** để kiểm tra đường thu/phát âm thanh khi cần | Xác nhận microphone và loa hoạt động |

## 7.4. Kiểm tra cảm xúc bằng giọng nói

| Bước | Hành động của người dùng | Hành vi của thiết bị |
| ---- | ----------------------- | -------------------- |
| 1 | Từ Trang chủ chọn Kiểm tra cảm xúc | Màn hình chuyển sang Kiểm tra cảm xúc |
| 2 | Nhấn S1 (`REC`) và nói trong tối đa 10 giây | Thiết bị hiển thị thời gian thu âm |
| 3 | Sau khi thu xong, nhấn S2 hoặc S3 (`EXEC`) | Thiết bị xử lý giọng nói tại Edge |
| 4 | Xem kết quả rồi nhấn S2/S3 (`CONFIRM`) để lưu | TFT hiển thị nhãn cảm xúc và độ tin cậy theo phần trăm |
| 5 | Nhấn S2/S3 lần nữa (`SUPPORT`) | Chuyển sang màn hình Support; S5 quay về màn hình trước |

Ví dụ kết quả:

| Trường | Giá trị |
| ------ | ------- |
| Cảm xúc | Căng thẳng |
| Độ tin cậy | 74% |
| Bước tiếp theo | Xác nhận kết quả rồi mở Support, hoặc quay về Trang chủ |

## 7.5. Sử dụng các dịch vụ hỗ trợ qua Cloud

Sau khi xác nhận Check-In, nhấn S2/S3 để mở **Support**. Firmware ưu tiên lấy danh sách hoạt động theo session gần nhất từ máy chủ; khi không lấy được dữ liệu, nó vẫn hiển thị một hoạt động fallback theo cảm xúc hiện tại. Màn hình chỉ hỗ trợ xem danh sách và mở chi tiết, không có thao tác bỏ qua hoặc đánh giá hoạt động.

| Cảm xúc fallback | Hoạt động fallback trong firmware |
| ----------------- | -------------------------------- |
| `Happy` | Capture the Moment |
| `Sad` | Small Reset Walk |
| `Anxious` hoặc `stressed` | Box Breathing |
| Nhãn khác | Breathing & Light Stretch |

Khi thiết bị ngoại tuyến hoặc máy chủ lỗi, Support vẫn dùng hoạt động fallback cục bộ.

## 7.6. Chọn bài hát hoặc podcast theo chủ đích

Từ Trang chủ, chọn **Discover** để mở danh mục nội dung. Màn hình này chỉ có hai lựa chọn: **Music** và **Podcast**. Nếu đã check-in, TFT hiển thị cảm xúc gần nhất và độ tin cậy để cho biết danh sách được ưu tiên theo ngữ cảnh đó; nếu chưa check-in, thiết bị dùng ngữ cảnh `Neutral (default)`.

Danh sách nội dung được lấy từ catalog của máy chủ. Các mục được AI đề xuất được đưa lên đầu danh sách và có nhãn `AI`; khi không tải được catalog mới, firmware dùng dữ liệu fallback cục bộ. Phiên bản hiện tại không có bước chọn category, chọn `Both`, nhập/nói chủ đích hoặc lưu/đánh giá nội dung ngay trên TFT.

| Màn hình | Nội dung hiển thị |
| -------- | ---------------- |
| Discover | Hai mục `Music` và `Podcast`, số lượng mục hiện có và số mục được AI ưu tiên; S4 đi xuống, S5 đi lên/quay lại, S2 hoặc S3 mở mục đang chọn. |
| Music | Danh sách cuộn tối đa bốn bài hát cùng lúc; mỗi mục có tiêu đề, category và thời lượng. Nhấn S3 để phát, S2 để dừng, S4/S5 để cuộn, S1 để quay lại Discover. |
| Podcast | Danh sách cuộn tối đa bốn tập cùng lúc; mỗi mục có tiêu đề, category và thời lượng. Nhấn S3 để phát, S2 để dừng, S4/S5 để cuộn, S1 để quay lại Discover. |

## 7.7. Sử dụng trò chuyện hỗ trợ cảm xúc qua Cloud

Chế độ **Companion Chat** mở trực tiếp từ Trang chủ. Thiết bị thu PCM 16-bit, 16 kHz trong tối đa 10 giây; nếu chưa có session check-in, firmware thử tạo một session `neutral` trước khi gửi yêu cầu. Khi có kết nối, máy chủ trả transcript, phản hồi văn bản và có thể kèm URL audio TTS. Nếu dịch vụ không khả dụng, firmware dùng phản hồi fallback.

| Bước | Hành động | Kết quả |
| ---- | --------- | ------- |
| 1 | Chọn Companion Chat từ Trang chủ, nhấn S1 (`REC`) và chia sẻ ngắn | Thiết bị bắt đầu thu âm |
| 2 | Chờ đủ thời gian thu, sau đó nhấn S2 hoặc S3 | Thiết bị gửi PCM và session hiện có hoặc session `neutral` |
| 3 | Đợi phản hồi | TFT hiển thị transcript/phản hồi; audio TTS được phát nếu có URL hợp lệ |
| 4 | Đọc phản hồi trên TFT | Người dùng có thể tiếp tục hoặc kết thúc |

Lưu ý: EmotiCare AIoT không thay thế chuyên gia sức khỏe tinh thần. Nếu người dùng có cảm giác nguy hiểm cho bản thân hoặc người khác, cần liên hệ ngay người thân, chuyên gia hoặc dịch vụ hỗ trợ khẩn cấp tại địa phương.

## 7.8. Xem trạng thái Wi-Fi và pairing

| Trạng thái | Ý nghĩa | Hành động đề xuất |
| ---------- | ------- | ----------------- |
| Online | Đã kết nối Wi-Fi và pair với máy chủ | Có thể gọi các API máy chủ; một số màn hình vẫn có fallback khi API lỗi |
| Unpaired | Đã kết nối Wi-Fi nhưng chưa pair với máy chủ | Mở WiFi Setup để nhập Server URL và pairing code |
| Setup AP | Thiết bị đang mở hotspot cấu hình | Kết nối `EmotiCare-Setup` và mở `192.168.4.1` |
| Offline | Chưa kết nối Wi-Fi | Mở WiFi Setup để cấu hình hoặc kết nối lại |

## 7.9. Xem báo cáo trên TFT

Màn hình **Insights** có thể mở trực tiếp từ Trang chủ. Người dùng chọn kỳ thống kê ngày, tuần hoặc tháng để xem biểu đồ tỷ lệ của tám nhãn cảm xúc. Thiết bị ưu tiên lấy dữ liệu từ máy chủ; nếu không lấy được dữ liệu hợp lệ, firmware hiển thị bảng dữ liệu mẫu cục bộ để giao diện vẫn hoạt động.

| Lựa chọn trên màn hình | Ý nghĩa | Giá trị gửi tới máy chủ |
| ----------------- | ------- | ------------ |
| Ngày | Xem thống kê trong một ngày | `GET /api/statistics/day` |
| Tuần | Xem thống kê trong một tuần | `GET /api/statistics/week` |
| Tháng | Xem thống kê trong một tháng | `GET /api/statistics/month` |

| Nội dung hiển thị | Ý nghĩa |
| ----------------- | ------- |
| Bộ chọn kỳ | Ba lựa chọn `Day`, `Week`, `Month`; kỳ đang chọn được làm nổi bật. |
| Biểu đồ cảm xúc | Tám thanh tỷ lệ phần trăm cho các nhãn `Angry`, `Calm`, `Disgust`, `Fearful`, `Happy`, `Neutral`, `Sad` và `Surprise`. |
| Dòng trạng thái | Hiển thị kỳ đang xem theo dạng `Period: <kỳ> | AI-analyzed`. |
| Chế độ AI assessment | Nhấn S1 (`AI VIEW`) để xem phần diễn giải do API `POST /api/statistics/{period}/explain` trả về; nhấn S1 lần nữa để quay lại biểu đồ. |
| Điều hướng | S2 hoặc S4 chuyển sang kỳ tiếp theo; S3 chuyển về kỳ trước; S5 quay lại màn hình trước. |

### Ví dụ nội dung báo cáo trên TFT

Các số liệu dưới đây là bảng fallback hiện có trong firmware. Chúng chỉ được dùng khi thiết bị không lấy được `emotion_distribution` hợp lệ từ máy chủ và không phải kết quả đánh giá sức khỏe tâm lý.

**Báo cáo ngày**

| Nội dung | Kết quả minh họa |
| -------- | ---------------- |
| Phân bố cảm xúc | Angry 4%; Calm 22%; Disgust 2%; Fearful 5%; Happy 42%; Neutral 16%; Sad 6%; Surprise 3% |
| Dòng trạng thái | `Period: Day | AI-analyzed` |

**Báo cáo tuần**

| Nội dung | Kết quả minh họa |
| -------- | ---------------- |
| Phân bố cảm xúc | Angry 7%; Calm 18%; Disgust 3%; Fearful 8%; Happy 34%; Neutral 18%; Sad 9%; Surprise 3% |
| Dòng trạng thái | `Period: Week | AI-analyzed` |

**Báo cáo tháng**

| Nội dung | Kết quả minh họa |
| -------- | ---------------- |
| Phân bố cảm xúc | Angry 5%; Calm 20%; Disgust 3%; Fearful 7%; Happy 38%; Neutral 17%; Sad 7%; Surprise 3% |
| Dòng trạng thái | `Period: Month | AI-analyzed` |

Nếu máy chủ hoặc kết nối không sẵn sàng, màn hình biểu đồ vẫn hiển thị bảng fallback nêu trên. Riêng chế độ **AI assessment** cần gọi API; khi không lấy được diễn giải, thiết bị hiển thị thông báo yêu cầu kiểm tra Wi-Fi và máy chủ.

## 7.10. Xử lý sự cố

| Vấn đề | Nguyên nhân có thể | Cách xử lý |
| ------ | ------------------ | ---------- |
| Thiết bị không nghe rõ | Microphone bị che hoặc môi trường quá ồn | Nói gần hơn, giảm nhiễu nền |
| Kết quả là không chắc chắn | Câu nói quá ngắn hoặc confidence thấp | Check-in lại bằng câu rõ hơn |
| Không lấy được gợi ý | Thiết bị offline hoặc Cloud timeout | Kiểm tra Wi-Fi và thử lại |
| Không phát được bài hát/podcast | Mục đang chọn không có URL phát hoặc audio output không khả dụng | Chọn mục khác, kiểm tra Wi-Fi và loa |
| Không có phản hồi hội thoại | Internet lỗi, máy chủ không trả kết quả hoặc thu âm chưa đủ | Kiểm tra Wi-Fi, thu lại rồi gửi bằng S2/S3 |
| Không xem được AI assessment | Không có Wi-Fi, chưa kết nối máy chủ hoặc API diễn giải không trả kết quả | Kiểm tra Wi-Fi và máy chủ, sau đó nhấn S1 để thử lại; biểu đồ fallback vẫn có thể xem. |
