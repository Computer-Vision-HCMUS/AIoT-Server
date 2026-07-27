# Hướng dẫn làm Edge Speech Emotion Recognition (không dùng AI hỗ trợ)

Tài liệu này dành cho teammate thực hiện thủ công toàn bộ quy trình nhận diện cảm xúc giọng nói trên máy tính và ESP32. Không dùng chatbot, công cụ sinh mã, hay dịch vụ AI để tạo code/dataset/kết quả. Mọi thay đổi phải được hiểu, tự gõ/kiểm tra và lưu lại trong commit riêng.

## 1. Mục tiêu và cấu trúc

Pipeline của thư mục `docs/ai/edge-ser` là:

```text
WAV/PCM mono -> extractor 45 feature -> classifier -> 8 nhãn RAVDESS
```

Các nhãn là: `neutral`, `calm`, `happy`, `sad`, `angry`, `fearful`, `disgust`, `surprised`.

Thư mục quan trọng:

```text
tools/train.py              train model native và export include/classify.h
tools/run_pipeline.py       chạy mẫu WAV: extract rồi classify
tools/train_esp32.py        export model nhỏ hơn cho ESP32
tools/verify_esp32_extractor.cpp
include/                    header native được sinh từ train
esp32/                      component độc lập cho ESP32
samples/sample.wav          mẫu kiểm thử nhanh
reports/                    metrics, log train và báo cáo
data/ravdess-speech/        dataset cục bộ, không commit Git
```

## 2. Chuẩn bị môi trường Windows

Mở PowerShell tại thư mục `AIoT-Server/docs/ai/edge-ser`.

1. Cài Python 3.12+ và Git.
2. Cài C++ compiler hỗ trợ C++17: MSYS2/MinGW-w64 hoặc Visual Studio Build Tools.
3. Cài `ffmpeg`, sau đó kiểm tra:

```powershell
python --version
git --version
g++ --version
ffmpeg -version
```

4. Tạo môi trường Python và cài dependency:

```powershell
conda create -n edge-ser python=3.12 -y
conda activate edge-ser
python -m pip install --upgrade pip
python -m pip install -r .\tools\requirements.txt
```

Nếu không dùng Conda, tạo `.venv` bằng `python -m venv .venv`, kích hoạt `.\.venv\Scripts\Activate.ps1`, rồi chạy hai lệnh `pip` ở trên.

Không commit `.venv`, `build/`, `data/`, `*.joblib`, file WAV tải về hay các token/API key.

## 3. Lấy RAVDESS đúng cách

RAVDESS là dataset phát hành trên Zenodo, không có Git repository chính thức cần clone. Dùng bản **Audio_Speech_Actors_01-24** từ record Zenodo 1188976. Đây là phần dữ liệu được `train.py` chấp nhận: đúng 1.440 file speech WAV có tên `03-01-*.wav`.

```powershell
New-Item -ItemType Directory -Force .\data | Out-Null
Invoke-WebRequest `
  -Uri "https://zenodo.org/records/1188976/files/Audio_Speech_Actors_01-24.zip?download=1" `
  -OutFile .\data\ravdess-speech.zip
Expand-Archive -LiteralPath .\data\ravdess-speech.zip -DestinationPath .\data\ravdess-speech -Force
(Get-ChildItem .\data\ravdess-speech -Recurse -Filter '03-01-*.wav').Count
```

Lệnh cuối phải in `1440`. Nếu không phải 1440, kiểm tra lại: đã tải nhầm song/video, giải nén lồng thêm một cấp thư mục, hoặc file tải không hoàn tất. Không train khi số file sai.

### Clone repository tham khảo

Repository tham khảo cho cách export model C/C++ là `prasenjit52282/embedded-audio-emotion`; nó **không phải** RAVDESS và không được dùng dataset/model của nó cho dự án này.

```powershell
New-Item -ItemType Directory -Force .\third_party | Out-Null
git clone https://github.com/prasenjit52282/embedded-audio-emotion.git .\third_party\embedded-audio-emotion
```

Chỉ dùng để đọc/đối chiếu cách export. Pipeline hiện tại dùng `tools/export_model.py`, vì vậy không copy đè header hay model từ repository tham khảo.

## 4. Build và chạy sample trước khi train

Build native pipeline:

```powershell
New-Item -ItemType Directory -Force .\build | Out-Null
g++ -std=c++17 -O2 .\tools\native_pipeline.cpp -o .\build\ser_pipeline.exe
```

Chạy sample từng bước để dễ chẩn đoán:

```powershell
.\build\ser_pipeline.exe extract .\samples\sample.wav .\build\sample.features.json
.\build\ser_pipeline.exe classify .\build\sample.features.json
```

Hoặc chạy liên tiếp:

```powershell
python .\tools\run_pipeline.py .\samples\sample.wav
```

Lưu console output và `build/sample.features.json` vào báo cáo test. Nếu lỗi `ffmpeg not found`, thêm thư mục chứa `ffmpeg.exe` vào `PATH`, mở PowerShell mới rồi build/chạy lại.

## 5. Train lại model native

Sau khi sample chạy được và dataset có đúng 1.440 file:

```powershell
conda activate edge-ser
python .\tools\train.py `
  --dataset .\data\ravdess-speech `
  --extractor .\build\ser_pipeline.exe `
  --workers 4
```

Script sẽ:

1. Dùng **native extractor đang triển khai** để lấy 45 feature từ mọi WAV.
2. Lưu cache `build/ravdess_mfcc45_features.npz`.
3. Train Extra Trees 100 cây.
4. Ghi metrics vào `reports/train-metrics.json` và log vào `reports/train.log`.
5. Ghi đè `include/classify.h` bằng model mới.

Đọc cả `primary_evaluation` và `actor_held_out_evaluation`. Chỉ số actor-held-out phản ánh tốt hơn khi gặp người nói mới. Không chỉ báo cáo accuracy; phải báo cáo cả macro F1, confusion matrix (nếu bổ sung script) và số mẫu theo lớp.

Để thử cải thiện model một cách có kiểm soát, thay đổi một biến mỗi lần (ví dụ số cây, `max_depth`, hoặc feature), train lại cùng split/seed 42, rồi so sánh metrics với baseline trong báo cáo. Không chọn model chỉ vì nó đoán đúng một file sample.

## 6. Export và kiểm tra component ESP32

Sau khi train native thành công, export model rút gọn cho ESP32 từ cache feature:

```powershell
python .\tools\train_esp32.py `
  --cache .\build\ravdess_mfcc45_features.npz `
  --output .\esp32\include\classify.h `
  --trees 12 `
  --depth 8
```

Model ESP32 là Random Forest nhỏ hơn, nên phải đánh giá lại riêng về kích thước và độ chính xác; không dùng chỉ số Extra Trees native để tuyên bố kết quả trên thiết bị.

Kiểm tra extractor ESP32 ở desktop trước khi flash firmware:

```powershell
g++ -std=c++17 -O2 `
  -I .\esp32\include `
  .\tools\verify_esp32_extractor.cpp .\esp32\src\ser_esp32.cpp `
  -o .\build\verify_esp32_extractor.exe
```

`verify_esp32_extractor.exe` nhận PCM raw mono signed 16-bit và sample rate. Hãy ghi rõ cách chuyển WAV sang PCM (ví dụ bằng ffmpeg), sample rate đã dùng và sai số feature khi so với native extractor.

## 7. Tích hợp vào ESP32 sample

1. Sao chép các file sau vào component ESP-IDF/Arduino của firmware sample:

```text
esp32/include/classify.h
esp32/include/ser_esp32.h
esp32/src/ser_esp32.cpp
```

2. Thêm `ser_esp32.cpp` vào danh sách source của component; thêm thư mục `include` vào include path.
3. Để `ExtractorWorkspace` ở biến `static` hoặc global, **không** tạo trên stack của FreeRTOS task (khoảng 20 KiB).
4. I2S phải cung cấp PCM mono `int16_t`, tối thiểu 2.048 samples. Không truyền stereo interleaved trực tiếp; phải chọn một kênh hoặc downmix trước.

Ví dụ gọi từ firmware (phần lấy `pcm_samples` từ I2S do firmware sample chịu trách nhiệm):

```cpp
#include "ser_esp32.h"

static aiot::ser::esp32::ExtractorWorkspace ser_workspace;

bool classify_captured_audio(
    const int16_t* pcm_samples,
    size_t pcm_sample_count,
    uint32_t sample_rate_hz) {
  aiot::ser::esp32::Prediction prediction{};
  const bool ok = aiot::ser::esp32::classify_pcm(
      pcm_samples, pcm_sample_count, sample_rate_hz, ser_workspace, prediction);
  if (!ok) return false;

  Serial.printf("emotion=%s confidence=%.3f\\n", prediction.label, prediction.confidence);
  return true;
}
```

Không gọi module này trong ISR. Capture PCM trước, sau đó infer ở task thường. Không gửi audio thô hoặc kết quả lên mạng nếu chưa có yêu cầu/quyền riêng tư phù hợp.

## 8. Checklist trước khi bàn giao

- [ ] `ffmpeg`, compiler và Python environment hoạt động.
- [ ] Dataset speech có đúng 1.440 WAV.
- [ ] `samples/sample.wav` chạy được qua native pipeline.
- [ ] `reports/train-metrics.json` có accuracy và macro F1 trước/sau cải tiến.
- [ ] `include/classify.h` được sinh từ lần train đã ghi nhận.
- [ ] `esp32/include/classify.h` được export từ cache tương ứng.
- [ ] ESP sample compile thành công; workspace không nằm trên task stack.
- [ ] Test sample mục tiêu dự đoán `happy` được lưu output/ảnh serial log.
- [ ] Không có dataset, model trung gian, token hoặc file audio cá nhân trong commit.
