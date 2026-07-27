# Kết quả mong muốn: Edge Speech Emotion Recognition

## Mục tiêu cần bàn giao

1. Chạy được sample bằng pipeline native và có kết quả dự đoán cuối là **`happy`**.
2. Cải thiện độ chính xác model so với baseline hiện tại, bằng thay đổi có kiểm soát và có số liệu chứng minh.
3. Export model phù hợp ESP32 và tích hợp vào ESP sample để infer PCM mono cục bộ.
4. Toàn bộ quá trình thực hiện thủ công, không dùng AI hỗ trợ để sinh code, kết quả hay báo cáo.

## Tiêu chí nghiệm thu

### A. Test sample `happy`

- Dùng một file WAV sample đã biết nhãn mong muốn là `happy` (có thể thay `samples/sample.wav` bằng file kiểm thử được ghi rõ nguồn).
- Chạy:

```powershell
python .\tools\run_pipeline.py .\samples\sample.wav
```

- Console phải in nhãn cuối là `happy`.
- Lưu file feature JSON, command đã chạy và output console vào báo cáo. Nếu confidence được in ở ESP, ghi lại confidence; không tự đặt ngưỡng confidence khi chưa có đánh giá trên tập validation.

### B. Cải thiện model

- Chạy baseline trước, lưu `reports/train-metrics.json` và `reports/train.log` với tên/commit rõ ràng.
- Dataset phải là RAVDESS audio-only speech đủ 1.440 WAV; không trộn data không rõ nguồn.
- Báo cáo tối thiểu:
  - stratified 80/20 holdout: accuracy và macro F1;
  - actor-held-out (actors 21–24): accuracy và macro F1;
  - tham số model, seed, số feature, số cây/độ sâu và thời gian train;
  - so sánh baseline với bản đề xuất.
- Bản đề xuất chỉ được nhận là “cải thiện” khi ít nhất macro F1 actor-held-out **không giảm** và có một chỉ số đánh giá tăng so với baseline. Nếu có đánh đổi kích thước/latency cho ESP32, phải ghi rõ.

### C. Tích hợp ESP sample

- Firmware sample compile thành công với `ser_esp32.cpp`, `ser_esp32.h`, `classify.h`.
- Input là PCM signed 16-bit mono, tối thiểu 2.048 samples; sample rate được ghi trong log.
- `ExtractorWorkspace` dùng static/global, không đặt trên FreeRTOS task stack.
- Serial log hoặc UI phải hiển thị nhãn dự đoán; test mục tiêu hiển thị `happy`.
- Không thực hiện network call trong inference path và không ghi audio thô vào repository.

## Deliverables

- Code thay đổi và commit rõ ràng.
- `reports/train-metrics.json`, `reports/train.log` và báo cáo ngắn trước/sau.
- Output native pipeline cho sample `happy`.
- Ảnh/chụp serial log ESP sample dự đoán `happy`.
- Ghi chú tái lập: phiên bản Python, compiler, ffmpeg, board ESP32, sample rate và command đã dùng.

## Deadline

**09:00 sáng Thứ Năm, 30/07/2026 (giờ Việt Nam, UTC+7).**

Nếu có blocker (không tải được dataset, train lỗi, model không đạt `happy`, hoặc firmware không compile), báo ngay kèm command, log lỗi và phần đã thử; không chờ tới deadline mới báo.
