#!/usr/bin/env python3
import json
from pathlib import Path
import sys
import rosbag

folder = Path(sys.argv[1])
with rosbag.Bag(str(folder/'flight.bag')) as bag:
    info = bag.get_type_and_topic_info().topics
    topics = {name:dict(type=value.msg_type,messages=value.message_count)
              for name,value in info.items()}
    collisions = []
    for topic,msg,t in bag.read_messages(topics=['/tesse/collision']):
        collisions.append(dict(t=msg.header.stamp.to_sec(),object=msg.object_name))
    result = dict(duration_sim_s=bag.get_end_time()-bag.get_start_time(),
                  topics=topics,collision_messages=collisions)
    assert topics['/current_state']['messages'] > 100
    assert topics['/desired_state']['messages'] > 100
    assert topics['/desired_traj_vertices']['messages'] > 0
    result['required_topics'] = 'PASS'
(folder/'bag-validation.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
