# 01. Background

## 1.1. Product Overview

Trong môi trường học tập hiện đại, khả năng tập trung đang trở thành một trong những yếu tố quan trọng quyết định hiệu quả học tập, chất lượng làm việc và thói quen sinh hoạt cá nhân. Đặc biệt đối với sinh viên, việc duy trì sự tập trung trong thời gian dài ngày càng khó khăn bởi sự xuất hiện liên tục của điện thoại thông minh, mạng xã hội, tin nhắn và các nội dung gây xao nhãng.

Một trong những phương pháp quản lý thời gian phổ biến và hiệu quả hiện nay là phương pháp Pomodoro [1]. Phương pháp này chia thời gian học hoặc làm việc thành các khoảng tập trung ngắn, thường là 25 phút tập trung và 5 phút nghỉ, nhằm giúp người dùng duy trì nhịp học ổn định hơn. Tuy nhiên, phần lớn sản phẩm Pomodoro hiện tại chỉ dừng lại ở chức năng đếm thời gian, chưa ghi nhận dữ liệu học tập dài hạn và chưa hỗ trợ các nhu cầu liên quan như luyện tập thuyết trình hoặc cải thiện giấc ngủ.

Xuất phát từ nhu cầu đó, nhóm phát triển **SomniLearnAI**, một thiết bị đồng hồ thông minh AIoT đặt tại bàn học hoặc phòng ngủ. Sản phẩm kết hợp giữa thiết bị Edge, cảm biến, màn hình hiển thị realtime và dashboard web để hỗ trợ 3 nhóm nhu cầu chính:

* Học tập tập trung hơn theo phương pháp Pomodoro.
* Luyện tập thuyết trình và nhận điểm đánh giá sau mỗi phiên.
* Quan sát giấc ngủ, đặt báo thức, phát hiện tác nhân môi trường ảnh hưởng đến giấc ngủ và xem lại lịch sử trên dashboard.

SomniLearnAI không được định hướng như một thiết bị giải trí đa năng. Thay vào đó, sản phẩm tập trung vào vai trò trợ lý học tập và giấc ngủ nhỏ gọn, giúp người dùng xây dựng thói quen tốt hơn dựa trên dữ liệu.

**Slogan sản phẩm:**

> **SomniLearnAI - Learn better, sleep smarter, improve with data.**

---

## 1.2. Motivation

Động lực phát triển SomniLearnAI đến từ nhu cầu tạo ra một thiết bị chuyên biệt cho học tập và sinh hoạt cá nhân, hạn chế sự phụ thuộc vào điện thoại thông minh. Người dùng có thể dùng điện thoại để đặt Pomodoro hoặc ghi chú lịch học, nhưng điện thoại cũng là nguồn gây mất tập trung lớn nhất do thông báo, mạng xã hội và các ứng dụng giải trí.

Bên cạnh đó, sinh viên thường không chỉ cần học tập trung mà còn cần luyện tập thuyết trình, trình bày seminar và duy trì giấc ngủ ổn định. Các hoạt động này có liên hệ chặt chẽ với nhau: học tập thiếu tập trung làm giảm hiệu quả ôn luyện, thuyết trình thiếu luyện tập làm giảm sự tự tin, còn giấc ngủ kém khiến khả năng tập trung ngày hôm sau suy giảm.

SomniLearnAI được đề xuất như một thiết bị AIoT có mặt trực tiếp trong không gian học tập và nghỉ ngơi. Thiết bị hiển thị giờ hiện tại, thời gian Pomodoro, trạng thái phiên học, báo thức và môi trường phòng ngủ theo realtime. Khi có Internet, dữ liệu phiên được đồng bộ lên dashboard để người dùng xem lại số Pomodoro, điểm thuyết trình và chất lượng giấc ngủ theo ngày hoặc tháng.

Ngoài giá trị học thuật, dự án còn giúp nhóm tiếp cận quy trình phát triển một sản phẩm công nghệ hoàn chỉnh, từ nghiên cứu ý tưởng, thiết kế phần cứng, lập trình nhúng, xử lý dữ liệu cảm biến cho đến xây dựng dashboard. Đây là cơ hội để kết hợp tư duy sản phẩm, AIoT, Edge AI và trải nghiệm người dùng vào một prototype có tính ứng dụng thực tế.

---

## 1.3. Inspiration: EMO Desktop AIoT Companion

Một nguồn cảm hứng quan trọng cho SomniLearnAI là các thiết bị AIoT companion để bàn như **EMO**. EMO cho thấy một thiết bị nhỏ gọn đặt trên bàn có thể tạo cảm giác thân thiện, dễ tiếp cận và gắn bó hơn so với các ứng dụng thuần phần mềm.

![EMO desktop AIoT companion](images/emo.jpg)

Từ góc nhìn thiết kế sản phẩm, EMO gợi ý một số hướng đáng học hỏi:

* **Hiện diện vật lý trên bàn học:** thiết bị luôn nằm trong tầm nhìn của người dùng mà không cần mở điện thoại.
* **Giao diện cảm xúc và trực quan:** màn hình nhỏ có thể truyền tải trạng thái hệ thống một cách nhanh, thân thiện và dễ hiểu.
* **Tương tác tối giản:** người dùng thao tác trực tiếp với thiết bị thay vì đi qua nhiều lớp ứng dụng.
* **Cảm giác companion:** thiết bị không chỉ là công cụ đo đếm, mà còn là một vật thể công nghệ gần gũi trong không gian cá nhân.

SomniLearnAI lấy cảm hứng từ tinh thần này, nhưng định hướng chức năng khác EMO. Thay vì tập trung vào tương tác companion hoặc giải trí, SomniLearnAI tập trung vào học tập, luyện thuyết trình, quan sát giấc ngủ và dashboard dữ liệu dài hạn.

---

## 1.4. Intended Audience

SomniLearnAI hướng đến các nhóm người dùng có nhu cầu nâng cao khả năng tập trung, cải thiện kỹ năng trình bày và theo dõi thói quen nghỉ ngơi cá nhân, bao gồm:

* Sinh viên cần cải thiện khả năng tập trung khi học tập và ôn luyện.
* Sinh viên thường xuyên phải thuyết trình seminar, báo cáo môn học hoặc pitching ý tưởng.
* Người làm việc tại nhà cần duy trì phiên làm việc tập trung và hạn chế xao nhãng.
* Người muốn quan sát chất lượng giấc ngủ và các tác nhân môi trường ảnh hưởng đến giấc ngủ.
* Người yêu thích các thiết bị AIoT nhỏ gọn, có màn hình trực quan và có thể đặt trên bàn học hoặc đầu giường.

---

## 1.5. Similar Products and Comparison

Hiện nay có nhiều sản phẩm và giải pháp liên quan đến quản lý thời gian, thiết bị companion để bàn, theo dõi sức khỏe hoặc dashboard cá nhân. Tuy nhiên, mỗi nhóm giải pháp vẫn có giới hạn riêng khi đặt trong bối cảnh học tập, thuyết trình và giấc ngủ.

### Smartphone Applications

Các ứng dụng trên điện thoại như Pomodoro Timer, Forest hoặc Focus To-Do mang lại sự tiện lợi do người dùng có thể dễ dàng cài đặt và sử dụng. Tuy nhiên, điện thoại thông minh cũng chính là nguồn gây xao nhãng lớn bởi thông báo từ mạng xã hội, tin nhắn và các ứng dụng giải trí.

Do đó, mặc dù hỗ trợ quản lý thời gian hiệu quả, các ứng dụng này vẫn khó giúp người dùng tách khỏi môi trường gây phân tâm trong thời gian học.

---

### Smart Watches

Các thiết bị như Apple Watch hoặc Samsung Galaxy Watch hỗ trợ theo dõi sức khỏe, nhắc nhở công việc và quản lý thời gian khá hiệu quả. Một số thiết bị còn có khả năng theo dõi giấc ngủ và hiển thị dữ liệu sức khỏe theo ngày.

Tuy nhiên, smartwatch thường là thiết bị đeo đa chức năng, có mức giá cao và vẫn tích hợp nhiều thông báo có thể gây phân tâm. Bên cạnh đó, smartwatch không tối ưu cho bối cảnh đặt tại bàn học để hiển thị Pomodoro, điểm thuyết trình hoặc môi trường phòng ngủ theo realtime.

---

### Traditional Pomodoro Clocks

Các đồng hồ Pomodoro truyền thống có ưu điểm là đơn giản, dễ sử dụng và giúp hạn chế sự phụ thuộc vào điện thoại. Tuy nhiên, phần lớn sản phẩm chỉ có chức năng đếm thời gian cơ bản.

Nhóm sản phẩm này thường thiếu khả năng lưu lịch sử phiên học, thiếu liên kết với giấc ngủ, không hỗ trợ luyện tập thuyết trình và không có dashboard để quan sát tiến độ dài hạn.

---

### Desktop AIoT Companion Devices

Các thiết bị companion để bàn như EMO tạo ra trải nghiệm thân thiện nhờ hình dáng nhỏ gọn, màn hình biểu cảm và cảm giác hiện diện trong không gian cá nhân. Đây là nhóm sản phẩm truyền cảm hứng cho SomniLearnAI về mặt form factor và trải nghiệm tương tác trực tiếp.

Tuy nhiên, companion devices thường tập trung vào tương tác cảm xúc, giải trí nhẹ hoặc vai trò trợ lý để bàn. SomniLearnAI khác ở chỗ sản phẩm được thiết kế xoay quanh các phiên dữ liệu cụ thể: phiên Pomodoro, phiên luyện thuyết trình và phiên ngủ.

---

### Sleep Tracking Applications and Devices

Các ứng dụng hoặc thiết bị theo dõi giấc ngủ giúp người dùng xem thời lượng ngủ, điểm ngủ hoặc một số chỉ số sức khỏe. Tuy nhiên, nhiều giải pháp phụ thuộc vào điện thoại, đồng hồ đeo tay hoặc hệ sinh thái đóng.

SomniLearnAI hướng đến cách tiếp cận khác: đặt thiết bị trong phòng ngủ, đọc dữ liệu môi trường xung quanh và hiển thị realtime các yếu tố có thể ảnh hưởng đến giấc ngủ như ánh sáng, tiếng ồn, nhiệt độ, độ ẩm hoặc CO2 nếu có cảm biến mở rộng.

---

### SomniLearnAI Advantages

So với các sản phẩm hiện có, SomniLearnAI được định hướng là một thiết bị cân bằng giữa tính tối giản, tính thông minh và khả năng theo dõi dữ liệu dài hạn:

* Hỗ trợ Pomodoro ngay trên thiết bị vật lý để giảm phụ thuộc vào điện thoại.
* Hiển thị giờ hiện tại, thời gian còn lại và trạng thái phiên học theo realtime.
* Hỗ trợ luyện tập thuyết trình và ghi nhận điểm sau mỗi phiên.
* Quan sát giấc ngủ bằng Edge AI, đặt báo thức và phát hiện tác nhân môi trường làm giấc ngủ không ngon.
* Đồng bộ dữ liệu lên dashboard để xem số Pomodoro, tổng kết giấc ngủ theo tháng và danh sách điểm thuyết trình.
* Có form factor nhỏ gọn, thân thiện, lấy cảm hứng từ các thiết bị AIoT companion để bàn như EMO.
