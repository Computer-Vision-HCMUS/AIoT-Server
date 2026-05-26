# 04. User Manual

## 4.1. Overview

Tài liệu này hướng dẫn người dùng thao tác với SmartClock thông qua màn hình TFT và 5 nút vật lý. Các chức năng được tổ chức theo 3 nhóm mục tiêu chính:

* **Objective 1 - Hỗ trợ tập trung:** Pomodoro Timer và Seminar Practice.
* **Objective 2 - Hỗ trợ giấc ngủ:** Theo dõi chất lượng ngủ và đặt báo thức.
* **Objective 3 - Giải trí và trang trí:** Flappy Bird và Music Player.

SmartClock sử dụng một nút chuyển chế độ và các nút hành động theo từng màn hình. Người dùng có thể đi qua các chế độ theo vòng lặp:

```text
HOME → STUDY → SLEEP → RELAX → HOME
```

---

## 4.2. Button Layout

| Button | Chức năng chung |
| ------ | --------------- |
| Button 1 | Chuyển sang chế độ tiếp theo |
| Button 2 | Mở chức năng chính hoặc quay lại menu |
| Button 3 | Thực hiện hành động phụ như bắt đầu, tạm dừng hoặc chọn mục |
| Button 4 | Tăng giá trị, chuyển bài hoặc mở chức năng bổ sung |
| Button 5 | Giảm giá trị, quay bài hoặc mở cấu hình tùy theo màn hình |

Chức năng cụ thể của từng nút có thể thay đổi theo màn hình hiện tại. Người dùng nên quan sát phần hướng dẫn hiển thị trên màn hình hoặc giao diện mô phỏng để biết thao tác phù hợp.

---

## 4.3. Internet Connection Setup

SmartClock là Edge Device có thể hoạt động cục bộ và có thể kết nối Server khi có Internet. Trong trường hợp không có Wi-Fi cố định, người dùng có thể dùng điện thoại hoặc laptop làm điểm phát Wi-Fi để SmartClock truy cập Internet.

### Connection Model

```text
Phone/Laptop ↔ SmartClock_Setup AP
SmartClock Edge Device ↔ Phone/Laptop Hotspot ↔ Internet ↔ SmartClock Server
```

### Step 1: Open SmartClock Setup Network

1. Bật SmartClock.
2. Nếu thiết bị chưa có cấu hình Wi-Fi, SmartClock sẽ bật mạng setup tạm thời, ví dụ **SmartClock_Setup**.
3. Trên điện thoại hoặc laptop, mở danh sách Wi-Fi.
4. Kết nối vào mạng **SmartClock_Setup**.
5. Mở trang cấu hình của SmartClock nếu thiết bị yêu cầu.
6. Nhập tên Wi-Fi và mật khẩu mạng sẽ dùng cho SmartClock.
7. Lưu cấu hình và chờ SmartClock khởi động lại kết nối.

### Step 2 Option A: Connect Through Phone Hotspot

1. Mở phần cài đặt mạng trên điện thoại.
2. Bật **Personal Hotspot** hoặc **Mobile Hotspot**.
3. Đặt tên Wi-Fi và mật khẩu dễ nhận biết.
4. Nhập tên hotspot và mật khẩu này vào trang cấu hình SmartClock.
5. Chờ thiết bị kết nối.
6. Khi kết nối thành công, SmartClock có thể gửi dữ liệu hoặc nhận cấu hình từ Server.

### Step 2 Option B: Connect Through Laptop Hotspot

1. Kết nối laptop với Internet.
2. Bật tính năng **Mobile Hotspot** hoặc **Internet Sharing** trên laptop.
3. Kiểm tra tên Wi-Fi và mật khẩu hotspot.
4. Nhập tên hotspot và mật khẩu này vào trang cấu hình SmartClock.
5. Chờ trạng thái kết nối thành công.

### Online and Offline Usage

| Status | Behavior |
| ------ | -------- |
| Online | SmartClock có thể đồng bộ cấu hình, gửi dữ liệu theo dõi và mở rộng các chức năng phân tích qua Server. |
| Offline | Pomodoro, báo thức, điều hướng menu, Flappy Bird và một số chức năng cục bộ vẫn có thể hoạt động. |

### Notes

* Nên đặt điện thoại hoặc laptop gần SmartClock để tín hiệu Wi-Fi ổn định.
* Nếu kết nối thất bại, kiểm tra lại mật khẩu hotspot và khoảng cách giữa thiết bị.
* Khi dùng hotspot điện thoại, cần đảm bảo điện thoại còn pin và có kết nối dữ liệu di động.
* Một số chức năng phân tích hoặc lưu lịch sử có thể cần Internet để hoạt động đầy đủ.

---

## 4.4. Home Screen

Màn hình Home hiển thị tổng quan các nhóm chức năng của SmartClock. Đây là điểm bắt đầu khi thiết bị được bật.

### Main Actions

| Button | Action |
| ------ | ------ |
| Button 1 | Chuyển sang chế độ STUDY |
| Button 2-5 | Không sử dụng trên màn hình Home |

### Expected Result

Người dùng có thể nhanh chóng chuyển sang nhóm chức năng cần sử dụng mà không phải thao tác qua nhiều lớp menu phức tạp.

---

## 4.5. Objective 1: Study Mode

Study Mode hỗ trợ người dùng học tập và làm việc tập trung hơn. Chế độ này gồm 2 chức năng chính:

* Pomodoro Timer.
* Seminar Practice.

Từ Home Screen, nhấn **Button 1** để chuyển sang Study Mode.

### Study Menu

| Button | Action |
| ------ | ------ |
| Button 1 | Chuyển sang Sleep Mode |
| Button 2 | Mở Pomodoro Timer |
| Button 3 | Mở Seminar Practice |

---

## 4.6. Pomodoro Timer

Pomodoro Timer giúp người dùng chia thời gian làm việc thành các phiên tập trung và nghỉ ngơi. Cấu hình mặc định là 25 phút tập trung và 5 phút nghỉ, nhưng người dùng có thể điều chỉnh theo nhu cầu cá nhân.

### How To Use

1. Vào **Study Mode**.
2. Nhấn **Button 2** để mở **Pomodoro Timer**.
3. Nhấn **Button 3** để bắt đầu hoặc tạm dừng bộ đếm.
4. Nhấn **Button 4** để reset bộ đếm về thời gian ban đầu.
5. Nhấn **Button 5** để mở màn hình cấu hình thời gian.

### Pomodoro Configuration

| Button | Action |
| ------ | ------ |
| Button 2 | Lưu cấu hình và quay lại Pomodoro Timer |
| Button 3 | Chọn trường cần chỉnh: Study Time hoặc Break Time |
| Button 4 | Tăng giá trị thêm 1 phút |
| Button 5 | Giảm giá trị 1 phút |

### Expected Result

Khi phiên Pomodoro kết thúc, thiết bị phát tín hiệu thông báo để người dùng chuyển sang nghỉ ngơi hoặc bắt đầu phiên tiếp theo.

---

## 4.7. Seminar Practice

Seminar Practice hỗ trợ người dùng luyện tập thuyết trình, quản lý thời lượng trình bày và nhận đánh giá cơ bản sau khi luyện tập.

### How To Use

1. Vào **Study Mode**.
2. Nhấn **Button 3** để mở **Seminar Practice**.
3. Nhấn **Button 3** để bắt đầu ghi nhận phần trình bày.
4. Nhấn **Button 3** lần nữa để kết thúc phần trình bày.
5. Nhấn **Button 4** để xem đánh giá luyện tập.
6. Nhấn **Button 2** để quay lại Study Menu.

### Evaluation Information

Kết quả đánh giá có thể bao gồm:

* Thời lượng trình bày.
* Tốc độ nói ước tính.
* Độ rõ ràng.
* Mức độ tự tin hoặc chất lượng trình bày cơ bản.

### Expected Result

Người dùng nắm được thời lượng và chất lượng luyện tập để cải thiện kỹ năng thuyết trình trong các lần tiếp theo.

---

## 4.8. Objective 2: Sleep Mode

Sleep Mode hỗ trợ người dùng xây dựng thói quen nghỉ ngơi hợp lý hơn. Chế độ này gồm 2 chức năng chính:

* Theo dõi và đánh giá chất lượng ngủ.
* Đặt báo thức.

Từ Study Mode, nhấn **Button 1** để chuyển sang Sleep Mode.

### Sleep Menu

| Button | Action |
| ------ | ------ |
| Button 1 | Chuyển sang Relax Mode |
| Button 2 | Bắt đầu theo dõi giấc ngủ |
| Button 3 | Mở cài đặt báo thức |
| Button 4 | Mở cấu hình thời lượng ngủ |

---

## 4.9. Sleep Monitoring

Sleep Monitoring ghi nhận thời gian ngủ và tạo đánh giá cơ bản sau khi người dùng kết thúc phiên theo dõi.

### How To Use

1. Vào **Sleep Mode**.
2. Nhấn **Button 2** để bắt đầu theo dõi giấc ngủ.
3. Để thiết bị hoạt động trong suốt thời gian nghỉ ngơi.
4. Sau khi thức dậy, nhấn **Button 2** để dừng theo dõi.
5. Xem báo cáo chất lượng ngủ trên màn hình.
6. Nhấn **Button 2** để xác nhận và quay lại Sleep Menu.

### Expected Result

SmartClock hiển thị điểm đánh giá giấc ngủ, thời lượng nghỉ ngơi và gợi ý giúp người dùng điều chỉnh thói quen sinh hoạt.

---

## 4.10. Alarm Settings

Alarm Settings cho phép người dùng bật, tắt và cấu hình báo thức.

### How To Use

1. Vào **Sleep Mode**.
2. Nhấn **Button 3** để mở **Alarm Settings**.
3. Nhấn **Button 3** để bật hoặc tắt báo thức.
4. Nhấn **Button 4** để mở màn hình chỉnh thời lượng ngủ và giờ báo thức.
5. Nhấn **Button 2** để lưu cài đặt và quay lại Sleep Menu.

### Sleep Duration / Alarm Configuration

| Button | Action |
| ------ | ------ |
| Button 2 | Lưu cấu hình và quay lại Alarm Settings |
| Button 3 | Chọn trường cần chỉnh: Sleep Duration hoặc Alarm Hour |
| Button 4 | Tăng giá trị |
| Button 5 | Giảm giá trị |

### Expected Result

Khi đến giờ đã cài đặt, SmartClock phát âm thanh báo thức để nhắc người dùng thức dậy đúng giờ.

---

## 4.11. Objective 3: Relax Mode

Relax Mode hỗ trợ người dùng giải trí nhẹ nhàng trong thời gian nghỉ và tăng tính sinh động cho góc học tập hoặc làm việc. Chế độ này gồm 2 chức năng chính:

* Flappy Bird.
* Music Player.

Từ Sleep Mode, nhấn **Button 1** để chuyển sang Relax Mode.

### Relax Menu

| Button | Action |
| ------ | ------ |
| Button 1 | Chuyển về Home Screen |
| Button 2 | Mở Flappy Bird |
| Button 3 | Mở Music Player |

---

## 4.12. Flappy Bird

Flappy Bird là trò chơi mini giúp người dùng giải trí ngắn trong thời gian nghỉ.

### How To Use

1. Vào **Relax Mode**.
2. Nhấn **Button 2** để mở **Flappy Bird**.
3. Nhấn **Button 3** để điều khiển nhân vật nhảy.
4. Trò chơi kết thúc khi nhân vật va chạm hoặc rơi khỏi vùng chơi.
5. Nhấn **Button 2** để thoát về Relax Menu.

### Expected Result

Người dùng có trải nghiệm giải trí nhanh, đơn giản và phù hợp với các khoảng nghỉ ngắn.

---

## 4.13. Music Player

Music Player hỗ trợ phát nhạc thư giãn hoặc nhạc tập trung.

### How To Use

1. Vào **Relax Mode**.
2. Nhấn **Button 3** để mở **Music Player**.
3. Nhấn **Button 3** để phát hoặc tạm dừng nhạc.
4. Nhấn **Button 4** để chuyển sang bài tiếp theo.
5. Nhấn **Button 5** để quay lại bài trước.
6. Nhấn **Button 2** để quay lại Relax Menu.

### Expected Result

Người dùng có thể nghe nhạc để thư giãn, nghỉ ngơi hoặc tạo không gian hỗ trợ tập trung.

---

## 4.14. Notes

* Trước khi sử dụng, cần đảm bảo SmartClock đã được cấp nguồn và màn hình hiển thị bình thường.
* Khi đang cấu hình thời gian, nên kiểm tra kỹ giá trị trước khi nhấn lưu.
* Các chức năng đánh giá giấc ngủ và luyện tập seminar trong phiên bản hiện tại mang tính hỗ trợ cơ bản, có thể được mở rộng trong các phiên bản tiếp theo.
* Nếu muốn quay lại màn hình chính, tiếp tục nhấn **Button 1** để chuyển qua các chế độ theo vòng lặp.
