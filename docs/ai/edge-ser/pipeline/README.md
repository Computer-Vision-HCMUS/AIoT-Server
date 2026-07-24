# RAVDESS SER pipeline

Pipeline này tạo baseline có thể kiểm chứng cho input audio và output emotion:

```text
MP3/WAV → librosa decode → fixed acoustic features → TFLite → JSON prediction
```

RAVDESS audio-only speech có 1.440 WAV được gắn nhãn trong filename. Mặc định,
`train_ravdess.py` dùng stratified holdout để đo baseline; chọn `--evaluation actor`
để giữ toàn bộ actor 21–24 cho test nghiêm ngặt hơn.

## Train và export

Từ thư mục `edge-ser`:

```powershell
.\.venv\Scripts\python.exe .\pipeline\train_ravdess.py `
  --dataset .\data\ravdess-speech `
  --output .\models
```

Script chỉ tạo `models/ravdess_ser.tflite` nếu test accuracy của protocol đã chọn lớn hơn
50%. Metadata đi kèm (`ravdess_ser.metadata.json`) lưu labels, số sample, protocol
đánh giá và classification report.

## Predict từ MP3

```powershell
.\.venv\Scripts\python.exe .\pipeline\predict.py .\sample.mp3 `
  --model .\models\ravdess_ser.tflite `
  --metadata .\models\ravdess_ser.metadata.json `
  --output .\artifacts\result\sample.json
```

Output JSON có `emotion_label`, `confidence_score`, top-3 predictions, sample rate,
duration và inference latency.

## ESP32 và LibXtract

TFLite model nhận vector acoustic float32, không trực tiếp decode MP3. ESP32 cần:

1. Decode/capture PCM 16-bit mono.
2. Tái tạo đúng feature schema trong `features.py`.
3. Gọi TFLite Micro với vector feature đó.

LibXtract phù hợp cho phần native C/C++ vì các primitive của nó được thiết kế để
tái sử dụng magnitude spectrum giữa nhiều feature. Tuy nhiên không thay thế trực
tiếp `librosa`: phải benchmark feature parity trước khi dùng trên firmware.
