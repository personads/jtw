from pytocl.driver import Driver
from pytocl.car import State, Command
import sys
import numpy as np
import os,signal
from config import *
from utils.data import *
from disciples.mlp import MultiLayerPerceptron

SAVE_PATH = "../resources/gear"
LOAD_PATH = "../resources/gear/active.npy"
MODEL_PATH = '../resources/models/mlp/'

class GearDriver(Driver):
    # Override the `drive` method to create your own driver
    def __init__(self, save_path=SAVE_PATH, load_path=LOAD_PATH):
        super().__init__()
        self.epoch = 0
        self.save_path = save_path
        self.upshifts = np.load(load_path)
        self.last_gear = 0
        self.model = mlp = MultiLayerPerceptron()
        self.model.restore(MODEL_PATH)
        self.changed = False
        self.downshift = []
    def drive(self, carstate: State) -> Command:
        command = Command()
        current_state = state_to_vector(carstate)
        command_vector = self.model.take_wheel(current_state)
        command = vector_to_command(command_vector)

        command.accelerator = 1.0
        command.brake = 0.0

        current_gear = carstate.gear
        current_rpm = carstate.rpm

        if current_gear != self.last_gear:
            self.last_gear = current_gear
            print("Added downshift", carstate.gear)
            self.downshift.append(carstate.rpm)

        if current_gear == 0:
            command.gear = 1
        elif current_gear == 6:
            command.gear = current_gear
        elif self.upshifts[current_gear-1] <= current_rpm:
                command.gear = current_gear + 1
                self.last_gear = current_gear
        else:
            command.gear = current_gear
        if self.epoch > 2500:
            f = open(self.save_path + "/result.txt", 'w')
            if carstate.distance_raced < 20000:
                f.write(str(carstate.distance_raced))
                print(self.downshift)
            else:
                f.write(str(0))
            f.close()
            sys.exit()
        self.epoch += 1
        return command
