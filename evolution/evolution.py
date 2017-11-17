import numpy as np
import signal,os
from subprocess import Popen
import subprocess
from time import sleep
import os.path


config_path = "/home/kuro/Projects/ComputationalIntelligence/torcs-server/example_torcs_config.xml"
population_folder = "/home/kuro/Projects/ComputationalIntelligence/torcs-client/JesusTakeTheWheel/evolution/population"

sensors_size = 23
hidden_size = 50
output_size = 3

def create_weights(dev = 1.0):
    w1 = np.random.normal(size=(sensors_size, hidden_size),scale=dev)
    b1 = np.random.normal(size=(hidden_size) , scale=dev)
    w2 = np.random.normal(size=(hidden_size, output_size) ,scale=dev)
    b2 = np.random.normal(size=(output_size), scale=dev)
    return w1,b1,w2,b2

def weights_to_vector(w1,b1,w2,b2):
    result = w1.flatten()
    result = np.append(result,b1.flatten())
    result = np.append(result,w2.flatten())
    result = np.append(result,b2.flatten())
    return result

def vector_to_weights(vec):
    end_pointer = sensors_size*hidden_size
    w1 = vec[:end_pointer].reshape((sensors_size,hidden_size))
    b1 = vec[end_pointer:end_pointer+hidden_size]
    end_pointer = end_pointer + hidden_size

    w2 = vec[end_pointer:end_pointer + hidden_size*output_size].reshape((hidden_size,output_size))
    end_pointer = end_pointer + hidden_size*output_size

    b2 = vec[end_pointer:]
    return w1,b1,w2,b2

def createPopulations(creator_function, size):
    for i in range(size):
        individual = creator_function()


if __name__ == '__main__':
    population = []




    for i in range(1000):
        subprocess.call("/home/kuro/Projects/ComputationalIntelligence/torcs-client/JesusTakeTheWheel/train.sh")