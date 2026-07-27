# Phương pháp: nhận diện cảm xúc giọng nói RAVDESS-8

## Phạm vi

Module này nhận diện cảm xúc **từ đặc trưng âm học của giọng nói**, không phân
tích nội dung câu nói hoặc hình ảnh khuôn mặt. Dữ liệu chính là RAVDESS
audio-only speech: 1.440 phát ngôn của 24 diễn viên chuyên nghiệp, gồm tám nhãn
`neutral`, `calm`, `happy`, `sad`, `angry`, `fearful`, `disgust` và
`surprised`.

Nguồn dataset và taxonomy duy nhất được viện dẫn là bài báo RAVDESS của
Livingstone & Russo (2018). Mã export C/C++ tham khảo repo
`prasenjit52282/embedded-audio-emotion`, nhưng model trong dự án này được train
lại chỉ bằng RAVDESS, không dùng dữ liệu hoặc taxonomy của repo đó.

## Hợp đồng triển khai

```text
WAV/MP3 -> mono PCM -> extractor.h -> 45 số float -> classify.h -> cảm xúc
```

Schema `ravdess-mfcc45-v1` có 45 chiều: trung bình của 13 MFCC, độ lệch chuẩn
của 13 MFCC, 12 chroma, RMS, zero-crossing rate, spectral centroid, bandwidth,
rolloff, flatness và spectral contrast. Thứ tự nằm trong `extractor.h` và không
được thay đổi sau khi train.

`classify.h` là Extra Trees float32 gồm 100 cây, không giới hạn độ sâu, cân bằng
trọng số lớp và seed 42. Model được lưu joblib rồi được `tools/export_model.py`
gọi emlearn để tạo header. Header nhận đúng 45 giá trị float,
trả về chỉ số lớp; `native_pipeline.cpp` ánh xạ chỉ số đó về tám nhãn cảm xúc.

Chương trình native dùng `ffmpeg` để decode audio, trích xuất feature, ghi
feature ra JSON rồi gọi classifier. JSON giúp kiểm tra riêng từng bước.

## Đánh giá và giới hạn

Chỉ số mới nhất nằm trong `../reports/train-metrics.json`. Chỉ số chính dùng
stratified holdout 80/20, trong đó một diễn viên có thể xuất hiện ở cả train và
test nên thường lạc quan. Kết quả actor-held-out phù hợp hơn để ước lượng với
người nói mới.

RAVDESS là giọng tiếng Anh Bắc Mỹ được diễn xuất và thu trong điều kiện kiểm
soát. Vì vậy đây là prototype nghiên cứu, không phải công cụ đánh giá sức khỏe
tâm lý hoặc chẩn đoán cảm xúc lâm sàng. Trước khi đưa lên firmware, phải kiểm
tra native extractor tạo đúng vector như extractor lúc huấn luyện; sai khác
feature khiến mọi kết quả của classifier không còn hợp lệ.
