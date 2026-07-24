# Edge SER — Legacy artifacts

Các file trong thư mục này là snapshot/reference của pipeline cũ; không dùng để
đánh giá hoặc phát hành model mới.

| File | Mô tả |
| ---- | ----- |
| `classifier.h` | Random Forest export cũ; thiếu model/scaler train gốc. |
| `extractor/extractor.py` | Extractor 45 chiều cũ, dùng để đối chiếu feature parity. |
| `smart-device/ser_mp3.cpp` | Runner C++ MP3 đã khôi phục cho baseline cũ. |
| `result/` | Kết quả baseline cũ, không đạt tiêu chí chất lượng. |

Pipeline hiện hành nằm ở [`../pipeline`](../pipeline):

1. `train_ravdess.py` trích xuất feature từ RAVDESS audio-only speech, giữ hẳn
   một nhóm actor cho test, và dừng khi test accuracy không vượt 50%.
2. Khi đạt mục tiêu, script xuất `ravdess_ser.tflite` cùng metadata labels và
   báo cáo đánh giá.
3. `predict.py` nhận MP3/WAV, trích xuất cùng schema và in JSON gồm nhãn,
   confidence, top-3 dự đoán và latency.

Model/dataset sinh trong lúc train không được commit; xem `.gitignore` ở root
`edge-ser`. Firmware production vẫn thuộc `AIoT-Hardware/Smart Device/`.
