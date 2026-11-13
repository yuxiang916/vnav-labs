#include <iostream>
#include <Eigen/Dense>
int main() {
    Eigen::Matrix2d matrix = Eigen::Matrix2d::Identity();
    std::cout << "Lab1 environment OK\nEigen identity:\n" << matrix << '\n';
    return 0;
}
