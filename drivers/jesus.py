import numpy as np

from pytocl.driver import Driver
from pytocl.car import State, Command
from utils.data import *
from utils.swarm import *

class Jesus(Driver):
    """
    Method to guide car back onto track.

    Input:
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
    def __init__(self, model):
        super().__init__()
        # meta
        self.epoch = 0
        self.max_gear = 6
        self.expected_gear = 0
        self.holy_ghost = model
        # recovery
        self.max_unstuck_speed = 5
        self.min_unstuck_dist = .5
        self.max_unstuck_angle = 15

    def calc_gear(self, command, carstate):
        if carstate.rpm > 7000 and carstate.gear < self.max_gear:
            self.expected_gear = carstate.gear + 1

        if carstate.rpm < 3000 and carstate.gear > 0:
            self.expected_gear = carstate.gear - 1

        if carstate.gear != self.expected_gear:
            command.gear = self.expected_gear
            # print("attempting gear change from", carstate.gear, "to", self.expected_gear)
        if not command.gear:
            command.gear = carstate.gear or 1

    def drive(self, carstate: State) -> Command:
        command = Command()
        # recovery check
        if not self.is_on_track(carstate):
            current_state = state_to_vector(carstate)
            # default behaviour
            if 0 < np.abs(carstate.angle) < 30:
                command_vector = self.holy_ghost.take_wheel(current_state)
                command = vector_to_command(command_vector)
                self.calc_gear(command, carstate)
                apply_force_field(carstate, command)
                print(command)
                print("position:", carstate.race_position   )
                return command
            # reposition forward
            elif 30 < np.abs(carstate.angle) < 180:
                if carstate.speed_x > 0:
                    if carstate.angle < 0:
                        command.steering = -1
                    else:
                        command.steering = 1
                    command.gear = 1
                    command.brake = 0
                    command.accelerator = 0.3
                    # print('Reposition forward')
            # reposition backward
            elif carstate.speed_x < 0 and carstate.distance_from_center != 0:
                if carstate.angle < 0:
                        command.steering = -1
                else:
                    command.steering = 1
                command.gear = -1
                command.brake = 0
                command.accelerator = 0.3
                # print('Reposition backward')
        # recovery mode
        else:
            # Car points towards track center and is on LHS of track
            if carstate.angle * carstate.distance_from_center > 0 and carstate.distance_from_center > self.min_unstuck_dist:
                command.steering = 1
                command.gear = 1
                command.brake = 0
                command.accelerator = 0.3
                # print(1)
            # Car points towards track center and is on RHS of track
            if carstate.angle * carstate.distance_from_center > 0 and carstate.distance_from_center < -self.min_unstuck_dist:
                command.steering = 1
                command.gear = 1
                command.brake = 0
                command.accelerator = 0.3
                # print(2)
            # Car points outwards and is on LHS of track
            if carstate.angle * carstate.distance_from_center < 0 and carstate.distance_from_center > self.min_unstuck_dist:
                command.steering = - 1
                command.gear = -1
                command.brake = 0
                command.accelerator = 0.5
                # print(3)
            # Car points outwards and is on RHS of track
            if carstate.angle * carstate.distance_from_center < 0 and carstate.distance_from_center < -self.min_unstuck_dist:
                command.steering = -1
                command.gear = -1
                command.brake = 0
                command.accelerator = 0.3
                # print(4)
        self.epoch += 1
        return command

    def is_on_track(self, carstate: State):
        if carstate.speed_x < self.max_unstuck_speed and np.abs(carstate.distance_from_center) > self.min_unstuck_dist:
            recovery = True
        else:
            recovery = False
        # print("rect?", self.recovery, carstate.speed_x, np.abs(carstate.distance_from_center))
        return recovery
