# Báo cáo kết quả nhận diện cảm xúc giọng nói

## Phiên bản đánh giá

- Schema: `ravdess-mfcc45-v1`
- Dataset: RAVDESS audio-only speech
- Số mẫu: 1.440 WAV, 24 diễn viên, 8 nhãn cảm xúc
- Model: Random Forest, 30 cây, độ sâu tối đa 10, `class_weight=balanced`, seed 42
- Triển khai: `audio -> PCM mono -> 45 float -> classify.h -> emotion`

## Đặc trưng đầu vào

Vector có đúng 45 giá trị float, theo thứ tự trong `../include/extractor.h`:

- 13 giá trị trung bình MFCC
- 13 độ lệch chuẩn MFCC
- 12 chroma
- RMS, zero-crossing rate, spectral centroid, spectral bandwidth, spectral rolloff,
  spectral flatness và spectral contrast

Extractor dùng để tạo tập train cũng chính là extractor C++ chạy khi triển khai.
Vì vậy `classify.h` luôn nhận đúng schema mà nó đã được train.

## Kết quả train

| Giao thức | Accuracy | Macro-F1 |
| --- | ---: | ---: |
| Stratified holdout 80/20, seed 42 | 46.88% | 44.74% |
| Giữ riêng actors 21–24 | 31.67% | 28.66% |

Phân bố nhãn gồm 96 mẫu `neutral` và 192 mẫu cho mỗi nhãn còn lại: `calm`,
`happy`, `sad`, `angry`, `fearful`, `disgust`, `surprised`.

## Diễn giải

Kết quả actor-held-out thấp hơn holdout ngẫu nhiên, cho thấy mô hình vẫn chịu ảnh
hưởng đáng kể bởi khác biệt giữa người nói. Vì vậy chỉ số actor-held-out nên được
dùng làm mốc thực tế hơn với giọng nói mới.

RAVDESS là dữ liệu tiếng Anh Bắc Mỹ được diễn xuất trong điều kiện kiểm soát.
Mô hình chỉ phù hợp cho demo/nghiên cứu nhận diện cảm xúc từ âm học; không dùng
cho chẩn đoán sức khỏe tâm lý hoặc đánh giá cảm xúc có hệ quả cao.

## Tái lập

Từ thư mục `edge-ser`, build native pipeline trước, rồi train bằng Anaconda base:

```powershell
New-Item -ItemType Directory -Force build
g++ -std=c++17 -O2 .\tools\native_pipeline.cpp -o .\build\ser_pipeline.exe
conda run -n base python .\tools\train.py --dataset .\data\ravdess-speech
```

Nếu `ffmpeg` không có trong `PATH` của Anaconda, thêm
`--ffmpeg <đường-dẫn-ffmpeg.exe>`. Số liệu máy đọc được nằm trong
`train-metrics.json`.
