from pytocl.driver import Driver
from pytocl.car import State, Command

from config import *
from disciples.mlp import MultiLayerPerceptron

class MLPDriver(Driver):

    def __init__(self):
        super().__init__()
        self.epochCounter = 0
        self.model = MultiLayerPerceptron()
        self.model.load('mlp_driver_100k/')

    def calc_gear(self, command, carstate):
        acceleration = command.accelerator
        if acceleration > 0:
            if carstate.rpm > 8000:
                command.gear = carstate.gear + 1
        if carstate.rpm < 2500 and carstate.gear != 0:
            command.gear = carstate.gear - 1
        if not command.gear:
            command.gear = carstate.gear or 1

    def drive(self, carstate: State) -> Command:
        command = Command()
        current_state = state_to_vector(carstate)
        command_vector = self.model.predict([current_state])[0]
        command = vector_to_command(command_vector)
        self.calc_gear(command)
        return command
