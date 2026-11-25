# LAB4 轨迹规划与竞速

| 目录 | 内容 |
| --- | --- |
| `controller_pkg` | 几何控制器与轨迹跟踪 |
| `planner_pkg` | 赛道航点读取与轨迹规划 |
| `trajectory_generation_pkg` | 多项式轨迹生成与采样发布 |
| `dependencies` | 课程依赖和实际使用的 TESSE 桥接源码归档 |
| `tools` | 工作区准备、编译、试飞、数据采集及结果分析 |
| `results` | 飞行数据、rosbag、误差图和验证记录 |

环境为 Ubuntu 20.04、ROS Noetic。安装系统依赖：

```bash
sudo apt install python3-catkin-tools python3-pip python3-numpy python3-scipy python3-matplotlib \
  libeigen3-dev libgoogle-glog-dev libgflags-dev libnlopt-cxx-dev libyaml-cpp-dev \
  ros-noetic-tf2-eigen ros-noetic-ackermann-msgs ros-noetic-cmake-modules ffmpeg xvfb
```

在当前目录准备新的 `~/lab4_ws` 工作区；已有同名源码包时脚本会停止，避免覆盖：

```bash
bash tools/setup.sh
python3 -m pip install --user ~/lab4_ws/src/tesse-ros-bridge/tesse-interface
source ~/lab4_ws/devel/setup.bash
```

将课程 Lab4 仿真器放到 `~/vnav-builds/lab4`，使 `lab4.x86_64` 可执行。自动试飞脚本会启动仿真器、桥接、控制器和数据记录：

```bash
python3 ~/lab4-results/run_trial.py hover_reproduce --mode hover --seconds 100
python3 ~/lab4-results/run_trial.py race_reproduce --seconds 1800 --finish-hold 15
```

试飞结果保存到 `~/lab4-results/<试验名称>`。需要录屏时，先启动 `Xvfb :84 -screen 0 1280x720x24`，再给竞速命令增加 `--record`。

本次完成十二门赛道，用时 67.797 仿真秒；末门首次偏差超出中心窗口，经终点位置保持修正后通过。逐门结果见 `results/最终结果.json`。

[实验报告](../reports/LAB4_实验报告.pdf) · [10 倍速飞行视频](../videos/LAB4_赛道飞行视频_10倍速.mp4)
