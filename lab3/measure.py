#!/usr/bin/env python3
"""Sample actual and desired positions on the same ROS clock."""
import csv
import sys
from collections import deque
from pathlib import Path

import rospy
from geometry_msgs.msg import PoseStamped
from nav_msgs.msg import Odometry, Path as RosPath
from trajectory_msgs.msg import MultiDOFJointTrajectoryPoint
from tf.transformations import euler_from_quaternion


def yaw(q):
    return euler_from_quaternion([q.x, q.y, q.z, q.w])[2]


def main():
    rospy.init_node("lab3_measurement", anonymous=True)
    desired = None
    record_path = Path(sys.argv[1]).stem == "circle"
    actual_path = deque(maxlen=220)
    desired_path = deque(maxlen=220)
    actual_pub = rospy.Publisher("/lab3/path/actual", RosPath, queue_size=1, latch=True)
    desired_pub = rospy.Publisher("/lab3/path/desired", RosPath, queue_size=1, latch=True)
    last_viz = rospy.Time()

    def reference(msg):
        nonlocal desired
        desired = msg.transforms[0]

    rospy.Subscriber("/desired_state", MultiDOFJointTrajectoryPoint, reference, queue_size=1)
    with open(sys.argv[1], "w", newline="") as output:
        writer = csv.writer(output)
        writer.writerow("t x y z xd yd zd yaw yawd vx vy vz wx wy wz qx qy qz qw".split())

        def current(msg):
            nonlocal last_viz
            target = desired
            if target is None:
                return
            p, d = msg.pose.pose.position, target.translation
            v, w = msg.twist.twist.linear, msg.twist.twist.angular
            q = msg.pose.pose.orientation
            writer.writerow((msg.header.stamp.to_sec(), p.x, p.y, p.z, d.x, d.y, d.z,
                             yaw(q), yaw(target.rotation), v.x, v.y, v.z, w.x, w.y, w.z,
                             q.x, q.y, q.z, q.w))
            if not record_path or (msg.header.stamp - last_viz).to_sec() < 0.10:
                return
            last_viz = msg.header.stamp
            actual = PoseStamped(header=msg.header, pose=msg.pose.pose)
            reference = PoseStamped(header=msg.header)
            reference.pose.position.x = d.x
            reference.pose.position.y = d.y
            reference.pose.position.z = d.z
            reference.pose.orientation = target.rotation
            actual_path.append(actual)
            desired_path.append(reference)
            actual_pub.publish(RosPath(header=msg.header, poses=list(actual_path)))
            desired_pub.publish(RosPath(header=msg.header, poses=list(desired_path)))

        sub = rospy.Subscriber("/current_state", Odometry, current, queue_size=1)
        rospy.spin()
        sub.unregister()


if __name__ == "__main__":
    main()

