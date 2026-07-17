# AI Documentation

Tài liệu AI của **EmotiCare AIoT Server**, tổ chức theo lớp xử lý và bài toán.

## Cấu trúc

```text
docs/ai/
├── README.md                 ← bạn đang ở đây
├── cloud/                    ← AI chạy trên server (Gemini, Whisper)
├── edge-ser/                 ← Speech Emotion Recognition trên ESP32
└── sleep-stage/              ← Suy luận REM/NREM (gối thông minh + môi trường)
```

## Cloud AI

| Tài liệu | Mô tả |
| -------- | ----- |
| [cloud/gemini-whisper.md](cloud/gemini-whisper.md) | Tích hợp Gemini (chat/reason) và Whisper STT trên backend FastAPI |

## Edge SER (Speech Emotion Recognition)

| Tài liệu | Mô tả |
| -------- | ----- |
| [edge-ser/overview.md](edge-ser/overview.md) | Đặc tả Edge AI SER cho EmotiCare — workflow, nhãn cảm xúc, đồng bộ cloud |
| [edge-ser/references.md](edge-ser/references.md) | Bài báo, repo, Colab và link tham khảo |
| [edge-ser/research-log.md](edge-ser/research-log.md) | Nhật ký nghiên cứu: 45 đặc trưng, khả năng embed ESP32 |
| [edge-ser/artifacts/](edge-ser/artifacts/) | Snapshot code tham khảo (`classifier.h`, extractor, demo ESP32) |

Đặc tả hệ thống đầy đủ hơn: `docs/Spectification/EmotiCareAIoT/04_EdgeAI.md`.

## Sleep Stage Inference

| Tài liệu | Mô tả |
| -------- | ----- |
| [sleep-stage/problem-statement.md](sleep-stage/problem-statement.md) | Problem statement: suy luận REM/NREM từ FSR, âm thanh, nhiệt độ và môi trường |

Bài toán sleep stage là hướng nghiên cứu riêng, khác với SER của EmotiCare.

## Liên quan

- API testing: `docs/api/POSTMAN_TESTING.md`
- Dataset media: `docs/datasets/MEDIA_DATASET.md`
- Hardware / navigation: `docs/hardware/`
