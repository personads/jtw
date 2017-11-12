# -*- coding: utf-8 -*-
import torch
import numpy as np

from collections import defaultdict

from config import *

def cumulative_reward(state):
    res = 0.
    state = state_to_dict(state)
    print(state)
    res -= .5 * state['damage']
    res += .1 * state['distance_raced']
    res *= 1/state['race_position']
    edge_dists = sum([v for v in state['distances_from_edge']])
    res += .1 * edge_dists if edge_dists > 0 else -1. * edge_dists
    res -= 20* np.abs(state['distance_from_center'])
    res *= .1* state['speed_x'] if res > 0 else np.abs(state['speed_x'])
    return res
