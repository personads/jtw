from pytocl.driver import Driver
from pytocl.car import State, Command

from config import *
from utils.data import *
from disciples.mlp import MultiLayerPerceptron
from _datetime import datetime


class MLPDriver(Driver):

    def __init__(self, model_path):
        super().__init__()
        self.epoch = 0
        self.jesus = MultiLayerPerceptron(num_layers=3)
        self.jesus.restore(model_path)
        self.position = -1
        self.expected_gear = 0
        self.max_gear = 6

    def calc_gear(self, command, carstate):
        if carstate.rpm > 7000 and carstate.gear < self.max_gear:
            self.expected_gear = carstate.gear + 1

        if carstate.rpm < 3000 and carstate.gear != 0:
            self.expected_gear = carstate.gear - 1

        if carstate.gear != self.expected_gear:
            command.gear = self.expected_gear
            # print("attempting gear change from", carstate.gear, "to", self.expected_gear)
        if not command.gear:
            command.gear = carstate.gear or 1


    def drive(self, carstate: State) -> Command:
        command = Command()
        current_state = state_to_vector(carstate)
        command_vector = self.jesus.take_wheel(current_state)
        command = vector_to_command(command_vector)
        self.calc_gear(command, carstate)
        self.position = carstate.race_position
        self.epoch += 1
        return command

    def on_shutdown(self):
        with open("race_results/" + datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "w") as file:
            file.write(str(self.position))

