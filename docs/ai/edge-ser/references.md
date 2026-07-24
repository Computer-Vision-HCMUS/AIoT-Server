# Edge SER — References

## Paper

**On-device Emotion Recognition from Spoken Language in Embedded Devices**

| | |
| --- | --- |
| Authors | Neeraj Boddeda, Sharvari Wanjari, Shashank Goud Boorgu, Prasenjit Karmakar, Sandip Chakraborty |
| Venue | IEEE PerCom Workshops 2025 |
| DOI | [10.1109/PerComWorkshops65533.2025.00161](https://doi.org/10.1109/PerComWorkshops65533.2025.00161) |

Tiêu chí chọn: bài báo uy tín, có code, dùng RAVDESS, hướng edge AI cổ điển (acoustic features + lightweight classifier).

## Code & training

| Resource | Link |
| -------- | ---- |
| Upstream repo | [prasenjit52282/embedded-audio-emotion](https://github.com/prasenjit52282/embedded-audio-emotion) |
| Extractor source | [extractor.py](https://github.com/prasenjit52282/embedded-audio-emotion/blob/main/extractor.py) |
| Colab training | [Google Colab notebook](https://colab.research.google.com/drive/1bk95wKzYq3M3umNC5rwlbOJEHAtCVMHN?usp=sharing) |
| Team demo embed | [tail0ng/edge_ai_embedded-audio-emotion](https://github.com/tail0ng/edge_ai_embedded-audio-emotion) |

## Embedded DSP

| Resource | Link |
| -------- | ---- |
| Edge Impulse MFCC (C++) | [ei_run_dsp.h](https://github.com/edgeimpulse/inferencing-sdk-cpp/blob/master/classifier/ei_run_dsp.h) |
| LibXtract | [jamiebullock/LibXtract](https://github.com/jamiebullock/LibXtract) |

Pipeline tham khảo: Audio PCM → frame → pre-emphasis → power spectrum → Mel filterbank → log → DCT → MFCC.

LibXtract được tham khảo cho native C/C++ feature extraction: RMS/Energy, Zero Crossing Rate, Spectral Centroid, Rolloff, Flux, Flatness và MFCC. Cần benchmark kết quả với pipeline Python trước khi dùng các feature này cho classifier.

## Datasets (training)

CREMA-D, RAVDESS, SAVEE, TESS — xem chi tiết trong [overview.md](overview.md).
