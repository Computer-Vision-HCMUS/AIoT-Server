#include <cstdint>
#include <cstring>
#include <fstream>
#include <iostream>
#include <vector>

#include "ser_esp32.h"

int main(int argc, char** argv) {
    if (argc != 3) return 2;
    std::ifstream input(argv[1], std::ios::binary);
    std::vector<char> bytes((std::istreambuf_iterator<char>(input)), {});
    std::vector<int16_t> pcm(bytes.size() / sizeof(int16_t));
    std::memcpy(pcm.data(), bytes.data(), pcm.size() * sizeof(int16_t));
    aiot::ser::esp32::ExtractorWorkspace workspace{};
    float features[aiot::ser::esp32::kFeatureCount]{};
    if (!aiot::ser::esp32::extract_features(pcm.data(), pcm.size(), std::stoul(argv[2]), workspace, features)) return 1;
    for (float feature : features) std::cout << feature << '\n';
}
