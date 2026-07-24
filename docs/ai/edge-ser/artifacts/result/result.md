# Kết quả kiểm thử MP3 → cảm xúc

Ngày chạy: 2026-07-25

## Baseline cũ

Pipeline C++ dùng `classifier.h` 45 chiều từng dự đoán cả hai mẫu Happy và
Disgust thành Angry, với confidence 0.320 và 0.290. Artifact này được giữ để
đối chiếu nhưng không dùng để phát hành model.

## Model RAVDESS mới

- Dataset: RAVDESS audio-only speech, 1.440 WAV có ground-truth.
- Đầu vào model: 210 acoustic features từ mono PCM 22.05 kHz.
- Model: Keras MLP có chuẩn hóa feature, export `ravdess_ser.tflite`.
- Đánh giá: stratified random holdout 20%, seed 42, 288 mẫu test.
- Keras test accuracy: **63.89%**.
- TFLite test accuracy: **63.19%**.
- Macro F1: **62.64%**.

Kết quả vượt tiêu chí tối thiểu `>50%`. Đây là baseline stratified, không phải
đánh giá actor-independent; đánh giá theo actor holdout trước đó chỉ đạt 42.50%
và được ghi nhận là chưa đạt.

## Kiểm thử MP3

Một RAVDESS WAV có nhãn `happy` được encode lại thành MP3 và chạy qua TFLite:

| Input | Nhãn mong đợi | Nhãn dự đoán | Confidence | Kết quả |
| --- | --- | --- | ---: | --- |
| `happy-ravdess.mp3` | Happy | Happy | 94.77% | Đúng |

Output JSON gồm `emotion_label`, `confidence_score`, top-3 predictions,
sample rate, duration và latency. Xem lệnh tái lập trong
[`../../pipeline/README.md`](../../pipeline/README.md).

> [!WARNING]
> Accuracy 63.89% không có nghĩa mọi MP3 sẽ được phân loại đúng. Model chỉ được
> benchmark trên RAVDESS; cần đánh giá thêm với recording/microphone và người
> dùng thật trước khi dùng như tính năng sản phẩm.
