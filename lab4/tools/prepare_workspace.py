"""Adapt the course's legacy catkin wrappers to Ubuntu 20.04 system libraries."""
from pathlib import Path
import shutil

ws = Path.home() / 'lab4_ws'
deps = ws / 'src/dependencies'
for name, library, header in [
    ('glog_catkin', 'glog', 'glog/logging.h'),
    ('gflags_catkin', 'gflags', 'gflags/gflags.h'),
    ('yaml_cpp_catkin', 'yaml-cpp', 'yaml-cpp/yaml.h'),
    ('nlopt', 'nlopt_cxx', 'nlopt.hpp'),
]:
    folder = deps / name
    folder.mkdir(exist_ok=True)
    (folder / 'CMakeLists.txt').write_text(f'''cmake_minimum_required(VERSION 3.0.2)
project({name})
find_package(catkin REQUIRED)
find_path(SYSTEM_INCLUDE_DIR {header} REQUIRED)
find_library(SYSTEM_LIBRARY NAMES {library} REQUIRED)
catkin_package(INCLUDE_DIRS ${{SYSTEM_INCLUDE_DIR}} LIBRARIES ${{SYSTEM_LIBRARY}})
''')
    (folder / 'package.xml').write_text(f'''<package format="2">
<name>{name}</name><version>0.0.1</version>
<description>Course dependency wrapper using the Ubuntu system library.</description>
<maintainer email="lab@example.invalid">Lab user</maintainer><license>BSD</license>
<buildtool_depend>catkin</buildtool_depend></package>
''')
bridge = ws / 'src/tesse-ros-bridge'
if not bridge.exists():
    shutil.copytree(Path.home() / 'lab3_ws/src/tesse-ros-bridge', bridge)
node = bridge / 'ROS/src/tesse_ros_bridge/tesse_ros_node.py'
text = node.read_text()
text = text.replace("        assert(self.prev_time < metadata['time'])",
                    "        if metadata['time'] <= self.prev_time:\n            return")
text = text.replace("                if self.publish_clock:\n                    curr_ros_time = rospy.Time.from_sec(metadata['time'])",
                    "                curr_ros_time = rospy.Time.from_sec(metadata['time'])\n                if self.publish_clock:")
node.write_text(text)
print('Workspace prepared:', ws)

