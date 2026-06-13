# 08. Appendix & Reference

## 8.1. Key Terms

| Term | Description |
| ---- | ----------- |
| SomniLearnAI | Đồng hồ thông minh AIoT hỗ trợ Pomodoro, luyện thuyết trình, báo thức, quan sát giấc ngủ và dashboard quan sát dữ liệu phiên. |
| Edge Device | Thiết bị đặt gần người dùng, trực tiếp đọc cảm biến, hiển thị giao diện và nhận thao tác nút bấm. |
| Edge AI | Phần xử lý tại thiết bị cho use case quan sát giấc ngủ, gồm đọc cảm biến, tính sleep score cơ bản và phát hiện tác nhân môi trường. |
| Internet Service | Server, database và API phục vụ đồng bộ dữ liệu, dashboard quan sát và chấm điểm thuyết trình. |
| Dashboard Observation | Giao diện web để quan sát phiên học, phiên ngủ và phiên thuyết trình theo thời gian. |
| Study Session | Dữ liệu một phiên học Pomodoro. |
| Sleep Session | Dữ liệu một phiên quan sát giấc ngủ Edge AI. |
| Alarm Setting | Chức năng đặt giờ báo thức cục bộ trên Edge Device. |
| Presentation Session | Dữ liệu một phiên luyện thuyết trình, có thể chờ Server chấm điểm. |
| Hotspot | Điểm phát Wi-Fi từ điện thoại hoặc laptop để SomniLearnAI truy cập Internet. |
| Setup AP | Mạng Wi-Fi tạm thời do SomniLearnAI phát ra để người dùng cấu hình Internet. |
| Pomodoro | Phương pháp quản lý thời gian bằng cách chia phiên học/làm việc và nghỉ ngơi. |
| TFT Display | Màn hình màu dùng để hiển thị giao diện thiết bị. |
| INMP441 | Microphone digital giao tiếp I2S, dùng để ghi nhận âm thanh môi trường hoặc dữ liệu luyện thuyết trình. |

---

## 8.2. Screen Flow Summary

SomniLearnAI sử dụng luồng màn hình chính:

```text
HOME -> STUDY -> SLEEP -> STATUS -> HOME
```

| Mode | Main Use Cases |
| ---- | -------------- |
| HOME | Hiển thị giờ hiện tại, trạng thái kết nối và điểm bắt đầu |
| STUDY | Pomodoro Timer, Seminar Practice |
| SLEEP | Alarm Setting, Sleep Monitoring Edge AI, realtime environment display |
| STATUS | Kiểm tra Wi-Fi, trạng thái server và số phiên chưa đồng bộ |

---

## 8.3. Dashboard Summary

| Dashboard Area | Observation Purpose |
| -------------- | ------------------- |
| Study Observation | Quan sát số Pomodoro, tổng phút học và lịch sử phiên học |
| Sleep Observation | Quan sát điểm ngủ, thời lượng ngủ, tác nhân môi trường và tổng kết tháng |
| Presentation Observation | Quan sát danh sách các lần luyện nói, điểm thuyết trình và xu hướng cải thiện |

---

## 8.4. Hardware Reference Table

| Component | Role | Notes |
| --------- | ---- | ----- |
| ESP32-S3 | Main controller and Wi-Fi connection | Điều khiển giao diện, đọc nút bấm, đọc cảm biến và kết nối Internet |
| TFT Display | User interface | Hiển thị menu, timer, realtime environment và báo cáo ngắn |
| 5 Buttons | User input | Điều hướng các chế độ và chức năng |
| Light Sensor | Environment sensing | Ghi nhận ánh sáng môi trường |
| INMP441 | Audio sensing | Ghi nhận âm thanh môi trường hoặc dữ liệu luyện thuyết trình |
| Environment Sensors | Optional sensing | Đo nhiệt độ, độ ẩm hoặc CO2 nếu prototype mở rộng |
| DS3231 RTC | Time keeping | Giữ thời gian và timestamp phiên khi offline |

---

## 8.5. Internet Connection Reference

SomniLearnAI có thể kết nối Internet theo mô hình:

```text
Phone/Laptop <-> SomniLearnAI_Setup AP
SomniLearnAI Edge Device <-> Phone/Laptop Hotspot <-> Internet <-> SomniLearnAI Server <-> Dashboard
```

Khi dùng hotspot, người dùng cần đảm bảo:

* Điện thoại hoặc laptop đã bật chia sẻ Internet.
* Nếu SomniLearnAI chưa có cấu hình mạng, người dùng kết nối điện thoại hoặc laptop vào `SomniLearnAI_Setup` trước.
* SomniLearnAI được cấu hình đúng tên Wi-Fi và mật khẩu.
* Thiết bị phát hotspot ở đủ gần SomniLearnAI.
* Kết nối Internet ổn định nếu cần đồng bộ dashboard hoặc chấm điểm thuyết trình.

---

## 8.6. References

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
https://linhkienviet.vn/ca-mie-n-anh-sang
