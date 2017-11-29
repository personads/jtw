import datetime
import numpy as np
from pytocl.driver import Driver
from pytocl.car import State, Command

from utils.data import *


class Cheesus(Driver):
    def __init__(self):
        super().__init__()
        self.epochCounter = 0
        self.race_width = 0
        self.data = []
        self.corrections = 0
        self.state = -1
        self.last_angle = 0

    def smooth_steer(self, state, target, command):
        steering_error = target - state.distance_from_center
        if np.abs(steering_error) > .5:
            steering_error = .5 * np.sign(steering_error)
            steering_error = 0. if self.corrections < 1 else steering_error*(1/self.corrections)
            self.corrections += .1
            print("corrected:", steering_error, "\nstate:", state_to_dict(state))
        else:
            self.corrections = 0
        command.steering = self.steering_ctrl.control(
            steering_error,
            state.current_lap_time
        )

    def drive(self, carstate: State) -> Command:
        angle_change = 2

        command = Command()
        if self.epochCounter == 0:
            self.race_width = carstate.distances_from_edge[0] + carstate.distances_from_edge[18]
            self.epochCounter = 1
        if self.state == -1:
            v_x = 30
            self.accelerate(carstate, v_x, command)
            self.smooth_steer(carstate, 0.0, command)
            if carstate.distance_from_start > 50 and carstate.distance_from_start < 500:
                self.state = 0
        elif self.state == 0:
            if carstate.angle < self.last_angle - angle_change:
                self.last_angle = carstate.angle
                self.state = 1
            else:
                command.gear = 1
                if carstate.speed_x < 5:
                    command.accelerator = 1
                if carstate.speed_x > 0:
                    command.steering = 1
                else:
                    command.brake = 1

        elif self.state == 1:
            if carstate.angle < -89 and carstate.angle > -91:
                self.state = 2
            else:
                if carstate.angle < self.last_angle - angle_change:
                    self.last_angle = carstate.angle
                    self.state = 0
                else:
                    command.gear = -1
                    if carstate.speed_x < 0:
                        command.steering = -1
                    else:
                        command.brake = 1
                    if carstate.speed_x > -5:
                        command.accelerator = 1

        elif self.state == 2:
            command.brake = 1
            command.steering = 0
            command.accelerator = 0
            if carstate.speed_x > -1:
                self.state = 3

        elif self.state == 3:
            command.gear = 1
            command.steering = 0
            if carstate.speed_x < 10:
                command.accelerator = 1
            if carstate.speed_x < 0:
                command.brake = 1
            if carstate.distances_from_edge[9] > 0 and carstate.distances_from_edge[9] < 0.40 * self.race_width:
                self.state = 4
                if carstate.angle > -89:
                    command.steering = -0.1
                if carstate.angle < -91:
                    command.steering = 0.1


        elif self.state == 4:
            command.gear = -1
            command.steering = 0
            if carstate.speed_x > -10:
                command.accelerator = 1
            if carstate.speed_x > 0:
                command.brake = 1
            if carstate.distances_from_edge[9] < 0 or carstate.distances_from_edge[9] > 0.55 * self.race_width:
                self.state = 3
            if carstate.angle > -89:
                command.steering = -0.1
            if carstate.angle < -91:
                command.steering = +0.1
        print(self.state)
        return command

    def on_shutdown(self):
        pass
