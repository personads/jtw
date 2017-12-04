from pytocl.driver import Driver
from pytocl.car import State, Command
import numpy as np


from config import *
from utils.data import *
from disciples.mlp import MultiLayerPerceptron

class recmode_mlp(Driver):
    """
    Method to guide car back onto track.

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
        #self.jesus.restore(model_path)
        self.recovery = False
        self.max_unstuck_speed = 60
        self.min_unstuck_dist = 1
        self.max_unstuck_angle = 15

    def calc_gear(self, command, carstate):
        acceleration = command.accelerator
        if acceleration > 0:
            if carstate.rpm > 8000:
                command.gear = carstate.gear + 1
        if carstate.rpm < 2500 and carstate.gear != 0:
            command.gear = carstate.gear - 1
        if not command.gear:
            command.gear = carstate.gear or 1
        if carstate.speed_x < 0:
            command.gear =+1

    def drive(self, carstate: State) -> Command:

        command = Command()

        if self.offTrack(carstate) == False:
            current_state = state_to_vector(carstate)

        # MLP Driver
            if 0 < np.abs(carstate.angle) < 50:
                command_vector = self.jesus.take_wheel(current_state)
                command = vector_to_command(command_vector)
                self.calc_gear(command, carstate)
                self.epoch += 1
                print(command)
                return command

        # Reposition car
            elif 30 < np.abs(carstate.angle) < 180:
                if carstate.speed_x > 0:
                    command.steering = 1
                    command.gear = 1
                    command.brake = 0
                    command.accelerator = 0.3
                    print('Reposition forward')

            elif carstate.speed_x < 0 and carstate.distance_from_center != 0:
                if carstate.angle < 0:
                        command.steering = -1
                else:
                    command.steering = 1
                command.gear = -1
                command.brake = 0
                command.accelerator = 0.3
                print('Reposition backward')

        elif self.offTrack(carstate) == True:

            # Car points towards track center and is on LHS of track
            if carstate.angle * carstate.distance_from_center > 0 and carstate.distance_from_center > 1:
                self.steering = 1
                self.gear = 1
                self.brake = 0
                self.accelerator = 0.3
                print(1)

            # Car points towards track center and is on RHS of track
            if carstate.angle * carstate.distance_from_center > 0 and carstate.distance_from_center < -1:
                self.steering = 1
                self.gear = 1
                self.brake = 0
                self.accelerator = 0.3
                print(2)

            # Car points outwards and is on LHS of track
            if carstate.angle * carstate.distance_from_center < 0 and carstate.distance_from_center > 1:
                self.steering = - 1
                self.gear = -1
                self.brake = 0
                self.accelerator = 0.5
                print(3)

            # Car points outwards and is on RHS of track
            if carstate.angle * carstate.distance_from_center < 0 and carstate.distance_from_center < -1:
                self.steering = -1
                self.gear = -1
                self.brake = 0
                self.accelerator = 0.3
                print(4)

        print(command)
        return command

    def offTrack(self, carstate: State) -> Command:

        if carstate.speed_x < self.max_unstuck_speed and np.abs(carstate.distance_from_center) > self.min_unstuck_dist:
            self.recovery = True
        else:
            self.recovery = False
        return self.recovery