import datetime
import numpy as np
from pytocl.driver import Driver
from pytocl.car import State, Command
import keyboard

from utils.swarm import *

class ManualDriver(Driver):
    # Override the `drive` method to create your own driver

    def __init__(self):
        super().__init__()
        self.epochCounter = 0
        self.expected_gear = 0
        self.steering = 0
        self.data = []
        self.dataClean = []
        self.max_gear = 6

    def check_save_data(self):

        if keyboard.is_pressed("l"):
            self.dataClean.extend(self.data)
            print("Added", len(self.data), "into clean data")
            self.data = []

        if keyboard.is_pressed("j"):
            self.data = []
            print("Clear buffer")

    def calc_steering(self, command):
        STEERING_INTENSITY = 0.4
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

        if carstate.rpm > 7000 and carstate.gear < self.max_gear:
            self.expected_gear = carstate.gear + 1

        if carstate.rpm < 3000 and carstate.gear != 0:
            self.expected_gear = carstate.gear - 1

        if carstate.gear != self.expected_gear:
            command.gear = self.expected_gear
            # print("attempting gear change from", carstate.gear, "to", self.expected_gear)

        if not command.gear:
            command.gear = carstate.gear or 1
        if keyboard.is_pressed("h"):
            command.gear = carstate.gear - 1
        if keyboard.is_pressed("g"):
            command.gear = carstate.gear + 1

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

    def on_shutdown(self):
        if len(self.dataClean) > 200:
            filename = "data/" + datetime.datetime.now().strftime("%Y%m%d%H%M%S")+".csv"
            import csv
            with open(filename, 'w') as myfile:
                wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
                for i in range(len(self.dataClean)):
                    wr.writerow(self.dataClean[i])
            print("Saved ",len(self.dataClean)," into file")

    def drive(self, carstate: State) -> Command:
        # Interesting stuff
        command = Command()
        self.calc_steering(command)
        self.cal_acceleration(command,carstate)
        apply_force_field(carstate, command)
        self.epochCounter += 1
        self.append_data(command,carstate)
        self.check_save_data()
        return command
