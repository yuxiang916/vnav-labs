#!/usr/bin/env python3
"""Collect simulator telemetry and publish complete actual/reference RViz paths."""
import csv
import sys
import rospy
from geometry_msgs.msg import PoseStamped, PoseArray, Point
from visualization_msgs.msg import Marker, MarkerArray
from nav_msgs.msg import Odometry, Path
from trajectory_msgs.msg import MultiDOFJointTrajectoryPoint
from tf.transformations import euler_from_quaternion

rospy.init_node('lab4_measurement')
desired = None
actual_path, desired_path = [], []
actual_pub = rospy.Publisher('/lab4/path/actual', Path, queue_size=1, latch=True)
desired_pub = rospy.Publisher('/lab4/path/desired', Path, queue_size=1, latch=True)
gate_pub = rospy.Publisher('/lab4/gates', MarkerArray, queue_size=1, latch=True)
last_viz = 0

def gates(msg):
    markers = []
    for i, pose in enumerate(msg.poses):
        m = Marker()
        m.header.frame_id = 'world'
        m.ns, m.id, m.type, m.action = 'gates', i, Marker.LINE_STRIP, Marker.ADD
        m.pose = pose
        m.scale.x = 0.10
        m.color.r,m.color.g,m.color.b,m.color.a = 0.95,0.25,0.25,1.0
        m.points = [Point(0,y,z) for y,z in [(-1,-1),(1,-1),(1,1),(-1,1),(-1,-1)]]
        markers.append(m)
        label = Marker()
        label.header.frame_id = 'world'
        label.ns,label.id,label.type,label.action = 'labels',i,Marker.TEXT_VIEW_FACING,Marker.ADD
        label.pose.position.x = pose.position.x
        label.pose.position.y = pose.position.y
        label.pose.position.z = pose.position.z+1.7
        label.pose.orientation.w = 1
        label.scale.z = 0.9
        label.color.r,label.color.g,label.color.b,label.color.a = 1,1,1,1
        label.text = str(i+1)
        markers.append(label)
    gate_pub.publish(MarkerArray(markers=markers))

def reference(msg):
    global desired
    if msg.transforms:
        desired = msg

def yaw(q):
    return euler_from_quaternion([q.x,q.y,q.z,q.w])[2]

with open(sys.argv[1], 'w', newline='', buffering=1) as output:
    writer = csv.writer(output)
    writer.writerow('t x y z xd yd zd yaw yawd vx vy vz trajectory_t'.split())
    def current(msg):
        global last_viz
        if desired is None:
            return
        p, q = msg.pose.pose.position, msg.pose.pose.orientation
        v = msg.twist.twist.linear
        d = desired.transforms[0]
        t = msg.header.stamp.to_sec()
        writer.writerow([t,p.x,p.y,p.z,d.translation.x,d.translation.y,d.translation.z,
                         yaw(q),yaw(d.rotation),v.x,v.y,v.z,desired.time_from_start.to_sec()])
        if t-last_viz < 0.15:
            return
        last_viz = t
        a = PoseStamped(header=msg.header,pose=msg.pose.pose)
        r = PoseStamped(header=msg.header)
        r.pose.position.x,r.pose.position.y,r.pose.position.z = d.translation.x,d.translation.y,d.translation.z
        r.pose.orientation = d.rotation
        actual_path.append(a)
        desired_path.append(r)
        actual_pub.publish(Path(header=msg.header,poses=actual_path))
        desired_pub.publish(Path(header=msg.header,poses=desired_path))
    rospy.Subscriber('/desired_state', MultiDOFJointTrajectoryPoint, reference, queue_size=1)
    rospy.Subscriber('/desired_traj_vertices', PoseArray, gates, queue_size=1)
    rospy.Subscriber('/current_state', Odometry, current, queue_size=1)
    rospy.spin()
