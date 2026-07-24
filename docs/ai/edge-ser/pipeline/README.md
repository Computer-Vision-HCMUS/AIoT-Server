# PerCom-aligned RAVDESS-8 SER pipeline

```text
MP3/WAV → mono PCM → PerCom45 (`percom45-v1`) → Random Forest C header | TFLite MLP → JSON
```

Đây là adaptation theo bài PerCom 2025, không phải reproduction chính xác: giữ
toàn bộ 8 nhãn RAVDESS (`calm` được giữ lại), trong khi taxonomy của bài báo có
7 nhãn. `percom_features.py` tạo 45 đặc trưng: 13 scalar/prosodic, 13 MFCC
means, 12 chroma means và 7 spectral-contrast means.

## Tái lập train

Từ thư mục `edge-ser`:

```powershell
.\.venv\Scripts\python.exe .\pipeline\train_percom.py `
  --dataset .\data\ravdess-speech `
  --output .\models
```

Script cache feature matrix, dùng seed 42 và stratified holdout 20% làm chỉ số
chính; actor 21–24 được giữ ra riêng làm stress test. Cả Random Forest và MLP
chỉ được export khi test accuracy của chính chúng `>50%`. Artifacts là
`models/percom_rf.h`, `models/percom_mlp.tflite`, và
`models/percom45.metadata.json` (labels, schema, accuracy, Macro F1, per-class
F1, latency, size và protocol).

## Predict TFLite

```powershell
.\.venv\Scripts\python.exe .\pipeline\predict.py .\sample.mp3 `
  --artifact percom45-mlp `
  --output .\artifacts\result\sample.json
```

JSON ghi rõ artifact, schema/model version, nhãn, top-3, sample rate, duration
và latency. Filename không phải ground truth.

## Native RF và LibXtract parity

`artifacts/smart-device/ser_mp3.cpp` compile được với C++17 và `ffmpeg`; nó
include `models/percom_rf.h` và dùng float32 PerCom45 vector. Tuy nhiên native
extractor hiện chưa đạt parity với Python cho centroid, rolloff và flatness;
vì vậy **không deploy header này lên ESP32** trước khi hoàn tất LibXtract
benchmark.

```powershell
.\.venv\Scripts\python.exe .\pipeline\check_feature_parity.py `
  .\sample.wav .\native-features.json
```

Harness chỉ có thể pass các primitive đã đối chiếu. MFCC, flux và bandwidth
luôn bị đánh dấu `benchmark required`, không được suy diễn tương đương số học.
