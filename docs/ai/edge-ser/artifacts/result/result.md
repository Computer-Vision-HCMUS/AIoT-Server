# PerCom-aligned RAVDESS-8 results

Ngày chạy: 2026-07-25. Dataset là 1.440 RAVDESS audio-only speech WAV, giữ đủ
8 nhãn. Schema `percom45-v1` là adaptation theo PerCom: không thể coi là
reproduction 7-nhãn của bài báo.

## Primary evaluation

Stratified random holdout 20%, seed 42, 288 mẫu test:

| Artifact | Accuracy | Macro F1 | Kích thước |
| --- | ---: | ---: | ---: |
| Random Forest (30 trees, max depth 10) | 52.43% | 51.16% | C header 1,183,788 B |
| Keras MLP | 54.17% | 53.61% | — |
| TFLite MLP | 54.86% | 54.11% | 16,048 B |

Cả RF và TFLite đều qua acceptance gate `>50%`. Per-class report, order nhãn,
schema và latency được lưu trong `models/percom45.metadata.json`. RF desktop
mean inference time là 0.217 ms/vector; không suy diễn trực tiếp sang ESP32.

Actor-held-out stress test (actors 21–24) của RF chỉ đạt 30.42% accuracy /
29.31% Macro F1. Vì vậy kết quả stratified không đại diện cho khả năng tổng quát
qua speaker và không phù hợp để so sánh trực tiếp với 61.2% F1 của bài báo.

## Artifact và native status

- `models/percom_mlp.tflite`: artifact tích hợp khả thi hơn về kích thước.
- `models/percom_rf.h`: đã export float32 và native runner build thành công,
  nhưng header 1.18 MB vượt mục tiêu 256 KB của paper.
- Native parity fixture: RMS, ZCR và pause rate đạt tolerance; centroid,
  rolloff và flatness chưa đạt. MFCC, flux và bandwidth chưa benchmark với
  LibXtract. RF native **chưa được phép deploy** dù runner có thể chạy.

## End-to-end audio check

`Actor_01/03-01-03-01-01-01-01.wav` (ground truth filename `happy`) được
TFLite dự đoán `happy` với confidence 37.98%. Output:
`percom_happy_ravdess.json`. Các file `DC_h05.wav`, `happy.mp3`, và
`disgusting.mp3` không còn hiện diện trong working tree ở lần chạy này, nên
không thể báo cáo nhãn cho chúng.

> [!WARNING]
> Không coi filename của audio tùy ý là ground truth. Cần data speaker-held-out
> và native LibXtract parity trước khi dùng model trong sản phẩm.
