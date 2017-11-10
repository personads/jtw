# -*- coding: utf-8 -*-
import torch
import numpy as np

from collections import defaultdict

from config import *

#class RacingLoss(torch.nn.Criterion):
class RacingLoss:
    def __init__(self, weights={'current_lap_time': .05, 
                                'damage': .05, 
                                'distance_raced': 0.5, 
                                'race_position': .1,
                                'speed_x': .1,
                                'speed_y': .05,
                                'distances_from_edge': .1,
                                'distance_from_center': .05}):
        self.weights = defaultdict(float, weights)
        self.output = None
        self.gradInput = None

    def calc_loss(self, state):
        res = 0.
        state = state_to_dict(state)
        for prop in self.weights:
            print(prop, state[prop])
            if type(state[prop]) is tuple:
                for prop_val in state[prop]:
                    prop_val = np.abs(prop_val)
                    if prop == 'distaces_from_edge':
                        prop_val = 1/prop_val if prop_val > 0 else 1
                    res += self.weights[prop]/len(state[prop]) * prop_val
            else:
                prop_val = np.abs(state[prop])
                if prop in ['distance_raced', 'race_position', 'speed_x', 'speed_y']:
                    prop_val = 1/prop_val if prop_val > 0 else 1
                res += self.weights[prop] * prop_val
        return res

    def forward(self, state, _):
        self.output = self.calc_loss(state)
        return self.output

    def backward(self, state, _):
        return self.output
