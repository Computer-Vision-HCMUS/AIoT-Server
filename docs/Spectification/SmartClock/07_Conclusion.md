# 07. Conclusion

## 7.1. Project Summary

SomniLearnAI được xây dựng với định hướng trở thành một đồng hồ thông minh AIoT hỗ trợ học tập, luyện tập thuyết trình, quan sát giấc ngủ, đặt báo thức và quản lý lịch sử phiên cá nhân. So với định hướng SmartClock ban đầu, phiên bản đặc tả mới tập trung rõ hơn vào dữ liệu học tập và sức khỏe sinh hoạt thay vì các chức năng giải trí.

Về kiến trúc, SomniLearnAI vẫn sử dụng mô hình **Edge Device <-> Server**. Thiết bị Edge đảm nhiệm tương tác trực tiếp với người dùng, đọc dữ liệu cảm biến, hiển thị giờ và trạng thái realtime trên màn hình TFT. Server và dashboard đảm nhiệm lưu trữ, tổng hợp và hiển thị lịch sử các phiên học, phiên ngủ và phiên thuyết trình.

Ba nhóm mục tiêu chính của sản phẩm gồm:

* Hỗ trợ cải thiện khả năng tập trung khi học theo Pomodoro và luyện tập thuyết trình có chấm điểm.
* Hỗ trợ cải thiện giấc ngủ thông qua Sleep Monitoring Edge AI, báo thức cục bộ và phát hiện tác nhân môi trường ảnh hưởng đến giấc ngủ.
* Cung cấp dashboard quản lý phiên học, phiên ngủ và phiên thuyết trình để người dùng theo dõi tiến bộ dài hạn.

---

## 7.2. Mục tiêu muốn đạt được

### Objective 1: Supporting Study Focus and Presentation Practice

SomniLearnAI hỗ trợ người dùng học tập tập trung hơn thông qua Pomodoro Timer. Thiết bị hiển thị giờ hiện tại, trạng thái phiên học, thời gian còn lại và số Pomodoro đã hoàn thành. Cách tiếp cận này giúp người dùng quản lý thời gian học mà không cần phụ thuộc vào điện thoại.

Bên cạnh đó, Seminar Practice giúp người dùng luyện tập thuyết trình và ghi nhận thời lượng nói trên thiết bị. Điểm đánh giá thuyết trình được xử lý bởi Server khi có Wi-Fi, sau đó hiển thị trên dashboard để người dùng xem lại danh sách các lần nói và theo dõi xu hướng cải thiện.

### Objective 2: Supporting Better Sleep with Edge AI

SomniLearnAI hỗ trợ quan sát giấc ngủ bằng cách ghi nhận thời gian ngủ, dữ liệu âm thanh, ánh sáng và các chỉ số môi trường xung quanh. Trước khi ngủ, người dùng có thể đặt báo thức trực tiếp trên thiết bị để thức dậy đúng giờ mà không cần phụ thuộc vào điện thoại hoặc Internet. Trong quá trình sử dụng, thiết bị có thể hiển thị realtime môi trường phòng ngủ để người dùng nhận biết sớm các điều kiện chưa phù hợp.

Sau khi phiên ngủ kết thúc, Edge AI đánh giá chất lượng giấc ngủ, tạo điểm số và phát hiện các tác nhân có khả năng làm giấc ngủ không ngon như phòng quá sáng, tiếng ồn cao, nhiệt độ hoặc độ ẩm chưa phù hợp. Kết quả này giúp người dùng điều chỉnh môi trường ngủ trong các lần tiếp theo.

### Objective 3: Supporting Session Management Dashboard

Dashboard là thành phần giúp SomniLearnAI mở rộng từ một thiết bị Edge thành một hệ thống AIoT có khả năng theo dõi dài hạn. Người dùng có thể xem hôm đó đã học bao nhiêu Pomodoro, quan sát giấc ngủ theo tháng và xem danh sách điểm các lần luyện thuyết trình.

Việc bổ sung dashboard giúp dữ liệu không chỉ dừng ở màn hình thiết bị tại thời điểm sử dụng, mà còn trở thành lịch sử có thể phân tích, so sánh và tổng kết.

---

## 7.3. User Experience

SomniLearnAI được thiết kế với luồng sử dụng đơn giản trên thiết bị:

```text
HOME -> STUDY -> SLEEP -> STATUS -> HOME
```

Mỗi màn hình phục vụ một nhu cầu cụ thể:

* **HOME:** xem giờ hiện tại, trạng thái kết nối và điểm bắt đầu hệ thống.
* **STUDY:** sử dụng Pomodoro Timer và Seminar Practice.
* **SLEEP:** quan sát giấc ngủ, đặt báo thức, xem realtime môi trường và báo cáo giấc ngủ.
* **STATUS:** kiểm tra kết nối, số phiên chưa đồng bộ và trạng thái server.

Dashboard web bổ sung trải nghiệm xem lại dữ liệu dài hạn:

* **Study Sessions:** theo dõi số Pomodoro và tổng thời gian học.
* **Sleep Sessions:** theo dõi giấc ngủ theo tháng và tổng kết cuối tháng.
* **Presentation Sessions:** theo dõi điểm và danh sách các lần luyện nói.

---

## 7.4. Architecture and Hardware Value

SomniLearnAI tận dụng các thành phần phần cứng phổ biến như ESP32, màn hình TFT, nút vật lý, microphone, cảm biến ánh sáng và các cảm biến môi trường có thể mở rộng. Cách lựa chọn này phù hợp với giai đoạn prototype, đồng thời vẫn đủ nền tảng để triển khai các chức năng AIoT.

Mô hình Edge-Server mang lại các giá trị chính:

* Khi offline, thiết bị vẫn có thể chạy Pomodoro, đặt báo thức và Sleep Monitoring; Seminar Practice có thể ghi nhận phiên nhưng chưa chấm điểm đầy đủ.
* Khi online, thiết bị có thể đồng bộ dữ liệu phiên lên server.
* Dashboard giúp người dùng xem lại dữ liệu học tập, giấc ngủ và thuyết trình theo thời gian.
* Edge AI giúp xử lý một phần dữ liệu ngay trên thiết bị, giảm phụ thuộc vào server trong các tác vụ quan sát cơ bản.

---

## 7.5. Limitations

Dự án vẫn còn một số giới hạn cần được cải thiện trong các phiên bản tiếp theo:

* Điểm thuyết trình phụ thuộc Wi-Fi và Server; khi offline, kết quả có thể ở trạng thái chờ xử lý.
* Đánh giá giấc ngủ từ cảm biến môi trường chỉ mang tính hỗ trợ, không thay thế thiết bị y tế.
* Báo thức phụ thuộc vào thời gian hệ thống của Edge Device, vì vậy cần đảm bảo đồng hồ thiết bị được thiết lập hoặc đồng bộ chính xác.
* Một số cảm biến như CO2, độ ẩm hoặc nhiệt độ có thể chưa được triển khai đầy đủ trong prototype đầu tiên.
* Dashboard phụ thuộc vào khả năng đồng bộ dữ liệu qua Internet.
* Cơ chế lưu tạm khi offline cần được kiểm thử kỹ để tránh mất dữ liệu phiên.
* Chưa có đánh giá thực nghiệm với nhiều người dùng để chứng minh mức cải thiện tập trung hoặc chất lượng giấc ngủ.

---

## 7.6. Future Development

Trong tương lai, SomniLearnAI có thể được mở rộng theo các hướng sau:

* Cải thiện dịch vụ chấm điểm thuyết trình trên Server dựa trên tốc độ nói, độ rõ ràng, ngữ điệu và độ ổn định.
* Cải thiện mô hình Sleep Monitoring bằng cách kết hợp thêm nhiều cảm biến môi trường.
* Bổ sung tùy chọn báo thức nâng cao như lặp theo ngày, âm báo khác nhau hoặc báo thức thông minh dựa trên trạng thái ngủ.
* Bổ sung báo cáo học tập theo tuần, tháng và mục tiêu cá nhân.
* Bổ sung tổng kết giấc ngủ cuối tháng với gợi ý cá nhân hóa hơn.
* Tối ưu dashboard để so sánh xu hướng giữa phiên học, phiên ngủ và hiệu suất thuyết trình.
* Hoàn thiện cơ chế đồng bộ offline-first giữa Edge Device và server.
* Cải thiện thiết kế vỏ, bố trí nút và trải nghiệm hiển thị trên màn hình TFT.
* Bổ sung xác thực người dùng và bảo vệ dữ liệu cá nhân trên dashboard.

---

## 7.7. Final Conclusion

SomniLearnAI là phiên bản đặc tả có định hướng rõ ràng hơn cho một thiết bị đồng hồ thông minh AIoT phục vụ học tập và sinh hoạt cá nhân. Sản phẩm kết hợp Pomodoro, luyện tập thuyết trình, báo thức, quan sát giấc ngủ Edge AI và dashboard quản lý phiên để giúp người dùng không chỉ thực hiện hoạt động hằng ngày tốt hơn, mà còn nhìn lại tiến bộ của mình qua dữ liệu.

Với kiến trúc Edge-Server, khả năng hoạt động cục bộ, đồng bộ Internet và dashboard phân tích dài hạn, SomniLearnAI có nền tảng phù hợp để tiếp tục phát triển thành một trợ lý học tập và giấc ngủ nhỏ gọn, dễ sử dụng và có giá trị thực tiễn.

> **SomniLearnAI - Learn better, sleep smarter, improve with data.**
