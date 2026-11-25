cmake_minimum_required(VERSION 3.0.2)
project(trajectory_generation)
add_compile_options(-std=c++17)
find_package(catkin REQUIRED COMPONENTS
  roscpp tf tf2_geometry_msgs eigen_conversions geometry_msgs nav_msgs
  trajectory_msgs mav_trajectory_generation
)
find_package(Eigen3 REQUIRED)
catkin_package(CATKIN_DEPENDS roscpp tf tf2_geometry_msgs eigen_conversions
  geometry_msgs nav_msgs trajectory_msgs mav_trajectory_generation)
include_directories(${catkin_INCLUDE_DIRS} ${EIGEN3_INCLUDE_DIRS})
add_executable(trajectory_generation_node src/trajectory_generation_node.cpp)
add_executable(spiral_pose_publisher_node src/spiral_pose_publisher.cpp)
foreach(target trajectory_generation_node spiral_pose_publisher_node)
  add_dependencies(${target} ${catkin_EXPORTED_TARGETS})
  target_link_libraries(${target} ${catkin_LIBRARIES})
endforeach()
install(TARGETS trajectory_generation_node spiral_pose_publisher_node
  RUNTIME DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION})
install(DIRECTORY launch/ DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}/launch)
