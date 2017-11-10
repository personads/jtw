# -*- coding: utf-8 -*-
import torch
from torch.autograd import Variable

from config import *

class MultiLayerPerceptron(torch.nn.Module):
    def __init__(self, input_size=len(STATE_PROPERTIES), output_size=len(COMMAND_PROPERTIES), hidden_size=100):
        super(MultiLayerPerceptron, self).__init__()
        # set up variables
        self.input_size = input_size
        self.output_size = output_size
        self.hidden_size = hidden_size
        # set up layers
        self.layer1 = torch.nn.Linear(self.input_size, self.hidden_size)
        self.layer2 = torch.nn.Linear(self.hidden_size, self.output_size)
        # set up model
        self.criterion = torch.nn.MSELoss(size_average=False)
        self.optimizer = torch.optim.Adam(self.parameters(), lr=1e-4)

    def train(self, data_input, data_output, iterations):
        for i in range(iterations):
            model_output = self.predict(data_input, convert_output=False)
            loss = self.criterion(model_output, data_output)
            self.optimizer.zero_grad()
            loss.backward()
            if i%100 == 0: print(i, loss.data[0])
            self.optimizer.step()

    def predict(self, data_input, convert_output=True):
        layer1_out = self.layer1(data_input).clamp(min=0)
        model_output = self.layer2(layer1_out)
        return model_output
