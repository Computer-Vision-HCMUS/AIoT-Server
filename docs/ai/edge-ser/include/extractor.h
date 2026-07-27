#pragma once

#include <array>
#include <cstddef>

namespace aiot::ser {

// Contract shared by the DSP extractor and the Random Forest classifier.
constexpr std::size_t kFeatureCount = 45;
using Features = std::array<float, kFeatureCount>;

// PerCom45 / RAVDESS feature order.  Do not reorder these values after training.
inline constexpr std::array<const char*, kFeatureCount> kFeatureNames = {
    "energy", "zero_crossing_rate", "f0", "f2", "jitter", "shimmer",
    "band_energy_proxy", "pause_rate", "spectral_centroid", "spectral_bandwidth",
    "spectral_rolloff", "spectral_flux", "spectral_flatness",
    "mfcc_1", "mfcc_2", "mfcc_3", "mfcc_4", "mfcc_5", "mfcc_6", "mfcc_7",
    "mfcc_8", "mfcc_9", "mfcc_10", "mfcc_11", "mfcc_12", "mfcc_13",
    "chroma_1", "chroma_2", "chroma_3", "chroma_4", "chroma_5", "chroma_6",
    "chroma_7", "chroma_8", "chroma_9", "chroma_10", "chroma_11", "chroma_12",
    "spectral_contrast_1", "spectral_contrast_2", "spectral_contrast_3",
    "spectral_contrast_4", "spectral_contrast_5", "spectral_contrast_6",
    "spectral_contrast_7",
};

}  // namespace aiot::ser
