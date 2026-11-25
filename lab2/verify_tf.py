#!/usr/bin/env python3
import rospy, tf2_ros, numpy as np, time, json
from pathlib import Path
from visualization_msgs.msg import MarkerArray
rospy.init_node('lab2_tf_check',anonymous=True)
buf=tf2_ros.Buffer(); listener=tf2_ros.TransformListener(buf)
time.sleep(2)
out=Path(__file__).resolve().parent/'results'
rows=[]; errors=[]
def xyz(t):
    v=t.transform.translation; return np.array([v.x,v.y,v.z])
for _ in range(360):
    a=buf.lookup_transform('world','av1',rospy.Time(0),rospy.Duration(3))
    b=buf.lookup_transform('world','av2',a.header.stamp,rospy.Duration(3))
    rel=buf.lookup_transform('av1','av2',a.header.stamp,rospy.Duration(3))
    p1,p2,pr=map(xyz,[a,b,rel])
    c,s=p1[:2]; C=1-2*s*s
    expected=np.array([s*c-1,-s*s,C])
    q=a.transform.rotation
    R=np.array([[1-2*(q.y*q.y+q.z*q.z),2*(q.x*q.y-q.z*q.w),2*(q.x*q.z+q.y*q.w)],
                [2*(q.x*q.y+q.z*q.w),1-2*(q.x*q.x+q.z*q.z),2*(q.y*q.z-q.x*q.w)],
                [2*(q.x*q.z-q.y*q.w),2*(q.y*q.z+q.x*q.w),1-2*(q.x*q.x+q.y*q.y)]])
    xp=pr[0]+1; yp=(pr[1]+0.5+2*pr[2])/np.sqrt(5)
    errors.append([abs(c*c+s*s-1),np.max(abs(p2-np.array([s,0,C]))),
                   np.max(abs(pr-expected)),np.max(abs(pr-R.T@(p2-p1))),
                   abs(pr[2]-2*pr[1]-1),abs(4*xp*xp+4*yp*yp/5-1),
                   np.max(abs(R[:,1]-np.array([-s,c,0])))])
    rows.append([a.header.stamp.to_sec(),*p1,*p2,*pr,xp,yp])
    time.sleep(0.02)
markers=rospy.wait_for_message('/visuals',MarkerArray,timeout=5)
assert len(markers.markers)==5,len(markers.markers)
assert {m.header.frame_id for m in markers.markers}>={'world','av1','av2'}
maxerr=np.max(errors,axis=0)
assert np.max(maxerr)<1e-6,maxerr
np.savetxt(out/'trajectory.csv',rows,delimiter=',',header='stamp,av1_x,av1_y,av1_z,av2_x,av2_y,av2_z,rel_x,rel_y,rel_z,xp,yp',comments='')
result=dict(zip(['circle','world_av2','relative_formula','tf_composition','plane','ellipse','tangent_y'],maxerr.tolist()))
result.update(samples=len(rows),markers=len(markers.markers),result='PASS')
(out/'tf-validation.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
