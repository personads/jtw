from pytocl.driver import Driver
from pytocl.car import State, Command

from config import *
from utils.data import *
from disciples.mlp import MultiLayerPerceptron



class rec_mode_driver(Driver):
    """
    Method to guide car back onto the centre of the track.

    Input:
    State vector
    'angle'
    'speed_x'
    'speed_y'
    'speed_z'
    'distances_from_edge'
    'distance_from_center'

    Output:
    Command vector
        acceleration
        brake
        steering

    """
    def __init__(self, model_path):
        super().__init__()
        self.epoch = 0
        self.jesus = MultiLayerPerceptron()
        self.jesus.restore(model_path)

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
        if -1 < carstate.distance_from_center < 1:
            current_state = state_to_vector(carstate)
            command_vector = self.jesus.take_wheel(current_state)
            command = vector_to_command(command_vector)
            self.calc_gear(command, carstate)
            if self.epoch % 100 == 0:
                print(command_vector)
            self.epoch += 1

        elif carstate.distance_from_center < -1 and carstate.angle > 0:
            self.steering = 1
            v_x = 50
            self.accelerate(carstate, v_x, command)
            self.calc_gear(command, carstate)
            print('recmode')

        elif (carstate.distance_from_center > 1) and carstate.angle < 0:
            self.steering = 1
            v_x = 50
            self.accelerate(carstate, v_x, command)
            self.calc_gear(command, carstate)
            print('recmode')

        return command


