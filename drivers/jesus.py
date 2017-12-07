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
        self.min_unstuck_dist = .8
        self.max_unstuck_angle = 15
        self.state = 0
        self.rec_count = 0


    def calc_gear(self, command, carstate):
        upshift = np.array([7000, 9050, 9200, 9350, 9400])
        downshift = np.array([3000, 6000, 6700, 7000, 7300])
        if carstate.gear < self.max_gear and carstate.rpm > upshift[carstate.gear-1]:
            self.expected_gear = carstate.gear + 1

        elif carstate.rpm < downshift[carstate.gear-2] and carstate.gear > 0:
            self.expected_gear = carstate.gear - 1

        if carstate.gear != self.expected_gear:
            command.gear = self.expected_gear

        if carstate.gear == 0 or carstate.gear == -1:
            command.gear = 1

        if not command.gear:
            command.gear = carstate.gear or 1



    def drive(self, carstate: State) -> Command:
        command = Command()
        # Check if car is stuck
        if self.is_on_track(carstate):
            current_state = state_to_vector(carstate)

            # NO RECOVERY (default behaviour if car is facing kind of straight)
            if 0 < np.abs(carstate.angle) < 30:
                command_vector = self.holy_ghost.take_wheel(current_state)
                command = vector_to_command(command_vector)
                self.calc_gear(command, carstate)
                apply_force_field(carstate, command)
                if command.accelerator == 0 or carstate.speed_y > 0:
                   command.accelerator = 0.6
                print(command)
                print("position:", carstate.race_position)
                self.state = 0
                return command

            # Steering correction
            # 1)Forwards (car drives forward on track, but does not face toward center of track)
            elif 30 < np.abs(carstate.angle) < 180 and carstate.speed_x > 0:
                    # if car is facing left, steer right
                    if carstate.angle < 0:
                        command.steering = -1
                    # if car is facing right, steer left
                    else:
                        command.steering = 1
                    command.gear = 1
                    command.brake = 0
                    command.accelerator = 0.6
                    self.state = 1

        # RECOVERY MODE (car on track)
        elif not self.is_on_track(carstate):

            # Car stuck on 90 degree angle line
            if 88 < np.abs(carstate.angle) < 92:
                if carstate.angle * carstate.distance_from_center < 0:
                    command.steering = 1
                elif carstate.angle * carstate.distance_from_center > 0:
                    command.steering = -1
                command.gear = -1
                command.brake = 0
                command.accelerator = 0.6
                self.state = 3

            # Car points towards track center and on LHS of track
            if carstate.angle * carstate.distance_from_center > 0 and carstate.distance_from_center > self.min_unstuck_dist:
                if np.abs(carstate.angle) < 88:
                    self.drive_forward_left(command)
                    self.state = (1, 1)

                elif 88 < np.abs(carstate.angle) < 92:
                    self.drive_forward_right(command)
                    self.state = (1, -1)

                elif np.abs(carstate.angle) > 92:
                    self.drive_backward_left(command)
                    self.state = (-1, 1)

            # Car points outwards and on LHS of track
            if carstate.angle * carstate.distance_from_center < 0 and carstate.distance_from_center < -self.min_unstuck_dist:
                if np.abs(carstate.angle) > 92:
                    self.drive_backward_left(command)
                    self.state = (-1, 1)

                elif 88 < np.abs(carstate.angle) < 92:
                    self.drive_backward_right(command)
                    self.state = (-1, -1)

                elif np.abs(carstate.angle) < 88:
                    self.drive_backward_right(command)
                    self.state = (-1, -1)

            # Car points towards track center and on RHS of track
            if carstate.angle * carstate.distance_from_center > 0 and np.abs(carstate.angle) >= 90:
                if np.abs(carstate.angle) > 92:
                    self.drive_forward_right(command)
                    self.state = (1, -1)

                elif 88 < np.abs(carstate.angle) < 92:
                    self.drive_forward_right(command)
                    self.state = (1, -1)

                elif np.abs(carstate.angle) < 88:
                    self.drive_forward_right(command)
                    self.state = (1, -1)

            # Car points outwards and on RHS of track
            if carstate.angle * carstate.distance_from_center < 0 and np.abs(carstate.angle) < 90:
                if np.abs(carstate.angle) > 92:
                    self.drive_backward_right(command)
                    self.state = (-1, -1)

                elif 88 < np.abs(carstate.angle) < 92:
                    self.drive_backward_left(command)
                    self.state = (-1, 1)

                elif np.abs(carstate.angle) < 88:
                    self.drive_backward_right(command)
                    self.state = (-1, -1)

        if self.uphill(carstate):
           command.accelerator = 0.5

        self.epoch += 1
        print("state:", self.state)
        print(command)
        return command

    def uphill(self, carstate: State):
        if carstate.speed_y > 0.5:
            uphill = True
        else:
            uphill =False
        return uphill

    def is_on_track(self, carstate: State):
        if carstate.speed_x < self.max_unstuck_speed and np.abs(carstate.distance_from_center) > self.min_unstuck_dist:
            on_track = False
            self.rec_count = + 1
        else:
            on_track = True
            self.rec_count = 0
        return on_track

    def drive_forward_right(self, command, accelerator=.5):
        command.steering = -1+0.3*self.rec_count
        command.gear = 1
        command.accelerator = accelerator
        command.brake = 0
        print("driving forward right")

    def drive_forward_left(self, command, accelerator=.5):
        command.steering = 1-0.3*self.rec_count
        command.gear = 1
        command.accelerator = accelerator
        command.brake = 0
        print("driving forward left")

    def drive_backward_right(self, command, accelerator=.5):
        command.steering = -1+0.3*self.rec_count
        command.gear = -1
        command.accelerator = accelerator
        command.brake = 0
        print("driving backward right")

    def drive_backward_left(self, command, accelerator=.5):
        command.steering = 1-0.3*self.rec_count
        command.gear = -1
        command.accelerator = accelerator
        command.brake = 0
        print("driving backward left")
