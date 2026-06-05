# 06. Conclusion

## 6.1. Project Summary

SmartClock được xây dựng với định hướng trở thành một thiết bị đồng hồ thông minh nhỏ gọn, dễ sử dụng và phù hợp với không gian học tập, làm việc hoặc nghỉ ngơi cá nhân. Xuất phát từ nhu cầu giảm sự phụ thuộc vào điện thoại thông minh trong quá trình quản lý thời gian, dự án tập trung vào việc tạo ra một thiết bị chuyên biệt có khả năng hỗ trợ người dùng duy trì thói quen sinh hoạt hiệu quả hơn.

Về kiến trúc, SmartClock được thiết kế theo mô hình **Edge Device ↔ Server**. Thiết bị Edge xử lý tương tác trực tiếp với người dùng, đọc dữ liệu từ cảm biến và hiển thị thông tin trên màn hình TFT. Server đóng vai trò lưu trữ, phân tích và mở rộng các chức năng AIoT trong tương lai. Khi không có Wi-Fi cố định, SmartClock có thể được cấu hình qua mạng setup tạm thời và kết nối Internet thông qua hotspot từ điện thoại hoặc laptop.

Thông qua các nội dung đã trình bày ở các chương trước, SmartClock không chỉ đóng vai trò là một đồng hồ hiển thị thời gian, mà còn được mở rộng thành một thiết bị hỗ trợ cá nhân với 3 nhóm mục tiêu chính:

* Hỗ trợ tập trung và nâng cao hiệu suất học tập, làm việc.
* Hỗ trợ theo dõi giấc ngủ và xây dựng lịch sinh hoạt hợp lý.
* Cung cấp trải nghiệm giải trí nhẹ nhàng và tăng tính thẩm mỹ cho không gian cá nhân.

Các mục tiêu này được cụ thể hóa thông qua các chức năng như Pomodoro Timer, Seminar Practice, Sleep Monitoring, Alarm Settings, Flappy Bird và Music Player. Bên cạnh đó, phần Edge AI giúp SmartClock mở rộng khả năng theo dõi giấc ngủ từ mức ghi nhận thời lượng đơn giản sang hướng phân tích dữ liệu cảm biến, ước lượng REM/NREM và đưa ra gợi ý cải thiện môi trường ngủ.

---

## 6.2. Achieved Objectives

### Objective 1: Supporting Focus and Productivity

SmartClock hỗ trợ người dùng làm việc tập trung hơn thông qua Pomodoro Timer. Tính năng này cho phép chia thời gian làm việc thành các phiên tập trung và nghỉ ngơi rõ ràng, giúp người dùng quản lý thời gian hiệu quả mà không cần phụ thuộc vào điện thoại.

Bên cạnh đó, Seminar Practice mở rộng phạm vi hỗ trợ học tập bằng cách giúp người dùng luyện tập thuyết trình, ghi nhận thời lượng trình bày và xem đánh giá cơ bản sau khi hoàn thành. Điều này phù hợp với nhóm người dùng là sinh viên, nhân viên văn phòng hoặc những người thường xuyên phải trình bày ý tưởng.

### Objective 2: Supporting Better Sleep Habits

SmartClock hướng đến việc cải thiện chất lượng nghỉ ngơi thông qua chức năng theo dõi giấc ngủ và báo thức. Người dùng có thể bắt đầu phiên theo dõi giấc ngủ, kết thúc phiên khi thức dậy và xem báo cáo đánh giá cơ bản. Khi kết hợp với module Edge AI, hệ thống có thể khai thác dữ liệu âm thanh, ánh sáng, nhiệt độ, môi trường phòng ngủ và gối thông minh FSR để ước lượng trạng thái REM/NREM theo từng khoảng thời gian.

Chức năng báo thức giúp người dùng duy trì thời gian thức dậy ổn định. Khi kết hợp với việc theo dõi thời lượng ngủ, đánh giá điều kiện môi trường và nhận diện các dấu hiệu như tiếng ngáy hoặc số lần trở mình, SmartClock có thể hỗ trợ người dùng hình thành thói quen sinh hoạt điều độ hơn.

### Objective 3: Supporting Relaxation and Workspace Decoration

Ngoài các chức năng hỗ trợ học tập và nghỉ ngơi, SmartClock còn tích hợp các tính năng giải trí nhẹ như Flappy Bird và Music Player. Các chức năng này giúp thiết bị trở nên sinh động hơn, đồng thời tạo ra khoảng nghỉ ngắn phù hợp sau thời gian học tập hoặc làm việc căng thẳng.

Việc kết hợp giữa tính hữu ích và tính giải trí giúp SmartClock trở thành một thiết bị gần gũi hơn trong đời sống hằng ngày, thay vì chỉ là một công cụ đếm thời gian đơn thuần.

---

## 6.3. User Experience

SmartClock được thiết kế với luồng sử dụng đơn giản, xoay quanh 4 màn hình chính:

```text
HOME → STUDY → SLEEP → RELAX → HOME
```

Cách tổ chức này giúp người dùng dễ ghi nhớ vị trí của từng chức năng. Mỗi chế độ tương ứng với một nhóm nhu cầu cụ thể:

* **HOME:** điểm bắt đầu và tổng quan hệ thống.
* **STUDY:** hỗ trợ tập trung và luyện tập thuyết trình.
* **SLEEP:** hỗ trợ theo dõi giấc ngủ và báo thức.
* **RELAX:** hỗ trợ giải trí và thư giãn.

Việc sử dụng 5 nút vật lý giúp thao tác trở nên trực tiếp và hạn chế sự xao nhãng so với việc sử dụng ứng dụng trên điện thoại. Đây cũng là yếu tố phù hợp với mục tiêu ban đầu của dự án: tạo ra một thiết bị tối giản, thân thiện và tập trung vào trải nghiệm cá nhân.

---

## 6.4. Architecture and Hardware Value

SmartClock sử dụng các thành phần phần cứng phổ biến như ESP32-6288, TFT Display, 5 nút vật lý, cảm biến ánh sáng và microphone INMP441. Cách lựa chọn linh kiện này giúp sản phẩm có chi phí tiếp cận hợp lý, phù hợp với giai đoạn prototype và vẫn có khả năng mở rộng.

Mô hình Edge-Server giúp SmartClock cân bằng giữa khả năng hoạt động cục bộ và khả năng kết nối thông minh:

* Khi offline, thiết bị vẫn có thể sử dụng các chức năng cơ bản như Pomodoro, báo thức, menu, game và một số màn hình hiển thị.
* Khi online, thiết bị có thể gửi dữ liệu, nhận cấu hình, lưu lịch sử và mở rộng các chức năng phân tích như dashboard giấc ngủ, tổng hợp REM/NREM hoặc gợi ý cá nhân hóa.
* Việc dùng SmartClock làm setup access point tạm thời giúp người dùng cấu hình mạng bằng điện thoại hoặc laptop.
* Việc dùng điện thoại hoặc laptop làm hotspot giúp SmartClock linh hoạt hơn trong môi trường học tập, làm việc hoặc thử nghiệm.

Nhờ đó, SmartClock không bị phụ thuộc hoàn toàn vào hạ tầng mạng cố định nhưng vẫn có nền tảng để phát triển thành một hệ thống AIoT hoàn chỉnh hơn.

---

## 6.5. Limitations

Mặc dù SmartClock đã định hình được các chức năng cốt lõi, dự án vẫn còn một số giới hạn cần được cải thiện trong các phiên bản tiếp theo:

* Các chức năng đánh giá giấc ngủ, ước lượng REM/NREM và luyện tập seminar hiện mới dừng ở mức hỗ trợ cơ bản.
* Kết quả REM/NREM chỉ là ước lượng dựa trên tín hiệu gián tiếp, không thay thế PSG hoặc chẩn đoán y khoa.
* Một số nguồn dữ liệu như gối thông minh FSR, CO2, độ ẩm, nhiệt độ cơ thể hoặc nhịp tim có thể chưa được triển khai đầy đủ trong phiên bản prototype đầu tiên.
* Music Player và Flappy Bird chủ yếu phục vụ trải nghiệm mô phỏng hoặc giải trí nhẹ, chưa phải hệ thống giải trí hoàn chỉnh.
* Việc kết nối Internet thông qua hotspot phụ thuộc vào chất lượng mạng của điện thoại hoặc laptop.
* Cơ chế setup Wi-Fi cần được thiết kế cẩn thận để người dùng nhập thông tin mạng dễ dàng và an toàn.
* Chi phí phần cứng hiện mới là ước lượng cho prototype, có thể thay đổi theo thị trường linh kiện.
* Chưa có phần đánh giá thực nghiệm với người dùng thực tế để đo mức độ cải thiện tập trung hoặc chất lượng sinh hoạt.
* Một số tính năng AIoT vẫn còn tiềm năng mở rộng, chưa được triển khai đầy đủ trong phạm vi tài liệu hiện tại.

Những giới hạn này không làm thay đổi định hướng chính của sản phẩm, nhưng là cơ sở quan trọng để phát triển SmartClock thành một thiết bị hoàn thiện hơn.

---

## 6.6. Future Development

Trong tương lai, SmartClock có thể được mở rộng theo các hướng sau:

* Hoàn thiện thiết kế mạch, vỏ thiết bị và bố trí linh kiện cho phiên bản prototype ổn định hơn.
* Cải thiện thuật toán đánh giá giấc ngủ dựa trên nhiều dữ liệu hơn như ánh sáng, âm thanh, nhiệt độ, CO2, độ ẩm, FSR pillow hoặc thói quen sử dụng.
* Mở rộng module Edge AI để phân tích REM/NREM theo từng cửa sổ thời gian và đồng bộ kết quả lên dashboard.
* Mở rộng Seminar Practice với khả năng phân tích tốc độ nói, độ rõ ràng, ngữ điệu và mức độ tự tin.
* Bổ sung khả năng lưu lịch sử Pomodoro, lịch sử giấc ngủ và kết quả luyện tập.
* Cá nhân hóa giao diện và cấu hình theo từng người dùng.
* Kết nối với các nền tảng AIoT hoặc Smart Home để tăng khả năng tự động hóa.
* Tối ưu cơ chế kết nối Internet, cấu hình Wi-Fi và đồng bộ Edge-Server.
* Nâng cấp trải nghiệm giải trí với nhiều âm thanh thư giãn, nhạc tập trung hoặc trò chơi nhỏ khác.

Các hướng phát triển này sẽ giúp SmartClock không chỉ là một thiết bị hỗ trợ thời gian, mà còn trở thành một trợ lý cá nhân nhỏ gọn cho học tập, làm việc và sinh hoạt hằng ngày.

---

## 6.7. Final Conclusion

SmartClock là một dự án có tính thực tiễn cao, xuất phát từ nhu cầu rất phổ biến trong đời sống hiện đại: duy trì sự tập trung, quản lý thời gian, cải thiện giấc ngủ và tạo không gian cá nhân cân bằng hơn. So với các ứng dụng điện thoại hoặc thiết bị đa chức năng dễ gây xao nhãng, SmartClock hướng đến trải nghiệm tối giản, trực tiếp và tập trung vào những nhu cầu thiết yếu.

Với kiến trúc Edge-Server, khả năng cấu hình mạng qua setup access point, kết nối Internet linh hoạt qua điện thoại hoặc laptop, cùng bộ phần cứng prototype có chi phí hợp lý, SmartClock có nền tảng rõ ràng để tiếp tục phát triển thành một sản phẩm AIoT hoàn chỉnh hơn. Dự án thể hiện sự kết hợp giữa tư duy sản phẩm, thiết kế trải nghiệm người dùng, phần cứng nhúng và khả năng mở rộng công nghệ, phù hợp với định hướng xây dựng các thiết bị thông minh phục vụ đời sống hằng ngày.

> **SmartClock – Tập trung hơn, ngủ sâu hơn, sống thông minh hơn.**

