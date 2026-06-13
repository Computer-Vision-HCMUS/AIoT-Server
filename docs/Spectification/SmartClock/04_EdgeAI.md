# 04. Edge AI: Sleep Observation

## 4.1. Overview

Chương này tập trung vào **use case Edge AI duy nhất của SomniLearnAI: quan sát giấc ngủ**. Edge AI không được dùng để thay thế server, dashboard hoặc chức năng chấm điểm thuyết trình. Vai trò chính của Edge AI là đọc dữ liệu cảm biến gần người dùng, hiển thị môi trường phòng ngủ theo realtime và tạo đánh giá giấc ngủ cơ bản ngay trên thiết bị.

Khi người dùng bật Sleep Monitoring, thiết bị ghi nhận thời gian ngủ, ánh sáng, tiếng ồn và các chỉ số môi trường nếu có cảm biến mở rộng. Sau phiên ngủ, Edge Device tạo báo cáo ngắn gồm sleep score, tác nhân ảnh hưởng và gợi ý cải thiện. Dữ liệu này có thể đồng bộ lên dashboard để quan sát dài hạn ở chương 05.

---

## 4.2. Scope

Edge AI của SomniLearnAI chỉ bao gồm các tác vụ liên quan trực tiếp đến quan sát giấc ngủ tại thiết bị.

| Module | Main Purpose | Output |
| ------ | ------------ | ------ |
| Sleep Monitoring Edge AI | Quan sát giấc ngủ và môi trường phòng ngủ | Sleep score, tác nhân ảnh hưởng, gợi ý cải thiện |
| Environment Realtime Monitor | Theo dõi ánh sáng, tiếng ồn, nhiệt độ, độ ẩm hoặc CO2 | Trạng thái môi trường realtime trên màn hình |
| Sleep Feature Extraction | Tạo đặc trưng gọn nhẹ từ cảm biến ngủ | Feature summary cho báo cáo ngủ |

Các chức năng sau không thuộc phạm vi chương này:

| Function | Reason |
| -------- | ------ |
| Seminar Practice Scoring | Cần Wi-Fi và Server để xử lý/chấm điểm đầy đủ hơn |
| Dashboard Analytics | Được mô tả ở chương 05 vì phụ thuộc dữ liệu lịch sử trên Server |
| Monthly Sleep Summary | Được mô tả ở chương 05 vì cần tổng hợp nhiều phiên ngủ trong database |

---

## 4.3. Sleep Observation Use Case

Bài toán chính của Sleep Monitoring là hỗ trợ người dùng quan sát giấc ngủ tại nhà. Hệ thống không chẩn đoán y khoa, mà trả lời 3 câu hỏi thực tế:

* Người dùng đã ngủ trong bao lâu?
* Môi trường xung quanh trong phiên ngủ có phù hợp không?
* Tác nhân nào có khả năng làm giấc ngủ không ngon?

Use case này là phần thể hiện rõ nhất của Edge AI trong sản phẩm: cảm biến đọc dữ liệu tại phòng ngủ, thiết bị xử lý ngay tại chỗ và màn hình hiển thị kết quả để người dùng điều chỉnh môi trường ngủ.

---

## 4.4. Sleep Input Data

Module Sleep Edge AI sử dụng các nhóm dữ liệu sau:

| Nguồn dữ liệu | Tín hiệu thu thập | Ý nghĩa đối với bài toán |
| ------------- | ----------------- | ------------------------ |
| Microphone INMP441 | Tiếng ngáy, tiếng ồn môi trường khi ngủ | Phát hiện môi trường quá ồn, biến động âm thanh hoặc dấu hiệu ngáy |
| Cảm biến ánh sáng | Mức sáng theo thời gian | Phát hiện phòng quá sáng hoặc ánh sáng thay đổi trong phiên ngủ |
| Cảm biến nhiệt độ | Nhiệt độ phòng | Đánh giá điều kiện nhiệt độ có phù hợp cho giấc ngủ không |
| Cảm biến độ ẩm | Độ ẩm phòng | Phát hiện môi trường quá khô hoặc quá ẩm |
| Cảm biến CO2 | Nồng độ CO2 nếu có | Phát hiện phòng bí, thông khí kém |
| Dữ liệu thời gian | Giờ bắt đầu ngủ, giờ thức dậy, tổng thời lượng ngủ | Cung cấp ngữ cảnh theo phiên ngủ và hỗ trợ tính điểm chất lượng ngủ |
| Gối thông minh FSR | Tư thế ngủ, áp lực đầu/cổ, số lần trở mình | Nguồn dữ liệu mở rộng để phát hiện trở mình và độ ổn định giấc ngủ |

Trong phiên bản prototype, SomniLearnAI có thể bắt đầu với dữ liệu dễ thu thập như ánh sáng, âm thanh và thời lượng ngủ. Các nguồn dữ liệu như FSR, CO2 hoặc cảm biến môi trường đầy đủ có thể được bổ sung ở các phiên bản mở rộng.

---

## 4.5. Sleep Expected Output

Đầu ra của module Sleep Edge AI bao gồm:

* Tổng thời lượng ngủ.
* Điểm đánh giá chất lượng giấc ngủ.
* Realtime environment status khi người dùng quan sát trước hoặc trong phiên ngủ.
* Ghi nhận các yếu tố môi trường bất lợi như phòng quá sáng, quá ồn, nhiệt độ chưa phù hợp, CO2 cao hoặc độ ẩm không phù hợp.
* Tác nhân có khả năng làm giấc ngủ không ngon.
* Gợi ý cải thiện cho các lần ngủ tiếp theo.
* Feature summary để dashboard tổng hợp theo ngày hoặc tháng.

Ví dụ, nếu hệ thống ghi nhận phòng quá sáng, nhiều tiếng ồn và thời lượng ngủ ngắn, SomniLearnAI có thể đánh giá giấc ngủ chưa tốt và đề xuất giảm ánh sáng, giảm tiếng ồn hoặc điều chỉnh môi trường phòng ngủ.

---

## 4.6. Sleep Edge AI Processing Pipeline

Quy trình xử lý tổng quát của module Sleep Edge AI:

```text
Microphone
Light Sensor
Temperature / Humidity / CO2 Sensors
Optional FSR Pillow
        |
        v
Sensor Preprocessing
        |
        v
Feature Extraction by Time Window
        |
        v
Noise / Light / Environment Analysis
        |
        v
Sleep Quality Scoring
        |
        v
Factor Detection
        |
        v
Sleep Report Generation
        |
        v
Local Sleep Report
        |
        v
Optional Server Synchronization
```

Trong pipeline này:

1. Dữ liệu âm thanh được dùng để phát hiện tiếng ồn, tiếng ngáy và các thay đổi bất thường trong môi trường ngủ.
2. Dữ liệu ánh sáng, nhiệt độ, CO2 và độ ẩm được dùng để đánh giá điều kiện phòng ngủ.
3. Dữ liệu được chia theo từng cửa sổ thời gian, ví dụ 30 giây hoặc vài phút, để trích xuất đặc trưng.
4. Bộ luật suy luận hoặc mô hình Machine Learning nhẹ chạy trên Edge Device để tính sleep score và phát hiện tác nhân ảnh hưởng.
5. Thiết bị tạo báo cáo ngủ cục bộ để người dùng xem ngay sau phiên ngủ.
6. Khi có kết nối Internet, sleep session và feature summary được gửi lên Server để dashboard quan sát dài hạn.

---

## 4.7. Rule-based Sleep Inference Design

Ở giai đoạn prototype, SomniLearnAI có thể ưu tiên cách tiếp cận rule-based trước khi huấn luyện mô hình phức tạp. Cách này phù hợp với thiết bị nhúng vì dễ triển khai, dễ giải thích và không yêu cầu tài nguyên tính toán lớn.

Một số luật suy luận có thể được sử dụng:

| Dấu hiệu quan sát | Ý nghĩa suy luận |
| ----------------- | ---------------- |
| Thời lượng ngủ quá ngắn | Giấc ngủ có thể chưa đủ để phục hồi |
| Phòng quá sáng trong thời gian dài | Ánh sáng có thể ảnh hưởng đến chất lượng ngủ |
| Tiếng ồn cao hoặc biến động âm thanh nhiều | Môi trường ngủ có khả năng gây gián đoạn |
| Nhiệt độ quá cao hoặc quá thấp | Điều kiện phòng ngủ chưa phù hợp |
| CO2 cao hoặc độ ẩm không phù hợp | Phòng ngủ cần cải thiện thông khí hoặc điều chỉnh môi trường |
| Nhiều lần trở mình nếu có FSR | Giấc ngủ có thể không ổn định |

Trong tương lai, các luật này có thể được thay thế hoặc bổ sung bằng mô hình Machine Learning nhẹ như Decision Tree, Random Forest nhỏ, SVM hoặc TinyML model tùy theo tài nguyên của ESP32 và lượng dữ liệu huấn luyện thu thập được.

---

## 4.8. REM/NREM Extension

REM/NREM không phải trọng tâm của prototype, nhưng có thể là hướng mở rộng sau khi hệ thống có thêm dữ liệu. Giấc ngủ của con người thường được chia thành hai trạng thái chính:

* **NREM (Non-Rapid Eye Movement):** giai đoạn ngủ không có chuyển động mắt nhanh, cơ thể thường ổn định và thư giãn hơn.
* **REM (Rapid Eye Movement):** giai đoạn ngủ có chuyển động mắt nhanh, não hoạt động mạnh hơn và thường liên quan đến giấc mơ.

Phương pháp chuyên nghiệp để phân tích giấc ngủ là PSG, sử dụng nhiều tín hiệu sinh lý như EEG, EOG, EMG, ECG và hô hấp. SomniLearnAI không có đầy đủ các tín hiệu này, vì vậy REM/NREM chỉ nên được xem là hướng mở rộng và là ước lượng hỗ trợ.

Nếu prototype mở rộng có thêm dữ liệu FSR, âm thanh ổn định, môi trường phòng ngủ và dữ liệu thời gian đủ dài, hệ thống có thể thử nghiệm suy luận REM/NREM theo cửa sổ thời gian. Kết quả này cần được trình bày rõ là tham khảo, không phải kết luận y khoa.

---

## 4.9. Edge-Server Boundary

Ranh giới giữa Edge AI và Internet Service được xác định như sau:

| Component | Responsibility |
| --------- | -------------- |
| Edge Device | Quan sát giấc ngủ realtime, trích xuất đặc trưng, tính sleep score cơ bản và hiển thị báo cáo ngủ tại thiết bị |
| Server | Lưu sleep session, study session, presentation session và cung cấp API cho dashboard |
| Dashboard | Quan sát lịch sử theo ngày/tháng, so sánh xu hướng và hiển thị tổng kết |

Khi SomniLearnAI offline, Sleep Monitoring vẫn có thể tạo báo cáo cơ bản tại thiết bị. Dashboard chỉ cập nhật sau khi thiết bị online và đồng bộ dữ liệu lên Server.

---

## 4.10. Limitations

Module Edge AI của SomniLearnAI có một số giới hạn:

* Kết quả đánh giá giấc ngủ chỉ là thông tin hỗ trợ, không phải chẩn đoán y khoa.
* Kết quả REM/NREM nếu có chỉ là ước lượng tham khảo, không thay thế PSG.
* Edge Device không thực hiện chấm điểm thuyết trình đầy đủ; chức năng đó thuộc Internet Service.
* Độ chính xác phụ thuộc vào vị trí cảm biến, chất lượng microphone, nhiễu môi trường và thói quen ngủ của từng người.
* Một số cảm biến như FSR, CO2, độ ẩm hoặc nhiệt độ cơ thể có thể chưa có trong phiên bản prototype đầu tiên.
* Khi offline, dashboard chưa thể cập nhật ngay cho đến khi thiết bị đồng bộ lại.

---

## 4.11. Summary

Chương Edge AI tập trung vào một use case duy nhất: **quan sát giấc ngủ bằng Edge AI**. Thiết bị đọc dữ liệu môi trường, đánh giá chất lượng ngủ cơ bản và phát hiện tác nhân ảnh hưởng ngay tại Edge Device. Các chức năng quan sát dài hạn, tổng hợp theo tháng và chấm điểm thuyết trình được chuyển sang chương Internet Service.
