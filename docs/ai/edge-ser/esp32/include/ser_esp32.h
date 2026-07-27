#pragma once

#include <stdint.h>
#include <stddef.h>
#include <complex>

namespace aiot::ser::esp32 {

constexpr int kFeatureCount = 45;
constexpr int kClassCount = 8;
constexpr int kFftSize = 2048;
constexpr int kSpectrumBins = kFftSize / 2 + 1;

/** Allocate this once (global/static), not on a FreeRTOS task stack. */
struct ExtractorWorkspace {
    std::complex<float> fft[kFftSize];
    float power[kSpectrumBins];
};

struct Prediction {
    int class_index;
    const char* label;
    float confidence;
    float probabilities[kClassCount];
};

/**
 * Run the compact embedded model on a completed RAVDESS-MFCC45-v1 vector.
 * This function is allocation-free and safe to call from an ESP32 task.
 */
Prediction classify_features(const float features[kFeatureCount]);

/**
 * Convert mono signed PCM directly into the RAVDESS-MFCC45-v1 vector used by
 * classify.h. PCM must contain at least 2048 samples. No filesystem, heap,
 * WAV parser, ffmpeg, or ESP-IDF dependency is used.
 */
bool extract_features(const int16_t* pcm, size_t sample_count, uint32_t sample_rate,
                      ExtractorWorkspace& workspace, float features[kFeatureCount]);

/** Complete on-device stage: mono PCM -> 45 features -> emotion. */
bool classify_pcm(const int16_t* pcm, size_t sample_count, uint32_t sample_rate,
                  ExtractorWorkspace& workspace, Prediction& prediction);

}  // namespace aiot::ser::esp32
