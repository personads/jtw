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
        self.recovery = False
        self.epochs_unmoved = 0


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
            command.gear = carstate.gear if carstate.gear else 1

    def is_stuck(self, carstate):
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

    def drive(self, carstate: State) -> Command:
        command = Command()
        # Check if car is stuck
        # Steering correction
        # 1)Forwards (car drives forward on track, but does not face toward center of track)
        self.recovery = self.is_stuck(carstate) if not self.recovery else self.recovery
        if self.recovery:
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
                command.steering = recovery_steering if carstate.distance_from_center > 0 else -recovery_steering
                command.gear = 1 if carstate.angle * carstate.distance_from_center > 0 else -1
            else:
                command.steering = -carstate.distance_from_center
                command.accelerator = .5
                command.gear = 1
            # check if recovery complete
            if -10 < carstate.angle < 10 and -1 < carstate.distance_from_center < 1:
                self.recovery = False
        # NO RECOVERY (default behaviour if car is facing kind of straight)
        else:
            current_state = state_to_vector(carstate)
            command_vector = self.holy_ghost.take_wheel(current_state)
            command = vector_to_command(command_vector)
            self.calc_gear(command, carstate)
            apply_force_field(carstate, command)
        self.epoch += 1
        print("unmoved:", self.epochs_unmoved)
        print("angle:", carstate.angle)
        print("distance center:", carstate.distance_from_center)
        print("speed_x", carstate.speed_x)
        print(command)
        return command

    def uphill(self, carstate: State):
        if carstate.speed_z > 0.5:
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
