'''
functions for swarm behaviour
'''

from utils.data import *

OPPONENT_DISTANCE_MIN = 160.
EDGE_DISTANCE_MIN = 20.
AVOIDANCE_DECELARATION = .2
AVOIDANCE_STEERING = .1

def collect_distances(distances, sensors=None, weights=None):
    sensors = sensors if sensors else [i for i in range(len(distances))]
    weights = weights if weights else [1/len(sensors) for _ in range(len(sensors))]
    return sum([distances[s]*weights[i] for i, s in enumerate(sensors)])

def apply_force_field(state, command):
    state = state_to_dict(state, apply_mask=False)
    # calculate average distances in pie shape (17 is front and center)
    dist_front = collect_distances(state['opponents'], [s for s in range(13, 22)])
    dist_right = collect_distances(state['opponents'], [s for s in range(22, 31)])
    dist_back = collect_distances(state['opponents'], [s for s in range(31, 36)] + [s for s in range(4)])
    dist_left = collect_distances(state['opponents'], [s for s in range(4, 13)])
    # calculate average distance from edges
    dist_edges = collect_distances(state['distances_from_edge'])
    dist_edges_left = collect_distances(state['distances_from_edge'], [i for i in range(9)]) 
    dist_edges_right = collect_distances(state['distances_from_edge'], [i for i in range(10, 19)]) 
    # if front opponent distances are < minimum
    if dist_front < OPPONENT_DISTANCE_MIN:
        # if distance from edges > 100
        print("opponents in front:", dist_front, dist_right, dist_back, dist_left)
        if dist_edges > EDGE_DISTANCE_MIN and dist_edges > 0:
            # steer in direction of largest opening
            print("edges are far:", dist_edges, dist_edges_left, dist_edges_right)
            avoidance_steering = AVOIDANCE_STEERING
            # if right gap to edge is larger
            if dist_edges_left < dist_edges_right:
                # and if right opponent is farther away
                if dist_left < dist_right:
                    avoidance_steering *= -1
            # ig left gap to edge is larger
            else:
                # and if right opponent is farther away
                if dist_left < dist_right:
                    avoidance_steering *= -1
            # scale to distance
            avoidance_steering *= OPPONENT_DISTANCE_MIN/dist_front
            # add to steering set by holy ghost
            print("adjusting steering by:", avoidance_steering)
            command.steering += avoidance_steering
        else:
            # adjust acceleration proportionally
            print("edges are close:", dist_edges)
            avoidance_decelaration = AVOIDANCE_DECELARATION
            print("decelerating by:", avoidance_decelaration)
            command.brake += avoidance_decelaration
        print(command.accelerator, command.brake, command.steering)
    # if distances to rear opponent are < minimum
    if dist_back < OPPONENT_DISTANCE_MIN:
        print("opponents in back:", dist_front, dist_right, dist_back, dist_left)

