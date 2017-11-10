# -*- coding: utf-8 -*-
import torch

from collections import defaultdict

from config import *

class RacingLoss(torch.nn.Criterion):
    def __init__(self, weights={'current_lap_time': .05, 
                                'damage': .05, 
                                'distance_raced': 0.5, 
                                'race_position': .1,
                                'speed_x': .1,
                                'speed_y': .05,
                                'distance_from_edge': .1,
                                'distance_from_center': .05}):
        self.weights = defaultdict(float, weights)
        self.output = None
        self.gradInput = None

    def calc_loss(self, state):
        res = 0.
        state = state_to_dict(state)
        for prop in weights:
            if type(state[prop]) is tuple:
                for prop_val in state[prop]:
                    res += weights[prop]/len(state[prop]) * prop_val
            else:
                res += weights[prop] * state[prop]
        return res

    def forward(self, state, _):
        self.output = self.calc_loss(state)
        return self.output

    def backward(self, state, _):
        return self.output