# Lab1 复做指导

邵宇翔 · 研0 · 2026-11-13

实验已经在 Ubuntu 中实际运行。下面的步骤用于你自己复做、截图和理解结果。
在 VirtualBox 中启动 `VNAV-Ubuntu20.04`；用户名为 `syx`，密码见同目录的 `ubuntu-account.txt`。
以下命令全部输入 Ubuntu 终端，不能输入 Windows PowerShell。

## 1. Shell：确认目录，读文件并统计

```bash
cd ~/vnav-personal/lab1
pwd
ls
wc -l data/dante.txt
wc -w data/dante.txt
grep -c '[^[:space:]]' data/dante.txt
cat exercise1.txt
```

预期结果依次为19567、97676、14338。

- `wc -l`计算换行符数量；本次输入有结尾换行，因此对应19567行。
- `wc -w`按空白分隔统计单词，不能用文件字节数代替。
- 正则`[^[:space:]]`表示至少存在一个非空白字符，因此排除空行和仅空格/制表符组成的行。
- 如果只用`grep -c .`，只包含空格的行仍然会被计入，含义不同。

现在查看五次追加的结果：

```bash
cat fortunes.txt
```

原实验运行了一次预览，再执行五次追加。你可以在另一个文件安全复做：

```bash
: > fortunes-practice.txt
for i in 1 2 3 4 5; do
  /usr/games/fortune >> fortunes-practice.txt
done
cat fortunes-practice.txt
```

fortune内容随机，不能拿文字是否和报告完全一样来判断对错。一条fortune也可能有很多行，不能用文件行数判断执行次数。
`>`覆盖文件，`>>`追加。上面的`: >`只在开始清空练习文件，不会覆盖已完成的`fortunes.txt`。

## 2. Shell：理解管道与重定向

```bash
cd ~/vnav-personal/lab1/shell-practice
cat numbers.txt | sort -n
cat stdout-only.txt
cat combined.txt
cat tee-stdout.txt
cat tee-combined.txt
```

| 写法 | 写入文件 | 终端仍能看到什么 |
|---|---|---|
| `command > out.txt` | 标准输出 | 标准错误 |
| `command &> out.txt` | 标准输出和错误 | 两者都不显示 |
| `command \| tee out.txt` | 标准输出 | 标准输出和未重定向的错误 |
| `command \|& tee out.txt` | 标准输出和错误 | 两者都显示 |

`|`把左边标准输出交给右边程序处理，`tee`把输入同时显示并写入文件。`&>`和`|&`是这里所用Bash支持的语法。
`chmod +x hello.sh`赋予执行权限；`./hello.sh`中的`./`指当前目录。

## 3. C++：先理解热身题

```bash
cd ~/vnav-personal/lab1
cat cpp-warmup.txt
g++ -std=c++11 -Wall -Wextra -pedantic warmup_verify.cpp -o warmup_verify
./warmup_verify
```

你至少要能解释下面四点：

1. `++i`先加再取值，`i++`先取值再加，所以第一题最终是`i=2,j=1`。
2. 引用是原变量的别名，通过引用赋值会改原变量。
3. `*j**j`可拆成`(*j) * (*j)`，即解引用后相乘。
4. 类型字节数依赖平台：本次Ubuntu的`long`为8字节，不能据此断言Windows也是8字节。

## 4. RandomVector：直接编译和运行

```bash
cd ~/vnav-personal/lab1/RandomVector
g++ -std=c++11 -Wall -Wextra -pedantic -o random_vector main.cpp random_vector.cpp
./random_vector
```

本次固定种子314159，Ubuntu运行结果：

```text
Mean: 0.55804
Min: 0.0278694
Max: 0.982655
```

先看`random_vector.h`，它声明“能做什么”；再看`.cpp`，它定义“怎么做”；`main.cpp`负责创建对象并调用方法。

- 构造函数：用`rand()/double(RAND_MAX)`把整数随机数缩放到0至1，再乘上界。
- `mean()`：累计每个值除以元素个数的结果。先除后加可以减少大数求和溢出风险。
- `min()`、`max()`：先取第一个元素为候选，再遍历比较，不能一律从0开始。
- `printHistogram(5)`：在最小值与最大值之间建立5个等宽区间，计数后从最高行向下打印。

本次频数为`[5,1,4,3,7]`，总数20。每个`***`整体代表一个样本，不是3个样本。
最大值必须放最后一桶；所有值相同则统一放第一桶，避免用零作为区间宽度。

## 5. CMake：用同一组源码构建

```bash
cd ~/vnav-personal/lab1/RandomVector
cmake -S . -B build
cmake --build build -j2
./build/random_vector
```

`-S .`指定源码目录，`-B build`把编译中间文件放到build目录。
本项目把类实现编译成库，再将main链接到该库。两种构建产生的输出已逐字比较一致。

## 6. 运行独立检查

```bash
cd ~/vnav-personal/lab1
g++ -std=c++11 -Wall -Wextra -pedantic RandomVector/edge_cases.cpp RandomVector/random_vector.cpp -o RandomVector/edge_cases
python3 validate.py
cat results/sanitizers.txt
```

应看到`ALL_CHECKS_PASSED`。检查覆盖单元素、全零向量、非默认上界、200桶/100样本，以及7类非法参数。
测试根据实际输出独立复算统计量和频数，并检查频数之和等于样本数；ASan/UBSan检查内存越界和未定义行为。

## 7. Git：查看已完成的提交与冲突练习

```bash
cd ~/vnav-personal
git status
git log --oneline
cd ~/lab1-git-practice
git log --graph --oneline --all
cat me.txt
git diff HEAD~2
```

主分支和collaborator分支修改同一行，合并时会出现`<<<<<<<`、`=======`、`>>>>>>>`标记。
解决冲突必须编辑文件、去掉标记，再`git add`和`git commit`，不能仅仅删分支或忽略报错。
`HEAD~2`指沿第一父提交回溯两代，`git diff HEAD~2`比较那个提交与当前工作树。

本次本地作者使用姓名“邵宇翔”，`lab1@localhost`只是实验标识，不是真实邮箱。
目前没有远程仓库，也没有上传。若老师要求远程提交，需先确认仓库地址和权限，再在主仓库中设置remote并推送。
不要将`ubuntu-account.txt`、`ubuntu-password.txt`、虚拟机或整套LAB1目录上传。

## 8. 提交与答辩前检查

阅读PDF报告，确认姓名和阶段正确。提交包仅包含报告、源码、实际输入与日志、Git历史备份，不含账户密码和虚拟机镜像。
课堂派的具体提交要求优先；本地实验完成不等于已在课堂派或GitHub提交。
答辩时应能解释`>>`、引用/指针、随机数缩放、最大值归桶、CMake构建和合并冲突处理。
