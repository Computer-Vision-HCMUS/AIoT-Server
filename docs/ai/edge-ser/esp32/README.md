# ESP32 PCM emotion component

This folder is intentionally independent from `AIoT-Hardware`. It contains a
fixed-buffer PCM extractor plus a compact generated classifier for the existing
45-float `ravdess-mfcc45-v1` contract.

## Contents

- `include/classify.h`: 12-tree, depth-8 floating-point model (about 307 KiB source).
- `include/ser_esp32.h` and `src/ser_esp32.cpp`: allocation-free PCM extractor
  and inference API.
- `tools/train_esp32.py`: regenerates the compact model from the native feature cache.

## Integration contract

The caller captures mono signed PCM from I2S, allocates one workspace globally
or statically, then runs the complete local stage:

```cpp
static aiot::ser::esp32::ExtractorWorkspace workspace;
aiot::ser::esp32::Prediction prediction;
bool ok = aiot::ser::esp32::classify_pcm(
    pcm_samples, pcm_sample_count, sample_rate_hz, workspace, prediction);
```

This component does not own I2S pins, tasks, buffers, Wi-Fi, or UI. It can be
copied into an ESP-IDF component or an Arduino library without modifying the
hardware repository.

`ExtractorWorkspace` is about 20 KiB and must not be allocated on the default
FreeRTOS task stack. The input PCM buffer is owned by the caller; it must contain
at least 2,048 samples. The component has no I2S pin, task, filesystem, ffmpeg,
WAV, network, or UI dependency.
