# Problem Statement: Suy luận giai đoạn ngủ từ gối thông minh và cảm biến môi trường

## 1. Bối cảnh

Giấc ngủ của con người thường được chia thành hai trạng thái chính:

- **NREM (Non-Rapid Eye Movement)**: giai đoạn ngủ không có chuyển động mắt nhanh. Cơ thể thường thư giãn hơn, nhịp tim và hơi thở ổn định hơn, đồng thời đây là giai đoạn quan trọng cho quá trình phục hồi thể chất.
- **REM (Rapid Eye Movement)**: giai đoạn ngủ có chuyển động mắt nhanh. Não hoạt động gần giống khi thức, thường liên quan đến giấc mơ, xử lý trí nhớ và điều hòa cảm xúc.

Trong một đêm ngủ, REM và NREM thường lặp lại theo chu kỳ. Mỗi chu kỳ kéo dài khoảng 90 phút và có thể lặp lại 4-6 lần. Ở đầu đêm, NREM sâu thường chiếm nhiều hơn; về cuối đêm, thời lượng REM có xu hướng tăng lên.

Phương pháp chuẩn để phân tích giấc ngủ là PSG (Polysomnography), thường đo nhiều tín hiệu sinh lý như EEG, EOG, EMG, ECG và hô hấp. Tuy nhiên, PSG cần thiết bị chuyên dụng, phải gắn cảm biến trực tiếp lên cơ thể và khó triển khai trong môi trường nhà ở hằng ngày.

Du án này hướng đến một cách tiếp cận ít xâm lấn hơn: suy luận trạng thái ngủ REM/NREM dựa trên dữ liệu từ gối thông minh, âm thanh và các cảm biến môi trường trong phòng ngủ.

## 2. Vấn đề cần giải quyết

Bài toán đặt ra là:

> Làm thế nào có thể ước lượng trạng thái ngủ REM/NREM của người dùng bằng các tín hiệu thu được từ gối thông minh FSR, âm thanh, nhiệt độ và môi trường phòng ngủ?

Hệ thống không có mục tiêu thay thế PSG chuyên nghiệp. Thay vào đó, hệ thống cần cung cấp một ước lượng hợp lý về trạng thái ngủ dựa trên các dấu hiệu gián tiếp, phục vụ theo dõi giấc ngủ tại nhà.

## 3. Dữ liệu đầu vào

Hệ thống sử dụng các nhóm dữ liệu sau:

| Nguồn dữ liệu | Tín hiệu thu thập | Ý nghĩa đối với bài toán |
| --- | --- | --- |
| Gối thông minh FSR | Tư thế ngủ, áp lực đầu/cổ, số lần trở mình | Phát hiện tư thế, mức độ vận động và thay đổi tư thế trong đêm |
| Microphone | Tiếng ngáy, âm thanh khi ngủ | Phân tích hiện tượng ngáy và biến động hô hấp/âm thanh |
| Cảm biến nhiệt độ | Nhiệt độ cơ thể, nhiệt độ phòng | Theo dõi thay đổi thân nhiệt và điều kiện phòng ngủ |
| Cảm biến môi trường | CO2, ánh sáng, độ ẩm | Đánh giá chất lượng môi trường ngủ và các yếu tố có thể ảnh hưởng đến giấc ngủ |

## 4. Đầu ra mong muốn

Đầu ra của hệ thống là nhãn trạng thái ngủ theo từng khoảng thời gian:

- **NREM**: ngủ không REM, có xu hướng ổn định hơn, liên quan đến phục hồi thể chất.
- **REM**: ngủ REM, thường có hoạt động não cao hơn, liên quan đến giấc mơ và xử lý thông tin.

Ngoài nhãn REM/NREM, hệ thống có thể lưu thêm các thông tin hỗ trợ:

- Tư thế ngủ chủ đạo trong khoảng thời gian.
- Số lần trở mình.
- Mức độ ngáy.
- Nhiệt độ cơ thể và nhiệt độ phòng.
- Giá trị CO2, ánh sáng và độ ẩm.
- Mức độ tin cậy của kết quả suy luận nếu có.

## 5. Cách tiếp cận

Quy trình xử lý tổng quát:

```text
FSR Pillow
Microphone
Temperature Sensors
CO2 / Light / Humidity Sensors
        |
        v
Feature Extraction
        |
        v
Posture Detection
        |
        v
Toss and Turn Detection
        |
        v
Snoring Analysis
        |
        v
Temperature and Environment Analysis
        |
        v
Rule-based Sleep Stage Inference
        |
        v
REM / NREM Prediction
        |
        v
Heart Rate Comparison / Validation
```

Trong quy trình này:

1. Dữ liệu FSR được dùng để xác định tư thế ngủ và phát hiện thay đổi tư thế.
2. Dữ liệu âm thanh được dùng để phát hiện và phân tích tiếng ngáy.
3. Nhiệt độ cơ thể, nhiệt độ phòng và dữ liệu môi trường được dùng để bổ sung ngữ cảnh.
4. Các đặc trưng sau khi trích xuất được đưa vào bộ luật suy luận để phân loại REM/NREM.
5. Nếu có dữ liệu nhịp tim, kết quả có thể được đối chiếu để đánh giá độ hợp lý.

## 6. Giả định và giới hạn

Hệ thống dựa trên một số giả định:

- Trạng thái ngủ có thể được ước lượng từ các dấu hiệu gián tiếp như tư thế, số lần trở mình, âm thanh, nhiệt độ và môi trường.
- REM và NREM có các đặc điểm hành vi và sinh lý khác nhau đủ để tạo ra mẫu tín hiệu có thể khai thác.
- Dữ liệu nhịp tim, nếu có, được xem là tín hiệu hỗ trợ để kiểm chứng kết quả.

Giới hạn của bài toán:

- Hệ thống chỉ phân loại ở mức **REM/NREM**, không tách chi tiết N1, N2, N3 như PSG.
- Kết quả chỉ mang tính ước lượng, không phải chẩn đoán y khoa.
- Độ chính xác có thể bị ảnh hưởng bởi nhiều yếu tố như vị trí cảm biến, nhiễu âm thanh, tư thế ngủ bất thường, nhiệt độ phòng thay đổi đột ngột hoặc thói quen ngủ của từng người.

## 7. Mục tiêu cuối cùng

Mục tiêu của bài toán là xây dựng một module AI/rule-based có khả năng:

- Thu thập và tiền xử lý dữ liệu ngủ từ gối thông minh và cảm biến môi trường.
- Trích xuất các đặc trưng có liên quan đến hành vi ngủ.
- Phân loại trạng thái ngủ thành REM hoặc NREM theo từng khoảng thời gian.
- Đối chiếu kết quả với tín hiệu hỗ trợ như nhịp tim để tăng độ tin cậy.
- Cung cấp dữ liệu đầu ra phục vụ dashboard, thống kê và gợi ý cải thiện chất lượng giấc ngủ.
