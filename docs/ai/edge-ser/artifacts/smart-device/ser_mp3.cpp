/**
 * @file ser_mp3.cpp
 * @brief Desktop runner for speech-emotion recognition from an MP3 file.
 *
 * Dependencies: C++17 compiler and ffmpeg on PATH. ffmpeg is limited to MP3
 * decoding; acoustic feature extraction and model inference run in C++.
 */

#include <algorithm>
#include <array>
#include <cmath>
#include <complex>
#include <cstdint>
#include <cstdlib>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <numeric>
#include <sstream>
#include <stdexcept>
#include <string>
#include <string_view>
#include <vector>

#include "../classifier.h"

namespace aiot::ser {

constexpr int kFeatureCount = 45;
constexpr int kClassCount = 7;
constexpr int kFftSize = 2048;  // Matches librosa's default n_fft.
constexpr int kHopSize = 512;   // Matches extractor.py.
constexpr double kPi = 3.14159265358979323846;

using Features = std::array<int16_t, kFeatureCount>;
using Probabilities = std::array<float, kClassCount>;

struct AudioBuffer {
    int sample_rate_hz{};
    std::vector<float> samples;

    [[nodiscard]] double duration_seconds() const {
        return sample_rate_hz == 0 ? 0.0
                                   : static_cast<double>(samples.size()) / sample_rate_hz;
    }
};

struct Prediction {
    int class_index{};
    std::string_view label;
    Probabilities probabilities{};

    [[nodiscard]] float confidence() const { return probabilities.at(class_index); }
};

class WavReader final {
public:
    [[nodiscard]] static AudioBuffer read_pcm16_mono(const std::filesystem::path& path) {
        std::ifstream stream(path, std::ios::binary);
        if (!stream) {
            throw std::runtime_error("Cannot open decoded WAV file.");
        }

        const std::vector<uint8_t> bytes((std::istreambuf_iterator<char>(stream)), {});
        if (bytes.size() < 44 || fourcc(bytes, 0) != "RIFF" || fourcc(bytes, 8) != "WAVE") {
            throw std::runtime_error("ffmpeg did not produce a valid WAV file.");
        }

        WavFormat format;
        size_t data_offset = 0;
        size_t data_size = 0;
        for (size_t offset = 12; offset + 8 <= bytes.size();) {
            const auto chunk_size = read_u32(bytes, offset + 4);
            if (offset + 8 + chunk_size > bytes.size()) {
                break;
            }
            if (fourcc(bytes, offset) == "fmt " && chunk_size >= 16) {
                format.audio_format = read_u16(bytes, offset + 8);
                format.channel_count = read_u16(bytes, offset + 10);
                format.sample_rate_hz = static_cast<int>(read_u32(bytes, offset + 12));
                format.bits_per_sample = read_u16(bytes, offset + 22);
            } else if (fourcc(bytes, offset) == "data") {
                data_offset = offset + 8;
                data_size = chunk_size;
                break;
            }
            offset += 8 + chunk_size + (chunk_size & 1U);
        }

        if (format.audio_format != 1 || format.channel_count < 1 ||
            format.bits_per_sample != 16 || format.sample_rate_hz <= 0 || data_size == 0) {
            throw std::runtime_error("Expected a 16-bit PCM WAV file from ffmpeg.");
        }

        const size_t frame_count = data_size / (format.channel_count * sizeof(int16_t));
        AudioBuffer audio{format.sample_rate_hz, std::vector<float>(frame_count)};
        for (size_t frame = 0; frame < frame_count; ++frame) {
            const size_t sample_offset = data_offset + frame * format.channel_count * 2;
            audio.samples[frame] = static_cast<int16_t>(read_u16(bytes, sample_offset)) / 32768.0F;
        }
        return audio;
    }

private:
    struct WavFormat {
        uint16_t audio_format{};
        uint16_t channel_count{};
        int sample_rate_hz{};
        uint16_t bits_per_sample{};
    };

    [[nodiscard]] static uint16_t read_u16(const std::vector<uint8_t>& bytes, size_t offset) {
        return static_cast<uint16_t>(bytes[offset]) |
               (static_cast<uint16_t>(bytes[offset + 1]) << 8U);
    }

    [[nodiscard]] static uint32_t read_u32(const std::vector<uint8_t>& bytes, size_t offset) {
        return static_cast<uint32_t>(bytes[offset]) |
               (static_cast<uint32_t>(bytes[offset + 1]) << 8U) |
               (static_cast<uint32_t>(bytes[offset + 2]) << 16U) |
               (static_cast<uint32_t>(bytes[offset + 3]) << 24U);
    }

    [[nodiscard]] static std::string_view fourcc(const std::vector<uint8_t>& bytes, size_t offset) {
        return {reinterpret_cast<const char*>(bytes.data() + offset), 4};
    }
};

class Mp3Decoder final {
public:
    [[nodiscard]] AudioBuffer decode(const std::filesystem::path& mp3_path) const {
        if (!std::filesystem::exists(mp3_path)) {
            throw std::runtime_error("Input file does not exist: " + mp3_path.string());
        }

        const auto temporary_wav = std::filesystem::temp_directory_path() /
            ("aiot_ser_" + std::to_string(std::rand()) + ".wav");
        const std::string command = "ffmpeg -v error -y -i " + quote_argument(mp3_path) +
            " -ac 1 -c:a pcm_s16le " + quote_argument(temporary_wav);

        if (std::system(command.c_str()) != 0) {
            throw std::runtime_error("ffmpeg could not decode the MP3 file.");
        }

        try {
            auto audio = WavReader::read_pcm16_mono(temporary_wav);
            std::error_code ignored;
            std::filesystem::remove(temporary_wav, ignored);
            return audio;
        } catch (...) {
            std::error_code ignored;
            std::filesystem::remove(temporary_wav, ignored);
            throw;
        }
    }

private:
    [[nodiscard]] static std::string quote_argument(const std::filesystem::path& path) {
        const std::string value = path.string();
        if (value.find('"') != std::string::npos) {
            throw std::runtime_error("Input path cannot contain double quotes.");
        }
        return '"' + value + '"';
    }
};

class FastFourierTransform final {
public:
    static void apply(std::vector<std::complex<double>>& values) {
        const size_t length = values.size();
        for (size_t index = 1, reversed = 0; index < length; ++index) {
            size_t bit = length >> 1U;
            for (; reversed & bit; bit >>= 1U) {
                reversed ^= bit;
            }
            reversed ^= bit;
            if (index < reversed) {
                std::swap(values[index], values[reversed]);
            }
        }

        for (size_t block = 2; block <= length; block <<= 1U) {
            const std::complex<double> block_rotation(
                std::cos(2.0 * kPi / block), std::sin(2.0 * kPi / block));
            for (size_t start = 0; start < length; start += block) {
                std::complex<double> rotation(1.0, 0.0);
                for (size_t offset = 0; offset < block / 2; ++offset) {
                    const auto even = values[start + offset];
                    const auto odd = values[start + offset + block / 2] * rotation;
                    values[start + offset] = even + odd;
                    values[start + offset + block / 2] = even - odd;
                    rotation *= block_rotation;
                }
            }
        }
    }
};

class AcousticFeatureExtractor final {
public:
    [[nodiscard]] Features extract(const AudioBuffer& audio) const {
        if (audio.samples.size() < kFftSize) {
            throw std::runtime_error("Audio must be at least 2048 samples long.");
        }

        FrameStatistics statistics;
        for (size_t start = 0; start + kFftSize <= audio.samples.size(); start += kHopSize) {
            const auto power = power_spectrum(audio.samples, start);
            update_statistics(power, audio, start, statistics);
        }
        if (statistics.frame_count == 0) {
            throw std::runtime_error("No analysis frames were generated.");
        }

        return quantize(build_feature_vector(audio, statistics));
    }

private:
    static constexpr int kSpectrumBins = kFftSize / 2 + 1;

    struct FrameStatistics {
        int frame_count{};
        std::array<double, 13> mfcc_sum{};
        std::array<double, 12> chroma_sum{};
        std::array<double, 7> contrast_sum{};
        std::vector<double> previous_power = std::vector<double>(kSpectrumBins);
        std::vector<double> rms_values;
        std::vector<double> centroids;
        std::vector<double> bandwidths;
        std::vector<double> rolloffs;
        std::vector<double> flatnesses;
        std::vector<double> fluxes;
    };

    [[nodiscard]] static std::vector<double> power_spectrum(
        const std::vector<float>& samples, size_t start) {
        std::vector<std::complex<double>> frame(kFftSize);
        for (int index = 0; index < kFftSize; ++index) {
            const double hamming = 0.54 - 0.46 * std::cos(2.0 * kPi * index / (kFftSize - 1));
            frame[index] = static_cast<double>(samples[start + index]) * hamming;
        }
        FastFourierTransform::apply(frame);

        std::vector<double> power(kSpectrumBins);
        for (int bin = 0; bin < kSpectrumBins; ++bin) {
            power[bin] = std::norm(frame[bin]) / kFftSize;
        }
        return power;
    }

    static void update_statistics(const std::vector<double>& power, const AudioBuffer& audio,
                                  size_t start, FrameStatistics& output) {
        const auto [centroid, bandwidth, rolloff, flatness] = spectral_moments(power, audio.sample_rate_hz);
        output.centroids.push_back(centroid);
        output.bandwidths.push_back(bandwidth);
        output.rolloffs.push_back(rolloff);
        output.flatnesses.push_back(flatness);
        output.rms_values.push_back(frame_rms(audio.samples, start));

        if (output.frame_count > 0) {
            double positive_difference = 0.0;
            for (int bin = 0; bin < kSpectrumBins; ++bin) {
                positive_difference += std::max(0.0, power[bin] - output.previous_power[bin]);
            }
            output.fluxes.push_back(std::sqrt(positive_difference));
        }
        output.previous_power = power;
        update_chroma(power, audio.sample_rate_hz, output.chroma_sum);
        update_mfcc(power, audio.sample_rate_hz, output.mfcc_sum);
        update_spectral_contrast(power, output.contrast_sum);
        ++output.frame_count;
    }

    [[nodiscard]] static std::array<double, 4> spectral_moments(
        const std::vector<double>& power, int sample_rate) {
        double total_power = 0.0;
        double weighted_frequency = 0.0;
        double log_sum = 0.0;
        for (int bin = 0; bin < kSpectrumBins; ++bin) {
            const double frequency = static_cast<double>(bin) * sample_rate / kFftSize;
            total_power += power[bin];
            weighted_frequency += frequency * power[bin];
            log_sum += std::log(power[bin] + 1e-12);
        }
        const double centroid = weighted_frequency / (total_power + 1e-12);
        double weighted_variance = 0.0;
        double cumulative_power = 0.0;
        double rolloff = 0.0;
        for (int bin = 0; bin < kSpectrumBins; ++bin) {
            const double frequency = static_cast<double>(bin) * sample_rate / kFftSize;
            weighted_variance += (frequency - centroid) * (frequency - centroid) * power[bin];
            cumulative_power += power[bin];
            if (rolloff == 0.0 && cumulative_power >= total_power * 0.85) {
                rolloff = frequency;
            }
        }
        const double bandwidth = std::sqrt(weighted_variance / (total_power + 1e-12));
        const double flatness = std::exp(log_sum / kSpectrumBins) /
            (total_power / kSpectrumBins + 1e-12);
        return {centroid, bandwidth, rolloff, flatness};
    }

    [[nodiscard]] static double frame_rms(const std::vector<float>& samples, size_t start) {
        double energy = 0.0;
        for (int index = 0; index < kFftSize; ++index) {
            energy += static_cast<double>(samples[start + index]) * samples[start + index];
        }
        return std::sqrt(energy / kFftSize);
    }

    static void update_chroma(const std::vector<double>& power, int sample_rate,
                              std::array<double, 12>& chroma_sum) {
        for (int bin = 1; bin < kSpectrumBins; ++bin) {
            const double frequency = static_cast<double>(bin) * sample_rate / kFftSize;
            if (frequency < 40.0) {
                continue;
            }
            const int midi_note = static_cast<int>(std::lround(69.0 + 12.0 * std::log2(frequency / 440.0)));
            const int pitch_class = (midi_note % 12 + 12) % 12;
            chroma_sum[pitch_class] += power[bin];
        }
    }

    static void update_mfcc(const std::vector<double>& power, int sample_rate,
                            std::array<double, 13>& mfcc_sum) {
        constexpr int kMelFilterCount = 26;
        std::array<double, kMelFilterCount + 2> mel_points{};
        const double maximum_mel = hertz_to_mel(sample_rate / 2.0);
        for (int point = 0; point < static_cast<int>(mel_points.size()); ++point) {
            mel_points[point] = mel_to_hertz(maximum_mel * point / (mel_points.size() - 1));
        }

        std::array<double, kMelFilterCount> mel_energy{};
        for (int filter = 0; filter < kMelFilterCount; ++filter) {
            for (int bin = 0; bin < kSpectrumBins; ++bin) {
                const double frequency = static_cast<double>(bin) * sample_rate / kFftSize;
                double weight = 0.0;
                if (frequency >= mel_points[filter] && frequency <= mel_points[filter + 1]) {
                    weight = (frequency - mel_points[filter]) /
                        (mel_points[filter + 1] - mel_points[filter]);
                } else if (frequency > mel_points[filter + 1] && frequency <= mel_points[filter + 2]) {
                    weight = (mel_points[filter + 2] - frequency) /
                        (mel_points[filter + 2] - mel_points[filter + 1]);
                }
                mel_energy[filter] += weight * power[bin];
            }
        }

        for (int coefficient = 0; coefficient < 13; ++coefficient) {
            for (int filter = 0; filter < kMelFilterCount; ++filter) {
                mfcc_sum[coefficient] += std::log(mel_energy[filter] + 1e-12) *
                    std::cos(kPi * coefficient * (filter + 0.5) / kMelFilterCount);
            }
        }
    }

    static void update_spectral_contrast(const std::vector<double>& power,
                                         std::array<double, 7>& contrast_sum) {
        for (int band = 0; band < 7; ++band) {
            const int low = static_cast<int>(std::pow(static_cast<double>(band) / 7, 1.6) *
                                             (kSpectrumBins - 1));
            const int high = std::max(low + 1, static_cast<int>(
                std::pow(static_cast<double>(band + 1) / 7, 1.6) * (kSpectrumBins - 1)));
            double minimum = std::numeric_limits<double>::max();
            double maximum = 0.0;
            for (int bin = low; bin <= high; ++bin) {
                minimum = std::min(minimum, power[bin]);
                maximum = std::max(maximum, power[bin]);
            }
            contrast_sum[band] += 10.0 * std::log10((maximum + 1e-12) / (minimum + 1e-12));
        }
    }

    [[nodiscard]] static std::array<double, kFeatureCount> build_feature_vector(
        const AudioBuffer& audio, const FrameStatistics& data) {
        const double frame_count = data.frame_count;
        const double energy = average(data.rms_values);
        const double zcr = zero_crossing_rate(audio.samples);
        const auto [f0, f2] = pitch_features(audio, data.previous_power);
        const double jitter = mfcc_jitter(data.mfcc_sum, frame_count);
        const double shimmer = amplitude_shimmer(audio.samples);
        const double pause_rate = std::count_if(data.rms_values.begin(), data.rms_values.end(),
            [](double value) { return value < 0.01; }) / frame_count;

        std::array<double, kFeatureCount> values{};
        size_t index = 0;
        values[index++] = energy;
        values[index++] = zcr;
        values[index++] = f0;
        values[index++] = f2;
        values[index++] = jitter;
        values[index++] = shimmer;
        values[index++] = average(data.bandwidths);
        values[index++] = pause_rate;
        values[index++] = average(data.centroids);
        values[index++] = average(data.bandwidths);
        values[index++] = average(data.rolloffs);
        values[index++] = average(data.fluxes);
        values[index++] = average(data.flatnesses);
        for (const double value : data.mfcc_sum) values[index++] = value / frame_count;
        const double chroma_total = std::accumulate(data.chroma_sum.begin(), data.chroma_sum.end(), 0.0);
        for (const double value : data.chroma_sum) values[index++] = value / (chroma_total + 1e-12);
        for (const double value : data.contrast_sum) values[index++] = value / frame_count;
        return values;
    }

    [[nodiscard]] static Features quantize(const std::array<double, kFeatureCount>& values) {
        // Integer ranges used by the emlearn-generated classifier.h artifact.
        static constexpr std::array<double, kFeatureCount> kScales = {
            10000, 1000, 10, 10, 100, 10000, 1, 100, 1, 1, 1, 10, 100,
            1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
            1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000,
            1, 1, 1, 1, 1, 1, 1};
        Features output{};
        for (int index = 0; index < kFeatureCount; ++index) {
            output[index] = static_cast<int16_t>(std::clamp(
                std::round(values[index] * kScales[index]), -32768.0, 32767.0));
        }
        return output;
    }

    [[nodiscard]] static std::pair<double, double> pitch_features(
        const AudioBuffer& audio, const std::vector<double>& last_power_spectrum) {
        const size_t sample_count = std::min(audio.samples.size(), static_cast<size_t>(audio.sample_rate_hz) * 5);
        int best_lag = audio.sample_rate_hz / 400;
        const int maximum_lag = audio.sample_rate_hz / 50;
        double best_correlation = -1.0;
        for (int lag = best_lag; lag <= maximum_lag; ++lag) {
            double correlation = 0.0, left_energy = 0.0, right_energy = 0.0;
            for (size_t sample = lag; sample < sample_count; ++sample) {
                correlation += audio.samples[sample] * audio.samples[sample - lag];
                left_energy += audio.samples[sample] * audio.samples[sample];
                right_energy += audio.samples[sample - lag] * audio.samples[sample - lag];
            }
            const double normalized = correlation / std::sqrt(left_energy * right_energy + 1e-18);
            if (normalized > best_correlation) {
                best_correlation = normalized;
                best_lag = lag;
            }
        }
        const double f0 = best_correlation > 0.15 ? static_cast<double>(audio.sample_rate_hz) / best_lag : 0.0;
        // F2 is a lightweight estimate of the largest spectral peak above 300 Hz.
        const int start_bin = std::max(1, static_cast<int>(300.0 * kFftSize / audio.sample_rate_hz));
        int peak_bin = start_bin;
        for (int bin = start_bin; bin < static_cast<int>(last_power_spectrum.size()); ++bin) {
            if (last_power_spectrum[bin] > last_power_spectrum[peak_bin]) {
                peak_bin = bin;
            }
        }
        const double f2 = static_cast<double>(peak_bin) * audio.sample_rate_hz / kFftSize;
        return {f0, f2};
    }

    [[nodiscard]] static double zero_crossing_rate(const std::vector<float>& samples) {
        size_t crossings = 0;
        for (size_t index = 1; index < samples.size(); ++index) {
            crossings += (samples[index] >= 0.0F) != (samples[index - 1] >= 0.0F);
        }
        return static_cast<double>(crossings) / std::max<size_t>(1, samples.size() - 1);
    }

    [[nodiscard]] static double mfcc_jitter(const std::array<double, 13>& mfcc_sum, double count) {
        double result = 0.0;
        for (int index = 1; index < 13; ++index) {
            result += std::abs(mfcc_sum[index] / count - mfcc_sum[index - 1] / count);
        }
        return result / 12.0;
    }

    [[nodiscard]] static double amplitude_shimmer(const std::vector<float>& samples) {
        double result = 0.0;
        for (size_t index = 1; index < samples.size(); ++index) {
            result += std::abs(samples[index] - samples[index - 1]);
        }
        return result / std::max<size_t>(1, samples.size() - 1);
    }

    [[nodiscard]] static double average(const std::vector<double>& values) {
        return values.empty() ? 0.0 : std::accumulate(values.begin(), values.end(), 0.0) / values.size();
    }

    [[nodiscard]] static double hertz_to_mel(double hertz) { return 2595.0 * std::log10(1.0 + hertz / 700.0); }
    [[nodiscard]] static double mel_to_hertz(double mel) { return 700.0 * (std::pow(10.0, mel / 2595.0) - 1.0); }
};

class EmotionClassifier final {
public:
    [[nodiscard]] Prediction predict(const Features& features) const {
        static constexpr std::array<std::string_view, kClassCount> kLabels = {
            "Angry", "Disgust", "Fear", "Happy", "Neutral", "Sad", "Surprise"};
        Prediction prediction;
        prediction.class_index = rf_predict(features.data(), kFeatureCount);
        rf_predict_proba(features.data(), kFeatureCount, prediction.probabilities.data(), kClassCount);
        prediction.label = kLabels.at(prediction.class_index);
        return prediction;
    }
};

/** Serializes the model-ready, fixed-point 45-element vector without external JSON dependencies. */
class FeatureJsonStore final {
public:
    static void write(const std::filesystem::path& output_path, const Features& features,
                      const AudioBuffer& audio) {
        std::ofstream stream(output_path, std::ios::trunc);
        if (!stream) {
            throw std::runtime_error("Cannot write feature JSON: " + output_path.string());
        }
        stream << "{\n"
               << "  \"schema_version\": 1,\n"
               << "  \"feature_count\": " << kFeatureCount << ",\n"
               << "  \"sample_rate_hz\": " << audio.sample_rate_hz << ",\n"
               << "  \"duration_seconds\": " << std::fixed << std::setprecision(6)
               << audio.duration_seconds() << ",\n"
               << "  \"features\": [";
        for (size_t index = 0; index < features.size(); ++index) {
            stream << features[index] << (index + 1 == features.size() ? "" : ", ");
        }
        stream << "]\n}\n";
    }

    [[nodiscard]] static Features read(const std::filesystem::path& input_path) {
        std::ifstream stream(input_path);
        if (!stream) {
            throw std::runtime_error("Cannot open feature JSON: " + input_path.string());
        }
        const std::string json((std::istreambuf_iterator<char>(stream)), {});
        const size_t key = json.find("\"features\"");
        const size_t open = key == std::string::npos ? std::string::npos : json.find('[', key);
        const size_t close = open == std::string::npos ? std::string::npos : json.find(']', open);
        if (open == std::string::npos || close == std::string::npos) {
            throw std::runtime_error("JSON must contain a features array.");
        }

        std::string array_text = json.substr(open + 1, close - open - 1);
        std::replace(array_text.begin(), array_text.end(), ',', ' ');
        std::istringstream values(array_text);
        Features features{};
        long long value = 0;
        size_t index = 0;
        while (values >> value) {
            if (index >= features.size()) {
                throw std::runtime_error("Feature JSON has more than 45 values.");
            }
            if (value < std::numeric_limits<int16_t>::min() ||
                value > std::numeric_limits<int16_t>::max()) {
                throw std::runtime_error("Feature value is outside int16 range.");
            }
            features[index++] = static_cast<int16_t>(value);
        }
        if (index != features.size()) {
            throw std::runtime_error("Feature JSON must contain exactly 45 integer values.");
        }
        return features;
    }
};

class SerApplication final {
public:
    [[nodiscard]] Features extract(const std::filesystem::path& input) {
        const auto audio = decoder_.decode(input);
        if (audio.duration_seconds() < 0.5) {
            throw std::runtime_error("Audio must be at least 0.5 seconds long.");
        }
        last_audio_ = audio;
        return extractor_.extract(audio);
    }

    [[nodiscard]] Prediction classify(const Features& features) const { return classifier_.predict(features); }
    [[nodiscard]] const AudioBuffer& last_audio() const { return last_audio_; }

private:
    Mp3Decoder decoder_;
    AcousticFeatureExtractor extractor_;
    EmotionClassifier classifier_;
    AudioBuffer last_audio_;
};

void print_usage() {
    std::cerr << "Usage:\n"
              << "  ser_mp3 extract <audio.mp3> <features.json>\n"
              << "  ser_mp3 classify <features.json>\n";
}

}  // namespace aiot::ser

int main(int argc, char** argv) {
    using namespace aiot::ser;
    if (argc < 2 || std::string_view(argv[1]) == "--help") {
        print_usage();
        return argc == 2 ? 0 : 2;
    }

    try {
        SerApplication application;
        const std::string_view command = argv[1];
        if (command == "extract" && argc == 4) {
            const Features features = application.extract(argv[2]);
            FeatureJsonStore::write(argv[3], features, application.last_audio());
            std::cout << "{\"status\":\"extracted\",\"output\":\"" << argv[3]
                      << "\",\"feature_count\":45}\n";
            return 0;
        }
        if (command == "classify" && argc == 3) {
            const Prediction prediction = application.classify(FeatureJsonStore::read(argv[2]));
            std::cout << std::fixed << std::setprecision(3)
                      << "{\"emotion_label\":\"" << prediction.label
                      << "\",\"confidence\":" << prediction.confidence() << "}\n";
            return 0;
        }
        print_usage();
        return 2;
    } catch (const std::exception& error) {
        std::cerr << "Error: " << error.what() << '\n';
        return 1;
    }
}
