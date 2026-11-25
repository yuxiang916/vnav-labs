#!/usr/bin/env python3
"""Drive ROS time from TESSE odometry when its clock timer cannot bootstrap."""
import rospy
from nav_msgs.msg import Odometry
from rosgraph_msgs.msg import Clock

rospy.init_node("lab3_odom_clock")
clock = rospy.Publisher("/clock", Clock, queue_size=1)
rospy.Subscriber("/current_state", Odometry,
                 lambda msg: clock.publish(Clock(clock=msg.header.stamp)), queue_size=1)
rospy.spin()
