#include "ser_esp32.h"

#include "classify.h"

#include <algorithm>
#include <cmath>
#include <cstring>

namespace aiot::ser::esp32 {

Prediction classify_features(const float features[kFeatureCount]) {
    static constexpr const char* kLabels[kClassCount] = {
        "angry", "calm", "disgust", "fearful", "happy", "neutral", "sad", "surprised"};
    Prediction prediction{};
    prediction.class_index = rf_predict(features, kFeatureCount);
    rf_predict_proba(features, kFeatureCount, prediction.probabilities, kClassCount);
    prediction.label = kLabels[prediction.class_index];
    prediction.confidence = prediction.probabilities[prediction.class_index];
    return prediction;
}

namespace {
constexpr float kPi = 3.14159265358979323846f;

void fft(std::complex<float>* values) {
    for (size_t i = 1, reversed = 0; i < kFftSize; ++i) {
        size_t bit = kFftSize >> 1U;
        for (; reversed & bit; bit >>= 1U) reversed ^= bit;
        reversed ^= bit;
        if (i < reversed) std::swap(values[i], values[reversed]);
    }
    for (size_t block = 2; block <= kFftSize; block <<= 1U) {
        const std::complex<float> step(std::cos(2.0f * kPi / block), std::sin(2.0f * kPi / block));
        for (size_t start = 0; start < kFftSize; start += block) {
            std::complex<float> rotation(1.0f, 0.0f);
            for (size_t offset = 0; offset < block / 2; ++offset) {
                const auto even = values[start + offset];
                const auto odd = values[start + offset + block / 2] * rotation;
                values[start + offset] = even + odd;
                values[start + offset + block / 2] = even - odd;
                rotation *= step;
            }
        }
    }
}

float mean(const float* values, int count) {
    float sum = 0.0f;
    for (int i = 0; i < count; ++i) sum += values[i];
    return count == 0 ? 0.0f : sum / count;
}
float hertz_to_mel(float hertz) { return 2595.0f * std::log10(1.0f + hertz / 700.0f); }
float mel_to_hertz(float mel) { return 700.0f * (std::pow(10.0f, mel / 2595.0f) - 1.0f); }
}

bool extract_features(const int16_t* pcm, size_t sample_count, uint32_t sample_rate,
                      ExtractorWorkspace& workspace, float features[kFeatureCount]) {
    if (pcm == nullptr || features == nullptr || sample_rate == 0 || sample_count < kFftSize) return false;
    float mfcc_sum[13]{}, mfcc_sq[13]{}, chroma_sum[12]{}, contrast_sum[7]{};
    float rms_sum = 0, centroid_sum = 0, bandwidth_sum = 0, rolloff_sum = 0, flatness_sum = 0;
    int frames = 0;
    for (size_t start = 0; start + kFftSize <= sample_count; start += 512) {
        float energy = 0;
        for (int i = 0; i < kFftSize; ++i) {
            const float sample = pcm[start + i] / 32768.0f;
            const float window = 0.54f - 0.46f * std::cos(2.0f * kPi * i / (kFftSize - 1));
            workspace.fft[i] = {sample * window, 0};
            energy += sample * sample;
        }
        fft(workspace.fft);
        float total = 0, weighted = 0, log_sum = 0;
        for (int bin = 0; bin < kSpectrumBins; ++bin) {
            const float p = std::norm(workspace.fft[bin]) / kFftSize;
            workspace.power[bin] = p;
            const float hz = bin * sample_rate / static_cast<float>(kFftSize);
            total += p; weighted += hz * p; log_sum += std::log(p + 1e-12f);
        }
        const float centroid = weighted / (total + 1e-12f);
        float variance = 0, cumulative = 0, rolloff = 0;
        for (int bin = 0; bin < kSpectrumBins; ++bin) {
            const float hz = bin * sample_rate / static_cast<float>(kFftSize);
            variance += (hz - centroid) * (hz - centroid) * workspace.power[bin];
            cumulative += workspace.power[bin];
            if (rolloff == 0 && cumulative >= total * .85f) rolloff = hz;
        }
        rms_sum += std::sqrt(energy / kFftSize); centroid_sum += centroid;
        bandwidth_sum += std::sqrt(variance / (total + 1e-12f)); rolloff_sum += rolloff;
        flatness_sum += std::exp(log_sum / kSpectrumBins) / (total / kSpectrumBins + 1e-12f);
        float frame_chroma[12]{}, mel[26]{};
        for (int bin = 1; bin < kSpectrumBins; ++bin) {
            const float hz = bin * sample_rate / static_cast<float>(kFftSize);
            if (hz >= 40) { const int note = static_cast<int>(std::lround(69 + 12 * std::log2(hz / 440.0f))); frame_chroma[(note % 12 + 12) % 12] += std::sqrt(workspace.power[bin]); }
        }
        const float chroma_max = *std::max_element(frame_chroma, frame_chroma + 12);
        if (chroma_max > 0) for (int i = 0; i < 12; ++i) chroma_sum[i] += frame_chroma[i] / chroma_max;
        const float max_mel = hertz_to_mel(sample_rate * .5f);
        for (int filter = 0; filter < 26; ++filter) for (int bin = 0; bin < kSpectrumBins; ++bin) {
            const float hz = bin * sample_rate / static_cast<float>(kFftSize);
            const float a = mel_to_hertz(max_mel * filter / 27), b = mel_to_hertz(max_mel * (filter + 1) / 27), c = mel_to_hertz(max_mel * (filter + 2) / 27);
            const float weight = hz >= a && hz <= b ? (hz-a)/(b-a) : (hz > b && hz <= c ? (c-hz)/(c-b) : 0);
            mel[filter] += weight * workspace.power[bin];
        }
        for (int coefficient = 0; coefficient < 13; ++coefficient) { float value = 0; for (int f = 0; f < 26; ++f) value += std::log(mel[f] + 1e-12f) * std::cos(kPi * coefficient * (f + .5f) / 26); mfcc_sum[coefficient] += value; mfcc_sq[coefficient] += value * value; }
        for (int band = 0; band < 7; ++band) { const int low = static_cast<int>(std::pow(band / 7.0f, 1.6f) * (kSpectrumBins - 1)); const int high = std::max(low + 1, static_cast<int>(std::pow((band + 1) / 7.0f, 1.6f) * (kSpectrumBins - 1))); float lo = 1e30f, hi = 0; for (int b = low; b <= high; ++b) { lo = std::min(lo, workspace.power[b]); hi = std::max(hi, workspace.power[b]); } contrast_sum[band] += 10 * std::log10((hi + 1e-12f) / (lo + 1e-12f)); }
        ++frames;
    }
    size_t index = 0;
    for (int i = 0; i < 13; ++i) features[index++] = mfcc_sum[i] / frames;
    for (int i = 0; i < 13; ++i) { const float m = mfcc_sum[i] / frames; features[index++] = std::sqrt(std::max(0.0f, mfcc_sq[i] / frames - m * m)); }
    for (int i = 0; i < 12; ++i) features[index++] = chroma_sum[i] / frames;
    int crossings = 0; for (size_t i = 1; i < sample_count; ++i) crossings += (pcm[i] >= 0) != (pcm[i-1] >= 0);
    features[index++] = rms_sum / frames; features[index++] = crossings / static_cast<float>(sample_count - 1);
    features[index++] = centroid_sum / frames; features[index++] = bandwidth_sum / frames; features[index++] = rolloff_sum / frames; features[index++] = flatness_sum / frames;
    features[index++] = mean(contrast_sum, 7) / frames;
    return true;
}

bool classify_pcm(const int16_t* pcm, size_t sample_count, uint32_t sample_rate,
                  ExtractorWorkspace& workspace, Prediction& prediction) {
    float features[kFeatureCount];
    if (!extract_features(pcm, sample_count, sample_rate, workspace, features)) return false;
    prediction = classify_features(features);
    return true;
}

}  // namespace aiot::ser::esp32
