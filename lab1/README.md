# LAB1 实验成果

姓名：邵宇翔；阶段：研0；日期：2026-11-13。

Ubuntu 20.04.6 x86_64、G++ 9.4.0、CMake 3.16.3、Git 2.25.1。

## 内容与状态

- `exercise1.txt`：指定文本统计，19567行、97676词、14338个非空白行。
- `fortunes.txt`：实际执行fortune五次，用`>>`追加得到。
- `cpp-warmup.txt`：全部10道热身题答案及解释。
- `RandomVector/`：按官方接口实现的必做版本，不使用`<algorithm>`。
- `warmup_verify.cpp`、`validate.py`、`RandomVector/edge_cases.cpp`：实际验证用代码。
- `results/`：Ubuntu实际运行输出、内存检查、Git冲突记录。
- `upstream-original/`：所克隆官方仓库的原始示例，保留来源对照。
- `environment-check/`：此前完成的CMake与Eigen环境检查示例。
- `shell-practice/`：文件操作、权限、管道、重定向与压缩解压练习。

## 编译与验证

在Ubuntu终端进入本目录后执行：

```bash
cd RandomVector
g++ -std=c++11 -Wall -Wextra -pedantic -o random_vector main.cpp random_vector.cpp
./random_vector
cmake -S . -B build
cmake --build build -j2
./build/random_vector
cd ..
g++ -std=c++11 -Wall -Wextra -pedantic warmup_verify.cpp -o warmup_verify
g++ -std=c++11 -Wall -Wextra -pedantic RandomVector/edge_cases.cpp RandomVector/random_vector.cpp -o RandomVector/edge_cases
python3 validate.py
```

## 参数约定

向量长度必须大于0，随机上界必须有限且非负，直方图区间数量必须大于0；否则抛出`std::invalid_argument`。
允许随机上界为0或只有1个元素，这时所有频数归入第一个区间。
一般情况使用左闭右开区间，最后一个区间包含最大值。每个`***`单元表示一个样本，不是三个样本。
随机种子为314159，采用`rand()/double(RAND_MAX)`；同一实现中可重复，随机序列不保证跨C库相同。

## Git状态与提交范围

已完成官方示例仓库克隆、本地答案仓库提交及独立仓库中的分支合并冲突练习。
本地Git作者邮箱`lab1@localhost`仅作为实验提交标识，未填写或推断真实邮箱。
已推送至私有仓库 https://github.com/yuxiang916/vnav-labs 的main分支；未向MIT组织或课堂派提交。
MIT网页中的组织账户属于MIT课程；本班课堂派作业以老师要求为准。
选择题目中的必做循环实现，未实现使用`<algorithm>`的选做加分版本。

## 来源

- 实验说明：https://vnav.mit.edu/labs_2023/lab1/exercises.html
- 官方示例：https://github.com/MIT-SPARK/VNAV-labs/tree/master/lab1
- 本次上游提交：cfed5695497ce37adb35d03ef1cbd3aa2cc4e60a
- 文本来源：https://raw.githubusercontent.com/dlang/dmd/master/druntime/benchmark/extra-files/dante.txt
- 实际输入SHA256：1cd578e12a35c885028c64ee6c6b3ee1643be9dd8e45e0a9fbfa77acb2f6c279
