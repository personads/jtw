import numpy as np
import torch.nn as nn
import torch.optim as optim

from sklearn import preprocessing

def SOM_pos(neuron, map_shape):
    pos = []
    for entry in map_shape:
        pos.append(neuron % entry)
        neuron //= entry
    return tuple(pos)


def SOM_step(input, weights, map_shape):
    if weights is None:
        outputDim = 1
        for entry in map_shape:
            outputDim *= entry
        weights = np.random.rand(outputDim,len(input))
    input = input.reshape(len(input), 1)

    out = weights.dot(input)

    #TODO


def PCA_step(input , weights, outputDim, learningRate):
    if weights is None:
        weights = np.random.rand(outputDim,len(input))

    #Calculate y
    input = input.reshape(len(input),1)
    output = weights.dot(input)

    #Hebb's learning
    gradients = output.dot(input.T)

    for i in range(len(input)):
        c = 0
        for j in range(outputDim):
            c += weights[j][i]*output[j]
            gradients[j][i] -= output[j] * c
    gradients *= learningRate
    weights += gradients
    return weights


def PCA_test():
    data1 = np.array([
        [2.5, 2.4, 2.4],
        [0.5, 0.7, 0.7],
        [2.2, 2.9, 2.9],
        [1.9, 2.2, 2.2],
        [3.1, 3.0, 3.0],
        [2.3, 2.7, 2.7],
        [2, 1.6, 1.6],
        [1, 1.1, 1.1],
        [1.5, 1.6, 1.6],
        [1.1, 0.9, 0.9],
    ])

    data2 = np.array([
        [2.5, 2.4],
        [0.5, 0.7],
        [2.2, 2.9],
        [1.9, 2.2],
        [3.1, 3.0],
        [2.3, 2.7],
        [2, 1.6],
        [1, 1.1],
        [1.5, 1.6],
        [1.1, 0.9],
    ])

    weights = None
    data = data2
    for i in range(100000):
        weights = PCA_step(data[i % len(data)], weights, 2, 0.001)

    print(weights)


class NetworkNN(nn.Module):
    def __init__(self, sensors, first):
        super().__init__()
        self.linear1 = nn.Linear(sensors,first)
        #self.linear2 = nn.Linear(first,second)
        self.optimizer = optim.SGD(self.parameters(), lr=0.01)

    def forward(self, x):
        x = self.linear1(x)

    def update(self, true, calc):
        loss = nn.MSELoss()
        output = loss(true,calc)
        output.backward()
        self.optimizer.step()

    def save(self):
        self.save_state_dict('mytraining.pt')