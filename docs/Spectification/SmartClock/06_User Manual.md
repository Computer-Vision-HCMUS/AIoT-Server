# 06. User Manual

## 6.1. Overview

Tài liệu này hướng dẫn người dùng thao tác với **SomniLearnAI** thông qua màn hình TFT, 5 nút vật lý trên thiết bị Edge và dashboard web. Các chức năng được tổ chức theo 3 nhóm mục tiêu chính:

* **Objective 1 - Hỗ trợ học tập:** Pomodoro Timer và Seminar Practice.
* **Objective 2 - Hỗ trợ giấc ngủ:** Sleep Monitoring Edge AI và hiển thị realtime môi trường xung quanh.
* **Objective 3 - Dashboard quản lý phiên:** xem lại phiên học, phiên ngủ và phiên thuyết trình.

Trên thiết bị Edge, người dùng có thể đi qua các màn hình theo vòng lặp:

```text
HOME -> STUDY -> SLEEP -> STATUS -> HOME
```

Dashboard web được dùng để xem lịch sử dài hạn sau khi thiết bị đồng bộ dữ liệu lên server.

---

## 6.2. Button Layout

| Button | Chức năng chung |
| ------ | --------------- |
| Button 1 | Chuyển sang màn hình hoặc chế độ tiếp theo |
| Button 2 | Mở chức năng chính, lưu cấu hình hoặc quay lại menu |
| Button 3 | Bắt đầu, tạm dừng, tiếp tục hoặc chọn mục |
| Button 4 | Tăng giá trị, xem kết quả hoặc chuyển mục tiếp theo |
| Button 5 | Giảm giá trị, mở cấu hình hoặc chuyển mục trước |

Chức năng cụ thể có thể thay đổi theo màn hình hiện tại. Người dùng nên quan sát phần nhãn nút hiển thị trên màn hình TFT trước khi thao tác.

---

## 6.3. Internet Connection Setup

SomniLearnAI là Edge Device có thể hoạt động cục bộ và có thể kết nối server khi có Internet. Khi không có Wi-Fi cố định, người dùng có thể dùng điện thoại hoặc laptop làm hotspot để thiết bị đồng bộ dữ liệu phiên.

### Connection Model

```text
Phone/Laptop <-> SomniLearnAI_Setup AP
SomniLearnAI Edge Device <-> Wi-Fi/Hotspot <-> Internet <-> SomniLearnAI Server <-> Dashboard
```

### Setup Steps

1. Bật SomniLearnAI.
2. Nếu thiết bị chưa có cấu hình Wi-Fi, thiết bị sẽ bật mạng setup tạm thời, ví dụ **SomniLearnAI_Setup**.
3. Trên điện thoại hoặc laptop, kết nối vào mạng setup này.
4. Mở trang cấu hình của thiết bị.
5. Nhập tên Wi-Fi hoặc hotspot và mật khẩu.
6. Lưu cấu hình và chờ thiết bị kết nối lại.
7. Khi trạng thái Online hiển thị, thiết bị có thể đồng bộ phiên học, phiên ngủ và phiên thuyết trình.

### Online and Offline Usage

| Status | Behavior |
| ------ | -------- |
| Online | Thiết bị đồng bộ dữ liệu phiên lên server; dashboard cập nhật lịch sử và biểu đồ. |
| Offline | Pomodoro và Sleep Monitoring vẫn hoạt động cục bộ; Seminar Practice có thể ghi nhận thời lượng hoặc lưu tạm phiên nhưng chưa chấm điểm đầy đủ. |
| Reconnected | Thiết bị gửi các phiên chưa đồng bộ lên server. |

---

## 6.4. Home Screen

Home Screen hiển thị giờ hiện tại, trạng thái kết nối và lối vào các chế độ chính.

### Main Actions

| Button | Action |
| ------ | ------ |
| Button 1 | Chuyển sang Study Mode |
| Button 2 | Xem trạng thái thiết bị |
| Button 3-5 | Không sử dụng trên Home Screen |

### Expected Result

Người dùng biết thời gian hiện tại, trạng thái Online/Offline và có thể nhanh chóng chuyển sang chế độ cần dùng.

---

## 6.5. Objective 1: Study Mode

Study Mode hỗ trợ người dùng học tập tập trung và luyện tập thuyết trình. Chế độ này gồm 2 chức năng chính:

* Pomodoro Timer.
* Seminar Practice.

Từ Home Screen, nhấn **Button 1** để chuyển sang Study Mode.

### Study Menu

| Button | Action |
| ------ | ------ |
| Button 1 | Chuyển sang Sleep Mode |
| Button 2 | Mở Pomodoro Timer |
| Button 3 | Mở Seminar Practice |
| Button 4 | Xem nhanh số Pomodoro hôm nay |
| Button 5 | Quay lại Home Screen |

---

## 6.6. Pomodoro Timer

Pomodoro Timer giúp người dùng chia thời gian học thành các phiên tập trung và nghỉ ngơi. Cấu hình mặc định có thể là 25 phút học và 5 phút nghỉ, nhưng người dùng có thể điều chỉnh theo nhu cầu.

Màn hình Pomodoro phải hiển thị:

* Giờ hiện tại.
* Trạng thái Study hoặc Break.
* Thời gian còn lại theo realtime.
* Số Pomodoro đã hoàn thành trong ngày.

### How To Use

1. Vào **Study Mode**.
2. Nhấn **Button 2** để mở **Pomodoro Timer**.
3. Nhấn **Button 3** để bắt đầu hoặc tạm dừng bộ đếm.
4. Nhấn **Button 4** để reset phiên hiện tại.
5. Nhấn **Button 5** để mở cấu hình thời gian.
6. Khi phiên kết thúc, xem thông báo trên màn hình và chờ thiết bị lưu phiên học.

### Pomodoro Configuration

| Button | Action |
| ------ | ------ |
| Button 2 | Lưu cấu hình và quay lại Pomodoro Timer |
| Button 3 | Chọn trường cần chỉnh: Study Time hoặc Break Time |
| Button 4 | Tăng giá trị thêm 1 phút |
| Button 5 | Giảm giá trị 1 phút |

### Expected Result

Người dùng hoàn thành phiên học có cấu trúc, biết số Pomodoro trong ngày và có dữ liệu để xem lại trên dashboard.

---

## 6.7. Seminar Practice

Seminar Practice hỗ trợ người dùng luyện tập thuyết trình và quản lý thời lượng trình bày. Điểm đánh giá đầy đủ cần Wi-Fi và Server; nếu thiết bị offline, phiên luyện tập có thể được lưu tạm và chấm điểm sau khi đồng bộ.

### How To Use

1. Vào **Study Mode**.
2. Nhấn **Button 3** để mở **Seminar Practice**.
3. Nhấn **Button 5** để cấu hình thời lượng mục tiêu nếu cần.
4. Nhấn **Button 3** để bắt đầu ghi nhận phần trình bày.
5. Trình bày bài nói trước thiết bị.
6. Nhấn **Button 3** lần nữa để kết thúc phiên.
7. Nhấn **Button 4** để xem trạng thái chấm điểm, điểm số và nhận xét nếu phiên đã được Server xử lý.
8. Nhấn **Button 2** để quay lại Study Menu.

### Evaluation Information

Khi thiết bị online và Server xử lý xong, kết quả đánh giá có thể bao gồm:

* Thời lượng trình bày.
* Tốc độ nói ước tính.
* Độ rõ ràng.
* Điểm tổng quan của phiên thuyết trình.
* Nhận xét ngắn để cải thiện lần nói tiếp theo.

### Expected Result

Người dùng ghi nhận được phiên luyện tập trên thiết bị và xem điểm số trên dashboard sau khi dữ liệu được Server chấm điểm.

---

## 6.8. Objective 2: Sleep Mode

Sleep Mode hỗ trợ người dùng quan sát giấc ngủ và môi trường phòng ngủ. Chế độ này tập trung vào **Sleep Monitoring Edge AI** và báo cáo chất lượng ngủ sau mỗi phiên.

Từ Study Mode, nhấn **Button 1** để chuyển sang Sleep Mode.

### Sleep Menu

| Button | Action |
| ------ | ------ |
| Button 1 | Chuyển sang Status Screen |
| Button 2 | Bắt đầu hoặc dừng Sleep Monitoring |
| Button 3 | Xem realtime môi trường xung quanh |
| Button 4 | Xem báo cáo phiên ngủ gần nhất |
| Button 5 | Quay lại Study Mode |

---

## 6.9. Sleep Monitoring Edge AI

Sleep Monitoring ghi nhận thời gian ngủ và dữ liệu môi trường xung quanh. Khi module Edge AI được bật, SomniLearnAI có thể kết hợp dữ liệu âm thanh, ánh sáng, nhiệt độ, độ ẩm, CO2 hoặc dữ liệu cảm biến liên quan để đánh giá chất lượng giấc ngủ.

Kết quả chỉ mang tính hỗ trợ theo dõi thói quen nghỉ ngơi, không phải kết luận y khoa.

### Realtime Environment Display

Màn hình realtime có thể hiển thị:

* Giờ hiện tại.
* Mức ánh sáng.
* Mức tiếng ồn.
* Nhiệt độ phòng nếu có cảm biến.
* Độ ẩm hoặc CO2 nếu có cảm biến.
* Cảnh báo ngắn khi môi trường có khả năng ảnh hưởng xấu đến giấc ngủ.

### How To Use

1. Vào **Sleep Mode**.
2. Nhấn **Button 3** để xem nhanh môi trường xung quanh trước khi ngủ.
3. Nhấn **Button 2** để bắt đầu theo dõi giấc ngủ.
4. Đặt thiết bị ở vị trí ổn định trong phòng.
5. Sau khi thức dậy, nhấn **Button 2** để dừng theo dõi.
6. Xem báo cáo chất lượng ngủ trên màn hình.
7. Khi có Internet, thiết bị đồng bộ phiên ngủ lên dashboard.

### Sleep Report Information

Báo cáo sau phiên ngủ có thể bao gồm:

* Tổng thời lượng ngủ.
* Điểm đánh giá chất lượng giấc ngủ.
* Nhận xét về ánh sáng, tiếng ồn, nhiệt độ, CO2 hoặc độ ẩm.
* Tác nhân có khả năng làm giấc ngủ không ngon.
* Gợi ý cải thiện cho lần ngủ tiếp theo.

### Expected Result

Người dùng biết chất lượng giấc ngủ và các yếu tố môi trường cần điều chỉnh.

---

## 6.10. Status Screen

Status Screen hiển thị trạng thái kết nối và đồng bộ dữ liệu.

### Status Information

| Information | Description |
| ----------- | ----------- |
| Wi-Fi status | Online hoặc Offline |
| Server sync | Trạng thái đồng bộ dữ liệu |
| Unsynced sessions | Số phiên chưa đồng bộ |
| Device time | Giờ hiện tại của thiết bị |

### Main Actions

| Button | Action |
| ------ | ------ |
| Button 1 | Quay về Home Screen |
| Button 2 | Thử đồng bộ lại |
| Button 3 | Xem số phiên chưa đồng bộ |
| Button 4 | Xem thông tin Wi-Fi |
| Button 5 | Quay lại Sleep Mode |

---

## 6.11. Objective 3: Dashboard

Dashboard là giao diện web dùng để xem lại dữ liệu đã đồng bộ từ SomniLearnAI. Người dùng truy cập dashboard bằng trình duyệt trên điện thoại hoặc laptop.

### Dashboard Main Tabs

| Tab | Purpose |
| --- | ------- |
| Overview | Xem tổng quan học tập, giấc ngủ và thuyết trình |
| Study Sessions | Xem số Pomodoro hôm nay và lịch sử phiên học |
| Sleep Sessions | Xem giấc ngủ theo tháng và tổng kết cuối tháng |
| Presentation Sessions | Xem điểm và danh sách các lần luyện nói |

---

## 6.12. Study Sessions Dashboard

### How To Use

1. Mở dashboard trên trình duyệt.
2. Chọn tab **Study Sessions**.
3. Xem số Pomodoro hoàn thành trong ngày.
4. Xem tổng phút học và danh sách phiên học.
5. Dùng bộ lọc ngày hoặc tháng nếu cần.

### Expected Result

Người dùng biết hôm đó đã học bao nhiêu Pomodoro và có thể theo dõi xu hướng học tập.

---

## 6.13. Sleep Sessions Dashboard

### How To Use

1. Mở dashboard trên trình duyệt.
2. Chọn tab **Sleep Sessions**.
3. Chọn tháng cần xem.
4. Xem biểu đồ thời lượng ngủ, điểm ngủ và tác nhân ảnh hưởng.
5. Xem phần tổng kết cuối tháng.

### Expected Result

Người dùng biết chất lượng giấc ngủ theo tháng và nhận được gợi ý cải thiện.

---

## 6.14. Presentation Sessions Dashboard

### How To Use

1. Mở dashboard trên trình duyệt.
2. Chọn tab **Presentation Sessions**.
3. Xem danh sách các lần luyện thuyết trình.
4. Xem điểm số, thời lượng và nhận xét từng phiên.
5. Quan sát biểu đồ xu hướng điểm số nếu có.

### Expected Result

Người dùng theo dõi được tiến bộ thuyết trình qua từng lần luyện tập.

---

## 6.15. Notes

* Trước khi sử dụng, cần đảm bảo SomniLearnAI đã được cấp nguồn và màn hình hiển thị bình thường.
* Khi đang cấu hình thời gian Pomodoro, nên kiểm tra kỹ giá trị trước khi lưu.
* Đánh giá giấc ngủ trên Edge Device mang tính hỗ trợ, có thể được mở rộng ở các phiên bản tiếp theo.
* Chấm điểm thuyết trình cần Wi-Fi và Server; khi offline, thiết bị chỉ lưu tạm phiên hoặc ghi nhận thời lượng.
* Khi dùng Sleep Monitoring, nên đặt thiết bị ở vị trí ổn định và hạn chế nguồn tiếng ồn hoặc ánh sáng bất thường.
* Kết quả giấc ngủ không thay thế thiết bị y tế hoặc phân tích chuyên nghiệp.
* Nếu thiết bị Offline, dữ liệu phiên vẫn có thể được lưu tạm và đồng bộ sau khi có Internet.
