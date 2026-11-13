# VNAV Lab 1

邵宇翔 · 研0 · GitHub: [yuxiang916](https://github.com/yuxiang916)

本仓库保存 Ubuntu 20.04 环境中的 Lab1 必做实验、源码、真实运行结果与报告。

## 阅读入口

- [实验报告](reports/LAB1_实验报告_邵宇翔.pdf)
- [逐步复做指导](Lab1_复做指导.md)
- [源码和答案说明](lab1/README.md)
- [实际检查结果](lab1/results/validation.txt)
- [Git 合并冲突记录](lab1/results/git-conflict-practice.log)

## 已验证结果

| 项目 | 结果 |
|---|---|
| dante.txt行数 / 单词数 / 非空白行数 | 19567 / 97676 / 14338 |
| RandomVector均值 / 最小值 / 最大值 | 0.55804 / 0.0278694 / 0.982655 |
| 五桶频数 | 5、1、4、3、7，总和20 |
| G++与CMake构建 | 输出逐字一致 |
| 边界与内存检查 | 全部通过 |

本机环境：Ubuntu 20.04.6 x86_64、G++ 9.4.0、CMake 3.16.3、Git 2.25.1、Eigen 3.3.7。

## 编译

在Ubuntu终端中进入源码目录：

```bash
cd lab1/RandomVector
g++ -std=c++11 -Wall -Wextra -pedantic -o random_vector main.cpp random_vector.cpp
./random_vector
cmake -S . -B build
cmake --build build -j2
./build/random_vector
```

## 内容范围

本地实验记录保留完整Git历史；独立冲突练习的历史备份位于`git-history/lab1-practice.bundle`。
未实现使用`<algorithm>`的选做加分版本。GitHub推送不等同于课堂派提交，课堂派上传需要按本班要求完成。
仓库不包含账户密码、虚拟机或Ubuntu镜像。

## 来源

- [MIT VNAV Lab1](https://vnav.mit.edu/labs_2023/lab1/exercises.html)
- [官方示例仓库](https://github.com/MIT-SPARK/VNAV-labs/tree/master/lab1)
- 本次上游提交：`cfed5695497ce37adb35d03ef1cbd3aa2cc4e60a`

题目对应循环实现位于`lab1/RandomVector/`；原始TODO模板仅保留在`lab1/upstream-original/`用于对照。
