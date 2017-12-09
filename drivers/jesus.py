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
        self.emer_brake = 0
        self.last_gear_upshift = -100


    def calc_gear(self, command, carstate):
        upshift = np.array([7000, 9050, 9200, 9350, 9400])
        downshift = np.array([3000, 6000, 6700, 7000, 7300])

        if carstate.gear < self.max_gear and carstate.rpm > upshift[carstate.gear-1]:
            self.expected_gear = carstate.gear + 1

        elif carstate.rpm < downshift[carstate.gear-2] and carstate.gear > 0:
            self.expected_gear = carstate.gear - 1

        if carstate.gear != self.expected_gear:
            if carstate.gear > self.expected_gear:
                command.gear = self.expected_gear
            elif carstate.gear < self.expected_gear and self.last_gear_upshift < self.epoch+20:
                command.gear = self.expected_gear
                self.last_gear_upshift = self.epoch

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

    def emergency_brake(self, carstate: State, command: Command):

        if carstate.distances_from_edge[9] < carstate.speed_x * 1.3 and carstate.speed_x > 60:
            if command.accelerator > 0.1:
                command.accelerator = 0
            if self.epoch % 2 == 0 and self.emer_brake < 0.8 and command.brake < 0.2:
                self.emer_brake += 0.2
            command.brake = self.emer_brake
            print("Distance from edge", carstate.distances_from_edge[9])
            print("Speed x", carstate.speed_x)
            print("Emergency Brake!!!", carstate.speed_x)
        else:
            self.emer_brake = 0


    def drive(self, carstate: State) -> Command:
        command = Command()
        ANGLE_THRESHOLD = 10
        BRAKING_CENTER_TRACK_THRESHOLD = 0.1
        # Check if car is stuck
        # Steering correction
        # 1)Forwards (car drives forward on track, but does not face toward center of track)
        self.recovery = self.is_stuck(carstate) if not self.recovery else self.recovery
        if self.recovery:
            print("Recovery")
            self.epochs_unmoved = 0
            if np.abs(carstate.angle) > ANGLE_THRESHOLD:
                recovery_steering = 1
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
                command.steering = -0.5 if carstate.distance_from_center > 0 else 0.5
                command.accelerator = .5
                command.gear = -1
            # check if recovery complete
            if -ANGLE_THRESHOLD < carstate.angle < ANGLE_THRESHOLD:
                self.recovery = False
        # NO RECOVERY (default behaviour if car is facing kind of straight)
        else:
            print("Normal")

            current_state = state_to_vector(carstate)
            command_vector = self.holy_ghost.take_wheel(current_state)
            command = vector_to_command(command_vector)
            self.calc_gear(command, carstate)
            #   apply_force_field(carstate, command)
            #self.emergency_brake(carstate, command)

            if np.abs(carstate.distance_from_center) > 1 and carstate.speed_x < 20:
                command.brake = 0
            if carstate.speed_x < -1:
                command.brake = 1
            if -1 < carstate.speed_x < 10 and np.abs(carstate.angle) < 90:
                #print("Speeding assistant")
                command.accelerator = 1
                command.brake = 0
            if carstate.distance_from_center > 1:
                if carstate.angle < 20:
                    command.steering = -0.1
                elif carstate.angle > 30:
                    command.steering = 0.1
                #print("Steering assistant", self.epoch)
            if carstate.distance_from_center < -1:
                if carstate.angle < -20:
                    command.steering = 0.1
                elif carstate.angle < -30:
                    command.steering = -0.1
                #print("Steering assistant", self.epoch)
            print(command)

        self.epoch += 1
        # print("unmoved:", self.epochs_unmoved)
        # print("angle:", carstate.angle)
        # print("distance center:", carstate.distance_from_center)
        # print("speed_x", carstate.speed_x)
        # print(command)
        return command
