idea của Tài trình bày ở đây

topic: QQUEUE — Nền tảng phòng xếp hàng ảo cho bệnh viện

        OKR (objective key result) #1:Giảm thời gian chờ của người đi khám bệnh.
            KR1 (key result 1): Cho phép bệnh nhân đặt lịch lấy số từ xa.
            KR2: Cho phép bệnh nhân theo dỏi trạng thái hàng chờ ảo.
            KR3: Dự đoán thời gian chờ và gợi ý thời điểm di chuyển phù hợp (AI),
                tối ưu chuyên biệt cho các trường hợp xét nghiệm máu hay kiểm tra liên quan thì không cần đi đến viện từ sớm (1), theo như link youtube (2)
        OKR #2: Giảm tụ tập đông người.
            KR1: cho phép bệnh nhân tự in phiếu như trong video (2)
        OKR #3: Tối ưu năng suất vận hành của bệnh viện.
            KR1: cung cấp thống kê để bệnh viện sắp xếp nhân lực phù hợp(AI).
            KR2: đồng bộ bệnh nhân đặt lịch qua app với bệnh nhân lấy số trực tiếp.
            

        
        (1)có phù hợp, tối ưu chuyên biệt thì chính là maximizing you expected utility => là AI.
        
        (2)(https://www.youtube.com/watch?v=sKjHW4xTAIQ),


        comment: nếu ghi theo kiểu okr thì phía sau phải là key result và key action chứ đâu phải use case nhỉ 
        đề tài của sinh viên HCMUS từng làm, thấy được đăng báo chính phủ,chưa tìm ra tài liệu kỹ thuật cụ thể.

Kiếm AI cho idea của Đức

3.0 HOME — Environmental Monitoring
Mục tiêu
Hiển thị realtime chất lượng môi trường xung quanh

   
    Nguồn chốt:
   https://github.com/edgeimpulse/expert-projects/blob/main/air-quality-and-environmental-projects/smart-building-sensor-fusion.md?utm_source=chatgpt.com

    Smart Building Ventilation with Environmental Sensor Fusion
    Created By: Jallson Suryo

    Rain and Thunder Sound - https://studio.edgeimpulse.com/public/270172/latest

    Weather Conditions - https://studio.edgeimpulse.com/public/274091/latest

    GitHub Repo: https://github.com/Jallson/SensorFusion_SmartBuilding

    {% embed url="https://youtu.be/mqk1IRz76HM" %}

    Introduction
    In a natural ventilation system, it is necessary to regulate the conditioning of air, humidity, temperature and light through adjusting window and louver/blind angles. An automatic system that can adapt to current conditions is the key to comfort and energy savings.

    Đoạn code xử lý, phân tích trên edge nằm ở:
    https://github.com/Jallson/SensorFusion_SmartBuilding/blob/main/weathersoundfusion_nano_ble33.ino?utm_source=chatgpt.com


  



3. MỨC ĐỘ KHÓ CÀI

Mức độ khó:
TRUNG BÌNH ĐẾN KHÁ KHÓ

Lý do:

1. Cần phần cứng tương ứng:
- Arduino Nano 33 BLE Sense.
- Servo điều khiển cửa sổ.
- Servo điều khiển louver/lam che.
- Nếu chạy đầy đủ thì cần thêm board âm thanh gửi tín hiệu mưa/sấm qua I2C.

2. Cần thư viện:
- Edge Impulse inference library.
- Arduino_HTS221 để đọc nhiệt độ, độ ẩm.
- Arduino_APDS9960 để đọc màu/độ sáng.
- Servo library.
- Wire library cho I2C.

3. Cần model Edge Impulse đã train sẵn:
- File code gọi run_classifier().
- Nhưng muốn chạy được thì phải có thư viện model Edge Impulse tương ứng được export về Arduino.

4. Nếu chỉ đọc code và hiểu luồng xử lý:
- Mức độ: trung bình.




4. THỜI GIAN / REALTIME

Có realtime không?
CÓ, nhưng là NEAR-REALTIME.

Lý do từ code:

delay(3000);

Ý nghĩa:
- Mỗi vòng loop có delay 3 giây.
- Vì vậy hệ thống không phản ứng liên tục từng mili-giây.
- Nó xử lý theo chu kỳ.

Đoạn code lấy mẫu theo thời gian:

int64_t next_tick = (int64_t)micros() + ((int64_t)EI_CLASSIFIER_INTERVAL_MS * 1000);

...

int64_t wait_time = next_tick - (int64_t)micros();

if(wait_time > 0) {
    delayMicroseconds(wait_time);
}

Ý nghĩa:
- Hệ thống lấy mẫu cảm biến theo interval của Edge Impulse.
- Dữ liệu được lấy theo nhịp thời gian định trước.
- Sau đó chạy inference trực tiếp trên board.

Đoạn code in thời gian xử lý:

ei_printf("Predictions (DSP: %d ms., Classification: %d ms., Anomaly: %d ms.):\r\n",
    result.timing.dsp,
    result.timing.classification,
    result.timing.anomaly
);

Ý nghĩa:
- result.timing.dsp = thời gian xử lý tín hiệu.
- result.timing.classification = thời gian phân loại.
- result.timing.anomaly = thời gian kiểm tra bất thường nếu có.
- Code có đo thời gian xử lý, chứng tỏ mô hình được chạy trực tiếp trên edge device.

Kết luận:
- Có xử lý realtime theo chu kỳ.
- Không phải hard real-time.
- Phù hợp gọi là near-real-time edge inference.


5. METHOD

Tên method:
Sensor Fusion + TinyML Classification on Edge Device

Dịch:
Hợp nhất cảm biến + phân loại TinyML trên thiết bị đầu cuối.

Method trong code gồm các bước:


6. TÓM TẮT NGẮN

Input:
- temperature
- humidity
- brightness
- tín hiệu mưa/sấm từ I2C

Output:
- nhãn môi trường: comfortable, overcast, sunny dry, sunny humid
- trạng thái mưa/sấm: rain, thunder
- điều khiển servo cửa sổ và lam che

Mức độ khó cài:
- Trung bình nếu chỉ chạy Nano 33 BLE Sense.
- Khá khó nếu chạy đầy đủ Nano BLE Sense + Nicla Voice + I2C + servo.

Realtime:
- Có, dạng near-real-time.
- Hệ thống xử lý theo chu kỳ, có delay 3000 ms trong loop.

Method:
- Sensor Fusion + TinyML Classification on Edge Device.
- Dữ liệu cảm biến được gom vào buffer.
- Buffer được chuyển thành signal.
- Mô hình Edge Impulse chạy bằng run_classifier()(nằm trong thư viện). 
- Kết quả phân loại được dùng để điều khiển servo.

Kết luận của tôi:
    near-real_time được đánhh giá là không nặng lắm, nhưng có cài được trên esp8266 không thì phải tìm hiểu tiếp, việc nó nhanh hay chậm có vẻ là vì Edge Impulse, tôi kêu chatgpt liệt kê phương pháp thay thế cho edge impulse với quy mô nhỏ hơn thì chỉ có decision tree là được thôi.