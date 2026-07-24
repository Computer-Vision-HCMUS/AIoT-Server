# Edge SER — Research Log

Nhật ký nghiên cứu triển khai Speech Emotion Recognition trên ESP32, dựa trên [embedded-audio-emotion](https://github.com/prasenjit52282/embedded-audio-emotion).

Tham khảo đầy đủ: [references.md](references.md).

---

## 2026-07-12 — Classifier smoke test

Đã xây dựng và chạy thử chương trình C++ độc lập trên máy tính:

- Truyền vector mẫu 45 đặc trưng (`int16_t`) vào `rf_predict()` và `rf_predict_proba()` trong `classifier.h`.
- Biên dịch bằng `g++`, thực thi thành công.
- Kết quả mẫu: **Class index 0 — Angry**, confidence cao nhất 0.48.

**Kết luận:** Luồng `feature input → classifier.h → class output` hoạt động. Chưa kiểm tra với âm thanh thực tế.

---

## 2026-07-14 — Feature vector (45 dimensions)

Theo `extractor.py`, vector đầu vào gồm:

| # | Feature |
| --- | ------- |
| 13 | MFCC |
| 12 | Chroma |
| 7 | Spectral Contrast |
| 1 | RMS / Energy |
| 1 | Zero Crossing Rate |
| 1 | F0 |
| 1 | F2 |
| 1 | Jitter |
| 1 | Shimmer |
| 1 | Band Energy *(thực tế code dùng Spectral Bandwidth)* |
| 1 | Pause Rate |
| 1 | Spectral Centroid |
| 1 | Spectral Bandwidth |
| 1 | Spectral Rolloff |
| 1 | Spectral Flux |
| 1 | Spectral Flatness |
| **45** | **Total** |

### Khả năng embed trên ESP32

#### Nhóm xanh — dễ, chắc chắn làm được (~10 features)

- RMS / Energy
- Zero Crossing Rate
- Pause Rate
- Spectral Centroid, Bandwidth, Rolloff, Flux, Flatness
- Shimmer *(theo cách tính của repo)*
- Jitter *(theo cách tính của repo, sau khi đã có MFCC)*

#### Nhóm vàng — làm được, cần so sánh với Python (~26 features)

- 13 MFCC
- 12 Chroma
- 1 F0

#### Nhóm đỏ — cần xem lại nghiêm túc

- 7 Spectral Contrast
- 1 F2
- 1 Band Energy *(hoặc đặc trưng đang bị đặt sai tên)*
- Định nghĩa Jitter / Shimmer so với chuẩn âm học

> Jitter và Shimmer dễ code nếu giữ nguyên repo; đưa vào nhóm đỏ vì cách tính có thể lệch định nghĩa chuẩn.

---

## 2026-07-16 — MFCC trên embedded

Edge Impulse xử lý khối 13 MFCC bằng C++ embedded:

```text
Audio PCM → frame → pre-emphasis → power spectrum → Mel filterbank → log → DCT → MFCC
```

Link: [ei_run_dsp.h](https://github.com/edgeimpulse/inferencing-sdk-cpp/blob/master/classifier/ei_run_dsp.h)

---

## 2026-07-24 — Đánh giá LibXtract cho native feature extraction

LibXtract là lựa chọn C/C++ để triển khai hoặc đối chiếu các acoustic feature ngoài Edge Impulse.

| Nhóm | Kết luận |
| --- | --- |
| Có thể dùng trực tiếp | RMS/Energy, Zero Crossing Rate, Spectral Centroid, Rolloff, Flux, Flatness, MFCC |
| Tự tính từ feature khác | Pause Rate từ RMS theo frame; Shimmer theo công thức hiện tại; Jitter từ chuỗi MFCC0 |
| Cần kiểm chứng với Python | Spectral Bandwidth/Variance, Spectral Flux và MFCC filterbank |

Thứ tự triển khai: bắt đầu với RMS, ZCR, Pause Rate và Shimmer; sau đó tái sử dụng một magnitude spectrum cho Centroid, Rolloff và Flatness. Chỉ thêm MFCC sau khi so sánh kết quả với pipeline huấn luyện.

Tham khảo: [LibXtract](https://github.com/jamiebullock/LibXtract).
