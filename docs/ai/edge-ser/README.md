# Edge speech-emotion recognition

This directory implements one clear pipeline:

```text
audio -> extractor.h -> 45 PerCom45 features -> classify.h -> 8 RAVDESS emotions
```

`extractor.h` is the feature-schema contract. `classify.h` is the generated
float32 Random Forest classifier. Neither header is an executable by itself;
`tools/native_pipeline.cpp` calls them in sequence.

## Layout

```text
include/       extractor.h and generated classify.h
tools/         training code and native runner
samples/       one WAV smoke-test input
reports/       metrics and label order from the latest training run
docs/          method and paper references
data/          local RAVDESS training data (not committed)
```

## Run the two stages

Install a C++17 compiler and `ffmpeg`, then run from this directory:

```powershell
New-Item -ItemType Directory -Force build
g++ -std=c++17 -O2 .\tools\native_pipeline.cpp -o .\build\ser_pipeline.exe

# Stage 1: audio -> exactly 45 features
.\build\ser_pipeline.exe extract .\samples\sample.wav .\build\features.json

# Stage 2: 45 features -> emotion label
.\build\ser_pipeline.exe classify .\build\features.json
```

Or run both stages:

```powershell
python .\tools\run_pipeline.py .\samples\sample.wav
```

## Retrain

The RAVDESS audio-only speech files must be in `data/ravdess-speech`. Create a
Python environment, install `tools/requirements.txt`, then run:

```powershell
python .\tools\train.py --dataset .\data\ravdess-speech
```

Training overwrites `include/classify.h` and `reports/train-metrics.json`.
Only deploy them after native feature-parity validation; model and extractor
are one contract.

Read [the methodology](docs/methodology.md) before interpreting predictions.
