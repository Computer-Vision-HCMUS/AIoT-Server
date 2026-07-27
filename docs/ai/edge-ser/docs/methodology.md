# Methodology: RAVDESS-8 speech emotion recognition

## Scope

This module detects emotion **from acoustic speech signals**, not from words or
facial images.  It is based primarily on RAVDESS audio-only speech: 1,440
utterances from 24 professional actors and eight labels: `neutral`, `calm`,
`happy`, `sad`, `angry`, `fearful`, `disgust`, and `surprised`.

The main dataset reference is Livingstone & Russo (2018), *The Ryerson
Audio-Visual Database of Emotional Speech and Song (RAVDESS)*.  The embedded
design is also informed by Boddeda et al. (2025), *On-device Emotion
Recognition from Spoken Language in Embedded Devices*.  PerCom is a design
reference only: this project retains RAVDESS's eight labels, while that paper
uses a different seven-label taxonomy.

## Deployed contract

```text
WAV/MP3 -> mono PCM -> extractor.h -> 45 float features -> classify.h -> emotion
```

`extractor.h` defines the stable `percom45-v1` ordering.  It contains 13
prosodic/spectral scalar values, 13 mean MFCCs, 12 mean chroma values, and 7
mean spectral-contrast values. `classify.h` is a generated float32 Random
Forest: 30 trees, maximum depth 10, trained with `seed=42` and balanced class
weights. It accepts exactly those 45 values and returns a class index.

The native runner decodes audio using `ffmpeg`, extracts features, serializes
them to JSON, then invokes the classifier.  The JSON file makes the two steps
inspectable and independently runnable.

## Evaluation and limitation

The latest training report is `../reports/train-metrics.json`. The primary
metric is a stratified 80/20 holdout. Because speakers occur in both splits, it
is optimistic; the actor-held-out result is the relevant warning for new
speakers. RAVDESS is acted North-American English recorded under controlled
conditions, so this is a prototype rather than a clinical emotion assessment.

Before firmware deployment, validate feature parity between the C++ extractor
and the training implementation. A classifier trained on mismatched feature
definitions is invalid even if both components compile.
