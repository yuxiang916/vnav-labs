# LAB3 三维轨迹跟踪

`controller_pkg` 包含几何控制器、悬停与圆轨迹发布节点。四元数题见 `deliverable_1.txt`，动力学推导见 [theory.md](theory.md)。`results` 保存悬停、圆轨迹数据和编译记录。

使用 Ubuntu 20.04、ROS Noetic、课程 Lab3 TESSE 仿真器与桥接程序。以课程 VNAV2021 版本的 Lab3 工作区为基础，将本目录的 `controller_pkg` 放入 `src`。另安装 `mav_comm`、`ros-noetic-ackermann-msgs` 和 `ros-noetic-tf2-eigen`，然后在工作区运行：

```bash
source /opt/ros/noetic/setup.bash
catkin build controller_pkg tesse_ros_bridge -j2
source devel/setup.bash
```

启动课程仿真器，在分别加载工作区的终端启动桥接与控制器：

```bash
roslaunch tesse_ros_bridge tesse_quadrotor_bridge.launch
roslaunch controller_pkg traj_tracking.launch static_pose:=true
```

悬停测试结束后关闭控制器，运行 `roslaunch controller_pkg traj_tracking.launch` 切换到圆轨迹。`measure.py` 用于采集位姿；里程计正常而仿真时钟停止时，可关闭桥接的时钟发布并运行 `odom_clock.py`。

[实验报告](../reports/LAB3_实验报告.pdf) · [飞行视频](../videos/LAB3_圆轨迹飞行视频.mp4)
