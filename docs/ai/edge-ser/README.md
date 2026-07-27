# Nhận diện cảm xúc từ giọng nói trên Edge

Thư mục này chỉ duy trì một pipeline rõ ràng:

```text
audio -> PCM mono -> extractor.h -> 45 đặc trưng âm học -> classify.h -> 8 cảm xúc RAVDESS
```

`extractor.h` định nghĩa hợp đồng: 13 MFCC mean, 13 MFCC std, 12 chroma và 7
đặc trưng phổ. `classify.h` là mô hình Random Forest float32 được train lại từ
chính native extractor và export bằng `tools/export_model.py`. Hai file header
không tự chạy độc lập; `tools/native_pipeline.cpp` gọi chúng tuần tự.

## Cấu trúc thư mục

```text
include/       extractor.h và classify.h đã sinh từ quá trình train
tools/         mã train và chương trình chạy native
samples/       một file WAV dùng kiểm thử nhanh
reports/       chỉ số của lần train gần nhất
docs/          phương pháp và tài liệu tham khảo
data/          dữ liệu RAVDESS cục bộ, không đưa lên Git
```

## Chạy hai giai đoạn

Cài C++17 compiler và `ffmpeg`, sau đó chạy tại thư mục này:

```powershell
New-Item -ItemType Directory -Force build
g++ -std=c++17 -O2 .\tools\native_pipeline.cpp -o .\build\ser_pipeline.exe

# Giai đoạn 1: audio -> đúng 45 đặc trưng
.\build\ser_pipeline.exe extract .\samples\sample.wav .\build\features.json

# Giai đoạn 2: 45 đặc trưng -> nhãn cảm xúc
.\build\ser_pipeline.exe classify .\build\features.json
```

Hoặc chạy liên tiếp hai giai đoạn:

```powershell
python .\tools\run_pipeline.py .\samples\sample.wav
```

## Huấn luyện lại

Các file audio-only speech của RAVDESS phải nằm trong `data/ravdess-speech`.
Tạo môi trường Python, cài `tools/requirements.txt`, sau đó chạy:

```powershell
conda run -n base python .\tools\train.py --dataset .\data\ravdess-speech
```

Lệnh train sẽ ghi đè `include/classify.h` và `reports/train-metrics.json`.
Nó gọi chính binary native để trích feature cho RAVDESS, vì vậy model và pipeline
triển khai luôn dùng cùng một định nghĩa 45 đặc trưng.

Đọc [phương pháp](docs/methodology.md) và [báo cáo kết quả](reports/bao-cao.md)
trước khi diễn giải kết quả dự đoán.
