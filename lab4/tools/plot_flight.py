#!/usr/bin/env python3
"""Plot recorded TESSE trajectories and tracking errors."""
import json
from pathlib import Path
import sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

folder = Path(sys.argv[1])
d = np.genfromtxt(folder/'flight.csv',delimiter=',',names=True)
m = json.loads((folder/'metrics.json').read_text())
t = d['t']-d['t'][0]
fig = plt.figure(figsize=(11,4.4))
ax = fig.add_subplot(121,projection='3d')
ax.plot(d['xd'],d['yd'],d['zd'],color='#2876c8',label='Reference',lw=1.5)
ax.plot(d['x'],d['y'],d['z'],color='#e57c22',label='TESSE measured',lw=1.2)
for gate in m['gates']:
    x,y,z = gate['center']
    ax.scatter([x],[y],[z],c='#b62c3a',s=12)
ax.set(xlabel='x [m]',ylabel='y [m]',zlabel='z [m]',title='Official Unity/TESSE course')
ax.set_title('Official Unity/TESSE course',fontsize=11,pad=10)
ax.legend(fontsize=8,loc='upper left')
ax = fig.add_subplot(122)
ax.plot(d['xd'],d['yd'],color='#2876c8',label='Reference',lw=1.5)
ax.plot(d['x'],d['y'],color='#e57c22',label='TESSE measured',lw=1.2)
for gate in m['gates']:
    x,y,z = gate['center']
    ax.scatter([x],[y],c='#b62c3a',s=18,zorder=4)
    ax.annotate(str(gate['gate']+1),(x,y),xytext=(3,5),textcoords='offset points',fontsize=8)
ax.set(xlabel='x [m]',ylabel='y [m]',title='XY projection / numbered gates')
ax.set_aspect('equal',adjustable='datalim')
ax.grid(alpha=.2)
ax.legend(fontsize=8)
fig.tight_layout()
fig.savefig(folder/'trajectory.png',dpi=180)
plt.close(fig)

fig,axes = plt.subplots(2,1,figsize=(10,5),sharex=True)
err = np.sqrt(sum((d[c]-d[c+'d'])**2 for c in ['x','y','z']))
axes[0].plot(t,err,c='#2876c8',lw=1)
axes[0].set(ylabel='3D error [m]',title='Tracking error from recorded telemetry')
yaw_err = np.rad2deg(np.arctan2(np.sin(d['yaw']-d['yawd']),np.cos(d['yaw']-d['yawd'])))
axes[1].plot(t,yaw_err,c='#e57c22',lw=1)
axes[1].set(xlabel='Simulation time since first desired sample [s]',ylabel='Yaw error [deg]')
for ax in axes:
    ax.grid(alpha=.2)
    for gate in m['gates']:
        if gate.get('passed_in_order'):
            ax.axvline(gate['time_s'],c='gray',alpha=.2,lw=.7)
fig.tight_layout()
fig.savefig(folder/'tracking_error.png',dpi=180)
plt.close(fig)
