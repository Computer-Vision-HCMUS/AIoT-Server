# Edge SER — Reference Artifacts

Snapshot code tham khảo từ demo [edge_ai_embedded-audio-emotion](https://github.com/tail0ng/edge_ai_embedded-audio-emotion), upstream [embedded-audio-emotion](https://github.com/prasenjit52282/embedded-audio-emotion).

**Không phải source of truth** — firmware chính nằm tại `AIoT-Hardware/Smart Device/`.

| File | Mô tả |
| ---- | ----- |
| `classifier.h` | Random Forest export — `rf_predict()`, `rf_predict_proba()` |
| `extractor/extractor.py` | Trích xuất 45 đặc trưng acoustic (Python) |
| `smart-device/main.cpp` | Demo inference C++ trên máy tính |
| `smart-device/demo.h` | Header hỗ trợ demo |
