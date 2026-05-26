# 04. User Manual

## 4.1. Overview

Tài liệu này hướng dẫn người dùng thiết lập và sử dụng VisionDriveAI. Hệ thống gồm Edge Device gắn trên xe máy, camera, cảm biến IMU, cụm cảnh báo rung/còi/LED và ứng dụng di động để theo dõi hành trình.

VisionDriveAI tập trung vào 3 nhóm chức năng:

* Phát hiện hành vi mất tập trung theo thời gian thực.
* Cảnh báo đa tầng ngay trên xe.
* Ghi log hành trình, phân tích Safety Score và cá nhân hóa mô hình.

---

## 4.2. Device Setup

### Mounting Position

1. Gắn Edge Device ở vị trí chắc chắn trên xe máy.
2. Đặt ESP32-CAM hướng về khuôn mặt và phần tay lái của người lái.
3. Gắn vibration motor gần khu vực ghi đông để người lái cảm nhận được rung.
4. Đặt buzzer và LED ở vị trí dễ nghe, dễ nhìn nhưng không che khuất tầm nhìn.
5. Đảm bảo dây nguồn và dây tín hiệu không ảnh hưởng thao tác lái xe.

### Power On

1. Kiểm tra pin LiPo hoặc nguồn cấp.
2. Bật Edge Device.
3. Chờ đèn trạng thái báo thiết bị sẵn sàng.
4. Mở Mobile App để kiểm tra kết nối nếu cần đồng bộ dữ liệu.

---

## 4.3. Mobile App Connection

VisionDriveAI có thể cảnh báo offline, nhưng Mobile App cần kết nối để xem dashboard, nhận thông báo và đồng bộ dữ liệu.

### Connect Edge Device to Mobile App

1. Bật Bluetooth hoặc Wi-Fi trên điện thoại.
2. Mở ứng dụng VisionDriveAI.
3. Chọn **Pair New Device**.
4. Chọn thiết bị VisionDriveAI trong danh sách.
5. Xác nhận kết nối.
6. Kiểm tra trạng thái camera, IMU và pin trên app.

### Online and Offline Usage

| Status | Behavior |
| ------ | -------- |
| Offline | Edge Device vẫn phát hiện mất tập trung và cảnh báo tại chỗ. |
| Online | App nhận log, gửi thông báo và đồng bộ dữ liệu lên Server để phân tích dài hạn. |

---

## 4.4. Starting a Ride

1. Bật Edge Device trước khi bắt đầu di chuyển.
2. Kiểm tra camera không bị che khuất.
3. Kiểm tra thiết bị có nhận được dữ liệu IMU.
4. Mở app và nhấn **Start Trip** nếu muốn ghi log hành trình.
5. Bắt đầu lái xe như bình thường.

### Expected Result

Hệ thống bắt đầu theo dõi hành vi người lái, chuyển động tay lái và sẵn sàng cảnh báo nếu phát hiện rủi ro.

---

## 4.5. Real-Time Distraction Detection

VisionDriveAI tự động phát hiện các hành vi mất tập trung mà người dùng không cần thao tác thủ công trong lúc lái xe.

### Detected Behaviors

| Behavior | Detection Source | Description |
| -------- | ---------------- | ----------- |
| Ngủ gật | Camera + Edge AI | Phát hiện mắt nhắm lâu hoặc đầu gật xuống. |
| Nhìn lạc hướng | Camera + Edge AI | Phát hiện hướng nhìn lệch khỏi đường trong thời gian liên tục. |
| Cầm điện thoại | Camera + IMU | Phát hiện tư thế tay cầm điện thoại khi xe đang di chuyển. |
| Lái xe thiếu ổn định | MPU-6050 | Phát hiện lắc lư, phanh gấp hoặc chuyển động bất thường. |

---

## 4.6. Alert System

VisionDriveAI sử dụng cảnh báo leo thang 3 mức:

| Level | Condition | Alert |
| ----- | --------- | ----- |
| Level 1 | Rủi ro mới xuất hiện | Rung nhẹ ở ghi đông |
| Level 2 | Rủi ro kéo dài | Rung mạnh và buzzer beep ngắn |
| Level 3 | Rủi ro nghiêm trọng hoặc kéo dài hơn | Còi liên tục và LED đỏ nháy |

### Reset Alert

Hệ thống tự reset khi người lái tập trung trở lại hoặc hành vi nguy hiểm không còn được phát hiện. Người dùng không nên thao tác trực tiếp với thiết bị trong lúc đang lái xe.

---

## 4.7. Trip Log and Notification

Khi Mobile App đang kết nối, mỗi sự kiện mất tập trung có thể được ghi lại với:

* Thời gian xảy ra sự kiện.
* Loại hành vi.
* Mức cảnh báo.
* Dữ liệu IMU liên quan.
* Metadata từ camera, ưu tiên quyền riêng tư.

### Push Notification

Nếu người dùng bật chia sẻ với người thân hoặc quản lý đội xe, app có thể gửi thông báo khi sự kiện nghiêm trọng xảy ra.

---

## 4.8. Safety Score

Sau mỗi chuyến đi, app tổng hợp dữ liệu và hiển thị Safety Score từ 0 đến 100.

### Score Inputs

* Số lần mất tập trung.
* Tổng thời gian mắt nhắm hoặc nhìn lạc hướng.
* Số lần cầm điện thoại.
* Số lần phanh gấp hoặc lắc tay lái bất thường.
* Tần suất cảnh báo mức 2 và mức 3.

### Expected Result

Người dùng có thể xem lại chất lượng chuyến đi và nhận biết thói quen cần cải thiện.

---

## 4.9. Personalization

Sau một thời gian sử dụng, VisionDriveAI có thể học baseline của từng người lái. Ví dụ, một người thường nhìn trái trước khi rẽ không nhất thiết bị xem là mất tập trung nếu hành vi đó xảy ra trong ngữ cảnh phù hợp.

### How It Works

1. Hệ thống thu thập dữ liệu hành trình trong 1-2 tuần.
2. Server phân tích pattern và baseline của người lái.
3. Mô hình hoặc ngưỡng cảnh báo được điều chỉnh.
4. Edge Device nhận cấu hình cá nhân hóa trong lần đồng bộ tiếp theo.

---

## 4.10. Notes

* Không điều chỉnh thiết bị khi đang lái xe.
* Đảm bảo camera không che khuất tầm nhìn và không vi phạm quyền riêng tư của người khác.
* Kiểm tra pin trước mỗi chuyến đi.
* Cảnh báo của VisionDriveAI chỉ là công cụ hỗ trợ, không thay thế trách nhiệm quan sát và điều khiển xe an toàn của người lái.
