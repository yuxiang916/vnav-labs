# LAB1 Shell、Git 与 C++

`RandomVector` 包含随机向量类与边界检查程序，`environment-check` 为编译环境检查。Shell 与 C++ 答案见 `exercise1.txt`、`fortunes.txt`、`cpp-warmup.txt`。运行记录保存在 `results`，Git 冲突练习保存在 `git-history`。

在当前目录运行：

```bash
g++ -std=c++11 -Wall -Wextra -pedantic RandomVector/main.cpp RandomVector/random_vector.cpp -o RandomVector/random_vector
./RandomVector/random_vector
cmake -S RandomVector -B build
cmake --build build
./build/random_vector
```

检查统计结果与边界情况：

```bash
g++ -std=c++11 RandomVector/edge_cases.cpp RandomVector/random_vector.cpp -o RandomVector/edge_cases
g++ -std=c++11 warmup_verify.cpp -o warmup_verify
python3 validate.py
```

[实验报告](../reports/LAB1_实验报告.pdf)
