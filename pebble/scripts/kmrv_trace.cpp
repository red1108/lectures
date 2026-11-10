#define main kmrv_original_main
#include "kmrv.cpp"
#undef main
#include <iostream>

int main(int argc, char** argv) {
    if (argc != 2) return 2;
    int length = std::stoi(argv[1]);
    if (length < 1) return 2;
    auto schedule = kmrv_path(length);
    std::cout << "[";
    for (size_t i = 0; i < schedule.size(); ++i) {
        if (i) std::cout << ",";
        std::cout << "{\"p\":[";
        for (size_t j = 0; j < schedule[i].pebble.size(); ++j) {
            if (j) std::cout << ",";
            std::cout << schedule[i].pebble[j];
        }
        std::cout << "],\"u\":[";
        for (size_t j = 0; j < schedule[i].unpebble.size(); ++j) {
            if (j) std::cout << ",";
            std::cout << schedule[i].unpebble[j];
        }
        std::cout << "],\"g\":[";
        for (size_t j = 0; j < schedule[i].measure.size(); ++j) {
            if (j) std::cout << ",";
            std::cout << schedule[i].measure[j];
        }
        std::cout << "]}";
    }
    std::cout << "]\n";
}
