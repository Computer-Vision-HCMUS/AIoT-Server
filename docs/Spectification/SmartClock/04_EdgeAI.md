# 04. Edge AI

## 4.1. Overview

Từ các mục tiêu đã trình bày ở phần trước, SmartClock không chỉ là một thiết bị hiển thị thời gian hoặc hỗ trợ Pomodoro, mà còn được định hướng trở thành một thiết bị AIoT có khả năng quan sát ngữ cảnh sinh hoạt của người dùng. Trong đó, nhóm chức năng liên quan đến giấc ngủ là phần thể hiện rõ nhất vai trò của Edge AI.

Edge AI trong SmartClock được dùng để xử lý dữ liệu gần người dùng, giảm phụ thuộc hoàn toàn vào Server và cho phép thiết bị đưa ra nhận định cơ bản ngay tại Edge Device. Đối với tính năng Sleep Monitoring, hệ thống có thể thu thập dữ liệu từ cảm biến ánh sáng, microphone, nhiệt độ, môi trường phòng ngủ và gối thông minh FSR để suy luận trạng thái ngủ của người dùng.

Mục tiêu của phần này là mô tả cách SmartClock có thể mở rộng từ chức năng theo dõi thời lượng ngủ đơn giản thành một module phân tích giấc ngủ có khả năng ước lượng trạng thái **REM/NREM**.

---

## 4.2. Sleep Stage Inference Problem

Giấc ngủ của con người thường được chia thành hai trạng thái chính:

* **NREM (Non-Rapid Eye Movement):** giai đoạn ngủ không có chuyển động mắt nhanh, cơ thể thường ổn định và thư giãn hơn, liên quan nhiều đến phục hồi thể chất.
* **REM (Rapid Eye Movement):** giai đoạn ngủ có chuyển động mắt nhanh, não hoạt động mạnh hơn, thường liên quan đến giấc mơ, xử lý trí nhớ và cảm xúc.

Phương pháp chuyên nghiệp để phân tích giấc ngủ là PSG (Polysomnography), sử dụng nhiều tín hiệu sinh lý như EEG, EOG, EMG, ECG và hô hấp. Tuy nhiên, PSG cần thiết bị chuyên dụng, khó sử dụng trong môi trường nhà ở hằng ngày và không phù hợp với mục tiêu prototype nhỏ gọn của SmartClock.

Vì vậy, bài toán của SmartClock được đặt ra như sau:

> Làm thế nào có thể ước lượng trạng thái ngủ REM/NREM của người dùng bằng các tín hiệu thu được từ gối thông minh FSR, âm thanh, nhiệt độ và môi trường phòng ngủ?

Hệ thống không nhằm thay thế thiết bị y tế hoặc PSG chuyên nghiệp. Thay vào đó, SmartClock cung cấp một ước lượng có tính hỗ trợ, giúp người dùng hiểu rõ hơn về thói quen nghỉ ngơi của mình và có thêm gợi ý cải thiện chất lượng giấc ngủ.

---

## 4.3. Input Data

Module Edge AI sử dụng các nhóm dữ liệu sau:

| Nguồn dữ liệu | Tín hiệu thu thập | Ý nghĩa đối với bài toán |
| --- | --- | --- |
| Gối thông minh FSR | Tư thế ngủ, áp lực đầu/cổ, số lần trở mình | Phát hiện tư thế, mức độ vận động và thay đổi tư thế trong đêm |
| Microphone INMP441 | Tiếng ngáy, âm thanh môi trường khi ngủ | Phân tích hiện tượng ngáy, tiếng ồn và biến động âm thanh |
| Cảm biến nhiệt độ | Nhiệt độ cơ thể, nhiệt độ phòng | Theo dõi thay đổi thân nhiệt và điều kiện phòng ngủ |
| Cảm biến môi trường | CO2, ánh sáng, độ ẩm | Đánh giá chất lượng môi trường ngủ và các yếu tố ảnh hưởng đến giấc ngủ |
| Dữ liệu thời gian | Giờ bắt đầu ngủ, giờ thức dậy, tổng thời lượng ngủ | Cung cấp ngữ cảnh theo phiên ngủ và hỗ trợ tính điểm chất lượng ngủ |

Trong phiên bản prototype, SmartClock có thể bắt đầu với các dữ liệu dễ thu thập hơn như ánh sáng, âm thanh và thời lượng ngủ. Các nguồn dữ liệu như FSR, CO2, độ ẩm hoặc nhiệt độ cơ thể có thể được bổ sung ở các phiên bản mở rộng.

---

## 4.4. Expected Output

Đầu ra của module Edge AI bao gồm:

* Nhãn trạng thái ngủ theo từng khoảng thời gian: **REM** hoặc **NREM**.
* Điểm đánh giá chất lượng giấc ngủ.
* Tổng thời lượng ngủ.
* Mức độ ổn định của giấc ngủ dựa trên số lần trở mình và biến động âm thanh.
* Ghi nhận các yếu tố môi trường bất lợi như phòng quá sáng, quá ồn, CO2 cao hoặc độ ẩm không phù hợp.
* Gợi ý cải thiện cho các lần ngủ tiếp theo.

Ví dụ, nếu hệ thống ghi nhận phòng quá sáng, nhiều tiếng ồn và người dùng trở mình nhiều lần, SmartClock có thể đánh giá giấc ngủ chưa tốt và đề xuất giảm ánh sáng, giảm tiếng ồn hoặc điều chỉnh môi trường phòng ngủ.

---

## 4.5. Edge AI Processing Pipeline

Quy trình xử lý tổng quát của module Sleep Edge AI:

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

Trong pipeline này:

1. Dữ liệu FSR được dùng để xác định tư thế ngủ và phát hiện thay đổi tư thế.
2. Dữ liệu âm thanh được dùng để phát hiện tiếng ngáy, tiếng ồn và các thay đổi bất thường trong môi trường ngủ.
3. Dữ liệu ánh sáng, nhiệt độ, CO2 và độ ẩm được dùng để đánh giá điều kiện phòng ngủ.
4. Các đặc trưng được trích xuất theo từng cửa sổ thời gian, ví dụ mỗi 30 giây hoặc mỗi vài phút.
5. Bộ luật suy luận hoặc mô hình Machine Learning nhẹ chạy trên Edge Device để phân loại REM/NREM hoặc tính điểm chất lượng ngủ.
6. Khi có kết nối Internet, dữ liệu có thể được gửi lên Server để lưu lịch sử, trực quan hóa trên dashboard hoặc cải thiện mô hình phân tích.

---

## 4.6. Rule-based Inference Design

Ở giai đoạn prototype, SmartClock có thể ưu tiên cách tiếp cận rule-based trước khi huấn luyện mô hình phức tạp. Cách này phù hợp với thiết bị nhúng vì dễ triển khai, dễ giải thích và không yêu cầu tài nguyên tính toán lớn.

Một số luật suy luận có thể được sử dụng:

| Dấu hiệu quan sát | Ý nghĩa suy luận |
| --- | --- |
| Ít thay đổi tư thế, âm thanh ổn định, môi trường tối | Giấc ngủ có xu hướng ổn định hơn, có thể thuộc NREM |
| Nhiều biến động âm thanh, nhịp thở/tiếng ngáy thay đổi, cơ thể ít vận động | Có thể là giai đoạn REM hoặc giai đoạn ngủ không ổn định |
| Nhiều lần trở mình liên tục | Chất lượng ngủ giảm hoặc người dùng đang ở trạng thái ngủ nông |
| Phòng quá sáng hoặc quá ồn | Điều kiện môi trường có thể làm giảm chất lượng giấc ngủ |
| CO2 cao, độ ẩm không phù hợp | Môi trường phòng ngủ cần được cải thiện |

Trong tương lai, các luật này có thể được thay thế hoặc bổ sung bằng mô hình Machine Learning như Decision Tree, SVM hoặc TinyML model tùy theo tài nguyên của ESP32 và lượng dữ liệu huấn luyện thu thập được.

---

## 4.7. Edge-Server Collaboration

Edge Device và Server phối hợp theo nguyên tắc:

* **Edge Device** xử lý dữ liệu thời gian thực, đọc cảm biến, trích xuất đặc trưng và đưa ra đánh giá cơ bản ngay tại thiết bị.
* **Server** lưu lịch sử giấc ngủ, tổng hợp dữ liệu theo ngày/tuần, hỗ trợ dashboard và có thể chạy các phân tích nặng hơn.

Khi SmartClock offline, thiết bị vẫn có thể ghi nhận phiên ngủ, tính thời lượng ngủ và đưa ra đánh giá cơ bản. Khi online, thiết bị đồng bộ dữ liệu lên Server để người dùng xem lịch sử, biểu đồ hoặc nhận gợi ý cá nhân hóa tốt hơn.

---

## 4.8. Limitations

Module Edge AI của SmartClock có một số giới hạn:

* Kết quả REM/NREM chỉ là ước lượng hỗ trợ, không phải chẩn đoán y khoa.
* Hệ thống không phân tách chi tiết N1, N2, N3 như PSG.
* Độ chính xác phụ thuộc vào vị trí cảm biến, chất lượng microphone, nhiễu môi trường và thói quen ngủ của từng người.
* Một số cảm biến như FSR, CO2, độ ẩm hoặc nhiệt độ cơ thể có thể chưa có trong phiên bản prototype đầu tiên.
* Nếu không có dữ liệu nhịp tim hoặc tín hiệu sinh lý trực tiếp, việc kiểm chứng kết quả REM/NREM sẽ còn hạn chế.

---

## 4.9. Summary

Edge AI giúp SmartClock mở rộng từ một thiết bị hỗ trợ thời gian thành một hệ thống AIoT có khả năng quan sát và phân tích ngữ cảnh sinh hoạt. Đối với tính năng giấc ngủ, SmartClock có thể kết hợp dữ liệu từ gối thông minh, microphone, ánh sáng, nhiệt độ và môi trường để ước lượng trạng thái REM/NREM, đánh giá chất lượng ngủ và đưa ra gợi ý cải thiện.

Phần Edge AI này là cầu nối giữa các mục tiêu sản phẩm ở chương trước và hướng dẫn sử dụng ở chương sau: người dùng vẫn thao tác đơn giản qua Sleep Mode, nhưng bên dưới thiết bị có thể thực hiện quy trình phân tích thông minh hơn để tạo ra báo cáo giấc ngủ có giá trị.
