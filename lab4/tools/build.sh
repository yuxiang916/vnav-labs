#!/usr/bin/env bash
set -eo pipefail
source /opt/ros/noetic/setup.bash
cd "$HOME/lab4_ws"
catkin config --extend /opt/ros/noetic --cmake-args -DCMAKE_BUILD_TYPE=Release
catkin build controller_pkg planner_pkg trajectory_generation tesse_ros_bridge -j2 -p1 --no-status
