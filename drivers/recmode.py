from pytocl.driver import Driver
from pytocl.car import State, Command
import numpy as np


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
        self.max_gear = 6
        self.expected_gear = 0
        self.steering = 0
        self.jesus = MultiLayerPerceptron()
        self.jesus.restore(model_path)
        self.recovery = False
        self.max_unstuck_speed = 15
        self.min_unstuck_dist = 5
        self.max_unstuck_angle = 20


    def calc_gear(self, command, carstate):
            if carstate.rpm > 7000 and carstate.gear < self.max_gear:
                self.expected_gear = carstate.gear + 1

            if carstate.rpm < 3000 and carstate.gear != 0:
                self.expected_gear = carstate.gear - 1

            if carstate.gear != self.expected_gear:
                command.gear = self.expected_gear

            if not command.gear:
                command.gear = carstate.gear or 1


    def drive(self, carstate: State) -> Command:

        command = Command()

        if self.offTrack(carstate) == False:
            self.jesus.restore('resources/models/mlp/')
            current_state = state_to_vector(carstate)
            command_vector = self.jesus.take_wheel(current_state)
            command = vector_to_command(command_vector)
            self.calc_gear(command, carstate)
            self.epoch += 1

        elif self.offTrack(carstate) == True:
            print('Offtrack')

            # Car points towards track center and is on LHS of track
            if carstate.angle * carstate.distance_from_center > 0 and carstate.distance_from_center > 1:
                self.steering = - carstate.angle
                self.gear = 1
                self.brake = 0
                self.accelerate = 0.5

            # Car points towards track center and is on RHS of track
            if carstate.angle * carstate.distance_from_center > 0 and carstate.distance_from_center < -1:
                self.steering = - carstate.angle
                self.gear = 1
                self.brake = 0
                self.accelerate = 0.5

            # Car points outwards and is on LHS of track
            if carstate.angle * carstate.distance_from_center < 0 and carstate.distance_from_center > 1:
                self.steering = - carstate.angle
                self.gear = -1
                self.brake = 0
                self.accelerate = 0.5

            # Car points outwards and is on RHS of track
            if carstate.angle * carstate.distance_from_center < 0 and carstate.distance_from_center < -1:
                self.steering = - carstate.angle
                self.gear = -1
                self.brake = 0
                self.accelerate = 0.5

        print(command)
        return command

    def offTrack(self, carstate: State) -> Command:

        if np.absolute(carstate.angle) > self.max_unstuck_angle and carstate.speed_x < self.max_unstuck_speed and np.abs(carstate.distance_from_center) > self.min_unstuck_dist:
            if carstate.distance_from_center * np.absolute(carstate.angle) < 0:
                self.recovery = True
            else:
                self.recovery = False
        else:
            self.recovery = False

        return self.recovery
