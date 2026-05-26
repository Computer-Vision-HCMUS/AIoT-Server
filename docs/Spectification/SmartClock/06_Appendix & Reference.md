# 06. Appendix & Reference

## 6.1. Appendix

### 6.1.1. Key Terms

| Term | Description |
| ---- | ----------- |
| SmartClock | Thiết bị đồng hồ thông minh hỗ trợ tập trung, giấc ngủ và giải trí cá nhân. |
| Edge Device | Thiết bị xử lý gần người dùng, trực tiếp đọc cảm biến, hiển thị giao diện và nhận thao tác nút bấm. |
| Server | Thành phần xử lý, lưu trữ và mở rộng các chức năng phân tích hoặc AIoT. |
| Hotspot | Điểm phát Wi-Fi từ điện thoại hoặc laptop để SmartClock truy cập Internet. |
| Setup AP | Mạng Wi-Fi tạm thời do SmartClock phát ra để điện thoại hoặc laptop kết nối vào và cấu hình Internet. |
| Pomodoro | Phương pháp quản lý thời gian bằng cách chia phiên làm việc và nghỉ ngơi. |
| TFT Display | Màn hình màu dùng để hiển thị giao diện thiết bị. |
| INMP441 | Microphone digital giao tiếp I2S, dùng để ghi nhận âm thanh. |

---

## 6.2. Screen Flow Summary

SmartClock sử dụng luồng màn hình chính:

```text
HOME → STUDY → SLEEP → RELAX → HOME
```

| Mode | Main Use Cases |
| ---- | -------------- |
| HOME | Hiển thị tổng quan và chuyển chế độ |
| STUDY | Pomodoro Timer, Seminar Practice |
| SLEEP | Sleep Monitoring, Alarm Settings |
| RELAX | Flappy Bird, Music Player |

---

## 6.3. Hardware Reference Table

| Component | Role | Notes |
| --------- | ---- | ----- |
| ESP32-6288 | Main controller and Wi-Fi connection | Điều khiển giao diện, đọc nút bấm, đọc cảm biến và kết nối Internet |
| TFT Display | User interface | Hiển thị menu, timer, báo cáo và trò chơi |
| 5 Buttons | User input | Điều hướng các chế độ và chức năng |
| Light Sensor | Environment sensing | Ghi nhận ánh sáng môi trường |
| INMP441 | Audio sensing | Ghi nhận âm thanh môi trường hoặc bài luyện tập |

---

## 6.4. Internet Connection Reference

SmartClock có thể kết nối Internet theo mô hình:

```text
Phone/Laptop ↔ SmartClock_Setup AP
SmartClock Edge Device ↔ Phone/Laptop Hotspot ↔ Internet ↔ SmartClock Server
```

Khi dùng hotspot, người dùng cần đảm bảo:

* Điện thoại hoặc laptop đã bật chia sẻ Internet.
* Nếu SmartClock chưa có cấu hình mạng, người dùng kết nối điện thoại hoặc laptop vào `SmartClock_Setup` trước.
* SmartClock được cấu hình đúng tên Wi-Fi và mật khẩu.
* Thiết bị phát hotspot ở đủ gần SmartClock.
* Kết nối Internet ổn định nếu cần đồng bộ hoặc phân tích dữ liệu.

---

## 6.5. References

[1] Pomodoro Technique, Wikipedia.  
https://en.wikipedia.org/wiki/Pomodoro_Technique

[2] ESP32 Series, Espressif Systems.  
https://www.espressif.com/en/products/socs/esp32

[3] INMP441 MEMS Microphone Module, InvenSense / TDK product information.  
https://invensense.tdk.com/products/digital/inmp441/

[4] TFT LCD, Wikipedia.  
https://en.wikipedia.org/wiki/Thin-film-transistor_liquid-crystal_display

[5] Mobile hotspot overview, Microsoft Support.  
https://support.microsoft.com/windows/use-your-windows-pc-as-a-mobile-hotspot-c89b0fad-72d5-41e8-f7ea-406ad9036b85

[6] Android tethering and hotspot help, Google Android Help.  
https://support.google.com/android/answer/9059108

[7] Cảm biến âm thanh INMP441 MEMS I2S, Nshop.  
https://nshopvn.com/product/cam-bien-am-thanh-inmp441-mems-i2s-micro-da-huong/

[8] Cảm biến cường độ ánh sáng quang trở, Nshop.  
https://nshopvn.com/product/cam-bien-cuong-do-anh-sang-quang-tro/

[9] Cảm biến ánh sáng, Linh Kiện Việt.  
https://linhkienviet.vn/ca-m-bie-n-anh-sang
