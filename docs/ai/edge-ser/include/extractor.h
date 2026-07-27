#pragma once

#include <array>
#include <cstddef>

namespace aiot::ser {

// Contract shared by the DSP extractor and the Random Forest classifier.
constexpr std::size_t kFeatureCount = 45;
using Features = std::array<float, kFeatureCount>;

// RAVDESS-MFCC45-v1 feature order. Do not reorder after training.
inline constexpr std::array<const char*, kFeatureCount> kFeatureNames = {
    "mfcc_1", "mfcc_2", "mfcc_3", "mfcc_4", "mfcc_5", "mfcc_6", "mfcc_7",
    "mfcc_8", "mfcc_9", "mfcc_10", "mfcc_11", "mfcc_12", "mfcc_13",
    "mfcc_std_1", "mfcc_std_2", "mfcc_std_3", "mfcc_std_4", "mfcc_std_5",
    "mfcc_std_6", "mfcc_std_7", "mfcc_std_8", "mfcc_std_9", "mfcc_std_10",
    "mfcc_std_11", "mfcc_std_12", "mfcc_std_13",
    "chroma_1", "chroma_2", "chroma_3", "chroma_4", "chroma_5", "chroma_6",
    "chroma_7", "chroma_8", "chroma_9", "chroma_10", "chroma_11", "chroma_12",
    "rms", "zero_crossing_rate", "spectral_centroid", "spectral_bandwidth",
    "spectral_rolloff", "spectral_flatness", "spectral_contrast",
};

}  // namespace aiot::ser
