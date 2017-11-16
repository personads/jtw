import datetime
import numpy as np
from pytocl.driver import Driver
from pytocl.car import State, Command

class Judas(Driver):
    def __init__(self):
        super().__init__()
        self.epochCounter = 0
        self.steering = 0
        self.data = []

    def save_data(self):
        filename = "data/" + datetime.datetime.now().strftime("%Y%m%d%H%M%S")+".csv"
        import csv
        with open(filename, 'w') as myfile:
            wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
            print("Saved ",len(self.data)," into file")
            for i in range(len(self.data)):
                wr.writerow(self.data[i])
        self.data = []

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
        command = Command()
        self.steer(carstate, 0.0, command)
        # ACC_LATERAL_MAX = 6400 * 5
        # v_x = min(80, math.sqrt(ACC_LATERAL_MAX / abs(command.steering)))
        v_x = 50
        self.accelerate(carstate, v_x, command)
        self.epochCounter += 1
        self.append_data(command,carstate)
        if self.epochCounter % 6000 == 0: self.save_data()
        return command
