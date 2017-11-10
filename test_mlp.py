import torch
from torch.autograd import Variable

from config import *
from disciples.mlp import MultiLayerPerceptron

if __name__ == '__main__':
    x = Variable(torch.randn(100, len(STATE_PROPERTIES)))
    y = Variable(torch.randn(100, len(COMMAND_PROPERTIES)), requires_grad=False)
    model = MultiLayerPerceptron()
    model.train(x, y, 10000)