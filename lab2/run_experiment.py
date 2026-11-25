#!/usr/bin/env python3
"""Run the real ROS nodes, collect evidence, and validate live transforms."""
import os, sys, time, signal, subprocess, json, math
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'results'
OUT.mkdir(exist_ok=True)
os.environ.update(DISPLAY=':88', LIBGL_ALWAYS_SOFTWARE='1', QT_X11_NO_MITSHM='1', DISABLE_ROS1_EOL_WARNINGS='1')
procs=[]
def start(args, name):
    log=open(OUT/(name+'.log'),'w')
    p=subprocess.Popen(args, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
    procs.append(p)
    return p
def stop(p):
    if p.poll() is None:
        os.killpg(p.pid,signal.SIGINT)
        try: p.wait(timeout=15)
        except subprocess.TimeoutExpired:
            os.killpg(p.pid,signal.SIGTERM); p.wait(timeout=8)
def cmd(args,name=None):
    r=subprocess.run(args,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=30)
    if name: (OUT/name).write_text(r.stdout)
    if r.returncode: raise RuntimeError(' '.join(args)+'\n'+r.stdout)
    return r.stdout
def capture(name):
    cmd([sys.executable,'-c',
         'from PyQt5.QtWidgets import QApplication; import sys; '
         'app=QApplication(sys.argv); '
         'assert app.primaryScreen().grabWindow(0).save(sys.argv[1])',str(OUT/name)])
def ready():
    for _ in range(90):
        r=subprocess.run(['rosnode','list'],stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,text=True)
        if r.returncode==0 and '/rosout' in r.stdout: return
        time.sleep(1)
    raise RuntimeError('ROS master timeout')

try:
    start(['Xvfb',':88','-screen','0','1600x1000x24','-ac'],'xvfb')
    time.sleep(2)
    core=start(['roscore'],'turtle-roscore'); ready()
    turtle=start(['rosrun','turtlesim','turtlesim_node'],'turtlesim')
    time.sleep(5)
    # Separate process so rospy does not bind this coordinator to one master.
    test=ROOT/'verify_turtle.py'
    cmd([sys.executable,str(test)],'turtle-validation.json')
    capture('01-turtlesim.png')
    stop(turtle); stop(core); time.sleep(2)

    static=start(['roslaunch','two_drones_pkg','two_drones.launch','static:=True'],'static-launch')
    ready(); time.sleep(18)
    nodes=cmd(['rosnode','list'],'static-nodes.txt')
    cmd(['rostopic','list','-v'],'static-topics.txt')
    for node in ['av1broadcaster','av2broadcaster','plots_publisher_node','rviz']:
        assert '/'+node in nodes
        cmd(['rosnode','info','/'+node],'static-'+node+'.txt')
    capture('02-static-rviz.png')
    stop(static); time.sleep(3)

    dynamic=start(['roslaunch','two_drones_pkg','two_drones.launch'],'dynamic-launch')
    ready(); time.sleep(15)
    cmd(['rosnode','list'],'dynamic-nodes.txt')
    cmd(['rostopic','list','-v'],'dynamic-topics.txt')
    cmd([sys.executable,str(ROOT/'verify_tf.py')],'tf-validation-console.txt')
    capture('03-world-rviz.png')
    cmd(['rosnode','kill','/rviz'])
    time.sleep(3)
    cfg=Path(os.environ['HOME'])/'vnav_ws/src/two_drones_pkg/config/default.rviz'
    relcfg=OUT/'av1.rviz'
    relcfg.write_text(cfg.read_text().replace('Fixed Frame: world','Fixed Frame: av1'))
    rel=start(['rosrun','rviz','rviz','-d',str(relcfg)],'av1-rviz')
    time.sleep(15)
    capture('04-av1-rviz.png')
    stop(rel); stop(dynamic)
    cmd([sys.executable,str(ROOT/'plot_results.py')],'plot-console.txt')
    (OUT/'COMPLETE').write_text('LAB2_RUNTIME_CHECKS_PASSED\n')
    print('LAB2_RUNTIME_CHECKS_PASSED',flush=True)
finally:
    for p in reversed(procs): stop(p)
