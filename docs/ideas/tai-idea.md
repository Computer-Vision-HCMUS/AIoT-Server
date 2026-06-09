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
    near-real_time được đánhh giá là không nặng lắm, nhưng có cài được trên esp8266 thỏa ý Đức không thì phải tìm hiểu tiếp, việc nó nhanh hay chậm có vẻ là vì Edge Impulse, tôi kêu chatgpt liệt kê phương pháp thay thế cho edge impulse với quy mô nhỏ hơn thì chỉ có decision tree là được thôi.

Về phần data:



kết luận có cái này là hợp nhất: https://www.kaggle.com/datasets/karthikiye/wearable-tech-sleep-quality

bao gồm:
    Heart Rate: nhịp tim.
    Body Temperature: nhiệt độ cơ thể.
    Room Temperature: nhiệt độ phòng.
    Humidity: độ ẩm.
    Sleep Stage: giai đoạn giấc ngủ.
        Biến Sleep Stage là biến phân loại, gồm 4 nhãn:
        Awake: trạng thái thức.
        Light: giấc ngủ nông.
        Deep: giấc ngủ sâu.
        REM: giai đoạn ngủ chuyển động mắt nhanh.

Tôi tự viết báo cáo văn phong lủng củng nên nhờ AI viết lại như sau:


Về mặt trình bày, nên bắt đầu bằng phần dataset, vì chính bộ dữ liệu sẽ cho thấy các biến nào có thể được sử dụng làm input cho mô hình. Từ bảng mô tả dataset, ta có thể rút ra các thông tin đầu vào như nhịp tim, nhiệt độ cơ thể, nhiệt độ phòng, độ ẩm và các nhãn phân loại giấc ngủ.


https://physionet.org/content/sleep-accel/1.0.0/
Đối với bài báo “Sleep Pattern Analysis…” của Wen-Hsun, phần mô tả dataset chưa thật sự rõ ràng. Vì vậy, cần tìm thêm một nguồn dữ liệu tương tự nhưng có mô tả dataset cụ thể hơn để làm cơ sở trình bày. Một nguồn có thể tham khảo là dataset “Motion and heart rate from a wrist-worn wearable and labeled sleep from polysomnography” của Olivia Walch. Tuy nhiên, dataset này có vẻ không được tổ chức dưới dạng một bảng duy nhất, mà được lưu thành nhiều file riêng biệt. 

Theo phần Data Description của Olivia Walch, ví dụ dữ liệu motion được lưu trong file có định dạng tên là:

[subject-id-number]_acceleration.txt

Mỗi dòng trong file này gồm các thông tin: thời gian tính bằng giây từ lúc bắt đầu , gia tốc theo trục x, gia tốc theo trục y và gia tốc theo trục z. Như vậy, bộ dữ liệu này mô tả khá rõ cấu trúc từng loại dữ liệu cảm biến, nhưng không  được trình bày sẵn dưới dạng một bảng tổng hợp duy nhất.

Bảng này sẽ gồm các cột tương ứng với các biến đầu vào và một cột đầu ra là nhãn giấc ngủ.

Tuy nhiên, dataset cần được lựa chọn sao cho tương đồng với các loại cảm biến được đề cập trong bài nghiên cứu . Nếu cần một nguồn đầy đủ hơn, có thể xem xét dữ liệu từ thiết bị DREamt, vì nguồn này có khả năng cung cấp nhiều thông tin sinh lý liên quan đến giấc ngủ.
https://physionet.org/content/dreamt/2.0.0/
Nhưng chưa tải được, cần xin quyền.

Ngoài ra, trên Kaggle có dataset “Wearable Tech Sleep Quality” của Karthik Iyer.
https://www.kaggle.com/datasets/karthikiye/wearable-tech-sleep-quality
 Mặc dù độ uy tín học thuật của nguồn này chưa thật sự rõ ràng, dataset này có ưu điểm là trình bày thông tin đầu vào khá trực quan. Dataset gồm một file CSV với các cột như:

Heart Rate, Body Temperature, Room Temperature, Humidity và Sleep Stage.

Trong đó, Sleep Stage là biến đầu ra, dùng để phân loại trạng thái giấc ngủ, gồm các nhãn: Awake, Light, Deep và REM. Dataset nhỏ.



Ngoài dataset trên, vẫn có thể tham khảo thêm các bộ dữ liệu như Sleep and Health Metrics. 
Tuy nhiên, các bộ dữ liệu này thường tập trung vào những biến như stress level, bedtime hoặc các chỉ số sức khỏe tổng quát, chứ không trực tiếp phân loại các giai đoạn giấc ngủ như REM, Light hay Deep. Vì vậy, nếu mục tiêu là xây dựng mô hình phân loại giai đoạn giấc ngủ, cần ưu tiên các dataset có nhãn sleep stage rõ ràng.



Research TinyML (Tiny Machine Learning – học máy siêu nhỏ), Edge Pulse.

- Edge AI (Edge Artificial Intelligence – trí tuệ nhân tạo biên).

- Edge Computing (điện toán biên).

- Network boundary (ranh giới mạng).

- Vì nếu dữ liệu nào cũng gửi lên cloud (đám mây) thì lượng dữ liệu sẽ quá nhiều, nên cần dùng Edge Computing (điện toán biên).

- Dữ liệu sẽ được tính toán trước ở edge (thiết bị biên/vùng biên mạng), sau đó chỉ gửi result (kết quả) đi. Nhờ vậy có thể giảm lượng data transmitted (dữ liệu được truyền đi).

- Latency (độ trễ): Edge Computing giúp giảm độ trễ trong một số tình huống cần phản hồi nhanh.

- Có những tối ưu liên quan đến việc làm cho độ trễ nhỏ hơn, ví dụ như shutdown (tắt hệ thống) hoặc các hệ thống khẩn cấp. Đây là phần trả lời cho câu hỏi của Chiến.

- Edge Computing cũng giúp giảm sự phụ thuộc vào network (mạng), ví dụ như trong xe tự hành. Nếu xe tự hành phải phụ thuộc quá nhiều vào mạng để gửi dữ liệu lên cloud rồi chờ kết quả trả về, hệ thống có thể bị chậm hoặc không ổn định.

- Bởi vì thiết bị chỉ gửi result (kết quả) đi, nên raw data (dữ liệu thô) như hình ảnh khuôn mặt hoặc thói quen cá nhân không nhất thiết bị collect (thu thập) vào database (cơ sở dữ liệu).

- Như vậy, Edge Computing giúp bảo vệ privacy (quyền riêng tư) tốt hơn.

- Tóm lại, Edge Computing có lợi ở các điểm chính: bandwidth (băng thông), latency (độ trễ), energy usage (mức tiêu thụ năng lượng), reliability (độ tin cậy) và privacy (quyền riêng tư).

- Edge AI (Edge Artificial Intelligence – trí tuệ nhân tạo biên).

- Hai ý quan trọng liên quan đến Edge AI là network (mạng) và privacy (quyền riêng tư).

- Ví dụ cho Edge AI (Edge Artificial Intelligence – trí tuệ nhân tạo biên) là home smart speaker (loa thông minh trong nhà).

- Edge AI (Edge Artificial Intelligence – trí tuệ nhân tạo biên) càng ngày càng được dùng nhiều vì AI (Artificial Intelligence – trí tuệ nhân tạo) chạy trên cloud thường tốn quá nhiều bandwidth (băng thông).

Ghi chú: Chỗ “Edge Pulse” có thể là “Edge Impulse”, nhưng nội dung này đang giữ đúng theo ghi chú ban đầu.
