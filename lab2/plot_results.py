#!/usr/bin/env python3
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # Register 3D projection on Ubuntu 20.04.
out=Path(__file__).resolve().parent/'results'
d=np.loadtxt(out/'trajectory.csv',delimiter=',',skiprows=1)
fig=plt.figure(figsize=(11,4.5))
ax=fig.add_subplot(121,projection='3d')
ax.plot(d[:,1],d[:,2],d[:,3],color='royalblue',label='AV1 / world')
ax.plot(d[:,4],d[:,5],d[:,6],color='orangered',label='AV2 / world')
ax.set(xlabel='x',ylabel='y',zlabel='z',title='World trajectories (live TF samples)'); ax.legend()
ax=fig.add_subplot(122,projection='3d')
ax.plot(d[:,7],d[:,8],d[:,9],color='orangered',label='AV2 / AV1')
ax.set(xlabel='x1',ylabel='y1',zlabel='z1',title='Relative ellipse: z1 = 2 y1 + 1'); ax.legend()
fig.tight_layout();fig.savefig(out/'05-trajectories.png',dpi=180);plt.close(fig)
fig,ax=plt.subplots(figsize=(6,5))
ax.plot(d[:,10],d[:,11],label='Live TF samples')
t=np.linspace(0,2*np.pi,500)
ax.plot(.5*np.sin(t),np.sqrt(5)/2*np.cos(t),'--',label='Analytical ellipse')
ax.set(xlabel='xp',ylabel='yp',title='Plane coordinates: b=0.5, a=sqrt(5)/2')
ax.axis('equal'); ax.grid(alpha=.3);ax.legend();fig.tight_layout()
fig.savefig(out/'06-plane-ellipse.png',dpi=180)
print('Plots generated from trajectory.csv')
