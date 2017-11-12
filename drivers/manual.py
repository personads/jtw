import datetime
import numpy as np
from pytocl.driver import Driver
from pytocl.car import State, Command
import keyboard
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim

from utils.rewards import cumulative_reward

class SteeringNN(nn.Module):
    def __init__(self, sensors, first):
        super().__init__()
        self.linear1 = nn.Linear(sensors, first)
        # self.linear2 = nn.Linear(first,second)
        self.optimizer = optim.SGD(self.parameters(), lr=0.01)

    def forward(self, x):
        x = self.linear1(x)

    def update(self, true, calc):
        loss = nn.MSELoss()
        output = loss(true, calc)
        output.backward()
        self.optimizer.step()

    def save(self):
        self.save_state_dict('mytraining.pt')


class ManualDriver(Driver):
    # Override the `drive` method to create your own driver

    def __init__(self):
        super().__init__()
        self.epochCounter = 0
        self.model = SteeringNN(19, 1)
        self.steering = 0
        self.data = []
        self.dataClean = []
        self.reward_function = cumulative_reward


    def check_save_data(self):

        if keyboard.is_pressed("l"):
            self.dataClean.extend(self.data)
            print("Added ", len(self.data), " into clean data")
            self.data = []

        if keyboard.is_pressed("l") and len(self.dataClean) > 200:
            filename = "data/" + datetime.datetime.now().strftime("%Y%m%d%H%M%S")+".csv"
            import csv

            with open(filename, 'w') as myfile:
                wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
                print("Saved ",len(self.dataClean)," into file")
                for i in range(len(self.dataClean)):
                    wr.writerow(self.dataClean[i])
            self.dataClean = []


        if keyboard.is_pressed("j"):
            self.data = []
            print("Clear buffer")

    def calc_steering(self, command):
        STEERING_INTENSITY = 0.5
        if keyboard.is_pressed("w"):
            command.accelerator = 1
        if keyboard.is_pressed("s"):
            command.brake = 1
        if keyboard.is_pressed("a"):
            if self.steering >= 0:
                self.steering = STEERING_INTENSITY
            else:
                self.steering = STEERING_INTENSITY

        if keyboard.is_pressed("d"):
            if self.steering <= 0:
                self.steering = -STEERING_INTENSITY
            else:
                self.steering = -STEERING_INTENSITY

        if not keyboard.is_pressed("a") and not keyboard.is_pressed("d"):
            self.steering = 0
        command.steering = self.steering


    def cal_acceleration(self, command, carstate):
        acceleration = command.accelerator

        if acceleration > 0:
            if abs(carstate.distance_from_center) >= 1:
                # off track, reduced grip:
                acceleration = min(0.4, acceleration)

            command.accelerator = min(acceleration, 1)

            if carstate.rpm > 8000:
                command.gear = carstate.gear + 1

        # else:
        #     command.brake = min(-acceleration,)

        if carstate.rpm < 2500 and carstate.gear != 0:
            command.gear = carstate.gear - 1

        if not command.gear:
            command.gear = carstate.gear or 1

    def append_data(self, command, carstate: State):
        res = []
        res.append(carstate.angle)
        res.append(carstate.current_lap_time)
        res.append(carstate.damage)
        res.append(carstate.distance_from_start)
        res.append(carstate.distance_raced)
        res.append(carstate.fuel)
        res.append(carstate.gear)
        res.append(carstate.last_lap_time)
        res.extend(carstate.opponents)
        res.append(carstate.race_position)
        res.append(carstate.rpm)
        res.append(carstate.speed_x)
        res.append(carstate.speed_y)
        res.append(carstate.speed_z)
        res.extend(carstate.distances_from_edge)
        res.extend(carstate.focused_distances_from_edge)
        res.append(carstate.distance_from_center)
        res.extend(carstate.wheel_velocities)

        res.append(command.accelerator)
        res.append(command.brake)
        res.append(command.gear)
        res.append(command.steering)
        res.append(command.focus)
        self.data.append(res)


    def drive(self, carstate: State) -> Command:
        # Interesting stuff


        command = Command()
        self.calc_steering(command)
        self.cal_acceleration(command,carstate)
        self.epochCounter += 1
        self.append_data(command,carstate)
        self.check_save_data()

        if self.epochCounter % 100 == 0: print("RacingReward:", self.reward_function(carstate), "\n")

        return command
