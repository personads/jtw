'''
functions for swarm behaviour
'''

from utils.data import *

OPPONENT_DISTANCE_MIN = 25.
EDGE_DISTANCE_MIN = 20.
AVOIDANCE_DECELARATION = .2
AVOIDANCE_STEERING = .05

def collect_distances(distances, sensors=None, weights=None):
    sensors = sensors if sensors else [i for i in range(len(distances))]
    weights = weights if weights else [1. for _ in range(len(sensors))]
    clipped_distances = [distances[s]*weights[i] for i, s in enumerate(sensors) if distances[s] < 200]
    if len(clipped_distances) < 1:
        return 200.
    return sum(clipped_distances)/len(clipped_distances)

def apply_force_field(state, command):
    state = state_to_dict(state, apply_mask=False)
    # calculate average distances in pie shape (17 is front and center)
    pie_weights = [1/i for i in range(4, 0, -1)] + [1.] + [1/i for i in range(1, 5)]
    dist_front = collect_distances(state['opponents'], [s for s in range(13, 22)], pie_weights)
    dist_right = collect_distances(state['opponents'], [s for s in range(22, 31)], pie_weights)
    dist_back = collect_distances(state['opponents'], [s for s in range(31, 36)] + [s for s in range(4)], pie_weights)
    dist_left = collect_distances(state['opponents'], [s for s in range(4, 13)], pie_weights)
    # calculate average distance from edges
    dist_edges = collect_distances(state['distances_from_edge'])
    dist_edges_left = collect_distances(state['distances_from_edge'], [i for i in range(9)]) 
    dist_edges_right = collect_distances(state['distances_from_edge'], [i for i in range(10, 19)])
    print("opponents distances:", dist_front, dist_right, dist_back, dist_left)
    # if front opponent distances are < minimum
    if dist_front < OPPONENT_DISTANCE_MIN:
        # if distance from edges > 100
        print("opponents in front:", dist_front, dist_right, dist_back, dist_left)
        if dist_edges > EDGE_DISTANCE_MIN and dist_edges > 0 and (dist_edges_right > EDGE_DISTANCE_MIN/2 or dist_edges_left > EDGE_DISTANCE_MIN/2):
            # steer in direction of largest opening
            print("edges are far:", dist_edges, dist_edges_left, dist_edges_right)
            # steer additionally into current direction
            avoidance_steering = AVOIDANCE_STEERING
            if command.steering < 0:
                avoidance_steering *= -1
            # if not previously steering, pick side with larger freedom
            elif command.steering == 0:
                avoidance_steering *= 1 if dist_edges_left > dist_edges_right else -1
            # if steering left, but edge distance insufficient, steer right
            if avoidance_steering > 0 and dist_edges_left < EDGE_DISTANCE_MIN/2:
                avoidance_steering *= -1
            # if steering right, but edge distance insufficient, steer left
            if avoidance_steering < 0 and dist_edges_right < EDGE_DISTANCE_MIN/2:
                avoidance_steering *= -1
            # scale to distance
            avoidance_steering *= OPPONENT_DISTANCE_MIN/dist_front
            # add to steering set by holy ghost
            print("adjusting steering by:", avoidance_steering)
            command.steering += avoidance_steering
        # if edges and opponents are too close to avoid
        else:
            # and car is not off track
            if dist_edges > 0:
                # adjust acceleration proportionally
                print("edges are close:", dist_edges)
                avoidance_decelaration = AVOIDANCE_DECELARATION
                print("decelerating by:", avoidance_decelaration)
                command.brake += avoidance_decelaration
    # if distances to rear opponent are < minimum
    if dist_left < OPPONENT_DISTANCE_MIN:
        print("opponents on left:", dist_left)
        # if not already steering right
        if command.steering >= 0:
            if dist_edges > EDGE_DISTANCE_MIN and dist_edges > 0 and dist_right > OPPONENT_DISTANCE_MIN:
                command.steering += -AVOIDANCE_STEERING
                print("adjusted command steering:", command.steering)
    if dist_right < OPPONENT_DISTANCE_MIN:
        print("opponents on right:", dist_right)
        # if not already steering left
        if command.steering <= 0:
            if dist_edges > EDGE_DISTANCE_MIN and dist_edges > 0 and dist_left > OPPONENT_DISTANCE_MIN:
                command.steering += AVOIDANCE_STEERING
                print("adjusted command steering:", command.steering)

