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
        self.emer_brake = 0
        self.last_gear_shift = -100
        self.my_gear = 0
        # cheesus
        self.cheesus_state = None
        self.track_width = 0
        self.last_angle = 0
        self.close_to_jesus = False
        #avoidance
        self.avoidance_state = 0
        self.last_acceleration = 0


    def calc_gear(self, command, carstate):
        '''
        Gear switching mechanism
        '''
        # evolved gear shifting RPMs
        upshift = np.array([7000, 9050, 9200, 9350, 9400])
        downshift = np.array([3000, 6000, 6700, 7000, 7300])
        # upshift
        if carstate.gear < self.max_gear and carstate.rpm > upshift[carstate.gear-1] and self.last_gear_shift < self.epoch+20:
            self.my_gear = carstate.gear + 1
            self.last_gear_shift = self.epoch
        # downshift
        elif carstate.rpm < downshift[carstate.gear-2] and carstate.gear > 1 and self.last_gear_shift < self.epoch+20:
            self.my_gear = carstate.gear - 1
            self.last_gear_shift = self.epoch
        # set gear
        else:
            if carstate.gear == 0 or carstate.gear == -1 and self.last_gear_shift < self.epoch+20:
                self.my_gear = 1
                self.last_gear_shift = self.epoch

        command.gear = self.my_gear


    def should_overtake(self, carstate):
        state = state_to_dict(carstate, apply_mask=False)
        # collect distance to opponents in front
        dist_opponents_f = state['opponents'][17]
        dist_opponents_fl = state['opponents'][16]
        dist_opponents_fr = state['opponents'][18]
        # collect edge distances
        dist_edges_f = state['distances_from_edge'][9]
        dist_edges_fl = state['distances_from_edge'][8]
        dist_edges_fr = state['distances_from_edge'][10]
        dist_edges_l = state['distances_from_edge'][0]
        dist_edges_r = state['distances_from_edge'][17]

        dist_threshold = min(carstate.speed_x, 40)
        if np.abs(self.avoidance_state) > 0:
            return True
        if dist_edges_f > 150 and carstate.speed_y < 3:
            # print("enough space in front:", dist_edges_f, dist_edges_fl, dist_edges_fr)
            if min([dist_opponents_f, dist_opponents_fl, dist_opponents_fr]) < dist_threshold:
                if dist_edges_l > 2 or dist_edges_r > 2:
                    # print("opponents in front:", dist_opponents_f, dist_opponents_fl, dist_opponents_fr)
                    dist_opponents_f = dist_opponents_f if dist_opponents_f < dist_threshold else 200
                    dist_opponents_fr = dist_opponents_fr if dist_opponents_fr < dist_threshold else 200
                    dist_opponents_fl = dist_opponents_fl if dist_opponents_fl < dist_threshold else 200
                    if dist_opponents_fl > dist_opponents_fr and dist_edges_l >= 3:
                        self.avoidance_state = 1
                    elif dist_opponents_fl > dist_opponents_fr and dist_edges_l < 3:
                        self.avoidance_state = -1
                    elif dist_opponents_fl < dist_opponents_fr and dist_edges_r >= 3:
                        self.avoidance_state = -1
                    elif dist_opponents_fl < dist_opponents_fr and dist_edges_r < 3:
                        self.avoidance_state = 1
                    else:
                        self.avoidance_state = 1 if dist_edges_l > dist_edges_r else -1
                    return True
        return False


    def is_stuck(self, carstate):
        '''
        Check whether car is stuck
        '''
        # count unmoved epochs
        if np.abs(carstate.speed_x) > 5 and np.abs(carstate.angle) < 90:
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
        print("Normal")

        current_state = state_to_vector(carstate)
        command_vector = self.holy_coast.take_wheel(current_state)
        command = vector_to_command(command_vector)
        self.calc_gear(command, carstate)

        if np.abs(carstate.distance_from_center) > 1 and carstate.speed_x < 20:
            command.brake = 0
        if carstate.speed_x < -1:
            command.brake = 1
        if -1 < carstate.speed_x < 10 and np.abs(carstate.angle) < 90:
            # print("Speeding assistant")
            command.accelerator = 1
            command.brake = 0
        if carstate.distance_from_center > 1:
            if carstate.angle < 20:
                command.steering = -0.1
            elif carstate.angle > 30:
                command.steering = 0.1
                # print("Steering assistant", self.epoch)
        if carstate.distance_from_center < -1:
            if carstate.angle > -20:
                command.steering = 0.1
            elif carstate.angle < -30:
                command.steering = -0.1
                # print("Steering assistant", self.epoch)
        apply_force_field(carstate, command)
        self.save_track_position(carstate)

        return command

    def overtake_drive(self, carstate):
        '''
        Behaviour for overtaking opponents
        '''
        print("Overtaking")
        command = Command()

        state = state_to_dict(carstate, apply_mask=False)
        # collect distance to opponents in front
        dist_opponents_f = state['opponents'][17]
        dist_opponents_l = state['opponents'][8]
        dist_opponents_r = state['opponents'][26]
        # sanity checks
        if min(state['opponents']) > min(carstate.speed_x, 40):
            self.avoidance_state = 0
            print("sanity giving back control (opponents)")
            return command
        if np.abs(carstate.distance_from_center) > .9:
            self.avoidance_state = 0
            print("sanity giving back control (center)")
            return command
        # init avoidance steering
        avoidance_steering = .1 * np.sign(self.avoidance_state)
        # check if already overtaking
        if np.abs(self.avoidance_state) == 1 and np.abs(carstate.angle) > min(10, 250 / carstate.speed_x):
            self.avoidance_state = 2 * np.sign(self.avoidance_state)
        # check if we should steer back
        if np.abs(self.avoidance_state) == 2:
            avoidance_steering *= -1
            # check if car should stop steering
            if np.abs(carstate.angle) < 5:
                avoidance_steering = 0
                self.avoidance_state = 3 * np.sign(self.avoidance_state)
        # check if pass was completed
        if self.avoidance_state == 3 and dist_opponents_l > 10:
            avoidance_steering = 0
            self.avoidance_state = 0
        if self.avoidance_state == -3 and dist_opponents_r > 10:
            avoidance_steering = 0
            self.avoidance_state = 0
        # create command
        command.steering = avoidance_steering
        print("avoidance steering: ", avoidance_steering)
        command.accelerator = 1
        command.gear = self.my_gear
        return command


    def recovery_drive(self, carstate):
        '''
        Recovery driving behaviour
        '''
        ANGLE_THRESHOLD = 10
        BRAKING_CENTER_TRACK_THRESHOLD = 0.1

        command = Command()
        self.epochs_unmoved = 0
        print("Recovery")

        if np.abs(carstate.angle) > ANGLE_THRESHOLD:
            recovery_steering = 0.9
            command.steering = recovery_steering if carstate.distance_from_center > 0 else -recovery_steering
            command.gear = 1 if carstate.angle * carstate.distance_from_center > 0 else -1

            if carstate.distance_from_center < 0:
                if (carstate.speed_x < -1 and carstate.angle < 0) or (carstate.speed_x > 1 and carstate.angle > 0):
                    if carstate.distance_from_center < -BRAKING_CENTER_TRACK_THRESHOLD:
                        command.brake = 1
                        command.accelerator = 0
                    else:
                        command.steering = -command.steering
                else:
                    command.accelerator = 0.5
                    command.brake = 0
            else:
                if (carstate.speed_x < -1 and carstate.angle > 0) or (carstate.speed_x > 1 and carstate.angle < 0):
                    if carstate.distance_from_center > BRAKING_CENTER_TRACK_THRESHOLD:
                        command.brake = 1
                        command.accelerator = 0
                    else:
                        command.steering = -command.steering
                else:
                    command.accelerator = 0.5
                    command.brake = 0
        else:
            command.steering = -1 if carstate.distance_from_center > 0 else 1
            command.accelerator = .5
            command.gear = -1
        # check if recovery complete
        if -ANGLE_THRESHOLD < carstate.angle < ANGLE_THRESHOLD:
            self.recovery = False
            print("The lord hath risen!")
        return command


    def cheesy_drive(self, carstate):
        '''
        Opponent obstruction behaviour
        '''
        command = Command()
        angle_change = 2
        self.check_jesus_position(carstate)
        print("close to jesus:", self.close_to_jesus)
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
            if np.abs(carstate.angle) > 88:
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
        elif self.cheesus_state in [4, 5]:
            command.gear = 1 if self.cheesus_state == 4 else -1
            command.steering = 0
            if np.abs(carstate.speed_x) < 3:
                command.accelerator = 1
            if (self.cheesus_state == 4 and carstate.distance_from_center > .03 * self.track_width)\
                or (self.cheesus_state == 5 and carstate.distance_from_center < -.03 * self.track_width):
                if self.close_to_jesus:
                    command.accelarator = .5
                else:
                    command.brake = 1
                    self.cheesus_state = 5 if self.cheesus_state == 4 else 4
            if np.abs(carstate.angle) < 89:
                command.steering = -0.2
            if np.abs(carstate.angle) > 91:
                command.steering = 0.2
        return command


    def drive(self, carstate: State) -> Command:
        '''
        Main driving method
        '''
        command = Command()
        # if not cheesus, drive normally
        if not self.is_cheesus():
            # Check if car is stuck
            self.recovery = self.is_stuck(carstate) if not self.recovery else self.recovery
            # if car is stuck, go into recovery mode
            if self.recovery:
                command = self.recovery_drive(carstate)
            # if car is not stuck, proceed normally
            else:
                # if car should overtake, go into overtaking mode
                if self.should_overtake(carstate):
                    print("avoidance state:", self.avoidance_state)
                    command = self.overtake_drive(carstate)
                # if car is free of opponents, drive normally
                else:
                    command = self.default_drive(carstate)
        # if car has entered cheesus mode
        else:
            command = self.cheesy_drive(carstate)
        self.last_acceleration = command.accelerator
        self.epoch += 1
        # print("unmoved:", self.epochs_unmoved)
        # print("angle:", carstate.angle)
        # print("distance center:", carstate.distance_from_center)
        # print("speed_x:", carstate.speed_x)
        # print("cheesus:", self.cheesus_state)
        # print(command)
        return command


    def is_cheesus(self):
        res = False
        if self.cheesus_state is None:
            if self.epoch % 25 == 0:
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
            try:
                with open(PATH_TRACK_POSITION, 'w') as fop:
                    track_position = carstate.distance_raced % self.track_length
                    fop.write(str(track_position))
                    print("saved track position to:", PATH_TRACK_POSITION)
            except:
                print("could not write track position to:", PATH_TRACK_POSITION)
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
        if self.epoch % 50 == 0:
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
        if not self.is_cheesus():
            try:
                os.remove(PATH_TRACK_POSITION)
            except:
                print("could not remove track position file:", PATH_TRACK_POSITION)
