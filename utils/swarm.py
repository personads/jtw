'''
functions for swarm behaviour
'''

from utils.data import *

OPPONENT_DISTANCE_MIN = 170.
EDGE_DISTANCE_MIN = 20.
AVOIDANCE_STEERING = .1

def calc_average_distance(distances, sensors=None):
    sensors = sensors if sensors else [i for i in range(len(distances))]
    return sum([distances[i] for i in sensors])/len(sensors)

def apply_force_field(state, command):
    state = state_to_dict(state, apply_mask=False)
    # calculate average distances in pie shape (17 is front and center)
    dist_front = calc_average_distance(state['opponents'], [s for s in range(13, 22)])
    dist_right = calc_average_distance(state['opponents'], [s for s in range(22, 31)])
    dist_back = calc_average_distance(state['opponents'], [s for s in range(31, 36)] + [s for s in range(4)])
    dist_left = calc_average_distance(state['opponents'], [s for s in range(4, 13)])
    # calculate average distance from edges
    dist_edges = calc_average_distance(state['distances_from_edge'])
    dist_edges_left = calc_average_distance(state['distances_from_edge'], [i for i in range(9)]) 
    dist_edges_right = calc_average_distance(state['distances_from_edge'], [i for i in range(10, 19)]) 
    # if front opponent distances are < minimum
    if dist_front < OPPONENT_DISTANCE_MIN:
        # if distance from edges > 100
        print("opponents are near:", dist_front, dist_right, dist_back, dist_left)
        if dist_edges > EDGE_DISTANCE_MIN and dist_edges > 0:
            # steer in direction of largest opening
            print("edges are far:", dist_edges, dist_edges_left, dist_edges_right)
            avoidance_steering = AVOIDANCE_STEERING if dist_edges_left > dist_edges_right else -AVOIDANCE_STEERING
            print("distance factor:", OPPONENT_DISTANCE_MIN/dist_front)
            avoidance_steering *= OPPONENT_DISTANCE_MIN/dist_front
            command.steering += avoidance_steering
        else:
            # adjust acceleration proportionally
            print("edges are close:", dist_edges)
        print(command.accelerator, command.brake, command.steering)
