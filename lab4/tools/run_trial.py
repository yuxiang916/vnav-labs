#!/usr/bin/env python3
"""Run a fresh official Unity/TESSE race, preserving real ROS evidence."""
import argparse
import os
from pathlib import Path
import signal
import shutil
import subprocess
import time

parser = argparse.ArgumentParser()
parser.add_argument('name')
parser.add_argument('--mode', choices=['hover', 'race'], default='race')
parser.add_argument('--seconds', type=float, default=160)
parser.add_argument('--record', action='store_true')
parser.add_argument('--export', type=Path)
parser.add_argument('--finish-hold', type=float, default=15,
                    help='Simulation seconds of recording after the reference reaches its end.')
args = parser.parse_args()
os.environ['ROS_HOSTNAME'] = 'localhost'
os.environ['ROS_IP'] = '127.0.0.1'
os.environ['ROS_MASTER_URI'] = 'http://localhost:11311'
os.environ['DISABLE_ROS1_EOL_WARNINGS'] = '1'
def interrupted(signum, frame):
    raise KeyboardInterrupt()
signal.signal(signal.SIGINT, interrupted)
signal.signal(signal.SIGTERM, interrupted)
out = Path.home() / 'lab4-results' / args.name
out.mkdir(parents=True, exist_ok=True)
processes = []

def start(label, command, cwd=None):
    log = (out / (label + '.log')).open('w')
    p = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT,
                         cwd=cwd, start_new_session=True)
    processes.append((label, p, log))
    return p

try:
    start('roscore', ['roscore'])
    time.sleep(3)
    sim = Path.home() / 'vnav-builds/lab4'
    start('unity', [str(sim/'lab4.x86_64'), '-batchmode', '-nographics',
                    '-logFile', str(out/'unity-player.log')], sim)
    time.sleep(4)
    start('bridge', ['roslaunch', 'tesse_ros_bridge', 'tesse_quadrotor_bridge.launch',
                    'publish_clock:=false', 'publish_collisions:=true'])
    start('clock', ['python3', str(Path.home()/'lab4-results/odom_clock.py')])
    import rospy
    from nav_msgs.msg import Odometry
    from trajectory_msgs.msg import MultiDOFJointTrajectoryPoint
    rospy.init_node('lab4_trial_coordinator', disable_signals=True)
    state = rospy.wait_for_message('/current_state', Odometry, timeout=40)
    print('INITIAL_STATE', state.pose.pose, flush=True)
    last_trajectory = [0.0, time.monotonic()]
    def desired(msg):
        t = msg.time_from_start.to_sec()
        if t != last_trajectory[0]:
            last_trajectory[:] = [t, time.monotonic()]
    rospy.Subscriber('/desired_state', MultiDOFJointTrajectoryPoint, desired, queue_size=1)
    start('measurement', ['python3', str(Path.home()/'lab4-results/measure.py'),
                          str(out/'flight.csv')])
    start('bag', ['rosbag', 'record', '-O', str(out/'flight.bag'),
                  '/current_state', '/desired_state', '/desired_traj_vertices',
                  '/tesse/collision', '/clock', '/rotor_speed_cmds'])
    if args.record:
        os.environ['DISPLAY'] = ':84'
        os.environ['LIBGL_ALWAYS_SOFTWARE'] = '1'
        start('rviz', ['rviz', '-d', str(Path.home()/'lab4-results/race.rviz')])
        time.sleep(4)
        start('video', ['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y',
              '-f', 'x11grab', '-video_size', '1280x720', '-framerate', '12',
              '-i', ':84.0', '-c:v', 'libx264', '-threads', '2',
              '-preset', 'ultrafast', '-pix_fmt', 'yuv420p',
              '-movflags', '+faststart', str(out/'rviz_drone_race.mp4')])
    time.sleep(3)
    if args.mode == 'hover':
        start('hover', ['roslaunch', 'planner_pkg', 'static_point_test.launch',
              'simulator_data_directory:='+str(sim/'lab4_Data')])
    else:
        start('controller', ['roslaunch', 'trajectory_generation', 'traj_following.launch'])
        time.sleep(3)
        start('waypoints', ['roslaunch', 'planner_pkg', 'traj_gen.launch',
              'simulator_data_directory:='+str(sim/'lab4_Data')])
    deadline = time.monotonic() + args.seconds
    finish_sim_time = None
    while time.monotonic() < deadline:
        failed = [(label, p.returncode) for label, p, _ in processes
                  if p.poll() is not None]
        if failed:
            raise RuntimeError('Trial process exited: '+str(failed))
        duration = rospy.get_param('/lab4/trajectory_duration', 0.0)
        if args.mode == 'race' and duration > 0 and last_trajectory[0] >= duration-1e-6:
            if finish_sim_time is None:
                finish_sim_time = rospy.Time.now().to_sec()
            if rospy.Time.now().to_sec()-finish_sim_time >= args.finish_hold:
                print('TRAJECTORY_END_HOLD', duration, flush=True)
                break
        time.sleep(2)
    print('TRIAL_FINISHED', flush=True)
finally:
    # A second stop request must not interrupt bag/video finalization.
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    signal.signal(signal.SIGTERM, signal.SIG_IGN)
    priority = {'video':0,'bag':1,'measurement':2,'rviz':3,'waypoints':4,
                'hover':5,'controller':5,'clock':6,'bridge':7,'unity':8,'roscore':9}
    for label, p, log in sorted(processes,key=lambda item:priority.get(item[0],5)):
        if p.poll() is None:
            os.killpg(p.pid, signal.SIGINT)
            try:
                p.wait(timeout=12)
            except subprocess.TimeoutExpired:
                os.killpg(p.pid, signal.SIGTERM)
                try:
                    p.wait(timeout=4)
                except subprocess.TimeoutExpired:
                    os.killpg(p.pid, signal.SIGKILL)
        log.close()
    if args.export:
        shutil.copytree(out, args.export/args.name, dirs_exist_ok=True)
