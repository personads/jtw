# -*- coding: utf-8 -*-
import torch
from torch.autograd import Variable

from config import *

class MultiLayerPerceptron(torch.nn.Module):
    def __init__(self, hidden_size=100):
        """
        In the constructor we instantiate two nn.Linear modules and assign them as
        member variables.
        """
        super(MultiLayerPerceptron, self).__init__()
        # set up variables
        self.hidden_size = hidden_size
        # set up layers
        self.layer1 = torch.nn.Linear(len(STATE_PROPERTIES), self.hidden_size)
        self.layer2 = torch.nn.Linear(self.hidden_size, len(COMMAND_PROPERTIES))
        # set up model
        self.criterion = torch.nn.MSELoss(size_average=False)
        self.optimizer = torch.optim.Adam(self.parameters(), lr=1e-4)

    # def _data_to_vectors(self, data, properties, requires_grad=True):
    #     res = []
    #     for instance in data:
    #         # create vector for current instance
    #         res.append([eval('instance.' + prop) for prop in properties])
    #     return Variable(res)

    # def _vectors_to_commands(self, vectors):
    #     res = []
    #     for vector in vectors:
    #         cur_command = Command()
    #         for p_i, prop in enumerate(COMMAND_PROPERTIES):
    #             eval('cur_command.' + prop) = vector[p_i]
    #         res.append(cur_command)
    #     return res

    def train(self, data_input, data_output, iterations):
        # data_input = self._data_to_vectors(data_input, STATE_PROPERTIES)
        # data_output = self._data_to_vectors(data_output, COMMAND_PROPERTIES, requires_grad=False)
        print("training...")
        for i in range(iterations):
            model_output = self.predict(data_input, convert_output=False)
            loss = self.criterion(model_output, data_output)
            self.optimizer.zero_grad()
            loss.backward()
            if i%100 == 0: print(i, loss.data[0])
            self.optimizer.step()

    def predict(self, data_input, convert_output=True):
        # data_input = self._data_to_vectors(data_input, STATE_PROPERTIES)
        layer1_out = self.layer1(data_input).clamp(min=0)
        model_output = self.layer2(layer1_out)
        return model_output