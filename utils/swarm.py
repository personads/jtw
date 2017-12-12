'''
functions for swarm behaviour
'''

from utils.data import *

OPPONENT_DISTANCE_MIN = 25.
EDGE_DISTANCE_MIN = 10.
AVOIDANCE_DECELARATION = .05

def collect_distances(distances, sensors=None, weights=None):
    sensors = sensors if sensors else [i for i in range(len(distances))]
    weights = weights if weights else [1. for _ in range(len(sensors))]
    clipped_distances = [distances[s]*weights[i] for i, s in enumerate(sensors) if distances[s] < 200]
    if len(clipped_distances) < 1:
        return 200.
    return sum(clipped_distances)/len(clipped_distances)

def apply_force_field(carstate, command):
    state = state_to_dict(carstate, apply_mask=False)
    # collect distance to opponents in front
    dist_opponents_f = state['opponents'][17]
    dist_opponents_fl = state['opponents'][16]
    dist_opponents_fr = state['opponents'][18]
    # collect edge distances
    dist_edges_l = state['distances_from_edge'][0]
    dist_edges_r = state['distances_from_edge'][17]
    dist_threshold = min(carstate.speed_x, 40)
    if min([dist_opponents_f, dist_opponents_fl, dist_opponents_fr]) < dist_threshold:
        if dist_edges_l <= 2 or dist_edges_r <= 2:
            command.brake = AVOIDANCE_DECELARATION

