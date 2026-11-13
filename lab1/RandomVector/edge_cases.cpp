#include "random_vector.h"
#include <cstdlib>
#include <limits>
#include <stdexcept>
#include <string>
int main(int argc, char** argv) {
    const std::string mode = argc > 1 ? argv[1] : "constant";
    if (mode == "invalid") {
        int caught = 0;
        try { RandomVector rv(0); } catch (const std::invalid_argument&) { ++caught; }
        try { RandomVector rv(-2); } catch (const std::invalid_argument&) { ++caught; }
        try { RandomVector rv(3, -1); } catch (const std::invalid_argument&) { ++caught; }
        try { RandomVector rv(3, std::numeric_limits<double>::infinity()); } catch (const std::invalid_argument&) { ++caught; }
        try { RandomVector rv(3, std::numeric_limits<double>::quiet_NaN()); } catch (const std::invalid_argument&) { ++caught; }
        RandomVector rv(2);
        try { rv.printHistogram(0); } catch (const std::invalid_argument&) { ++caught; }
        try { rv.printHistogram(-1); } catch (const std::invalid_argument&) { ++caught; }
        std::cout << "Invalid cases rejected: " << caught << "/7\n";
        return caught == 7 ? 0 : 1;
    }
    std::srand(314159);
    int size = mode == "single" ? 1 : mode == "many" ? 100 : 8;
    double bound = mode == "constant" ? 0 : mode == "scaled" ? 7.5 : 1;
    RandomVector rv(size, bound);
    rv.print();
    std::cout << "Mean: " << rv.mean() << "\nMin: " << rv.min() << "\nMax: " << rv.max() << "\nHistogram:\n";
    rv.printHistogram(mode == "many" ? 200 : 5);
}
