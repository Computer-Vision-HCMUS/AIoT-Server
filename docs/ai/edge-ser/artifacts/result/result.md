# Kết quả kiểm thử MP3 → cảm xúc

Ngày chạy: 2026-07-18

## Môi trường

- Chương trình: `smart-device/ser_mp3.cpp` (C++17)
- Decoder MP3: `ffmpeg`
- Inference: Random Forest export trong `classifier.h`
- Tiền xử lý: mono PCM, giữ sample rate gốc (`sr=None` tương ứng với `extractor.py`), STFT 2048 và hop 512.

## Kết quả

| File input | Sample rate | Thời lượng | Nhãn dự đoán | Confidence | Nhãn mong đợi từ tên file |
| --- | ---: | ---: | --- | ---: | --- |
| `test/disgusting.mp3` | 48000 Hz | 3.264 s | Angry | 0.290 | Disgust |
| `test/happy.mp3` | 48000 Hz | 6.936 s | Angry | 0.320 | Happy |

## Nhận xét

Pipeline C++ đã đọc MP3, trích xuất 45 đặc trưng và gọi được model. Tuy nhiên, cả hai mẫu đều bị phân loại thành `Angry`, với confidence thấp. Vì vậy model export hiện tại **chưa đủ tin cậy để sử dụng thực tế**.

Đã cải thiện bước tiền xử lý để gần `extractor.py` hơn (không ép resample 16 kHz và thay FFT 1024 bằng 2048). Kết quả vẫn không khớp, cho thấy cần có dữ liệu train, nhãn ground-truth, pipeline scaler/quantization và model gốc để train/export lại; chỉ có `classifier.h` thì không thể huấn luyện lại một model chính xác theo cách có kiểm chứng.
