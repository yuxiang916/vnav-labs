# LAB2 ROS 与坐标变换

`two_drones_pkg` 包含坐标变换、轨迹发布节点和 RViz 配置。`verify_tf.py` 检查坐标变换，`verify_turtle.py` 检查 turtlesim，`plot_results.py` 绘制结果；`results` 保存采样数据、截图和验证记录。

将 `two_drones_pkg` 复制到 ROS Noetic 的 catkin 工作区 `src`，在工作区中运行：

```bash
source /opt/ros/noetic/setup.bash
catkin build
source devel/setup.bash
roslaunch two_drones_pkg two_drones.launch static:=True
```

关闭静态场景后，启动动态场景：

```bash
roslaunch two_drones_pkg two_drones.launch
```

加载工作区后，可在本实验目录运行 `python3 verify_tf.py`。`run_experiment.py` 为带 Xvfb 截图的数据采集脚本，另需 NumPy、PyQt5 和 turtlesim。

[实验报告](../reports/LAB2_实验报告.pdf)
