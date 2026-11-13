#include <iostream>
#include <string>
#include <limits>
void reset(int &i) { i = 0; }
int main() {
    { int i=0,j; j=++i; j=i++; std::cout << "Operators1: " << i << ' ' << j << '\n'; }
    { int i=42; std::string output=(i<42)?"a":"b"; std::cout << "Operators2: " << output << '\n'; }
    { int i; int& ri=i; i=5; ri=10; std::cout << "Reference1: " << i << ' ' << ri << '\n'; }
    { int i=42; int* j=&i; *j=*j**j; std::cout << "Pointer2: " << *j << '\n'; }
    { int i[4]={42,24,42,24}; *(i+2)=*(i+1)-i[3]; std::cout << "Pointer3: " << *(i+2) << '\n'; }
    { int j=42; reset(j); std::cout << "Reference4: " << j << '\n'; }
    std::cout << "sizeof(short,int,long,long long): " << sizeof(short) << ' ' << sizeof(int) << ' ' << sizeof(long) << ' ' << sizeof(long long) << '\n';
    std::cout << "sizeof(float,double): " << sizeof(float) << ' ' << sizeof(double) << '\n';
    std::cout << "digits10(float,double): " << std::numeric_limits<float>::digits10 << ' ' << std::numeric_limits<double>::digits10 << '\n';
    { int i; i=3.14; std::cout << "FloatToInt: " << i << '\n'; }
    { unsigned char c=-1; std::cout << "UnsignedChar: " << static_cast<int>(c) << '\n'; }
    { int i=42; if(i){i=0;}else{i=43;} std::cout << "Condition: " << i << '\n'; }
}
