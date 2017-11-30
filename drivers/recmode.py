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
        #print(carstate.angle)
        #print(carstate.distance_from_center)

        if -1 < carstate.distance_from_center < 1 and -80 < carstate.angle < 80:
            current_state = state_to_vector(carstate)
            command_vector = self.jesus.take_wheel(current_state)
            command = vector_to_command(command_vector)
            self.calc_gear(command, carstate)
            if carstate.speed_x < 0 and carstate.rpm < 1000:
                self.steering = 1
                command.gear = 1
                v_x = 20
                self.accelerate(carstate, v_x, command)

            elif carstate.speed_x > 0 and carstate.rpm < 1000:
                self.steering = -1
                command.gear = 1
                v_x = 20
                self.accelerate(carstate, v_x, command)

            self.epoch += 1
            print(command)
            return command

        # Reposition car on track
        if -1 < carstate.distance_from_center < 1 and -180 < carstate.angle < -80:
                self.steeringering = -1
                v_x = 20
                self.accelerate(carstate, v_x, command)
                command.gear = 1
                print('recmode1')

        elif -1 < carstate.distance_from_center < 1 and 80 < carstate.angle < 180:
                self.steeringering = 1
                v_x = 20
                self.accelerate(carstate, v_x, command)
                command.gear = -1
                print('recmode2')

        # Car on right side of track
        elif carstate.distance_from_center < -1:
            if 0 < carstate.angle <= 90:
                self.steeringering = 1
                v_x = 20
                self.accelerate(carstate, v_x, command)
                command.gear = -1
                print('recmode3')

            elif 90 < carstate.angle < 180:
                self.steering = 1
                v_x = 20
                self.accelerate(carstate, v_x, command)
                command.gear = -1
                print('recmode4')


            elif -90 < carstate.angle <= 0:
                self.steering = 0.5
                v_x = 20
                self.accelerate(carstate, v_x, command)
                command.gear = 1
                print('recmode5')

            elif -180 < carstate.angle <= -90:
                self.steering = 1
                v_x = 20
                self.accelerate(carstate, v_x, command)
                command.gear = 1
                print('recmode6')


        # Car on left side of track
        elif carstate.distance_from_center > 1:
            if -180 < carstate.angle <= -90:
                self.steering = -1
                v_x = 15
                self.accelerate(carstate, v_x, command)
                command.gear = -1
                print('recmode7')

            elif -90 < carstate.angle < 0:
                self.steering = 1
                v_x = 30
                self.accelerate(carstate, v_x, command)
                command.gear = 2
                print('recmode8')

            elif 0 < carstate.angle < 90:
                self.steering = 1
                v_x = 20
                self.accelerate(carstate, v_x, command)
                command.gear = 1
                print('recmode9')

            elif 90 < carstate.angle < 180:
                self.steering = -1
                v_x = 20
                self.accelerate(carstate, v_x, command)
                command.gear = 1
                print('recmode10')

        return command


