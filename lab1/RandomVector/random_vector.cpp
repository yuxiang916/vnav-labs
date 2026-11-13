#include "random_vector.h"
#include <cmath>
#include <cstdlib>
#include <stdexcept>

RandomVector::RandomVector(int size, double max_val) {
    if (size <= 0) throw std::invalid_argument("size must be positive");
    if (!std::isfinite(max_val) || max_val < 0)
        throw std::invalid_argument("max_val must be finite and nonnegative");
    vect.reserve(static_cast<std::size_t>(size));
    for (int i = 0; i < size; ++i)
        vect.push_back((std::rand() / static_cast<double>(RAND_MAX)) * max_val);
}

void RandomVector::print() {
    for (double value : vect) std::cout << value << ' ';
    std::cout << '\n';
}

double RandomVector::mean() {
    // Divide before summing to avoid overflow for large finite inputs.
    double result = 0;
    for (double value : vect) result += value / vect.size();
    return result;
}

double RandomVector::max() {
    double result = vect.front();
    for (double value : vect)
        if (value > result) result = value;
    return result;
}

double RandomVector::min() {
    double result = vect.front();
    for (double value : vect)
        if (value < result) result = value;
    return result;
}

void RandomVector::printHistogram(int bins) {
    if (bins <= 0) throw std::invalid_argument("bins must be positive");
    const double low = min(), high = max();
    std::vector<std::size_t> counts(static_cast<std::size_t>(bins), 0);
    for (double value : vect) {
        int index = 0;
        if (high > low) {
            const double position = (value - low) / (high - low);
            // max() belongs in the final bin, rather than index == bins.
            index = position >= 1.0 ? bins - 1 : static_cast<int>(position * bins);
        }
        ++counts[static_cast<std::size_t>(index)];
    }
    std::size_t height = 0;
    for (std::size_t count : counts)
        if (count > height) height = count;
    for (std::size_t row = height; row > 0; --row) {
        for (std::size_t count : counts)
            std::cout << (count >= row ? "*** " : "    ");
        std::cout << '\n';
    }
}
