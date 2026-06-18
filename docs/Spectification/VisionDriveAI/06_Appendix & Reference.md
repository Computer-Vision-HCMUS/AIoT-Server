# 06. Appendix & Reference

## 6.1. Appendix

### 6.1.1. Key Terms

| Term | Description |
| ---- | ----------- |
| VisionDriveAI | Hệ thống AIoT phát hiện mất tập trung cho người lái xe máy nội đô. |
| Edge Device | Thiết bị gắn trên xe, xử lý camera, IMU và cảnh báo tại chỗ. |
| Computer Vision | Kỹ thuật xử lý hình ảnh để nhận diện khuôn mặt, hướng nhìn hoặc tư thế tay. |
| Sensor Fusion | Kết hợp dữ liệu từ nhiều cảm biến để tăng độ tin cậy khi ra quyết định. |
| IMU | Cảm biến đo gia tốc và con quay hồi chuyển, dùng để phân tích chuyển động tay lái. |
| Safety Score | Điểm đánh giá mức độ an toàn của chuyến đi, thường trong thang 0-100. |
| Personalization | Cá nhân hóa mô hình dựa trên baseline hành vi của từng người lái. |

---

## 6.2. Use Case Summary

| Objective | Use Cases | AI |
| --------- | --------- | -- |
| Objective 1: Real-time detection | Ngủ gật/nhìn lạc hướng, cầm điện thoại | UC-1.1, UC-1.2 |
| Objective 2: Alert and app feedback | Cảnh báo leo thang, thông báo realtime + AI pattern | UC-2.2 |
| Objective 3: Trip analytics and personalization | Safety Score, cá nhân hóa model | UC-3.2 |

---

## 6.3. Hardware Reference Table

| Component | Role | Estimated Price |
| --------- | ---- | --------------- |
| ESP32-S3 | Edge inference + Wi-Fi/BLE | 150,000 VND |
| ESP32-CAM | Camera nhận diện mặt và tay | 80,000 VND |
| MPU-6050 | Gia tốc kế + con quay hồi chuyển | 30,000 VND |
| Vibration Motor DC | Rung tay lái cảnh báo | 20,000 VND |
| Buzzer + LED RGB | Còi và đèn cảnh báo đa mức | 15,000 VND |
| LiPo Battery + Charging Module | Nguồn độc lập cho prototype | 80,000 VND |

---

## 6.4. References

[1] ESP32-S3 Series, Espressif Systems.  
https://www.espressif.com/en/products/socs/esp32-s3

[2] ESP32 Camera Driver, Espressif Component Registry.  
https://components.espressif.com/components/espressif/esp32-camera

[3] MPU-6050 Six-Axis MotionTracking Device, TDK InvenSense.  
https://invensense.tdk.com/products/motion-tracking/6-axis/mpu-6050/

[4] MediaPipe Face Mesh, Google AI.  
https://ai.google.dev/edge/mediapipe/solutions/vision/face_landmarker

[5] MobileNet, Google Research.  
https://research.google/pubs/mobilenets-efficient-convolutional-neural-networks-for-mobile-vision-applications/

[6] Edge AI, IBM overview.  
https://www.ibm.com/think/topics/edge-ai
