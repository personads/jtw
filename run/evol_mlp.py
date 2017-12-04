#! /usr/bin/env python3
import numpy as np
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from pytocl.main import main
from drivers.evol_mlp import EvolMLPDriver

save_folder = "/home/kuro/Projects/ComputationalIntelligence/torcs-client/JesusTakeTheWheel/evolution/results"
sensors_size = 23
hidden_size = 50
output_size = 3

def create_weights(dev = 1.0):
    w1 = np.random.normal(size=(sensors_size, hidden_size),scale=dev)
    b1 = np.random.normal(size=(hidden_size) , scale=dev)
    w2 = np.random.normal(size=(hidden_size, output_size) ,scale=dev)
    b2 = np.random.normal(size=(output_size), scale=dev)
    return w1,b1,w2,b2


if __name__ == '__main__':
    w1, b1, w2, b2 = create_weights()

    main(EvolMLPDriver(save_folder, 1, w1, b1, w2, b2))
