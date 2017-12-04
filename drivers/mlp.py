from pytocl.driver import Driver
from pytocl.car import State, Command

from config import *
from utils.data import *
from drivers.jesus import Jesus
from disciples.mlp import MultiLayerPerceptron
from _datetime import datetime


class MLPDriver(Jesus):

    def __init__(self, model_path):
        mlp = MultiLayerPerceptron()
        mlp.restore(model_path)
        super().__init__(mlp)


