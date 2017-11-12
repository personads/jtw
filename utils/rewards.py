# -*- coding: utf-8 -*-
import torch
import numpy as np

from collections import defaultdict

from config import *

class RacingReward:
    def __init__(self, weights={'damage': -1., 
                                'distance_raced': 1., 
                                'race_position': 1.,
                                'speed_x': 1.,
                                'distances_from_edge': 1.,
                                'distance_from_center': -.5}):
        self.weights = defaultdict(float, weights)

    def calc_reward(self, state):
        res = 0.
        state = state_to_dict(state)
        for prop in self.weights:
            print(prop, state[prop])
            if type(state[prop]) is tuple:
                for prop_val in state[prop]:
                    res += self.weights[prop]/len(state[prop]) * prop_val
            else:
                res += self.weights[prop] * state[prop]
        return res
