#!/usr/bin/env python3
"""Evaluate real telemetry against the course gate planes, in course order."""
import argparse
import csv
import json
from pathlib import Path
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument('flight', type=Path)
parser.add_argument('gates', type=Path)
parser.add_argument('--aperture-half-size', type=float, default=0.75,
                    help='Conservative center crossing window, not a mesh collision test.')
args = parser.parse_args()
d = np.genfromtxt(args.flight, delimiter=',', names=True)
d = np.atleast_1d(d)
if not len(d):
    raise SystemExit('No flight samples')
points = np.column_stack([d[x] for x in ['x','y','z']])
targets = np.column_stack([d[x] for x in ['xd','yd','zd']])
gates = []
with args.gates.open() as f:
    for row in csv.reader(f):
        if not row or not row[0].startswith('red_square_drone_door'):
            continue
        name = row[0]
        index = int(name.split('(')[1].split(')')[0]) if '(' in name else 0
        x,y,z,qx,qy,qz,qw = map(float,row[1:])
        # Unity y/z swap and quaternion vector negation, as in course publisher.
        qx,qy,qz = -qx,-qz,-qy
        yaw = np.arctan2(2*(qw*qz+qx*qy),1-2*(qy*qy+qz*qz))
        gates.append((index,np.array([x,z,y]),yaw))
gates.sort(key=lambda gate:gate[0])
cursor = 0
crossings = []
for gate_number,(index,center,yaw) in enumerate(gates):
    normal = np.array([np.cos(yaw),np.sin(yaw),0])
    tangent = np.array([-np.sin(yaw),np.cos(yaw),0])
    relative = points-center
    signed = relative@normal
    previous_center = gates[gate_number-1][1] if gate_number else points[0]
    forward_sign = 1.0 if float((center-previous_center)@normal) >= 0 else -1.0
    hits = np.flatnonzero(signed[:-1]*signed[1:] < 0)
    result = {'gate':index,'center':center.tolist(),
              'closest_center_distance_m':float(np.min(np.linalg.norm(relative,axis=1))),
              'passed_in_order':False}
    for i in hits:
        if i < cursor:
            continue
        if (signed[i+1]-signed[i])*forward_sign <= 0:
            continue
        alpha = signed[i]/(signed[i]-signed[i+1])
        offset = (1-alpha)*relative[i]+alpha*relative[i+1]
        lateral,vertical = float(offset@tangent),float(offset[2])
        if max(abs(lateral),abs(vertical)) <= args.aperture_half_size:
            t = (1-alpha)*d['t'][i]+alpha*d['t'][i+1]
            result.update(passed_in_order=True,forward_crossing=True,time_s=float(t-d['t'][0]),
                          lateral_error_m=lateral,vertical_error_m=vertical)
            cursor = i+1
            break
    crossings.append(result)
    if not result['passed_in_order']:
        # Do not count later gates as ordered if this gate was missed.
        cursor = len(points)
errors = np.linalg.norm(points-targets,axis=1)
yaw_error = np.arctan2(np.sin(d['yaw']-d['yawd']),np.cos(d['yaw']-d['yawd']))
summary = dict(samples=len(d),duration_sim_s=float(d['t'][-1]-d['t'][0]),
    position_rmse_m=float(np.sqrt(np.mean(errors**2))),
    position_max_error_m=float(max(errors)),
    yaw_rmse_deg=float(np.rad2deg(np.sqrt(np.mean(yaw_error**2)))),
    max_speed_m_s=float(max(np.sqrt(d['vx']**2+d['vy']**2+d['vz']**2))),
    final_position=points[-1].tolist(),final_target=targets[-1].tolist(),
    gates_passed_in_order=sum(g['passed_in_order'] for g in crossings),
    gate_count=len(gates),crossing_window_half_size_m=args.aperture_half_size,
    complete=all(g['passed_in_order'] for g in crossings),gates=crossings)
if summary['complete']:
    race_duration = crossings[-1]['time_s']
    race_mask = d['t']-d['t'][0] <= race_duration
    summary['race_duration_sim_s'] = race_duration
    summary['race_position_rmse_m'] = float(np.sqrt(np.mean(errors[race_mask]**2)))
    summary['race_position_max_error_m'] = float(max(errors[race_mask]))
    summary['race_yaw_rmse_deg'] = float(np.rad2deg(np.sqrt(np.mean(yaw_error[race_mask]**2))))
output = args.flight.with_name('metrics.json')
output.write_text(json.dumps(summary,indent=2),encoding='utf-8')
print(json.dumps(summary,indent=2))
