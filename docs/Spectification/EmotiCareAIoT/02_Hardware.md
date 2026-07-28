# 02. Phần cứng

## 2.1. Vai trò phần cứng

Phần cứng là điểm tương tác trực tiếp với người dùng. Thiết bị thu giọng nói, nhận thao tác nút bấm, hiển thị nội dung ngắn trên TFT, phát tín hiệu âm thanh khi cần và kết nối Wi-Fi. Logic Edge AI, API và dữ liệu được mô tả tại từng tình huống sử dụng ở Chương 03.

## 2.2. Danh mục phần cứng

| Phần cứng | Vai trò | Giá (VNĐ) |
| --- | --- | ---: |
| ESP32-S AI Thinker | Bộ não trung tâm, xử lý toàn bộ thiết bị và kết nối Wi-Fi | 250.000 |
| LCD TFT ST7789 | Hiển thị menu, cảm xúc, gợi ý, hội thoại và báo cáo | 190.000 |
| INMP441 | Micro thu âm giọng nói qua I2S | 35.000 |
| MAX98357 I2S và loa 3W Class D | Khuếch đại âm thanh và phát loa | 90.000 |
| Module nút bấm 5 cái | Điều hướng màn hình và thao tác trên thiết bị | 30.000 |
| Breadboard | Nối dây, thử nghiệm mạch | 20.000 |
| Dây nối mạch | Kết nối các linh kiện | 30.000 |
| Dây nối nguồn | Cấp nguồn để thiết bị hoạt động | 70.000 |
| Bao bì phần cứng | Hoàn thiện phần bên ngoài của thiết bị | 100.000 |

## 2.3. Kết nối phần cứng

| Nhóm | Kết nối chính | Mục đích |
| --- | --- | --- |
| INMP441 | I2S: SCK, WS, SD | Thu tín hiệu giọng nói |
| LCD TFT ST7789 | SPI: CS, RST, DC, MOSI, SCLK, đèn nền | Hiển thị giao diện |
| Module nút bấm | GPIO | Điều hướng thao tác |
| MAX98357 I2S và loa 3W | I2S | Phát tín hiệu phản hồi và âm thanh |
| Wi-Fi | Tích hợp trên vi điều khiển | Kết nối dịch vụ Cloud |

## 2.4. Tổng chi phí

**Tổng chi phí phần cứng: 815.000 VNĐ.**

Mức giá này là danh mục đã chốt cho mẫu thử. Breadboard và dây nối phục vụ giai đoạn lắp ráp/kiểm tra; bao bì phần cứng dùng để hoàn thiện hình thức thiết bị.

## 2.5. Ràng buộc phần cứng

- Màn hình có không gian hạn chế, vì vậy nội dung cần ngắn và dễ đọc.
- Microphone cần hoạt động tốt trong môi trường demo không quá ồn.
- Wi-Fi là điều kiện để dùng các chức năng Cloud.
- Thiết bị phải hiển thị rõ trạng thái đang ghi âm, kết nối mạng và đồng bộ.
- Mẫu thử không phải thiết bị y tế và không thay thế chuyên gia sức khỏe tinh thần.
