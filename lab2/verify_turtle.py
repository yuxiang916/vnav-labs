#!/usr/bin/env python3
import rospy, time, json
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
rospy.init_node('lab2_turtle_check',anonymous=True)
pub=rospy.Publisher('/turtle1/cmd_vel',Twist,queue_size=10)
initial=rospy.wait_for_message('/turtle1/pose',Pose,timeout=10)
time.sleep(1)
msg=Twist(); msg.linear.x=1.0; msg.angular.z=0.8
for _ in range(75): pub.publish(msg); time.sleep(0.1)
pub.publish(Twist())
final=rospy.wait_for_message('/turtle1/pose',Pose,timeout=5)
dist=((final.x-initial.x)**2+(final.y-initial.y)**2)**0.5
assert dist>0.05,dist
print(json.dumps({'initial':[initial.x,initial.y,initial.theta],
                  'final':[final.x,final.y,final.theta],
                  'displacement':dist,'result':'PASS'},indent=2))
