# Edge AI Speech Emotion Recognition

Tài liệu này mô tả module nhận diện cảm xúc từ giọng nói (SER) chạy theo hướng
edge AI. Mục tiêu là biến audio MP3/WAV thành một trong tám nhãn cảm xúc RAVDESS,
đồng thời chuẩn bị hai artifact để tích hợp thiết bị: Random Forest C header và
TensorFlow Lite MLP.

```text
MP3/WAV → decode mono PCM → PerCom45 features → RF C header | TFLite MLP → JSON
```

> [!IMPORTANT]
> Pipeline là adaptation theo bài báo PerCom Workshops 2025, không phải bản tái
> lập chính xác. Bài báo dùng 7 nhãn, còn dự án giữ nguyên 8 nhãn RAVDESS, gồm
> cả `calm`.

## Mục lục

- [Dataset](#dataset)
- [Pipeline train](#pipeline-train)
- [Pipeline test](#pipeline-test)
- [Kết quả hiện tại](#kết-quả-hiện-tại)
- [Tích hợp Edge/ESP32](#tích-hợp-edgeesp32)
- [Nguồn tham khảo](#nguồn-tham-khảo)

## Dataset

Training dùng **RAVDESS audio-only speech** với 1.440 WAV, cấu trúc mặc định:

```text
data/ravdess-speech/
└── Actor_01/
    └── 03-01-03-01-01-01-01.wav
```

Nhãn được đọc từ phần thứ ba trong tên file RAVDESS:

| Mã | Nhãn |
| --- | --- |
| 01 | `neutral` |
| 02 | `calm` |
| 03 | `happy` |
| 04 | `sad` |
| 05 | `angry` |
| 06 | `fearful` |
| 07 | `disgust` |
| 08 | `surprised` |

Không dùng filename của audio ngoài RAVDESS làm ground truth. Các file test MP3
chỉ là input suy luận, không phải mẫu đánh giá đã gắn nhãn.

## Pipeline train

### Cài đặt

Yêu cầu Python 3.12 và `ffmpeg` nếu cần decode MP3. Tại thư mục này:

```powershell
.\.venv\Scripts\python.exe -m pip install -r .\pipeline\requirements.txt
```

### Train và export

```powershell
.\.venv\Scripts\python.exe .\pipeline\train_percom.py `
  --dataset .\data\ravdess-speech `
  --output .\models
```

Pipeline cố định seed 42, cache matrix đặc trưng trong
`models/percom45_features.npz`, và train hai model trên cùng vector
`percom45-v1` 45 chiều:

1. **Random Forest**: 30 cây, `max_depth=10`, export qua `emlearn` thành
   `models/percom_rf.h`.
2. **MLP**: chuẩn hóa input, Dense 96 → 48 → 8, export thành
   `models/percom_mlp.tflite`.

Vector PerCom45 gồm 13 scalar/prosodic features (energy, ZCR, F0/F2, jitter,
shimmer, pause rate, centroid, bandwidth, rolloff, flux, flatness), 13 MFCC
means, 12 chroma means và 7 spectral-contrast means.

### Train thực sự làm gì?

1. **Quét và đọc nhãn** — script chỉ lấy các WAV `03-01-*.wav`. Nó đọc emotion
   code và actor ID từ filename RAVDESS, nên không cần một file CSV nhãn riêng.
2. **Decode audio** — `librosa` đọc audio mono ở sample rate gốc; không ép toàn
   bộ audio về cùng sample rate để giữ hành vi extractor tham chiếu.
3. **Chia frame và trích xuất PerCom45** — audio được phân tích theo cửa sổ
   FFT 2.048 samples, hop 512 samples. Các feature theo frame được lấy trung
   bình thành một vector cố định 45 số cho mỗi file. Model không nhận trực tiếp
   waveform hoặc MP3 bytes.
4. **Cache feature matrix** — `features`, `labels`, `actors` được lưu vào
   `percom45_features.npz`. Các lần chạy sau tái sử dụng cache; xóa file này
   nếu thay extractor, dataset hoặc feature schema.
5. **Chia train/test** — stratified 80/20 bảo đảm mỗi lớp có tỷ lệ gần giống
   nhau trong tập test. Đây là phép đo chính và có speaker overlap. Stress test
   tách toàn bộ actors 21–24, nghiêm ngặt hơn vì model phải gặp speaker mới.
6. **Huấn luyện hai model** — RF học các rule dạng cây từ 45 số. MLP trước hết
   `adapt` lớp Normalization trên train set, rồi học trọng số qua backpropagation
   với early stopping theo `val_accuracy`; test set không được dùng để fit
   normalizer hoặc chọn epoch.
7. **Đo và xuất artifact** — script tính accuracy, Macro F1 và per-class
   precision/recall/F1. RF được xuất C float32 bằng `emlearn`; Keras MLP được
   convert TFLite và chạy lại bằng TFLite Interpreter trên cùng test set để
   tránh báo cáo nhầm metric của Keras thay cho artifact deploy.

Accuracy là tỷ lệ dự đoán đúng tổng thể. Macro F1 là trung bình F1 không trọng
số theo lớp, giúp nhìn rõ hơn hiệu năng ở lớp ít mẫu như `neutral`. Artifact
chỉ được coi là qua acceptance gate khi accuracy của chính model `>50%`.
Metadata đầy đủ nằm tại `models/percom45.metadata.json`.

## Pipeline test

### Suy luận TFLite

```powershell
.\.venv\Scripts\python.exe .\pipeline\predict.py .\artifacts\test\happy.mp3 `
  --artifact percom45-mlp `
  --output .\artifacts\result\percom_happy.json
```

JSON output bao gồm model/schema version, nhãn dự đoán, confidence, top-3,
sample rate, duration, số feature và inference latency.

### Một lần test thực sự diễn ra như thế nào?

1. `predict.py` đọc metadata để kiểm tra model có schema `percom45-v1` và lấy
   đúng thứ tự tám labels. Thứ tự này là một phần của contract model: thay đổi
   thứ tự sẽ làm index output ánh xạ sang nhãn sai.
2. Input MP3/WAV được `librosa`/backend decode về mono PCM. MP3 chỉ là định
   dạng lưu trữ; neural model không infer trực tiếp trên compressed MP3.
3. `percom_features.extract_features()` chạy chính xác schema train và tạo
   vector `float32` 45 chiều. Script dừng nếu model input shape không phải 45,
   nhằm ngăn chạy nhầm model 210-feature cũ.
4. TFLite Interpreter nạp `percom_mlp.tflite`, cấp phát tensor, đặt vector ở
   input tensor và gọi `invoke()`. Output là 8 xác suất softmax theo label
   order trong metadata.
5. Xác suất cao nhất trở thành `emotion_label`; ba phần tử lớn nhất tạo
   `top_k_predictions`. `confidence_score` là softmax score, không phải mức
   chắc chắn tuyệt đối hoặc xác suất đúng trên mọi domain.
6. JSON được ghi vào `artifacts/result/` để có thể review lại input, schema,
   model, dự đoán và latency mà không cần chạy lại.

### Chạy toàn bộ mẫu test

```powershell
.\.venv\Scripts\python.exe .\pipeline\predict.py .\artifacts\test\DC_h05.wav `
  --output .\artifacts\result\percom_DC_h05.json
.\.venv\Scripts\python.exe .\pipeline\predict.py .\artifacts\test\happy.mp3 `
  --output .\artifacts\result\percom_happy.json
.\.venv\Scripts\python.exe .\pipeline\predict.py .\artifacts\test\disgusting.mp3 `
  --output .\artifacts\result\percom_disgusting.json
```

### Kiểm tra native feature parity

```powershell
.\.venv\Scripts\python.exe .\pipeline\check_feature_parity.py `
  .\sample.wav .\native-features.json
```

Harness chỉ xác nhận những primitive đã được benchmark. Không được coi MFCC,
spectral flux hoặc spectral bandwidth là tương đương số học với LibXtract cho
đến khi có fixture native pass.

Native parity là test khác với ML accuracy: nó kiểm tra Python và C/C++ có tạo
ra cùng feature vector hay không. Nếu vector khác, Random Forest có thể đưa ra
nhãn khác dù C header export hoàn toàn đúng. Vì thế phải pass parity trước khi
đưa native RF lên ESP32.

## Kết quả hiện tại

RAVDESS-8, stratified random holdout 20%, seed 42 (288 mẫu test):

| Artifact | Accuracy | Macro F1 | Kích thước |
| --- | ---: | ---: | ---: |
| Random Forest | 52.43% | 51.16% | C header 1,183,788 B |
| Keras MLP | 54.17% | 53.61% | — |
| TFLite MLP | 54.86% | 54.11% | 16,048 B |

Actor-held-out stress test của RF cho actors 21–24 chỉ đạt 30.42% accuracy và
29.31% Macro F1. Do đó số liệu stratified không đại diện cho khả năng tổng quát
giữa các speaker, và không thể so sánh trực tiếp với 61.2% F1 trong bài báo.

Kết quả suy luận mới nhất trên `artifacts/test/`:

| Input | Dự đoán | Confidence |
| --- | --- | ---: |
| `DC_h05.wav` | `happy` | 91.82% |
| `happy.mp3` | `disgust` | 95.89% |
| `disgusting.mp3` | `disgust` | 91.49% |

Kết quả chi tiết được lưu trong `artifacts/result/percom_*.json`. Không dùng
tên file làm nhãn thật nếu chưa được xác nhận.

## Tích hợp Edge/ESP32

- `models/percom_mlp.tflite` là artifact gọn hơn và phù hợp hơn để đánh giá
  tích hợp TFLite Micro.
- `models/percom_rf.h` đã export float32 và
  `artifacts/smart-device/ser_mp3.cpp` build được bằng C++17 với `ffmpeg`.
- RF C header hiện 1.18 MB, vượt mục tiêu 256 KB được báo cáo trong bài paper.
- Native extractor chưa đạt parity với Python ở centroid, rolloff và flatness;
  MFCC, flux và bandwidth chưa benchmark với LibXtract. Vì vậy **chưa deploy
  Random Forest native lên ESP32**.

Xem chi tiết kết quả tại [`artifacts/result/result.md`](artifacts/result/result.md)
và hướng dẫn pipeline tại [`pipeline/README.md`](pipeline/README.md).

## Nguồn tham khảo

- Boddeda et al., *On-device Emotion Recognition from Spoken Language in
  Embedded Devices*, IEEE PerCom Workshops 2025.
  [DOI: 10.1109/PerComWorkshops65533.2025.00161](https://doi.org/10.1109/percomworkshops65533.2025.00161)
- [Repository tham chiếu embedded-audio-emotion](https://github.com/prasenjit52282/embedded-audio-emotion)
- [LibXtract](https://github.com/jamiebullock/LibXtract) cho native DSP
- [`references.md`](references.md): tài liệu, upstream code và trạng thái
  benchmark LibXtract.
- [`overview.md`](overview.md): tổng quan nghiên cứu, kiến trúc và giới hạn.
