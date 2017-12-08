import os

import numpy as np

from pytocl.driver import Driver
from pytocl.car import State, Command
from config import *
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
        self.track_length = None
        self.max_gear = 6
        self.expected_gear = 0
        self.holy_coast = model
        # recovery
        self.recovery = False
        self.epochs_unmoved = 0
        # cheesus
        self.cheesus_state = None
        self.track_width = 0
        self.last_angle = 0
        self.close_to_jesus = False


    def calc_gear(self, command, carstate):
        '''
        Gear switching mechanism
        '''
        # evolved gear shifting RPMs
        upshift = np.array([7000, 9050, 9200, 9350, 9400])
        downshift = np.array([3000, 6000, 6700, 7000, 7300])
        # upshift
        if carstate.gear < self.max_gear and carstate.rpm > upshift[carstate.gear-1]:
            self.expected_gear = carstate.gear + 1
        # downshift
        elif carstate.rpm < downshift[carstate.gear-2] and carstate.gear > 0:
            self.expected_gear = carstate.gear - 1
        # set gear
        if carstate.gear != self.expected_gear:
            command.gear = self.expected_gear
        # recover gear
        if carstate.gear == 0 or carstate.gear == -1:
            command.gear = 1
        # starting gear
        if not command.gear:
            command.gear = carstate.gear if carstate.gear else 1


    def is_stuck(self, carstate):
        '''
        Check whether car is stuck
        '''
        # count unmoved epochs
        if np.abs(carstate.speed_x) > 1:
            self.epochs_unmoved = 0
        else:
            self.epochs_unmoved += 1
        # check if stuck
        if self.epoch < 200:
            return False
        if self.epochs_unmoved > 80:
            return True
        return False


    def default_drive(self, carstate):
        '''
        Default driving behaviour using Holy Coast
        '''
        command = Command()
        current_state = state_to_vector(carstate)
        command_vector = self.holy_coast.take_wheel(current_state)
        command = vector_to_command(command_vector)
        self.calc_gear(command, carstate)
        apply_force_field(carstate, command)
        self.save_track_position(carstate)
        return command


    def recovery_drive(self, carstate):
        '''
        Recovery driving behaviour
        '''
        command = Command()
        self.epochs_unmoved = 0
        # fix angle
        if np.abs(carstate.angle) > 10:
            recovery_steering = 1
            if carstate.distance_from_center < 0:
                if (carstate.speed_x < -1 and carstate.angle < 0) or (carstate.speed_x > 1 and carstate.angle > 0):
                    command.brake = 1
                    command.accelerator = 0
                else:
                    command.accelerator = 0.5
                    command.brake = 0
            else:
                if (carstate.speed_x < -1 and carstate.angle > 0) or (carstate.speed_x > 1 and carstate.angle < 0):
                    command.brake = 1
                    command.accelerator = 0
                else:
                    command.accelerator = 0.5
                    command.brake = 0
            # set steering
            command.steering = recovery_steering if carstate.distance_from_center > 0 else -recovery_steering
            command.gear = 1 if carstate.angle * carstate.distance_from_center > 0 else -1
        # fix position
        else:
            command.steering = -carstate.distance_from_center
            command.accelerator = .5
            if not self.is_stuck(carstate):
                command.gear = 1
            else:
                command.gear = -1
        # check if recovery complete
        if -10 < carstate.angle < 10 and -1 < carstate.distance_from_center < 1:
            self.recovery = False
        return command


    def cheesy_drive(self, carstate):
        '''
        Opponent obstruction behaviour
        '''
        command = Command()
        angle_change = 2
        self.check_jesus_position(carstate)
        # enter obstruction mode
        if self.cheesus_state == 0:
            # come to a stop
            if carstate.speed_x > 1:
                command.brake = 1
            # once stopped, measure track and enter turning procedure
            else:
                self.track_width = carstate.distances_from_edge[0] + carstate.distances_from_edge[18]
                self.cheesus_state = 1
        # turning procedure
        elif self.cheesus_state == 1:
            if carstate.angle < self.last_angle - angle_change:
                self.last_angle = carstate.angle
                self.cheesus_state = 2
            else:
                command.gear = 1
                if carstate.speed_x < 5:
                    command.accelerator = 1
                if carstate.speed_x > 0:
                    command.steering = 1
                else:
                    command.brake = 1
        # turning procedure
        elif self.cheesus_state == 2:
            if carstate.angle < -89 and carstate.angle > -91:
                self.cheesus_state = 3
            else:
                if carstate.angle < self.last_angle - angle_change:
                    self.last_angle = carstate.angle
                    self.cheesus_state = 1
                else:
                    command.gear = -1
                    if carstate.speed_x < 0:
                        command.steering = -1
                    else:
                        command.brake = 1
                    if carstate.speed_x > -5:
                        command.accelerator = 1
        # exit turning procedure
        elif self.cheesus_state == 3:
            command.brake = 1
            command.steering = 0
            command.accelerator = 0
            if carstate.speed_x > -1:
                self.cheesus_state = 4
        # oscillation forward
        elif self.cheesus_state == 4:
            command.gear = 1
            command.steering = 0
            if carstate.speed_x < 10:
                command.accelerator = 1
            if carstate.speed_x < 0:
                command.brake = 1
            if carstate.distances_from_edge[9] > 0 and carstate.distances_from_edge[9] < 0.40 * self.track_width:
                if self.close_to_jesus:
                    command.accelerator = 1
                else:
                    self.cheesus_state = 5
            if carstate.angle > -89:
                command.steering = -0.1
            if carstate.angle < -91:
                command.steering = 0.1
        # oscillation backward
        elif self.cheesus_state == 5:
            command.gear = -1
            command.steering = 0
            if carstate.speed_x > -10:
                command.accelerator = 1
            if carstate.speed_x > 0:
                command.brake = 1
            if carstate.distances_from_edge[9] < 0 or carstate.distances_from_edge[9] > 0.55 * self.track_width:
                if self.close_to_jesus:
                    command.accelerator = 1
                else:
                    self.cheesus_state = 4
            if carstate.angle > -89:
                command.steering = -0.1
            if carstate.angle < -91:
                command.steering = +0.1
        return command


    def drive(self, carstate: State) -> Command:
        '''
        Main driving method
        '''
        command = Command()
        # Check if car is stuck
        self.recovery = self.is_stuck(carstate) if not self.recovery else self.recovery
        # if car is stuck, go into recovery mode
        if self.recovery:
            command = self.recovery_drive(carstate)
        # if car is not stuck, proceed normally
        else:
            # if not cheesus, drive normally
            if not self.is_cheesus():
                command = self.default_drive(carstate)
            # if car has entered cheesus mode
            else:
                command = self.cheesy_drive(carstate)
        self.epoch += 1
        print("unmoved:", self.epochs_unmoved)
        print("angle:", carstate.angle)
        print("distance center:", carstate.distance_from_center)
        print("speed_x", carstate.speed_x)
        print(command)
        return command


    def is_cheesus(self):
        res = False
        if self.cheesus_state is None:
            if self.epoch % 100 == 0:
                if os.path.isfile(PATH_TRACK_POSITION):
                    self.cheesus_state = 0
        elif self.cheesus_state >= 0:
            res = True
        else:
            res = False
        return res


    def save_track_position(self, carstate):
        # measuring track length
        if carstate.last_lap_time > 0 and not self.track_length:
            self.track_length = carstate.distance_raced
            self.cheesus_state = -1
            print("measured track as:", self.track_length)
        # communicating track position
        if self.epoch % 100 == 0 and self.track_length:
            try:
                with open(PATH_TRACK_POSITION, 'w') as fop:
                    track_position = carstate.distance_raced % self.track_length
                    fop.write(str(track_position))
                    print("saved track position to:", PATH_TRACK_POSITION)
            except:
                print("could not write track position to:", PATH_TRACK_POSITION)


    def check_jesus_position(self, carstate):
        if self.epochCounter % 100 == 0:
            # Jesus is always close by default
            self.close_to_jesus = False
            try:
                with open(PATH_TRACK_POSITION, 'r') as fop:
                    jesus_track_position = int(''.join(fop.readlines()))
                # check if Jesus is close
                jesus_cheesus_distance = np.abs(carstate.distance_from_start - jesus_track_position)
                if jesus_cheesus_distance < 500:
                    self.close_to_jesus = True
            except:
                print("could not read track position from:", PATH_TRACK_POSITION)


    def on_shutdown(self):
        # delete track position file
        try:
            os.remove(PATH_TRACK_POSITION)
        except:
            print("could not remove track position file:", PATH_TRACK_POSITION)
