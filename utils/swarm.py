'''
functions for swarm behaviour
'''

OPPONENT_DISTANCE_MIN = 50.
EDGE_DISTANCE_MIN = 100.

def calc_average_distance(distances, sensors):
    return sum([distances[i] for i in sensors])/len(sensors)

def apply_force_field(state, command):
    # calculate average distances in pie shape (17 is front and center)
    dist_front = calc_average_distance(state['opponents'], [s for s in range(13, 22)])
    dist_right = calc_average_distance(state['opponents'], [s for s in range(22, 31)])
    dist_back = calc_average_distance(state['opponents'], [s for s in range(31, 36)] + [s for s in range(4)])
    dist_left = calc_average_distance(state['opponents'], [s for s in range(4, 13)])
    # calculate average distance from edges
    dist_edges = sum(state['distances_from_edges'])/len(state['distances_from_edges'])
    # if front opponent distances are < minimum
    if dist_front < OPPONENT_DISTANCE_MIN:
        # if distance from edges > 100
        print("opponents are near:", dist_front, dist_right, dist_back, dist_left)
        if dist_edges > 100:
            # steer in direction of largest opening
            print("edges are far:", dist_edges)
        else:
            # adjust acceleration proportionally
            print("edges are close:", dist_edges)