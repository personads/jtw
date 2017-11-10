# -*- coding: utf-8 -*-
import torch
import numpy as np

from collections import defaultdict

from config import *

class RacingLoss:
    def __init__(self, weights={'current_lap_time': .0, 
                                'damage': .05, 
                                'distance_raced': 0.5, 
                                'race_position': .1,
                                'speed_x': .1,
                                'distances_from_edge': .1,
                                'distance_from_center': .05}):
        self.weights = defaultdict(float, weights)
        self.output = None
        self.gradInput = None

    def _get_property_value(self, prop, value):
        res = value
        if prop in ['distance_raced', 'race_position', 'speed_x', 'distances_from_edge']:
            if value > 0:
                res = 1/res
            elif value == 0:
                res = 1
        res = np.abs(res)
        return res

    def calc_loss(self, state):
        res = 0.
        state = state_to_dict(state)
        for prop in self.weights:
            print(prop, state[prop])
            if type(state[prop]) is tuple:
                for prop_val in state[prop]:
                    res += self.weights[prop]/len(state[prop]) * self._get_property_value(prop, prop_val) 
            else:
                res += self.weights[prop] * self._get_property_value(prop, state[prop])
        return res

    def forward(self, state, _):
        self.output = self.calc_loss(state)
        return self.output

    def backward(self, state, _):
        self.gradInput = self.output
        return self.gradInput
